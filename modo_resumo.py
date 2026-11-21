# -*- coding: utf-8 -*-
"""MODO RESUMO do Kakashi (15/11/2026) — o 3º modo, ao lado do RÁPIDO e do PROFUNDO.

Pedido dele (15/11 ~20h20): «tem o modo resumo, aí... tem o modo rápido e o profundo... eu ligo o Kakashi, falo tudo bonitinho... quando
termina, já cola tudo pro Claude... print com links com a minha transcrição... de uma maneira inteligente... e rápida... mais rápido que
uma leitura do Kakashi rápido» · «tudo que foi print que eu tirei, desenhei, copiei... mas não cheguei a colar... ou link que eu mostrei».

O que faz: lê a gravação que acabou de concluir (PC, ou o _olho de uma do Premiere) e monta UM texto, na ordem do relógio:
- a fala dele: 15/11 ~21h (ele: «isso é muito demorado... algum fluxo que demore 10 segundos... não pode deixar mais rápido, mas ficar
  burro») pelo Whisper do DITADO (whisper-server 8178 do OpenWhispr: o MESMO large-v3-turbo, já carregado — 3:46 em 4,7 s × 97 s no
  processador, 97% das palavras iguais) com as regras do Tandera (rapido=True). Com o Premiere aberto a placa é dele: vai pelo
  processador, a menos que config.json "resumo_placa_com_premiere": true. 8178 fora do ar = o processador de antes (fala_da_sessao).
  A rápida fica em fala_resumo.json (o PROFUNDO continua transcrevendo do jeito dele);
- no minuto em que aconteceu: o print que ele copiou (Page Down / Win+Shift+S / imagem copiada), o desenho que fez na tela,
  o link e o texto que copiou, os arquivos que copiou, o que terminou de baixar no Downloads e as páginas do Chrome em que ele
  clicou/parou (a extensão manda na hora — 15/11: o histórico do Chrome esperava 12 s e trazia visita que não era dele, ex. buscas
  no Gmail no meio de uma correção do Fly X-tudo; sem a extensão, o links.json se já existir, sem esperar).
Fica de fora: o ditado do OpenWhispr (já foi colado e a voz dele já está na fala) e o que o próprio Kakashi copiou («/kakashi»).
Sem modelo nenhum resumindo por cima: quem resume é o Claude que recebe (mais rápido, sem placa, e nenhuma fala dele se perde).
As imagens vão pelo CAMINHO no texto (o Claude Code abre o arquivo); nada sobe pra internet.

Saída: RESUMO.md na pasta da gravação (a 1ª) — é o texto que o Kakashi cola.
  pythonw modo_resumo.py <pasta> [<pasta> ...] [--andamento <arquivo.json>]   (código 0 = RESUMO.md pronto; 2 = nenhuma pasta)
  --andamento: a barra do Kakashi lê dali a etapa e a previsão («COMPILANDO 60% · PRONTO EM 3 S»).
"""
import datetime, json, os, re, sys, time
os.environ["TANDERA_PEDIDO_DELE"] = "1"     # 20/11 (otimização): o resumo é ação DELE na hora — nunca «trabalho de fundo» pro porteiro da placa

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

ESPERA_FALA_S = 240        # o concluir junta pedaços/replay antes de gravar duracao_s (o do Premiere espera o painel até 3 min)
ESPERA_LINKS_S = 60        # o concluir grava "links" ~12 s depois (o histórico do Chrome demora a ir pro disco)
GRUDA_S = 40               # frases seguidas viram um parágrafo até 40 s (ou até aparecer um print/link no meio)
DESENHO_JUNTA_S = 4        # traços em sequência (4 s) = um desenho só: fica o print do último (o desenho inteiro)
TEXTO_MAX = 700            # texto copiado comprido: o começo no resumo, o inteiro no arquivo
DITADO = "http://127.0.0.1:8178"   # o whisper-server do OpenWhispr (o ditado): large-v3-turbo já carregado
# previsão do tempo da fala (medido 15/11 em 3:46: 4,7 s no 8178, 96 s no processador) — só pra barra dizer «pronto em X»
TAXA = {"ditado": (0.02, 0.8), "processador": (0.43, 3.0)}
ANDAMENTO = None           # o arquivo que a barra lê (--andamento)


def andamento(**k):
    """grava a etapa e a previsão pra barra do Kakashi (nunca derruba o resumo)"""
    if not ANDAMENTO:
        return
    try:
        try:
            d = json.load(open(ANDAMENTO, encoding="utf-8"))
        except (OSError, ValueError):
            d = {}
        d.update(k, agora=time.time())
        tmp = ANDAMENTO + ".tmp"
        json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(tmp, ANDAMENTO)
    except Exception:
        pass


def cfg():
    try:
        return json.load(open(os.path.join(AQUI, "config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _tandera(resumo_pc):
    """o pacote do Tandera (no PC dele: resumo_pc.TANDERA; no pacote do time: resumo_pc.pasta_tandera())"""
    f = getattr(resumo_pc, "pasta_tandera", None)
    pasta = f() if callable(f) else getattr(resumo_pc, "TANDERA", None)
    if not pasta:
        return None
    if pasta not in sys.path:
        sys.path.insert(0, pasta)
    import tandera
    return tandera


def ditado_no_ar():
    import urllib.request
    try:
        urllib.request.urlopen(DITADO + "/", timeout=1.5).read(64)
        return True
    except Exception:
        return False


def como_transcrever(resumo_pc):
    """«ditado» (8178, rápido) ou «processador» (o de sempre).
    20/11 (otimização, item 2 — ele: «é pra rodar tudo na placa de video po... tem que funcionar mesmo eu usando o Premiere»): o Whisper
    do ditado JÁ ESTÁ carregado na placa (residente): usar ele não pede memória nova, então o Premiere aberto não tira mais o resumo do
    ditado. Só vai pro processador se o ditado estiver fora do ar, ou se for trabalho de fundo (o Claude sozinho) com ele editando."""
    if not ditado_no_ar():
        return "processador", "o ditado (8178) está fora do ar"
    try:
        tandera = _tandera(resumo_pc)
        from tandera import porteiro
        if porteiro.fundo() and not porteiro.liberada_pro_fundo():
            return "processador", "trabalho de fundo com o Premiere %s (regra 9)" % porteiro.premiere()
    except Exception as e:
        return "processador", "Tandera: %r" % e
    return "ditado", ""


def fala_rapida(p, desloc, resumo_pc):
    """a fala pelo Whisper do ditado, com as regras do Tandera; cache em fala_resumo.json (refaz se o fala.wav mudou).
    20/11 noite: a fala transcrita DURANTE a gravação (_ao_vivo\\fala.json, ver AoVivo) vem primeiro — aí não transcreve nada."""
    wav = os.path.join(p, "fala.wav")
    if not os.path.isfile(wav):
        return []
    viva = getattr(resumo_pc, "fala_ao_vivo", lambda _p: None)(p)
    if viva is not None:
        return [(a + desloc, b + desloc, tx, False) for a, b, tx in viva]
    cache = os.path.join(p, "fala_resumo.json")
    marca = [os.path.getsize(wav), int(os.path.getmtime(wav))]
    try:
        c = json.load(open(cache, encoding="utf-8"))
        if c.get("marca") != marca:
            raise ValueError
        segs = c["segmentos"]
    except (OSError, ValueError, KeyError):
        tandera = _tandera(resumo_pc)
        # 8178 caiu no meio = o Whisper do Tandera NA PLACA (20/11 noite; era «cpu» — a lei dele de 20/11: «é pra rodar tudo na placa de
        # video... tem que funcionar mesmo eu usando o Premiere»; quem divide a placa com o Premiere é o porteiro do Tandera)
        r = tandera.transcrever(wav, idioma="pt", rapido=True, dispositivo="cuda")
        inventadas = getattr(resumo_pc, "INVENTADAS", r"$^")
        segs = [[s["ini"], s["fim"], s["txt"]] for s in r["segmentos"] if not re.fullmatch(inventadas, s["txt"].strip())]
        json.dump({"marca": marca, "via": r.get("via") or "?", "segmentos": segs}, open(cache, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)
    return [(a + desloc, b + desloc, tx, False) for a, b, tx in segs]


def log(msg):
    try:
        with open(os.environ.get("KAKASHI_LOG") or os.path.join(AQUI, "kakashi.log"), "a", encoding="utf-8") as f:   # 20/11: o teste aponta outro
            f.write(datetime.datetime.now().strftime("%d/%m %H:%M:%S") + " resumo: " + msg + "\n")
    except OSError:
        pass


def mmss(t):
    t = max(0, int(t))
    return "%d:%02d" % (t // 60, t % 60)


def ler_meta(p):
    try:
        return json.load(open(os.path.join(p, "sessao.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def pasta_da_fala(p):
    """a pasta que tem a gravação do PC: ela mesma ou o _olho (Premiere). None = não é gravação que dá pra resumir (ex.: a do app de cartões)"""
    for c in (p, os.path.join(p, "_olho")):
        if os.path.isfile(os.path.join(c, "eventos.jsonl")) and (ler_meta(c).get("tipo") == "pc" or os.path.isfile(os.path.join(c, "fala.wav"))):
            return c
    if os.path.isdir(os.path.join(p, "_olho")):        # Premiere: o _olho ainda não virou sessão (o painel está juntando)
        return os.path.join(p, "_olho")
    return None


def esperar(p, chave, limite):
    t0 = time.time()
    while time.time() - t0 < limite:
        m = ler_meta(p)
        if m.get("descartada"):
            return None
        if chave in m and (chave != "duracao_s" or os.path.isfile(os.path.join(p, "fala.wav"))):
            return m
        time.sleep(0.5)
    return ler_meta(p)


def pasta_downloads():
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as k:
                return winreg.QueryValueEx(k, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        except OSError:
            pass
    return os.path.join(os.path.expanduser("~"), "Downloads")


def baixados(ini, fim):
    """o que terminou de baixar no Downloads durante a gravação (o áudio do WhatsApp, o arquivo salvo)"""
    pasta, out = pasta_downloads(), []
    try:
        nomes = os.listdir(pasta)
    except OSError:
        return out
    for n in nomes:
        if n.startswith("~") or n.lower().endswith((".crdownload", ".tmp", ".part", ".partial", ".download", ".ini")):
            continue
        c = os.path.join(pasta, n)
        try:
            m = os.path.getmtime(c)
        except OSError:
            continue
        if os.path.isfile(c) and ini <= m <= fim + 3:
            out.append((m - ini, c))
    return sorted(out)


NAVEGADORES = ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "arc.exe", "google chrome", "safari", "firefox")
IMAGENS_MAX = 20          # 16/11: o máximo de imagens coladas numa mensagem (o Claude aceita até 20 anexos por mensagem)
MARCA_IMG = re.compile(r"⟦IMG:(.+?)⟧")


def img(caminho):
    """16/11: a imagem que vai COLADA no Claude (no montar vira «imagem N»)"""
    return "⟦IMG:%s⟧" % caminho


def itens_da_sessao(p, meta, rep):
    """[(t, linha)] do que ele copiou, desenhou, baixou e abriu — no relógio da sessão"""
    evs = []
    for l in open(os.path.join(p, "eventos.jsonl"), encoding="utf-8", errors="replace"):
        if l.strip("\x00 \r\n\t"):
            try:
                evs.append(json.loads(l))
            except ValueError:
                pass
    itens, vistos = [], set()

    def add(t, linha, chave):
        if chave in vistos or t < rep:
            return
        vistos.add(chave)
        itens.append((t, linha))

    A = lambda rel: os.path.normpath(os.path.join(p, rel))      # noqa: E731
    videos = []

    def _baixa(u):
        """20/11: link de vídeo (YouTube, Insta, TikTok...) → entra na fila de baixar e a linha diz onde vai cair"""
        try:
            import baixar_link
        except Exception:
            return ""
        if not baixar_link.eh_video(u) or cfg().get("baixar_links") is False:
            return ""
        if u not in videos:
            videos.append(u)
        return "  → ⬇ vídeo e som baixando em %s (andamento no estado.json de lá)" % os.path.join(p, "baixados")
    # o que ele copiou
    for e in evs:
        if e.get("tipo") != "copiou":
            continue
        app, oq, t = (e.get("app") or "").lower(), e.get("o_que"), float(e.get("t", 0))
        if "whispr" in app or "whisper" in app:                  # ditado: já foi colado, e a voz já está na fala
            continue
        if oq in ("imagem", "captura") and e.get("arquivo"):
            de = "print que tirei" if (oq == "captura" or app.startswith("pythonw") or app.startswith("python")) else "imagem que copiei"
            add(t, "🖼 %s: %s" % (de, img(A(e["arquivo"]))), ("img", e["arquivo"]))
        elif oq == "arquivos" and e.get("arquivos"):
            for c in e["arquivos"]:
                add(t, "📎 arquivo que copiei: %s" % c, ("arq", c))
        elif oq == "link" and e.get("texto"):
            u = e["texto"].strip()
            add(t, "🔗 link que copiei: %s%s" % (u, _baixa(u)), ("url", u))
        elif oq == "texto" and e.get("texto"):
            tx = e["texto"].strip()
            if tx.startswith("/kakashi") or app.startswith("pythonw"):   # o que o próprio Kakashi copiou
                continue
            extra = ""
            if len(tx) > TEXTO_MAX:
                tx = tx[:TEXTO_MAX].rstrip() + "…"
                extra = " (inteiro em %s)" % A(e["arquivo"]) if e.get("arquivo") else ""
            add(t, "📋 texto que copiei%s: «%s»" % (extra, tx.replace("\r", "")), ("txt", tx))
    # o que ele desenhou na tela (a barra): o print logo depois do traço; traços seguidos = um desenho, vale o último print
    tracos = sorted(float(e.get("t", 0)) for e in evs if e.get("tipo") == "traco")
    prints_traco = sorted((float(e.get("t", 0)), e["arquivo"]) for e in evs
                          if e.get("tipo") == "print" and e.get("motivo") == "traco" and e.get("arquivo"))
    grupos = []
    for t in tracos:
        if grupos and t - grupos[-1][-1] <= DESENHO_JUNTA_S:
            grupos[-1].append(t)
        else:
            grupos.append([t])
    for g in grupos:
        cands = [(tp, a) for tp, a in prints_traco if g[0] - 0.5 <= tp <= g[-1] + DESENHO_JUNTA_S]
        if cands:
            tp, a = cands[-1]
            add(g[0], "✏️ desenhei na tela%s: %s" % ((" (%d traços)" % len(g)) if len(g) > 1 else "", img(A(a))), ("des", a))
    # o que terminou de baixar
    ini = meta.get("inicio_epoch") or 0
    fim = (meta.get("fim_epoch") or ini + (meta.get("duracao_s") or 0))
    for t, c in baixados(ini, fim):
        add(t, "⬇️ baixei: %s" % c, ("arq", c))
    # as páginas do Chrome: onde ele clicou/parou (a extensão, na hora); sem a extensão, o links.json se já existir (sem esperar)
    # 16/11 12:35 (ele: «ta meio zuado esse resumo... foi link do fly xtudo pra nada»): a extensão manda «parou» até de uma aba que
    # está ATRÁS (o mouse passou por cima da janela do Fly X-tudo enquanto ele usava o AppPessoal). Agora a página só entra se ele CLICOU
    # nela ou se ela era a janela da FRENTE naquele segundo (o último evento «janela» antes, Chrome com o mesmo título).
    janelas = sorted((float(e.get("t", 0)), (e.get("app") or "").lower(), e.get("titulo") or "") for e in evs if e.get("tipo") == "janela")

    def na_frente(t, titulo):
        ant = [j for j in janelas if j[0] <= t + 0.3]
        if not ant or not titulo:
            return False
        _tj, app, tit = ant[-1]
        if app != "chrome.exe" and app not in NAVEGADORES:
            return False
        a, b = tit.strip().lower(), titulo.strip().lower()
        return bool(a) and (a == b or a.startswith(b) or b.startswith(a))
    links, vistos_url = [], set()
    for e in evs:
        u = (e.get("url") or "").strip()
        if e.get("tipo") == "chrome" and e.get("motivo") != "clique" and not na_frente(float(e.get("t", 0)), e.get("titulo")):
            continue
        if e.get("tipo") in ("chrome", "janela") and u and u not in vistos_url:
            vistos_url.add(u)
            links.append({"url": u, "titulo": e.get("titulo") or "", "t": e.get("t", 0)})
    # 16/11: a janela onde ele clicou e que não mandou endereço (o AppPessoal e o DUBX abrem em janela de app, sem a extensão): pelo menos
    # o nome dela, uma vez — senão o RESUMO não diz em que tela ele estava
    titulos_com_link = {(l.get("titulo") or "").strip().lower() for l in links}
    for e in evs:
        if e.get("tipo") != "clique":
            continue
        app, tit = (e.get("app") or "").lower(), (e.get("titulo") or "").strip()
        if app not in NAVEGADORES or not tit or tit.lower() in titulos_com_link:
            continue
        add(float(e.get("t", 0)), "🪟 cliquei na janela do Chrome «%s»" % tit, ("jan", tit.lower()))
    if not links:
        try:
            links = json.load(open(os.path.join(p, "links.json"), encoding="utf-8")).get("links") or []
        except (OSError, ValueError):
            links = []
    for l in links:
        u = (l.get("url") or "").strip()
        if not u or u.startswith(("chrome://", "about:", "chrome-extension://", "edge://")):
            continue
        tit = re.sub(r"\s+", " ", (l.get("titulo") or "")).strip()[:90]
        add(float(l.get("t", 0)), "🌐 no Chrome: %s%s%s" % ((tit + " — ") if tit else "", u, _baixa(u)), ("url", u))
    # 20/11: os links de vídeo vão baixando sozinhos (vídeo + som) em <pasta>aixados, sem atrasar o RESUMO
    if videos:
        try:
            import baixar_link
            baixar_link.em_segundo_plano(p, videos)
            log("baixando %d link(s) de vídeo em %s" % (len(videos), os.path.join(p, "baixados")))
        except Exception as e:
            log("baixar links: %r" % e)
    return sorted(itens, key=lambda x: x[0])


PRINT_LONGE_S = 6          # dois prints automáticos ficam pelo menos 6 s longe um do outro
PRINT_SEM_AQUI_S = 20      # fala sem «aqui/isso/ó»: um print a cada ~20 s de fala, pra nada ficar sem imagem
JA_FEZ_S = 10              # 15/11 ~21h30 (ele: «se eu tivesse tirado print, desenhado... a tua análise... vai saber, ah, o Luan já fez
                           # aqui, então não precisa levar mais nada... o Kakashi ele é inteligente»): print/desenho DELE cobre ±10 s


# 16/11 12:40 (ele, depois do RESUMO das 12:35: «foi link do fly xtudo pra nada» · «o resumo tem q ser inteligente po, e não no modo
# fodase»). O de 12:35 pegou o print no «aqui» de «gravar um resumo curto aqui» (não apontava nada) e deixou SEM imagem o que
# importava: «passo pra cá... tá vendo? fica pulando, se teletransportando» — um defeito que MEXE, que um print parado não mostra.
# Agora: (1) «cá / ali / lá» também apontam; (2) «tá vendo / olha só / fica pulando / voltando / piscando...» = ele está MOSTRANDO
# algo acontecer → uma TIRA de 3 quadros do vídeo (antes · durante · depois), recortados em volta do mouse; (3) o momento vale mais
# quando o mouse PAROU ou CLICOU ali perto (é aí que ele aponta de verdade); (4) apontando com o Claude ou a barra do Kakashi na
# frente não conta (está falando comigo, não mostrando); (5) sem print perto, sai um quadro do vídeo naquele segundo.
APONTA_R = re.compile(r"\b(aqui|isso|esse|essa|este|esta|ó|olha|cá|ali|lá)\b", re.I)
DEMONSTRA = re.compile(r"\b(t[aá]|est[aá]) vendo\b|\bviu\?|\bolha s[oó]\b|\bfica(ndo)? (pulando|voltando|piscando|travando|sumindo|tremendo|"
                       r"mudando|indo)\b|teletransport|\bn[aã]o (vai|anda|mexe|carrega|funciona)\b", re.I)
SEQ_PASSO_S = 1.2          # a tira: quadros 1,2 s antes e depois
SEM_JANELA = 0x08000000    # CREATE_NO_WINDOW: o ffmpeg nunca abre janela na tela dele


def _mouse_em(evs, t):
    pts = [(abs(float(e.get("t", 0)) - t), e["x"], e["y"]) for e in evs
           if e.get("tipo") in ("mouse", "clique", "sob_mouse", "print") and e.get("x") is not None and e.get("y") is not None]
    return min(pts)[1:] if pts else None


def _frente_em(evs, t):
    js = [e for e in evs if e.get("tipo") == "janela" and float(e.get("t", 0)) <= t + 0.3]
    return ((js[-1].get("app") or "").lower(), js[-1].get("titulo") or "") if js else ("", "")


def _quadro(p, t, xy, escala_tela, desloc=0.0):
    """um quadro do tela.mp4 no segundo t, recortado em volta do mouse (círculo vermelho); None se não der"""
    import subprocess
    from PIL import Image, ImageDraw
    v = os.path.join(p, "tela.mp4")
    if not os.path.isfile(v):
        return None
    tmp = os.path.join(p, "_resumo", "_q_%06d.png" % int(t * 100))
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % max(0.0, t - desloc), "-i", v, "-frames:v", "1", tmp],
                       creationflags=SEM_JANELA if sys.platform == "win32" else 0, timeout=20, check=False)
        im = Image.open(tmp).convert("RGB")
    except Exception:
        return None
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    W, H = 720, 450                      # no vídeo de 1920 = ~1440 x 900 da tela 4K: dá pra ler e ver o entorno
    cx, cy = (xy[0] * escala_tela, xy[1] * escala_tela) if xy else (im.width / 2, im.height / 2)
    x0 = int(min(max(0, cx - W / 2), max(0, im.width - W))); y0 = int(min(max(0, cy - H / 2), max(0, im.height - H)))
    im = im.crop((x0, y0, x0 + W, y0 + H))
    if xy:
        d = ImageDraw.Draw(im); mx, my = cx - x0, cy - y0
        d.ellipse((mx - 22, my - 22, mx + 22, my + 22), outline=(255, 30, 46), width=3)
    return im


def _tira(p, t, evs, escala_tela, desloc):
    """3 quadros (antes · durante · depois) lado a lado, com o minuto em cima de cada um → caminho do jpg"""
    from PIL import Image, ImageDraw
    qs = []
    for dt in (-SEQ_PASSO_S, 0.0, SEQ_PASSO_S):
        tt = max(0.0, t + dt)
        q = _quadro(p, tt, _mouse_em(evs, tt), escala_tela, desloc)
        if q is not None:
            qs.append((tt, q))
    if len(qs) < 2:
        return None
    w, h = qs[0][1].size
    tira = Image.new("RGB", (w * len(qs) + 8 * (len(qs) - 1), h + 30), (12, 12, 14))
    d = ImageDraw.Draw(tira)
    for k, (tt, q) in enumerate(qs):
        x = k * (w + 8)
        tira.paste(q, (x, 30))
        d.text((x + 8, 8), "%s  %s" % (mmss(tt), ("antes", "durante", "depois")[k] if len(qs) == 3 else ""), fill=(255, 214, 10))
    out = os.path.join(p, "_resumo", "%s_sequencia.jpg" % mmss(t).replace(":", ""))
    tira.save(out, quality=88)
    return out


def prints_inteligentes(p, fala, dur, rep, ja, resumo_pc):
    """15/11 ~21h25 (ele: «achei que ia ter uns prints automáticos inteligentes... do lugar que eu mostrei... com o mouse com aquela
    paradinha vermelha»), refeito em 16/11 12:40 (ver o bloco acima). → [(t, linha)] com ⟦IMG:...⟧ (vira «imagem N» colada)."""
    evs = []
    for l in open(os.path.join(p, "eventos.jsonl"), encoding="utf-8", errors="replace"):
        if l.strip("\x00 \r\n\t"):
            try:
                evs.append(json.loads(l))
            except ValueError:
                continue
    prints = [e for e in evs if e.get("tipo") == "print" and e.get("motivo") != "traco" and e.get("arquivo") and float(e.get("t", 0)) >= rep]
    mon = next((e.get("monitor") for e in prints if e.get("monitor")), None) or [0, 0, 3840, 2160]
    escala_tela = 1920.0 / max(1, (mon[2] - mon[0])) if mon[2] - mon[0] > 1920 else 1.0       # o tela.mp4 é 1920 de largura
    # onde o mouse PAROU ou CLICOU (o gesto de apontar de verdade)
    gestos = [float(e.get("t", 0)) for e in evs if e.get("tipo") in ("clique", "sob_mouse") or
              (e.get("tipo") == "app_pessoal" and e.get("acao") in ("parou", "clique")) or (e.get("tipo") == "chrome" and e.get("motivo") in ("parou", "clique"))]
    alvo = []                              # (prioridade, t, rótulo, tipo)  tipo: "seq" | "ponto"
    for a, b, tx, *_ in fala:
        if t_ok(a, rep) and DEMONSTRA.search(tx):
            m = DEMONSTRA.search(tx)
            t = a + (max(b, a + 0.5) - a) * (m.start() / max(1, len(tx)))
            alvo.append((0, t, "mostrando: «%s»" % m.group(0).strip(), "seq"))
        for m in APONTA_R.finditer(tx):
            t = a + (max(b, a + 0.5) - a) * (m.start() / max(1, len(tx)))
            if not t_ok(t, rep):
                continue
            perto_gesto = any(-1.5 <= g - t <= 2.5 for g in gestos)
            forte = m.group(0).lower() in ("aqui", "ó", "olha", "cá")
            alvo.append((1 if perto_gesto else (2 if forte else 3), t, "«%s»" % m.group(0), "ponto"))
    if not any(x[0] <= 2 for x in alvo):    # falou sem apontar: um a cada ~20 s de fala
        ultimo = -1e9
        for a, _b, _tx, *_ in fala:
            if a - ultimo >= PRINT_SEM_AQUI_S and t_ok(a, rep):
                alvo.append((4, a, "falando", "ponto")); ultimo = a
    teto = max(4, min(12, int(float(dur or 0) / 12) + 2))
    escolhidos = []
    for prio, t, rot, tipo in sorted(alvo, key=lambda x: (x[0], x[1])):
        if len(escolhidos) >= teto:
            break
        app, _tit = _frente_em(evs, t)
        if app in ("claude.exe", "claude", "pythonw.exe", "python.exe"):     # falando comigo / mexendo na barra: não está mostrando nada
            continue
        longe = PRINT_LONGE_S if tipo == "ponto" else SEQ_PASSO_S * 2
        if any(abs(t - x[1]) < longe for x in escolhidos) or any(abs(t - tj) <= JA_FEZ_S for tj in ja):
            continue
        escolhidos.append((prio, t, rot, tipo))
    out = []
    A = lambda rel: os.path.normpath(os.path.join(p, rel))      # noqa: E731
    for prio, t, rot, tipo in sorted(escolhidos, key=lambda x: x[1]):
        if tipo == "seq":
            arq = _tira(p, t, evs, escala_tela, DESLOC_TELA.get(p, 0.0))
            if arq:
                out.append((t, "🎞 o que eu estava mostrando acontecer (%s) — antes · durante · depois: %s" % (rot, img(arq))))
                continue
        cand = [e for e in prints if -1.0 <= float(e["t"]) - t <= 2.0] or [e for e in prints if abs(float(e["t"]) - t) <= 3.0]
        if cand:
            e = min(cand, key=lambda e: abs(float(e["t"]) - t))
            perto = e.get("perto") if e.get("perto") and os.path.isfile(A(e["perto"])) else None
            out.append((float(e["t"]), "📸 onde eu mostrei (%s): %s" % (rot, img(A(perto) if perto else A(e["arquivo"])))))
            continue
        q = _quadro(p, t, _mouse_em(evs, t), escala_tela, DESLOC_TELA.get(p, 0.0))     # sem print perto: um quadro do vídeo
        if q is not None:
            arq = os.path.join(p, "_resumo", "%s_quadro.jpg" % mmss(t).replace(":", ""))
            q.save(arq, quality=88)
            out.append((t, "📸 onde eu mostrei (%s): %s" % (rot, img(arq))))
    return out


def t_ok(t, rep):
    return t >= rep


DESLOC_TELA = {}           # pasta → quanto o tela.mp4 está deslocado do relógio da sessão (replay); o resumo_de preenche


def elementos_app_pessoal(evs, rep):
    """16/11: o que o AppPessoal registrou onde ele PAROU ou CLICOU (o elemento de verdade: «faixa ssd», «EP04»...) — passar por cima não
    conta. Uma linha por elemento, no 1º momento, com quantas vezes."""
    vistos = {}
    for e in evs:
        if e.get("tipo") != "app_pessoal" or e.get("acao") not in ("parou", "clique", "clicou") or float(e.get("t", 0)) < rep:
            continue
        k = (e.get("k") or "", e.get("id") or "")
        if k not in vistos:
            vistos[k] = [float(e.get("t", 0)), e.get("titulo") or "", 0, set()]
        vistos[k][2] += 1; vistos[k][3].add(e.get("acao"))
    out = []
    for (tipo, ident), (t, tit, n, acoes) in vistos.items():
        verbo = "cliquei" if acoes & {"clique", "clicou"} else "parei o mouse"
        out.append((t, "🧩 no AppPessoal, %s em: %s «%s»%s%s" % (verbo, tipo or "elemento", ident, (" (%s)" % tit) if tit else "",
                                                          (" — %d vezes" % n) if n > 1 else "")))
    return out


def resumo_de(p):
    """(cabeçalho, [(t, linha)], segundos) de uma gravação"""
    import resumo_pc
    andamento(etapa="fechando a gravação")
    meta = esperar(p, "duracao_s", ESPERA_FALA_S)
    if meta is None:
        raise RuntimeError("descartada")
    if meta.get("replay_s"):          # com replay o fala.wav ainda muda depois do duracao_s (o replay entra na frente): espera o fim
        meta = esperar(p, "links", ESPERA_LINKS_S) or meta
    rep = meta.get("replay_s") or 0
    juntos = meta.get("replay_juntado") or []
    desloc = rep if (rep and "fala" not in juntos) else 0
    t0 = time.time()
    aviso = ""
    espera_viva(p)          # 20/11 noite: o AO VIVO fechando o último trecho → espera ele (segundos) em vez de transcrever tudo de novo
    via, porque = como_transcrever(resumo_pc)
    a, b = TAXA[via]
    andamento(etapa="transcrevendo", via=via, ini_fala=t0, previsto_fala_s=round(a * float(meta.get("duracao_s") or 0) + b, 1))
    try:
        fala = None
        if via == "ditado":
            try:
                fala = fala_rapida(p, desloc, resumo_pc)
            except Exception as e:
                porque = "o ditado falhou (%r)" % e
                andamento(etapa="transcrevendo", via="processador", ini_fala=time.time(),
                          previsto_fala_s=round(TAXA["processador"][0] * float(meta.get("duracao_s") or 0) + TAXA["processador"][1], 1))
        if fala is None:
            fala = resumo_pc.fala_da_sessao(p, desloc)
            via = "processador"
        if getattr(resumo_pc, "fala_ao_vivo", lambda _p: None)(p) is not None:
            via, porque = "ao vivo (transcrita durante a gravação)", ""
        log("fala de %s transcrita em %.1f s pelo %s%s (%d trechos)" % (os.path.basename(p), time.time() - t0, via,
                                                                    (" — " + porque) if porque and via != "ditado" else "", len(fala)))
    except (Exception, SystemExit) as e:
        # ex.: no pacote do time com "transcricao": "ardi" quem transcreve é o Claude — o resumo sai mesmo assim, com os prints e
        # links, e o aviso diz que a fala falta (o Claude transcreve pela pasta)
        fala, aviso = [], re.sub(r"\s+", " ", str(e)).strip()[:300] or e.__class__.__name__
        log("fala de %s NÃO transcrita: %s" % (os.path.basename(p), aviso))
    if rep:
        fala = [x for x in fala if x[0] >= rep]
    try:
        _evs0 = [json.loads(l) for l in open(os.path.join(p, "eventos.jsonl"), encoding="utf-8", errors="replace") if l.strip("\x00 \r\n\t")]
    except (OSError, ValueError):
        _evs0 = []
    telas = telas_usadas(_evs0, rep)
    fala, trocas = corrigir_nomes(fala, _evs0)
    frs = resumo_pc.frases(fala)
    andamento(etapa="juntando")
    itens = itens_da_sessao(p, meta, rep)        # 15/11: sem esperar o links.json (as páginas vêm da extensão)
    DESLOC_TELA[p] = rep if (rep and "tela" not in juntos) else 0.0
    try:                                          # 16/11: o elemento do AppPessoal onde ele parou/clicou
        _evs = [json.loads(l) for l in open(os.path.join(p, "eventos.jsonl"), encoding="utf-8", errors="replace") if l.strip("\x00 \r\n\t")]
        itens = sorted(itens + elementos_app_pessoal(_evs, rep), key=lambda x: x[0])
    except Exception as e:
        log("elementos do AppPessoal: %r" % e)
    try:                                          # 15/11 ~21h25: os prints automáticos do lugar que ele mostrou
        ja = [t for t, l in itens if l.startswith(("🖼", "✏️"))]
        itens = sorted(itens + prints_inteligentes(p, fala, meta.get("duracao_s"), rep, ja, resumo_pc), key=lambda x: x[0])
    except Exception as e:
        log("prints automáticos: %r" % e)
    # a linha do tempo: frases seguidas viram um parágrafo; um item no meio abre outro
    linhas, par, par_t = [], [], None
    fila = sorted([(t, 0, f) for t, f in frs] + [(t, 1, l) for t, l in itens], key=lambda x: (x[0], x[1]))
    for t, eh_item, txt in fila:
        if eh_item:
            if par:
                linhas.append((par_t, "[%s] %s" % (mmss(par_t), " ".join(par)))); par = []
            linhas.append((t, "   [%s] %s" % (mmss(t), txt)))
        else:
            if par and t - par_t > GRUDA_S:
                linhas.append((par_t, "[%s] %s" % (mmss(par_t), " ".join(par)))); par = []
            if not par:
                par_t = t
            par.append(txt)
    if par:
        linhas.append((par_t, "[%s] %s" % (mmss(par_t), " ".join(par))))
    dur = meta.get("duracao_s") or 0
    quando = (meta.get("inicio_local") or "")[:16].replace("T", " ")
    try:
        quando = datetime.datetime.strptime(quando, "%Y-%m-%d %H:%M").strftime("%d/%m %H:%M")
    except ValueError:
        pass
    onde = "Premiere" if meta.get("olho_premiere") else "PC"
    cab = "%s · %s · %s" % (onde, quando, mmss(dur))
    saida = [l for _, l in linhas]
    if aviso:
        saida.insert(0, "(A FALA NÃO FOI TRANSCRITA AQUI: %s — transcrever o fala.wav da pasta antes de agir)" % aviso)
    return cab, saida, len(frs), len(itens), {"telas": telas, "trocas": trocas}


AVISO_IMAGENS = ("As imagens vão anexadas nesta mensagem, na ordem: «imagem 1» = a 1ª anexada. 📸 = print de onde eu apontei (o círculo "
                 "vermelho é o mouse); 🎞 = antes · durante · depois de algo que eu mostrei acontecendo.")
O_QUE_FAZER = ["1. Diga em 1–2 linhas o que entendeu que eu quero (sobre o app, não sobre a gravação).",
               "2. Resolva «aqui / isso / cá / esse» pelas imagens e pelos elementos citados no mesmo minuto.",
               "3. Faça o que eu pedi até o fim. Se depender de escolha minha, pergunte antes, citando o minuto exato.",
               "4. Feche com o que mudou e a prova de cada coisa (print, teste ou commit)."]
NAO_E_TELA = ("claude.exe", "claude", "pythonw.exe", "python.exe", "explorer.exe", "openwhispr.exe", "")


def telas_usadas(evs, rep):
    """16/11: as janelas onde ele CLICOU (o que estava usando de verdade), sem o Claude, a barra do Kakashi e a área de trabalho"""
    out = []
    for e in evs:
        if e.get("tipo") != "clique" or float(e.get("t", 0)) < rep:
            continue
        app, tit = (e.get("app") or "").lower(), (e.get("titulo") or "").strip()
        if app in NAO_E_TELA or not tit:
            continue
        nome = "Chrome" if app in NAVEGADORES else re.sub(r"\.exe$", "", e.get("app") or "", flags=re.I)
        r = "%s «%s»" % (nome, tit[:60])
        if r not in out:
            out.append(r)
    return out


def _uma_letra(a, b):
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def corrigir_nomes(fala, evs):
    """16/11: o nome que a transcrição ouviu errado vira o nome da janela que estava na tela (ex.: «Figmo» → «Figma», a janela se
    chamava Figma). Só nome de janela curta (até 3 palavras: nome de app), só troca de UMA letra no mesmo tamanho, mesma 1ª letra e 5+ letras
    — assim «projeto» nunca vira «Projetos». → (fala corrigida, [(ouvido, certo)])"""
    nomes = set()
    for e in evs:
        if e.get("tipo") in ("janela", "clique", "chrome"):
            tit = (e.get("titulo") or "").strip()
            if 0 < len(tit.split()) <= 3:
                for w in re.findall(r"[A-Za-zÀ-ÿ]{5,}", tit):
                    nomes.add(w)
    if not nomes:
        return fala, []
    trocas = []

    def troca(m):
        w = m.group(0)
        if any(w.lower() == n.lower() for n in nomes):
            return w
        for n in nomes:
            if w[0].lower() == n[0].lower() and _uma_letra(w.lower(), n.lower()):
                if (w, n) not in trocas:
                    trocas.append((w, n))
                return n
        return w
    nova = []
    for x in fala:
        x = list(x)
        x[2] = re.sub(r"[A-Za-zÀ-ÿ]{5,}", troca, x[2])
        nova.append(tuple(x))
    return nova, trocas


def montar(pastas):
    blocos, n_frs, n_itens, feitas = [], 0, 0, []
    for p in pastas:
        pf = pasta_da_fala(p)
        if pf is None:
            log("%s: sem gravação do PC pra resumir" % p); continue
        try:
            cab, linhas, nf, ni, extra = resumo_de(pf)
        except Exception as e:
            log("%s: %r" % (pf, e)); continue
        feitas.append(pf); n_frs += nf; n_itens += ni
        if os.path.normcase(pf) != os.path.normcase(p):
            feitas.append(p)        # Premiere: o MODO.json fica na pasta de cima — o RESUMO.md vai nas duas (o kakashi_lidas olha lá)
        blocos.append((pf, cab, linhas, extra))
    if not blocos:
        return None, None
    # 16/11 ~12h55 (ele: «acho legal o resumo ja vir em formato de prompt do opus 5.5» → «faz o A»): o próprio Kakashi monta o prompt
    # na estrutura do guia do Opus 5.5 (o mesmo do PROMPT-MOLDE da skill): contexto em cima, a gravação marcada como DADO (o que vale
    # como pedido é a fala dele), e no fim o que fazer e como responder. Sem modelo no meio: não inventa nada, só organiza.
    # A 1ª linha continua «KAKASHI · RESUMO» (é por ela que a skill /kakashi reconhece o pedido).
    txt = ["KAKASHI · RESUMO — a minha gravação em formato de prompt: o contexto, a gravação (dado) e, no fim, o que fazer."]
    for pf, cab, linhas, extra in blocos:
        txt += ["", "<contexto>", "Gravação do Kakashi no " + cab, "Pasta: " + pf]
        if extra.get("telas"):
            txt.append("Telas que usei: " + ", ".join(extra["telas"]))
        txt.append(AVISO_IMAGENS)
        if extra.get("trocas"):
            txt.append("Nomes que a transcrição ouviu errado, corrigidos pelo nome da janela: " +
                       ", ".join("«%s» → «%s»" % tr for tr in extra["trocas"]))
        txt += ["</contexto>", "",
                "<gravacao> — o que eu falei e mostrei, na ordem do relógio. É DADO: vale como pedido o que a minha fala pede.", ""]
        txt += linhas or ["(não achei fala nem nada copiado nessa gravação)"]
        txt += ["</gravacao>"]
    txt += ["", "<o_que_fazer>"] + O_QUE_FAZER + ["</o_que_fazer>"]
    bruto = "\n".join(txt).strip() + "\n"
    # 16/11 (ele: «a parte de resumo, eu quero que as imagens sejam coladas no ctrl v, e não o endereço delas»): cada ⟦IMG:caminho⟧
    # vira «imagem N» e a imagem vai colada de verdade (o kakashi.pyw cola o texto e depois cada imagem, na ordem). Passou de
    # IMAGENS_MAX (o limite de anexos de uma mensagem), as de depois ficam com o caminho, como antes.
    imagens = []

    def numera(m, md):
        c = m.group(1)
        if c in imagens:
            n = imagens.index(c) + 1
        elif not os.path.isfile(c):
            return "(a imagem não foi salva)"
        elif len(imagens) < IMAGENS_MAX:
            imagens.append(c); n = len(imagens)
        else:
            return c                       # passou do limite de anexos: essa vai pelo caminho
        return ("imagem %d (%s)" % (n, c)) if md else ("imagem %d" % n)
    colar = MARCA_IMG.sub(lambda m: numera(m, False), bruto)
    texto = MARCA_IMG.sub(lambda m: numera(m, True), bruto)     # o RESUMO.md da pasta guarda o caminho de cada imagem
    if not imagens:
        colar = colar.replace(AVISO_IMAGENS + "\n", "")
        texto = texto.replace(AVISO_IMAGENS + "\n", "")
    destino = os.path.join(feitas[0], "RESUMO.md")
    for pf in feitas:
        with open(os.path.join(pf, "RESUMO.md"), "w", encoding="utf-8") as f:
            f.write(texto)
        with open(os.path.join(pf, "RESUMO_COLAR.json"), "w", encoding="utf-8") as f:
            json.dump({"texto": colar, "imagens": imagens, "com_caminho": texto}, f, ensure_ascii=False, indent=1)
    log("RESUMO.md pronto (%d frases, %d itens, %d imagens pra colar) em %s" % (n_frs, n_itens, len(imagens), destino))
    return destino, texto


# =====================================================================================================================================
# AO VIVO (20/11/2026 ~21h) — a fala transcrita DURANTE a gravação. Pedido dele (20/11 ~20h20): «seria perfeito se a análise do Kakashi
# já ficava pronta no final da gravação, tá ligado? Enquanto tá gravando, já tá recolhendo, fazendo as paradas, tá ligado? Que é o tempo
# que você perde pra poder ficar analisando tudo» · e antes: «como você consegue otimizar isso de forma que você não fique burro e o
# resultado não seja condenado?». Só o RECOLHER sai da frente: a leitura (LEITURA.md, PROMPT.md, sabotador, Opus) não muda nem encolhe.
#
#   pythonw modo_resumo.py --ao-vivo <pasta da sessão> [--premiere <pasta da sessão do painel>] [--pai <pid do Kakashi>]
#
# O Kakashi liga UM destes por gravação (GravacaoPC; no Premiere o OlhoPremiere, com a pasta do painel). A cada ~30–40 s de voz,
# cortado no ponto mais quieto (nunca no meio da palavra), o trecho vai pro motor quente do Tandera (7797) com via «quente»: o Whisper
# que já estiver na placa — o do ditado (8178) ou o do Tandera, que o porteiro divide com o Premiere (um motor só). Motor quente fora
# do ar = o Tandera rapido=True (8178 com as regras do Tandera; sem o 8178, o Whisper do Tandera NA PLACA). Cada trecho fica em
# _ao_vivo\trechos.json com o pedaço da gravação e o segundo DENTRO do arquivo; o LEITURA.md vai sendo escrito (PARCIAL) a cada trecho.
# No fim falta só o último trecho: o relógio final é aplicado (pausas, pedaços apagados, atraso do microfone), o que ficou sem trecho é
# transcrito do arquivo final, e saem _ao_vivo\fala.json (a fala inteira no relógio do fala.wav) e o LEITURA.md COMPLETO = o DOSSIÊ,
# que o RESUMO, o /kakashi rápido e o profundo leem. Pedaço apagado sai; pausa não grava, então não transcreve; cancelar apaga o
# dossiê (o Kakashi para este processo e apaga _ao_vivo antes de mover a pasta); trazer de volta um pedaço devolve as falas dele.
# Sem motor quente, sem 8178 e sem placa (ex.: o Mac do time), ou qualquer erro: não sai fala.json e tudo segue o caminho de antes.
AO_VIVO = "_ao_vivo"
TRECHO_MIN_S, TRECHO_MAX_S = 30.0, 40.0    # cada trecho: 30–40 s, cortado no ponto mais quieto desse intervalo
JANELA_SIL_S = 0.3                          # o «silêncio» procurado: a janela de 0,3 s com menos energia (a pausa entre frases)
LACUNA_MIN_S = 1.0                          # pedaço do relógio final sem trecho (≥ 1 s) = transcreve do arquivo final no fim
PARCIAL_CADA_S = 15.0                       # o LEITURA.md parcial é reescrito no máximo a cada 15 s (e só com trecho novo)
ESPERA_FINAL_S = 240                        # o Kakashi/painel juntando os pedaços: espera o relógio final até 4 min
ESPERA_LINKS_FIM_S = 30                     # depois do dossiê: espera o histórico do Chrome (links.json) pra reescrever com os links
# o pedido ao motor quente: «placa» = o Whisper do PRÓPRIO Tandera (o mesmo da transcrição de antes) na placa pelo porteiro; sem vaga, o
# do ditado (8178). Medido 20/11 na gravação de 1:36 (prova_5): Tandera 163 de 164 palavras iguais à transcrição inteira de antes
# (99,4%) e as 7 falas do PROMPT; o do ditado direto, 155 de 164 (94,5%), e «Cadê?» virou «A ver.» — por isso o do Tandera vem primeiro.
VIA_AO_VIVO = os.environ.get("KAKASHI_AO_VIVO_VIA") or "placa"


def _json_atomico(caminho, obj):
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=0)
    os.replace(tmp, caminho)


def _ler_json(caminho, padrao=None):
    try:
        return json.load(open(caminho, encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def espera_viva(p, limite=90):
    """a gravação teve o AO VIVO (_ao_vivo\\estado.json): espera ele escrever o _ao_vivo\\fala.json (segundos) em vez de transcrever
    tudo de novo. Sem ao vivo, falhou, cancelou ou parou de bater = volta na hora (e o caminho de antes transcreve)."""
    t0 = time.time()
    while time.time() - t0 < limite:
        e = _ler_json(os.path.join(p, AO_VIVO, "estado.json"))
        if not e:
            return False
        if os.path.isfile(os.path.join(p, AO_VIVO, "fala.json")):
            return True
        if e.get("estado") in ("falhou", "cancelado", "sem kakashi", "abandonado") or time.time() - float(e.get("batida") or 0) > 15:
            return False
        time.sleep(0.2)
    return False


def _processo_vivo(pid):
    """o Kakashi (o pai) ainda está aberto? (Windows: OpenProcess + GetExitCodeProcess; fora do Windows: os.kill 0)"""
    if not pid:
        return True
    if sys.platform != "win32":
        try:
            os.kill(int(pid), 0); return True
        except OSError:
            return False
    import ctypes
    k = ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, int(pid))         # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    try:
        cod = ctypes.c_ulong()
        return bool(k.GetExitCodeProcess(h, ctypes.byref(cod))) and cod.value == 259     # STILL_ACTIVE
    finally:
        k.CloseHandle(h)


def _wav_info(arq):
    """(início dos dados, taxa, canais, largura, quadros escritos ATÉ AGORA) — o wav pode estar crescendo (cabeçalho sem tamanho)"""
    try:
        with open(arq, "rb") as f:
            cab = f.read(4096)
        tam = os.path.getsize(arq)
    except OSError:
        return None
    i = cab.find(b"fmt ")
    j = cab.find(b"data", i + 8) if i >= 0 else -1
    if i < 0 or j < 0:
        return None
    can = int.from_bytes(cab[i + 10:i + 12], "little") or 1
    taxa = int.from_bytes(cab[i + 12:i + 16], "little") or 48000
    larg = (int.from_bytes(cab[i + 22:i + 24], "little") // 8) or 2
    ini = j + 8
    return ini, taxa, can, larg, max(0, (tam - ini) // (can * larg))


def _ler_pcm(arq, info, de_s, ate_s):
    ini, taxa, can, larg, n = info
    q0, q1 = max(0, int(round(de_s * taxa))), min(n, int(round(ate_s * taxa)))
    if q1 <= q0:
        return b""
    with open(arq, "rb") as f:
        f.seek(ini + q0 * can * larg)
        return f.read((q1 - q0) * can * larg)


def _energias(pcm, info, passo_s=0.05):
    """energia (RMS de 16 bits) a cada 50 ms, do 1º canal — sem numpy (o Python do Kakashi não tem)"""
    import array
    _ini, taxa, can, larg, _n = info
    if larg != 2:
        return []
    a = array.array("h")
    a.frombytes(pcm[: len(pcm) // 2 * 2])
    if sys.byteorder != "little":
        a.byteswap()
    passo = max(1, int(taxa * passo_s)) * can
    out = []
    for k in range(0, len(a) - passo + 1, passo):
        b = a[k:k + passo:can * 4]             # 1 amostra em 4 do 1º canal: sobra precisão pra achar a pausa
        out.append((sum(x * x for x in b) / max(1, len(b))) ** 0.5)
    return out


def _corte_no_silencio(arq, info, de_s, ate_s):
    """o segundo (no arquivo) do meio da janela de 0,3 s mais quieta entre de_s e ate_s (empate = a mais tarde: trecho maior)"""
    en = _energias(_ler_pcm(arq, info, de_s, ate_s), info)
    k = max(1, int(round(JANELA_SIL_S / 0.05)))
    if len(en) < k:
        return ate_s
    soma = sum(en[:k]); melhor, onde = soma, 0
    for i in range(1, len(en) - k + 1):
        soma += en[i + k - 1] - en[i - 1]
        if soma <= melhor:
            melhor, onde = soma, i
    return de_s + (onde + k / 2.0) * 0.05


def _wav_temp(pcm, info, nome):
    """o trecho num wav de verdade (fechado, com tamanho) na pasta temporária — nunca na pasta da sessão (o cancelar move ela)"""
    import tempfile, wave
    _ini, taxa, can, larg, _n = info
    arq = os.path.join(tempfile.gettempdir(), "kakashi_aovivo_%d_%s.wav" % (os.getpid(), nome))
    with wave.open(arq, "wb") as w:
        w.setnchannels(can); w.setsampwidth(larg); w.setframerate(taxa); w.writeframes(pcm)
    return arq


def _transcrever_arquivo(arq, resumo_pc):
    """→ (segmentos [[ini, fim, txt]] no relógio do arquivo, «via»). O motor quente do Tandera (7797) com via «quente» (o Whisper que já
    está na placa: o do ditado 8178 ou o do Tandera pelo porteiro); fora do ar = o Tandera rapido=True NA PLACA (e liga o motor quente
    pro próximo trecho). As regras do Tandera (só os trechos com som, laço, frase inventada) valem nos dois."""
    tandera = _tandera(resumo_pc)
    from tandera import residente
    r = None
    if residente.usar():
        try:
            r = residente.pedir("/transcrever", {"audio": os.path.abspath(arq), "idioma": "pt", "via": VIA_AO_VIVO}, timeout=900)["r"]
            via = r.get("como") or "motor quente"
        except residente.Caiu:
            r = None
    else:
        residente.ligar()
    if r is None:
        r = tandera.transcrever(arq, idioma="pt", rapido=True, dispositivo="cuda")
        via = "Tandera rápido (%s)" % (r.get("via") or "?")
    inventadas = getattr(resumo_pc, "INVENTADAS", r"$^")
    segs = [[round(float(s["ini"]), 2), round(float(s["fim"]), 2), s["txt"].strip()] for s in r.get("segmentos") or []
            if (s.get("txt") or "").strip() and not re.fullmatch(inventadas, s["txt"].strip())]
    return segs, via


class AoVivo:
    """o processo que recolhe a fala enquanto ele grava (ver o bloco acima)"""

    def __init__(self, pasta, premiere=None, pai=None):
        import resumo_pc
        self.rp = resumo_pc
        self.pasta = os.path.abspath(pasta)
        self.prem = os.path.abspath(premiere) if premiere else None
        self.pai = pai
        self.nome = os.path.basename(os.path.dirname(self.pasta) if self.prem else self.pasta)
        self.dir = os.path.join(self.pasta, AO_VIVO)
        os.makedirs(self.dir, exist_ok=True)
        d = _ler_json(os.path.join(self.dir, "trechos.json"), {}) or {}
        self.trechos = d.get("trechos") or []          # retoma o que já tinha (o Kakashi reabriu no meio da gravação)
        self.falhas = d.get("falhas") or []
        self.feito = {}
        for t in self.trechos:
            self.feito[t["chave"]] = max(self.feito.get(t["chave"], 0.0), t["fim"])
        self.tam = {}                                  # chave → (tamanho, quando mudou): arquivo fechado só vale parado há 1 s
        self.t_parcial = 0.0
        self.novos_desde_parcial = 0
        self.inicio = time.time()

    # ---- estado (o RESUMO e o Kakashi leem) ----
    def batida(self, estado, **extra):
        try:
            _json_atomico(os.path.join(self.dir, "estado.json"), dict({"estado": estado, "batida": round(time.time(), 2), "pid": os.getpid(),
                                                                         "trechos": len(self.trechos), "falhas": len(self.falhas)}, **extra))
        except OSError:
            pass

    def outro_rodando(self):
        e = _ler_json(os.path.join(self.dir, "estado.json"), {}) or {}
        return (e.get("pid") not in (None, os.getpid()) and e.get("estado") in ("gravando", "finalizando")
                and time.time() - float(e.get("batida") or 0) < 5 and _processo_vivo(e.get("pid")))

    def salvar(self):
        _json_atomico(os.path.join(self.dir, "trechos.json"), {"fonte": "premiere" if self.prem else "pc", "trechos": self.trechos,
                                                               "falhas": self.falhas})

    # ---- de onde vem a voz ----
    def sinal(self):
        """PC: o que o Kakashi conta em _ao_vivo\\pedacos.json (pedaços, pausa, fim, cancelar)"""
        return _ler_json(os.path.join(self.dir, "pedacos.json"), {}) or {}

    def meta_painel(self):
        return _ler_json(os.path.join(self.prem, "sessao.json"), {}) or {} if self.prem else {}

    def fontes(self):
        """[(n, arquivo, fechado, apagado)] — PC: o arquivo da voz de cada pedaço; Premiere: as parteNN.wav do painel"""
        out = []
        if self.prem:
            for p in self.meta_painel().get("partes") or []:
                arq = os.path.join(self.prem, p.get("audio") or "parte%02d.wav" % p["n"])
                if not os.path.isfile(arq):            # pedaço apagado: o painel move os arquivos dele na hora
                    alt = os.path.join(self.prem, "_pedacos_apagados", os.path.basename(arq))
                    arq = alt if os.path.isfile(alt) else arq
                out.append((p["n"], arq, p.get("fim") is not None, bool(p.get("apagada"))))
            return out
        for p in self.sinal().get("pedacos") or [{"n": 1, "dur": None, "apagado": False}]:
            n = p["n"]
            out.append((n, os.path.join(self.pasta, "fala.wav" if n == 1 else "fala_p%02d.wav" % n), p.get("dur") is not None, bool(p.get("apagado"))))
        return out

    def terminou(self):
        """None (gravando) · "fim" · "cancelado" """
        if self.prem:
            if not os.path.isdir(self.prem):
                return "cancelado"
            m = self.meta_painel()
            if m.get("descartada") or m.get("estado") == "descartada":
                return "cancelado"
            if m.get("estado") in ("finalizando", "concluida"):
                return "fim"
            mo = _ler_json(os.path.join(self.pasta, "sessao.json"), {}) or {}
            return "fim" if mo.get("duracao_s") is not None else None
        if not os.path.isdir(self.pasta):
            return "cancelado"
        s = self.sinal()
        if s.get("cancelar"):
            return "cancelado"
        return "fim" if s.get("fim") else None

    # ---- transcrever ----
    def _estavel(self, k, arq):
        try:
            tam = os.path.getsize(arq)
        except OSError:
            return False
        v = self.tam.get(k)
        if v is None or v[0] != tam:
            self.tam[k] = (tam, time.time()); return False
        return time.time() - v[1] >= 1.0

    def _trecho(self, k, n, arq, info, de, ate, rotulo=None):
        t0 = time.time()
        tmp = None
        try:
            tmp = _wav_temp(_ler_pcm(arq, info, de, ate), info, k)
            segs, via = _transcrever_arquivo(tmp, self.rp)
            self.trechos.append({"chave": k, "n": n, "arq": rotulo or os.path.basename(arq), "ini": round(de, 3), "fim": round(ate, 3),
                                 "segs": [[round(de + a, 2), round(de + b, 2), tx] for a, b, tx in segs], "via": via,
                                 "levou_s": round(time.time() - t0, 2), "em": round(time.time(), 2)})
            self.novos_desde_parcial += 1
        except Exception as e:                      # o buraco é coberto no fim, pelo arquivo final
            self.falhas.append({"chave": k, "ini": round(de, 3), "fim": round(ate, 3), "erro": repr(e)[:300], "em": round(time.time(), 2)})
            log("ao vivo %s: trecho %s %s–%s falhou: %r" % (self.nome, k, mmss(de), mmss(ate), e))
        finally:
            if tmp:
                try:
                    os.remove(tmp)
                except OSError:
                    pass
        self.feito[k] = ate
        self.salvar()

    def _cortar_e_transcrever(self, k, n, arq, info, de, ate, ate_o_fim, rotulo=None):
        """de → ate em trechos de 30–40 s cortados no silêncio; ate_o_fim=False deixa o que ainda não deu 40 s pra depois"""
        while not self.parar():
            falta = ate - de
            if ate_o_fim:
                if falta < 0.3:
                    break
                corte = ate if falta <= TRECHO_MAX_S else _corte_no_silencio(arq, info, de + TRECHO_MIN_S, de + TRECHO_MAX_S)
            else:
                if falta < TRECHO_MAX_S + 0.5:      # meio segundo de folga: o ffmpeg pode estar no meio de um pacote
                    break
                corte = _corte_no_silencio(arq, info, de + TRECHO_MIN_S, de + TRECHO_MAX_S)
            self._trecho(k, n, arq, info, de, corte, rotulo)
            de = corte

    def passo(self, ate_o_fim=False):
        """transcreve o que já dá em cada arquivo (fechado e parado há 1 s = até o fim)"""
        antes = len(self.trechos) + len(self.falhas)
        for n, arq, fechado, apagado in self.fontes():
            if ate_o_fim and apagado:               # no fim, pedaço apagado não volta mais: não precisa transcrever o resto dele
                continue
            info = _wav_info(arq)
            if not info:
                continue
            k = "p%02d" % n
            fim_arq = info[4] / float(info[1])
            fechou = ate_o_fim or (fechado and self._estavel(k, arq))
            self._cortar_e_transcrever(k, n, arq, info, self.feito.get(k, 0.0), fim_arq, fechou)
            if self.parar():
                break
        return len(self.trechos) + len(self.falhas) - antes

    _parar = False

    def parar(self):
        if not self._parar and self.terminou() == "cancelado":
            self._parar = True
        return self._parar

    def ler_rabos(self):
        """PC, no concluir: o que falta de cada pedaço vai pra um wav temporário AGORA — o Kakashi espera o «rabo.ok» (até 3 s) antes de
        renomear/juntar os pedaços. Devolve [(k, n, arquivo temporário, info, de, nome)]"""
        out = []
        if self.sinal().get("rabo_tarde"):          # o Kakashi não esperou mais (3 s): os arquivos já podem ter sido renomeados/juntados
            log("ao vivo %s: o último trecho chegou tarde — sai do arquivo final (lacuna)" % self.nome)
            return out
        for n, arq, _f, apagado in self.fontes():
            info = _wav_info(arq) if not apagado else None
            if not info:
                continue
            k = "p%02d" % n
            de, fim_arq = self.feito.get(k, 0.0), info[4] / float(info[1])
            if fim_arq - de < 0.3:
                continue
            tmp = _wav_temp(_ler_pcm(arq, info, de, fim_arq), info, "rabo_" + k)
            out.append((k, n, tmp, _wav_info(tmp), de, os.path.basename(arq)))
        try:
            open(os.path.join(self.dir, "rabo.ok"), "w").write("%.2f" % time.time())
        except OSError:
            pass
        return out

    # ---- o relógio final ----
    def mapa_final(self):
        """{n: (começo do pedaço no fala.wav final, atraso do microfone no começo, duração do pedaço)} + a duração final + o wav final.
        PC: o sessao.json do Kakashi depois de juntar; Premiere: o sessao.json do painel (as partes que ficaram, na ordem) e o fala.wav
        do _olho (= o audio.wav do painel)."""
        meta = _ler_json(os.path.join(self.pasta, "sessao.json"), {}) or {}
        base = {}
        if self.prem:
            mp = self.meta_painel()
            t = 0.0
            for p in sorted(mp.get("partes") or [], key=lambda x: x["n"]):
                if p.get("apagada") or p.get("fim") is None or p["fim"] <= p["inicio"]:
                    continue
                dw = p["fim"] - p["inicio"]
                atraso = p.get("atraso_audio")
                if atraso is None:                  # a mesma conta do painel (_alinhar_e_juntar): o que falta no arquivo vai pro começo
                    arq = os.path.join(self.prem, p.get("audio") or "parte%02d.wav" % p["n"])
                    info = _wav_info(arq)
                    da = info[4] / float(info[1]) if info else dw
                    caiu = p.get("mic_caiu_em")
                    vivo = dw if caiu is None else min(dw, max(0.0, caiu - p["inicio"]))
                    atraso = max(0.0, vivo - da)
                base[p["n"]] = (t, float(atraso), dw)
                t += dw
            return base, meta, os.path.join(self.pasta, "fala.wav"), 0.0
        rep = meta.get("replay_s") or 0
        off = rep if (rep and "fala" in (meta.get("replay_juntado") or [])) else 0.0
        peds = meta.get("pedacos")
        if not peds:                                # um pedaço só: o fala.wav É o arquivo gravado (sem cortar nem juntar)
            base[1] = (0.0, 0.0, 1e12)
        else:
            atraso = {x.get("pedaco"): float(x.get("s") or 0) for x in meta.get("mic_atraso") or [] if x.get("onde") == "comeco"}
            t = 0.0
            for p in peds:
                if p.get("apagado") or (p.get("dur") or 0) <= 0.2:
                    continue
                base[p["n"]] = (t, atraso.get(p["n"], 0.0), float(p["dur"]))
                t += float(p["dur"])
        return base, meta, os.path.join(self.pasta, "fala.wav"), off

    def mapear(self, base, off):
        """os trechos no relógio do fala.wav final → (segmentos, intervalos cobertos)"""
        segs, cob = [], []
        for n, (b0, pad, dur) in base.items():
            if pad > 0:
                cob.append((off + b0, off + b0 + pad))
            lim = dur - pad                         # o arquivo mais comprido que o pedaço foi cortado no fim
            for tr in self.trechos:
                if tr["n"] != n:
                    continue
                if tr["ini"] < lim:
                    cob.append((off + b0 + pad + tr["ini"], off + b0 + pad + min(tr["fim"], lim)))
                for a, b, tx in tr["segs"]:
                    if a < lim - 0.05:
                        segs.append([round(off + b0 + pad + a, 2), round(off + b0 + pad + min(b, lim), 2), tx])
        return segs, cob

    @staticmethod
    def lacunas(cob, dur):
        out, t = [], 0.0
        for a, b in sorted(cob):
            if a - t >= LACUNA_MIN_S:
                out.append((t, a))
            t = max(t, b)
        if dur - t >= LACUNA_MIN_S:
            out.append((t, dur))
        return out

    def esperar_final(self):
        """o relógio final pronto: PC = sessao.json com duracao_s (o Kakashi juntou os pedaços); Premiere = o _olho concluído (o painel
        juntou o audio.wav e o fala.wav do _olho está ligado). None = cancelado/descartado ou não ficou pronto a tempo"""
        t0 = time.time()
        while time.time() - t0 < ESPERA_FINAL_S:
            if self.terminou() == "cancelado":
                return None
            m = _ler_json(os.path.join(self.pasta, "sessao.json"), {}) or {}
            if m.get("descartada"):
                return None
            if m.get("duracao_s") is not None and os.path.isfile(os.path.join(self.pasta, "fala.wav")):
                if not self.prem or self.meta_painel().get("estado") == "concluida":
                    return m
            self.batida("finalizando")
            time.sleep(0.2)
        return None

    def fim_da_gravacao(self):
        """o instante do concluir (pra medir «dossiê pronto em X s»): PC = o que o Kakashi escreveu no sinal; Premiere = o fim da última parte"""
        if self.prem:
            fins = [p.get("fim") for p in self.meta_painel().get("partes") or [] if p.get("fim")]
            return max(fins) if fins else None
        return self.sinal().get("concluiu_epoch")

    # ---- o dossiê ----
    def parcial(self, forcar=False):
        """o LEITURA.md PARCIAL (gravando): a fala até agora no relógio ao vivo + o que o olho já registrou"""
        if not self.novos_desde_parcial or (not forcar and time.time() - self.t_parcial < PARCIAL_CADA_S):
            return
        segs, apagados = [], set()
        if self.prem:
            partes = {p["n"]: p for p in self.meta_painel().get("partes") or []}
            for tr in self.trechos:
                p = partes.get(tr["n"])
                if p is None or p.get("apagada"):
                    continue
                segs += [[float(p.get("t0") or 0) + a, float(p.get("t0") or 0) + b, tx] for a, b, tx in tr["segs"]]
        else:
            peds = {p["n"]: p for p in self.sinal().get("pedacos") or []}
            apagados = {n for n, p in peds.items() if p.get("apagado")}
            for tr in self.trechos:
                p = peds.get(tr["n"]) or {"ini": 0.0}
                if tr["n"] in apagados:
                    continue
                segs += [[float(p.get("ini") or 0) + a, float(p.get("ini") or 0) + b, tx] for a, b, tx in tr["segs"]]
        try:
            self.rp.gerar(self.pasta, parcial=True, fala_viva=sorted(segs), apagados=apagados)
            self.t_parcial, self.novos_desde_parcial = time.time(), 0
        except Exception as e:
            log("ao vivo %s: LEITURA parcial: %r" % (self.nome, e))

    def limpar(self):
        """cancelado: o dossiê some (a gravação em si fica como o cancelar já deixa: _descartadas, nada apagado)"""
        import shutil
        for p in self._pastas_possiveis():
            try:
                shutil.rmtree(os.path.join(p, AO_VIVO), ignore_errors=True)
                lt = os.path.join(p, "LEITURA.md")
                if os.path.isfile(lt) and "DOSSIÊ PARCIAL" in open(lt, encoding="utf-8", errors="replace").read(600):
                    os.remove(lt)
            except OSError:
                pass
        log("ao vivo %s: cancelado — dossiê apagado" % self.nome)

    def _pastas_possiveis(self):
        """onde a pasta pode estar depois do cancelar: no lugar ou em _descartadas (PC: a sessão; Premiere: o _olho da sessão do painel)"""
        if self.prem:
            raiz, nome = os.path.dirname(self.prem), os.path.basename(self.prem)
            cands = [self.prem] + [os.path.join(raiz, "_descartadas", n) for n in (os.listdir(os.path.join(raiz, "_descartadas"))
                                   if os.path.isdir(os.path.join(raiz, "_descartadas")) else []) if n == nome or n.startswith(nome + "_")]
            return [os.path.join(c, "_olho") for c in cands if os.path.isdir(os.path.join(c, "_olho"))]
        raiz, nome = os.path.dirname(self.pasta), os.path.basename(self.pasta)
        return [c for c in (self.pasta, os.path.join(raiz, "_descartadas", nome)) if os.path.isdir(c)]

    def finalizar(self):
        t_viu = time.time()
        self.batida("finalizando")
        rabos = self.ler_rabos() if not self.prem else []
        if self.prem:
            self.passo(ate_o_fim=True)
        for k, n, tmp, info, de, nome in rabos:     # PC: o último trecho de cada pedaço (do wav temporário, no relógio do arquivo)
            self._cortar_e_transcrever_desloc(k, n, tmp, info, de, nome)
            try:
                os.remove(tmp)
            except OSError:
                pass
        if self.parar():
            self.limpar(); return 0
        meta = self.esperar_final()
        if meta is None:
            if self.terminou() == "cancelado" or (_ler_json(os.path.join(self.pasta, "sessao.json"), {}) or {}).get("descartada"):
                self.limpar(); self.batida("cancelado"); return 0
            self.batida("falhou", erro="o relógio final não ficou pronto em %d s" % ESPERA_FINAL_S); return 1
        base, meta, wav, off = self.mapa_final()
        segs, cob = self.mapear(base, off)
        info = _wav_info(wav)
        dur_wav = info[4] / float(info[1]) if info else float(meta.get("duracao_s") or 0)
        lac = self.lacunas(cob, dur_wav)
        for a, b in lac:                              # o que ficou sem trecho (microfone reaberto, trecho que falhou): do arquivo final
            antes = len(self.trechos)
            self._cortar_e_transcrever_final(wav, _wav_info(wav), a, b)
            for tr in self.trechos[antes:]:
                segs += [list(s) for s in tr["segs"]]
        segs.sort(key=lambda s: (s[0], s[1]))
        try:
            marca = [os.path.getsize(wav), int(os.path.getmtime(wav))]
        except OSError:
            self.batida("falhou", erro="sem fala.wav no fim"); return 1
        concluiu = self.fim_da_gravacao()
        vias = sorted({t.get("via", "?").split(" · ")[0] for t in self.trechos})
        _json_atomico(os.path.join(self.dir, "fala.json"), {
            "marca": marca, "completa": True, "segmentos": segs, "via": vias, "trechos": len(self.trechos), "falhas": len(self.falhas),
            "lacunas": [[round(a, 2), round(b, 2)] for a, b in lac], "fonte": "premiere" if self.prem else "pc",
            "concluiu_epoch": concluiu, "fala_pronta_epoch": round(time.time(), 2), "dur_s": round(dur_wav, 2)})
        t_fala = time.time()
        self.batida("fala pronta")
        if self.prem:
            self._fala_md(segs)
        try:
            self.rp.gerar(self.pasta, com_quadros=True)
        except Exception as e:
            log("ao vivo %s: o dossiê (LEITURA.md) falhou: %r" % (self.nome, e))
            self.batida("falhou", erro="LEITURA: %r" % e); return 1
        t_dossie = time.time()
        ref = concluiu or t_viu
        log("ao vivo %s: DOSSIÊ PRONTO %.1f s depois do concluir (fala %.1f s; %d trechos ao vivo, %d lacunas, %d falhas; %s)" % (
            self.nome, t_dossie - ref, t_fala - ref, len(self.trechos), len(lac), len(self.falhas), ", ".join(vias)))
        self.batida("pronto", dossie_s=round(t_dossie - ref, 2), fala_s=round(t_fala - ref, 2), leitura=os.path.join(self.pasta, "LEITURA.md"))
        # o histórico do Chrome só vai pro disco ~12 s depois: quando o links.json sair, o dossiê é reescrito com os links (sem transcrever)
        t0 = time.time()
        while time.time() - t0 < ESPERA_LINKS_FIM_S:
            m = _ler_json(os.path.join(self.pasta, "sessao.json"), {}) or {}
            if "links" in m or m.get("descartada"):
                break
            time.sleep(0.5)
        if os.path.isfile(os.path.join(self.pasta, "links.json")) and os.path.isdir(self.pasta):
            try:
                self.rp.gerar(self.pasta, com_quadros=True)
                log("ao vivo %s: dossiê reescrito com os links do histórico do Chrome (%.1f s depois do concluir)" % (self.nome, time.time() - ref))
                self.batida("pronto", dossie_s=round(t_dossie - ref, 2), fala_s=round(t_fala - ref, 2), links_s=round(time.time() - ref, 2),
                            leitura=os.path.join(self.pasta, "LEITURA.md"))
            except Exception as e:
                log("ao vivo %s: reescrever com os links: %r" % (self.nome, e))
        return 0

    def _cortar_e_transcrever_desloc(self, k, n, tmp, info, de, nome):
        """o rabo (wav temporário que começa em «de» no arquivo do pedaço): trechos de 30–40 s, guardados no relógio do arquivo do pedaço"""
        antes, antes_f = len(self.trechos), len(self.falhas)
        fim = info[4] / float(info[1]) if info else 0.0
        self._cortar_e_transcrever(k, n, tmp, info, 0.0, fim, True, rotulo=nome)
        for tr in self.trechos[antes:]:
            tr["ini"] = round(tr["ini"] + de, 3); tr["fim"] = round(tr["fim"] + de, 3)
            tr["segs"] = [[round(a + de, 2), round(b + de, 2), tx] for a, b, tx in tr["segs"]]
        for f in self.falhas[antes_f:]:
            f["ini"] = round(f["ini"] + de, 3); f["fim"] = round(f["fim"] + de, 3)
        self.feito[k] = de + fim
        self.salvar()

    def _cortar_e_transcrever_final(self, wav, info, a, b):
        """lacuna do relógio final: do fala.wav final, já no relógio dele (n = 0: não pertence a pedaço nenhum)"""
        if info:
            self._cortar_e_transcrever("final", 0, wav, info, a, min(b, info[4] / float(info[1])), True, rotulo="fala.wav (final)")

    def _fala_md(self, segs):
        """Premiere: o _transcricao\\FALA.md da sessão do painel (o passo 2 da skill) já sai pronto, do dossiê"""
        try:
            d = os.path.join(self.prem, "_transcricao"); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "FALA.md"), "w", encoding="utf-8") as f:
                f.write("# FALA (dossiê ao vivo: transcrita durante a gravação, trechos de 30–40 s cortados no silêncio)\n\n")
                f.writelines("[%s] %s\n" % (mmss(a), tx) for a, _b, tx in segs)
        except OSError as e:
            log("ao vivo %s: FALA.md: %r" % (self.nome, e))

    def rodar(self):
        if self.outro_rodando():
            log("ao vivo %s: já tem outro processo ao vivo nessa pasta — saindo" % self.nome); return 0
        self.batida("gravando")
        log("ao vivo %s: começou (%s)" % (self.nome, "Premiere" if self.prem else "PC"))
        ocioso = time.time()
        while True:
            est = self.terminou()
            if est == "cancelado":
                self.limpar(); return 0
            if est == "fim":
                break
            if not _processo_vivo(self.pai):
                self.batida("sem kakashi"); log("ao vivo %s: o Kakashi fechou no meio da gravação — parei (o caminho de antes cobre)" % self.nome)
                return 1
            try:
                if self.passo():
                    ocioso = time.time()
                self.parcial()
            except Exception as e:
                log("ao vivo %s: %r" % (self.nome, e))
            if time.time() - ocioso > 6 * 3600:
                self.batida("abandonado"); return 1
            self.batida("gravando")
            time.sleep(0.25)
        try:
            return self.finalizar()
        except Exception as e:
            log("ao vivo %s: finalizar: %r" % (self.nome, e))
            self.batida("falhou", erro=repr(e)[:300]); return 1


def main():
    global ANDAMENTO
    args = sys.argv[1:]
    if "--ao-vivo" in args:                     # 20/11 noite: o processo que recolhe a fala DURANTE a gravação
        def opt(nome):
            return args[args.index(nome) + 1] if nome in args and args.index(nome) + 1 < len(args) else None
        pai = opt("--pai")
        sys.exit(AoVivo(opt("--ao-vivo"), opt("--premiere"), int(pai) if pai else None).rodar())
    if "--andamento" in args:
        i = args.index("--andamento")
        ANDAMENTO = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    pastas = [a for a in args if not a.startswith("--")]
    if not pastas:
        sys.exit("uso: modo_resumo.py <pasta> [<pasta> ...]")
    destino, _ = montar(pastas)
    andamento(etapa="pronto" if destino else "nao saiu")
    if destino is None:
        sys.exit(2)
    print(destino)


if __name__ == "__main__":
    main()
