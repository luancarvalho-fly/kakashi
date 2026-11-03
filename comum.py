# -*- coding: utf-8 -*-
"""As peças do olho.py que não dependem do sistema (porte pro Mac, 02/11/2026): o resumo_pc.py lê gravações por aqui,
sem carregar o ctypes.windll do olho.py. O olho.py importa tudo daqui de volta, então quem usa olho.X continua igual.

- historico_chrome / links_da_sessao / baixar_refs ... páginas abertas no Chrome e a imagem dos pins
- t_da_sessao / fim_da_sessao ... o relógio da gravação
- duracao / ler_wav ... ffprobe e wav
03/11: juntado no Kakashi do Luan a partir das funções ATUAIS do olho.py dele (o comum.py do porte vinha da versão de 02/11
01h43 e trazia de volta a folga de 2 s antes / 5 s depois que ele mandou tirar às 15h41: «não é pra você pegar coisa anterior ou
coisa depois»). As partes do Mac (Safari, aba da frente, perfil do Chrome no Mac) são do porte do Gu.
"""
import datetime, html, json, os, re, shutil, sqlite3, subprocess, sys, tempfile, time
import urllib.request

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
SEM_JANELA = 0x08000000 if os.name == "nt" else 0     # CREATE_NO_WINDOW só existe no Windows (fora dele o subprocess recusa)

# ------------------------------------------------------------------ Chrome: páginas abertas + imagens dos pins
def _chrome_hist():
    """pacote da Fly: o perfil do Chrome mais usado DESTA pessoa (o History mexido por último)"""
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data")
    try:
        cands = [os.path.join(base, d, "History") for d in os.listdir(base) if os.path.isfile(os.path.join(base, d, "History"))]
    except OSError:
        cands = []
    return max(cands, key=os.path.getmtime) if cands else os.path.join(base, "Default", "History")


CHROME_HIST = _chrome_hist()
if sys.platform == "darwin":      # porte pro Mac (Gu, 02/11): o perfil do Chrome mais usado no Mac
    _base_mac = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    try:
        _cands = [os.path.join(_base_mac, d, "History") for d in os.listdir(_base_mac) if os.path.isfile(os.path.join(_base_mac, d, "History"))]
    except OSError:
        _cands = []
    CHROME_HIST = max(_cands, key=os.path.getmtime) if _cands else os.path.join(_base_mac, "Default", "History")


def historico_chrome(ini_epoch, fim_epoch):
    """[{epoch, url, titulo}] das visitas entre os dois instantes (cópia do History; a hora bate com o relógio da gravação)"""
    tmp = os.path.join(tempfile.gettempdir(), "kakashi_history_%d.sqlite" % os.getpid())
    for src in (CHROME_HIST, CHROME_HIST.replace("\\\\localhost\\C$", "C:")):
        try:
            shutil.copyfile(src, tmp)
            break
        except OSError:
            continue
    else:
        raise OSError("não consegui copiar o histórico do Chrome")
    try:
        con = sqlite3.connect(tmp)
        a = int((ini_epoch + 11644473600) * 1e6); b = int((fim_epoch + 11644473600) * 1e6)
        linhas = con.execute("SELECT v.visit_time, u.url, u.title FROM visits v JOIN urls u ON u.id = v.url "
                             "WHERE v.visit_time BETWEEN ? AND ? ORDER BY v.visit_time", (a, b)).fetchall()
        con.close()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    out = []
    for vt, url, tit in linhas:
        if re.match(r"(chrome|about|chrome-extension|devtools|edge)://", url or "") or url.startswith("chrome-search:"):
            continue
        if out and out[-1]["url"] == url and vt / 1e6 - 11644473600 - out[-1]["epoch"] < 3:
            continue                     # redirecionamento / recarregou na hora: uma visita só
        out.append({"epoch": round(vt / 1e6 - 11644473600, 2), "url": url, "titulo": tit or ""})
    return out


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"


def _baixar(url, t=20, limite=40_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.read(limite), r.headers.get("Content-Type", "")


def og_image(url):
    pagina, _ = _baixar(url, limite=3_000_000)
    s = pagina.decode("utf-8", "replace")
    for pad in (r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"',
                r'<meta[^>]+name="og:image"[^>]+content="([^"]+)"'):
        m = re.search(pad, s, re.I)
        if m:
            return html.unescape(m.group(1))
    return None


def imagem_do_pin(pin_id, url):
    """A página do pin NÃO traz og:image (21/10: o Pinterest manda só o app em JS). O widget público dá a imagem dos pins
    públicos; pin de pasta SECRETA (a APP_PESSOAL dele) volta vazio → None (fica valendo o print nativo da página)."""
    try:
        b, _ = _baixar("https://widgets.pinterest.com/v3/pidgets/pins/info/?pin_ids=" + pin_id)
        d = (json.loads(b).get("data") or [None])[0]
        if d and d.get("images"):
            maior = max(d["images"].values(), key=lambda v: v.get("width") or 0)
            return maior.get("url")
    except Exception:
        pass
    try:
        return og_image(url)
    except Exception:
        return None


def baixar_refs(links, pasta):
    """Pin do Pinterest = baixa a imagem (tenta a original); link direto de imagem = baixa. Marca link["ref"] = _refs\\arquivo.
    Pin privado: link["ref_erro"] = "pin privado" (a imagem não sai sem o login dele; o print da página fica valendo)."""
    dest = os.path.join(pasta, "_refs")
    feitos = {}
    for l in links:
        u = l["url"]
        m = re.search(r"pinterest\.[a-z.]+/pin/([\w-]+)", u)
        img = nome = None
        try:
            if m:
                nome = "pin_" + m.group(1)
                if nome in feitos:
                    if feitos[nome]:
                        l["ref"] = feitos[nome]
                    else:
                        l["ref_erro"] = "pin privado"
                    continue
                feitos[nome] = None
                img = imagem_do_pin(m.group(1), u)
                if not img:
                    l["ref_erro"] = "pin privado"
                    continue
            elif re.search(r"\.(jpe?g|png|webp|gif)(\?|$)", u, re.I) or "i.pinimg.com" in u:
                nome = "img_" + hashlib.sha1(u.encode()).hexdigest()[:10]
                img = u
            if not img:
                continue
            tentativas = [img]
            if "i.pinimg.com" in img and "/originals/" not in img:
                tentativas.insert(0, re.sub(r"i\.pinimg\.com/[^/]+/", "i.pinimg.com/originals/", img))
            for tent in tentativas:
                try:
                    dados, tipo = _baixar(tent)
                except Exception:
                    continue
                if not dados or not tipo.startswith("image"):
                    continue
                ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(tipo.split(";")[0], ".jpg")
                os.makedirs(dest, exist_ok=True)
                with open(os.path.join(dest, nome + ext), "wb") as f:
                    f.write(dados)
                l["ref"] = feitos[nome] = "_refs\\" + nome + ext
                l["ref_url"] = tent
                break
        except Exception as e:
            l["ref_erro"] = str(e)[:120]
    return links


def t_da_sessao(epoch, meta):
    """segundo da gravação de um instante do relógio de parede. Sessão PC: epoch − início. Olho do Premiere (23/10): relógio
    do PAINEL, sem as pausas nem os pedaços apagados (relogio_trechos = [[inicio, t0, fim], ...] das partes que ficaram);
    instante numa pausa ou num pedaço apagado = o segundo do corte (igual ao t_gravacao do CORRETOR)"""
    ini = meta.get("inicio_epoch") or 0
    tre = meta.get("relogio_trechos")
    if not tre:
        return epoch - ini
    for e0, t0, e1 in tre:
        if epoch < e0:
            return t0
        if epoch <= e1:
            return t0 + (epoch - e0)
    e0, t0, e1 = tre[-1]
    return t0 + (e1 - e0)


def fim_da_sessao(meta):
    """epoch do fim (o olho do Premiere guarda fim_epoch: com pausa, início + duração não chega no fim)"""
    return meta.get("fim_epoch") or (meta.get("inicio_epoch") or 0) + (meta.get("duracao_s") or 0)


def links_da_sessao(pasta, meta, baixar=True):
    """lê o histórico do Chrome no intervalo EXATO da sessão → links.json na pasta; devolve a lista
    (02/11: tirada a folga de 2 s antes e 5 s depois; ele: "não é pra você pegar coisa anterior ou coisa depois")"""
    ini = meta.get("inicio_epoch") or 0
    fim = fim_da_sessao(meta)
    if sys.platform == "darwin":
        # Mac (porte do Gu, 02/11): o histórico (Chrome e Safari) só com o Acesso Total ao Disco; sem ele, os endereços que o próprio
        # navegador deu a cada janela/aba nova (eventos "janela" com "url"). Os dois juntos, sem repetir. Também do atalho ao atalho.
        try:
            links = historico_chrome(ini, fim)
        except Exception as e:
            links = []; erro = e
        else:
            erro = None
        vistos = {l["url"] for l in links}
        try:
            for linha in open(os.path.join(pasta, "eventos.jsonl"), encoding="utf-8"):
                ev = json.loads(linha) if linha.strip() else {}
                if ev.get("tipo") == "janela" and ev.get("url") and ev["url"] not in vistos:
                    vistos.add(ev["url"])
                    links.append({"epoch": round(ini + ev.get("t", 0), 2), "url": ev["url"], "titulo": ev.get("titulo", ""),
                                  "navegador": ev.get("app", ""), "de": "aba da frente"})
        except OSError:
            pass
        if erro is not None and not links:
            raise erro
        links.sort(key=lambda l: l["epoch"])
    else:
        links = historico_chrome(ini, fim)
    for l in links:
        l["t"] = round(t_da_sessao(l["epoch"], meta), 2)
    if baixar:
        baixar_refs(links, pasta)
    with open(os.path.join(pasta, "links.json"), "w", encoding="utf-8") as f:
        json.dump({"lido_em": datetime.datetime.now().replace(microsecond=0).isoformat(), "links": links}, f, ensure_ascii=False, indent=1)
    return links

SAFARI_HIST = os.path.expanduser("~/Library/Safari/History.db")


def historico_safari(ini_epoch, fim_epoch):
    """Mac: [{epoch, url, titulo}] do Safari (History.db + o -wal, onde ficam as visitas mais novas; precisa do Acesso Total ao
    Disco). O relógio do Safari conta desde 01/01/2001."""
    d = tempfile.mkdtemp(prefix="kakashi_safari_")
    try:
        for suf in ("", "-wal", "-shm"):
            if os.path.isfile(SAFARI_HIST + suf):
                shutil.copyfile(SAFARI_HIST + suf, os.path.join(d, "History.db" + suf))
        con = sqlite3.connect(os.path.join(d, "History.db"))
        linhas = con.execute("SELECT v.visit_time, i.url, v.title FROM history_visits v JOIN history_items i ON i.id = v.history_item "
                             "WHERE v.visit_time BETWEEN ? AND ? ORDER BY v.visit_time",
                             (ini_epoch - 978307200, fim_epoch - 978307200)).fetchall()
        con.close()
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out = []
    for vt, url, tit in linhas:
        ep = round(vt + 978307200, 2)
        if out and out[-1]["url"] == url and ep - out[-1]["epoch"] < 3:
            continue
        out.append({"epoch": ep, "url": url, "titulo": tit or "", "navegador": "Safari"})
    return out


if sys.platform == "darwin":
    _historico_so_chrome = historico_chrome

    def historico_chrome(ini_epoch, fim_epoch):
        """Mac: o Chrome E o Safari juntos, na ordem do relógio. Só falha se os dois falharem (sem o Acesso Total ao Disco)."""
        out, erros = [], []
        for nome, f in (("Chrome", _historico_so_chrome), ("Safari", historico_safari)):
            try:
                out += f(ini_epoch, fim_epoch)
            except Exception as e:
                erros.append("%s: %s" % (nome, e))
        if len(erros) == 2:
            raise OSError("não consegui ler o histórico do Chrome nem do Safari (falta o Acesso Total ao Disco?): " + " · ".join(erros))
        return sorted(out, key=lambda l: l["epoch"])


def duracao(arq):
    try:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", arq],
                           capture_output=True, timeout=30, creationflags=SEM_JANELA)
        return float(r.stdout.decode().strip())
    except Exception:
        return 0.0


def ler_wav(arq):
    """(bytes PCM, taxa, canais, largura). Aguenta wav de processo morto (tamanho 'desconhecido' no cabeçalho)."""
    with open(arq, "rb") as f:
        b = f.read()
    i = b.find(b"fmt ")
    canais, taxa = int.from_bytes(b[i + 10:i + 12], "little"), int.from_bytes(b[i + 12:i + 16], "little")
    larg = int.from_bytes(b[i + 22:i + 24], "little") // 8
    j = b.find(b"data", i)
    dados = b[j + 8:]
    return dados[: len(dados) // (canais * larg) * canais * larg], taxa, canais, larg
