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
    """«ditado» (8178, rápido) ou «processador» (o de sempre). Premiere aberto = a placa é dele (regra 9), salvo o config."""
    if not ditado_no_ar():
        return "processador", "o ditado (8178) está fora do ar"
    try:
        tandera = _tandera(resumo_pc)
        from tandera import base
        if base.premiere_aberto() and not cfg().get("resumo_placa_com_premiere"):
            return "processador", "Premiere aberto (a placa é dele)"
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
    # o que ele copiou
    for e in evs:
        if e.get("tipo") != "copiou":
            continue
        app, oq, t = (e.get("app") or "").lower(), e.get("o_que"), float(e.get("t", 0))
        if "whispr" in app or "whisper" in app:                  # ditado: já foi colado, e a voz já está na fala
            continue
        if oq in ("imagem", "captura") and e.get("arquivo"):
            de = "print que tirei" if (oq == "captura" or app.startswith("pythonw") or app.startswith("python")) else "imagem que copiei"
            add(t, "🖼 %s: %s" % (de, A(e["arquivo"])), ("img", e["arquivo"]))
        elif oq == "arquivos" and e.get("arquivos"):
            for c in e["arquivos"]:
                add(t, "📎 arquivo que copiei: %s" % c, ("arq", c))
        elif oq == "link" and e.get("texto"):
            add(t, "🔗 link que copiei: %s" % e["texto"].strip(), ("url", e["texto"].strip()))
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
            add(g[0], "✏️ desenhei na tela%s: %s" % ((" (%d traços)" % len(g)) if len(g) > 1 else "", A(a)), ("des", a))
    # o que terminou de baixar
    ini = meta.get("inicio_epoch") or 0
    fim = (meta.get("fim_epoch") or ini + (meta.get("duracao_s") or 0))
    for t, c in baixados(ini, fim):
        add(t, "⬇️ baixei: %s" % c, ("arq", c))
    # as páginas do Chrome: onde ele clicou/parou (a extensão, na hora); sem a extensão, o links.json se já existir (sem esperar)
    links, vistos_url = [], set()
    for e in evs:
        u = (e.get("url") or "").strip()
        if e.get("tipo") in ("chrome", "janela") and u and u not in vistos_url:
            vistos_url.add(u)
            links.append({"url": u, "titulo": e.get("titulo") or "", "t": e.get("t", 0)})
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
        add(float(l.get("t", 0)), "🌐 no Chrome: %s%s" % ((tit + " — ") if tit else "", u), ("url", u))
    return sorted(itens, key=lambda x: x[0])


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
    frs = resumo_pc.frases(fala)
    andamento(etapa="juntando")
    itens = itens_da_sessao(p, meta, rep)        # 15/11: sem esperar o links.json (as páginas vêm da extensão)
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
    return cab, saida, len(frs), len(itens)


def montar(pastas):
    blocos, n_frs, n_itens, feitas = [], 0, 0, []
    for p in pastas:
        pf = pasta_da_fala(p)
        if pf is None:
            log("%s: sem gravação do PC pra resumir" % p); continue
        try:
            cab, linhas, nf, ni = resumo_de(pf)
        except Exception as e:
            log("%s: %r" % (pf, e)); continue
        feitas.append(pf); n_frs += nf; n_itens += ni
        if os.path.normcase(pf) != os.path.normcase(p):
            feitas.append(p)        # Premiere: o MODO.json fica na pasta de cima — o RESUMO.md vai nas duas (o kakashi_lidas olha lá)
        blocos.append((pf, cab, linhas))
    if not blocos:
        return None, None
    txt = ["KAKASHI · RESUMO (a gravação, na ordem: o que eu falei + o que eu mostrei no minuto; as imagens estão no caminho)"]
    for pf, cab, linhas in blocos:
        txt += ["", "## " + cab, "Pasta: " + pf, ""]
        txt += linhas or ["(não achei fala nem nada copiado nessa gravação)"]
    texto = "\n".join(txt).strip() + "\n"
    destino = os.path.join(feitas[0], "RESUMO.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(texto)
    for pf in feitas[1:]:
        with open(os.path.join(pf, "RESUMO.md"), "w", encoding="utf-8") as f:
            f.write(texto)
    log("RESUMO.md pronto (%d frases, %d itens) em %s" % (n_frs, n_itens, destino))
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
