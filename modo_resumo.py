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
    """a fala pelo Whisper do ditado, com as regras do Tandera; cache em fala_resumo.json (refaz se o fala.wav mudou)"""
    wav = os.path.join(p, "fala.wav")
    if not os.path.isfile(wav):
        return []
    cache = os.path.join(p, "fala_resumo.json")
    marca = [os.path.getsize(wav), int(os.path.getmtime(wav))]
    try:
        c = json.load(open(cache, encoding="utf-8"))
        if c.get("marca") != marca:
            raise ValueError
        segs = c["segmentos"]
    except (OSError, ValueError, KeyError):
        tandera = _tandera(resumo_pc)
        r = tandera.transcrever(wav, idioma="pt", rapido=True, dispositivo="cpu")   # 8178 caiu no meio = o Whisper do Tandera NO PROCESSADOR
        inventadas = getattr(resumo_pc, "INVENTADAS", r"$^")
        segs = [[s["ini"], s["fim"], s["txt"]] for s in r["segmentos"] if not re.fullmatch(inventadas, s["txt"].strip())]
        json.dump({"marca": marca, "via": r.get("via") or "?", "segmentos": segs}, open(cache, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)
    return [(a + desloc, b + desloc, tx, False) for a, b, tx in segs]


def log(msg):
    try:
        with open(os.path.join(AQUI, "kakashi.log"), "a", encoding="utf-8") as f:
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


def main():
    global ANDAMENTO
    args = sys.argv[1:]
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
