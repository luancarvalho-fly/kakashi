# -*- coding: utf-8 -*-
"""BAIXAR LINK do Kakashi (20/11/2026): o vídeo e o áudio de um link que ele mostrou na gravação, sozinho.

Pedido dele (20/11): «pegar a ferramenta que ele usa pra baixar as coisas da internet automatico, pra vc n ficar com mais nenhuma trava
de download, conseguir baixar oq vc quiser pelo kakashi» → «já atualiza o kakashi com essa nova feature». A ferramenta do Edu (Claude
dele, recado ponte-edu 20/11 16:18) = yt-dlp + ffmpeg (o /watch), e o login que já está no navegador (--cookies-from-browser).

O que faz: o modo_resumo chama isto em segundo plano (não atrasa o RESUMO) pra cada link de vídeo que ele copiou ou abriu no navegador
durante a gravação (YouTube, Instagram, TikTok, X, Vimeo, Loom, Facebook, Twitch, Kwai, Pinterest, Reddit, Drive público...).
Baixa em <pasta da gravação>\\baixados\\: o vídeo com o som (mp4) e o som sozinho (m4a/mp3), e grava baixados\\estado.json com o que
deu certo, o arquivo e o erro de cada um (o Claude lê esse arquivo e sabe se ainda está baixando).
Ordem das tentativas: sem login → com o login do Chrome → Edge → Firefox (o que estiver instalado). Nenhum cookie vai pra arquivo.
Slack e Drive privado o yt-dlp não abre: aí o estado diz «baixar pelo navegador».

  pythonw baixar_link.py <pasta> <url> [<url> ...]
  python  baixar_link.py --teste <url>          → baixa numa pasta temporária e diz o resultado (pra conferir o yt-dlp)
"""
import datetime, json, os, re, shutil, subprocess, sys, tempfile, time

AQUI = os.path.dirname(os.path.abspath(__file__))
SEM_JANELA = 0x08000000 if os.name == "nt" else 0      # CREATE_NO_WINDOW: nada de janela de terminal na tela dele
TEMPO_MAX_S = 15 * 60                                  # um link: no máximo 15 min (live longa não trava a fila)
ALTURA_MAX = 1080                                      # 1080p basta pra ver e cortar referência; 4K só se pedir

# os sites de vídeo (o link da página do Chrome só baixa se for um destes — Gmail e Fly X-tudo não)
VIDEO = re.compile(r"""^https?://(?:[\w-]+\.)*(?:
      youtube\.com/(?:watch|shorts/|live/|embed/)|youtu\.be/|
      instagram\.com/(?:[\w.]+/)?(?:reels?|p|tv)/|
      tiktok\.com/(?:@[\w.-]+/(?:video|photo)/|t/)|vm\.tiktok\.com/|vt\.tiktok\.com/|
      (?:x|twitter)\.com/[\w]+/status/|
      vimeo\.com/\d|player\.vimeo\.com/|
      loom\.com/(?:share|embed)/|
      (?:facebook|fb)\.com/(?:watch|reel|[\w.]+/videos/|share/[rv]/)|fb\.watch/|
      twitch\.tv/(?:videos/|[\w]+/clip/)|clips\.twitch\.tv/|
      kwai\.com/|pinterest\.[\w.]+/pin/|pin\.it/|
      reddit\.com/r/[\w]+/comments/|v\.redd\.it/|
      dailymotion\.com/video/|streamable\.com/|
      drive\.google\.com/file/d/|
      soundcloud\.com/[\w-]+/[\w-]+
    )""", re.X | re.I)
SEM_YTDLP = re.compile(r"^https?://(?:[\w-]+\.)*(?:slack\.com|slack-files\.com|notion\.so|figma\.com)/", re.I)


def eh_video(url):
    return bool(VIDEO.match((url or "").strip()))


def _ffmpeg():
    f = shutil.which("ffmpeg")
    if f:
        return os.path.dirname(f)
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    try:
        for d in os.listdir(base):
            if d.lower().startswith("gyan.ffmpeg"):
                for r, _ds, fs in os.walk(os.path.join(base, d)):
                    if "ffmpeg.exe" in fs:
                        return r
    except OSError:
        pass
    return None


def navegadores():
    """os navegadores instalados, na ordem de tentar (o Chrome é o dele)"""
    out = []
    if os.name == "nt":
        la, pf, pf86 = os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")
        if os.path.isdir(os.path.join(la, "Google", "Chrome", "User Data")):
            out.append("chrome")
        if os.path.isdir(os.path.join(la, "Microsoft", "Edge", "User Data")):
            out.append("edge")
        if any(os.path.isdir(os.path.join(b, "Mozilla Firefox")) for b in (pf, pf86) if b):
            out.append("firefox")
    else:
        h = os.path.expanduser("~/Library/Application Support")
        for nome, pasta in (("chrome", "Google/Chrome"), ("safari", "../Safari"), ("firefox", "Firefox"), ("edge", "Microsoft Edge")):
            if os.path.isdir(os.path.join(h, pasta)):
                out.append(nome)
    return out


def _ytdlp(args, timeout):
    cmd = [sys.executable.replace("pythonw.exe", "python.exe"), "-m", "yt_dlp"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, creationflags=SEM_JANELA)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _erro(txt):
    linhas = [l.strip() for l in txt.splitlines() if "ERROR" in l]
    return (linhas[-1] if linhas else txt.strip().splitlines()[-1] if txt.strip() else "?")[:300]


def baixar(url, destino, ate=None):
    """→ dict(url, ok, video, audio, titulo, login, erro, segundos)"""
    t0 = time.time()
    res = {"url": url, "ok": False, "video": None, "audio": None, "titulo": None, "login": None, "erro": None}
    if SEM_YTDLP.match(url):
        res["erro"] = "site fechado pro yt-dlp (Slack/Notion/Figma): baixar pelo navegador"
        return res
    os.makedirs(destino, exist_ok=True)
    ff = _ffmpeg()
    molde = os.path.join(destino, "%(title).70B [%(id)s].%(ext)s")
    base = ["--no-playlist", "--no-progress", "--restrict-filenames", "--windows-filenames", "--no-mtime",
            "-f", "bv*[height<=%d]+ba/b[height<=%d]/bv*+ba/b" % (ALTURA_MAX, ALTURA_MAX), "--merge-output-format", "mp4",
            "-k", "-x", "--audio-format", "m4a",            # -x com -k: fica o vídeo (mp4) E o som sozinho (m4a)
            "--print", "after_move:filepath", "--print", "title", "-o", molde]
    if ff:
        base += ["--ffmpeg-location", ff]
    ultimo, erros = "", []
    for login in [None] + navegadores():
        if ate and time.time() > ate:
            break
        args = list(base) + (["--cookies-from-browser", login] if login else []) + [url]
        try:
            cod, txt = _ytdlp(args, TEMPO_MAX_S)
        except subprocess.TimeoutExpired:
            ultimo = "passou de %d min" % (TEMPO_MAX_S // 60)
            continue
        if cod == 0:
            ditos = [l.strip() for l in txt.splitlines() if l.strip()]
            arqs = [l for l in ditos if os.path.isfile(l)]
            res["titulo"] = next((l for l in ditos if not os.path.isfile(l) and not l.startswith(("[", "WARNING", "ERROR"))), None)
            res["audio"] = next((a for a in arqs if a.lower().endswith((".m4a", ".mp3", ".opus", ".ogg", ".wav"))), None)
            # o vídeo: o mp4 com o mesmo nome do som (o -k o guarda), ou o que foi dito
            nome = os.path.splitext(res["audio"])[0] if res["audio"] else None
            cands = [nome + e for e in (".mp4", ".mkv", ".webm")] if nome else []
            res["video"] = next((c for c in cands + arqs if os.path.isfile(c) and c.lower().endswith((".mp4", ".mkv", ".webm"))), None)
            res.update(ok=bool(res["video"] or res["audio"]), login=login or "sem login")
            if res["ok"]:
                break
            ultimo = "o yt-dlp terminou mas não achei o arquivo"
        else:
            e = _erro(txt)
            if login and re.search(r"cookie database|decrypt|DPAPI|App-Bound", e, re.I):
                e = "login do %s: o navegador não deixa ler (%s)" % (login, e[:120])
            erros.append(e if login else "sem login: " + e)
            ultimo = e
            if re.search(r"Unsupported URL|is not a valid URL", e):
                break                                  # login não resolve site que o yt-dlp não conhece
    # o -k guarda também os pedaços separados (.f251.webm, .f395.mp4): fica só o vídeo final e o som
    for n in os.listdir(destino):
        if re.search(r"\.f\d+[\w-]*\.\w+$", n):
            try:
                os.remove(os.path.join(destino, n))
            except OSError:
                pass
    if not res["ok"]:
        res["erro"] = " · ".join(erros) or ultimo or "?"
    res["segundos"] = round(time.time() - t0, 1)
    return res


def gravar_estado(pasta_b, estado):
    tmp = os.path.join(pasta_b, "estado.json.tmp")
    json.dump(estado, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(pasta_b, "estado.json"))


def rodar(pasta, urls):
    pasta_b = os.path.join(pasta, "baixados")
    os.makedirs(pasta_b, exist_ok=True)
    urls = list(dict.fromkeys(u.strip() for u in urls if u and u.strip()))
    estado = {"comecou": datetime.datetime.now().isoformat(timespec="seconds"), "terminou": None,
              "links": [{"url": u, "ok": None, "andamento": "na fila"} for u in urls]}
    gravar_estado(pasta_b, estado)
    for i, u in enumerate(urls):
        estado["links"][i]["andamento"] = "baixando"
        gravar_estado(pasta_b, estado)
        try:
            r = baixar(u, pasta_b)
        except Exception as e:
            r = {"url": u, "ok": False, "erro": repr(e)[:300]}
        r["andamento"] = "pronto" if r.get("ok") else "falhou"
        estado["links"][i] = r
        gravar_estado(pasta_b, estado)
    estado["terminou"] = datetime.datetime.now().isoformat(timespec="seconds")
    gravar_estado(pasta_b, estado)
    return estado


def em_segundo_plano(pasta, urls):
    """chamado pelo modo_resumo: solta o download sem esperar e sem janela. → a pasta onde vai cair"""
    urls = [u for u in urls if u]
    if not urls:
        return None
    py = sys.executable
    if os.name == "nt" and py.lower().endswith("python.exe") and os.path.isfile(py[:-10] + "pythonw.exe"):
        py = py[:-10] + "pythonw.exe"
    flags = (SEM_JANELA | 0x00000008 | 0x00000200) if os.name == "nt" else 0   # + DETACHED_PROCESS + NEW_PROCESS_GROUP
    subprocess.Popen([py, os.path.join(AQUI, "baixar_link.py"), pasta] + urls, cwd=AQUI, creationflags=flags,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=(os.name != "nt"))
    return os.path.join(pasta, "baixados")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = sys.argv[1:]
    if a[:1] == ["--teste"]:
        d = tempfile.mkdtemp(prefix="kakashi-baixar-")
        for u in a[1:]:
            print(json.dumps(baixar(u, d), ensure_ascii=False, indent=1))
        print("pasta:", d)
    elif len(a) >= 2:
        rodar(a[0], a[1:])
    else:
        print(__doc__)
        sys.exit(2)
