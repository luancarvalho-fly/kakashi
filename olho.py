# -*- coding: utf-8 -*-
"""OLHO DE DEUS do Kakashi do PC (P3, 21/10/2026). As peças que o kakashi.pyw usa gravando e o resumo_pc.py usa lendo.

Pedido dele: "o Kakashi é a evolução de uma gravação de vídeo" / "o bom do Kakashi é que eu só falo ... você que tem que ser
inteligente pra entender o que eu tô falando". Nada de tecla extra pra ele apertar.

- UIA ............ o elemento debaixo do mouse pelo Windows UI Automation (nome, tipo, app, retângulo), só ctypes (sem biblioteca)
- print_nativo ... print na resolução NATIVA do monitor onde o cursor está, cursor marcado + recorte 800x500 em volta
- ler_area ....... o que ele copiou (texto, link, imagem, arquivos); conteúdo de gerenciador de senha NUNCA é lido
- historico_chrome / baixar_refs ... páginas abertas no Chrome (endereço + título + hora) e a imagem dos pins do Pinterest
- extrair_* / juntar_* ... o replay (os 2 min antes do atalho) e a junção com a gravação
Só CPU. Nunca toca som.
"""
import array, ctypes, ctypes.wintypes as wt, datetime, hashlib, html, json, os, re, shutil, sqlite3, subprocess, tempfile, time
import urllib.request, wave

if os.name == "nt":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    ole32 = ctypes.windll.ole32
    oleaut32 = ctypes.windll.oleaut32
else:       # porte pro Mac (02/11): as linhas de preparo do Windows viram nada; as peças do Mac entram no FIM deste arquivo
    import mac
    user32 = kernel32 = ole32 = oleaut32 = mac.SemWindows()
oleaut32.SysFreeString.argtypes = [ctypes.c_void_p]
ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]


def exe_do_pid(pid):
    h = kernel32.OpenProcess(0x1000, False, int(pid or 0))   # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(520); tam = wt.DWORD(520)
        return os.path.basename(buf.value) if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(tam)) else ""
    finally:
        kernel32.CloseHandle(h)


# ------------------------------------------------------------------ UI Automation (o que está debaixo do mouse)
class GUID(ctypes.Structure):
    _fields_ = [("a", ctypes.c_uint32), ("b", ctypes.c_uint16), ("c", ctypes.c_uint16), ("d", ctypes.c_ubyte * 8)]


def _guid(s):
    g = GUID()
    ole32.CLSIDFromString(ctypes.c_wchar_p(s), ctypes.byref(g))
    return g


def _metodo(ptr, idx, *argtypes):
    vt = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)(vt[idx])


class UIA:
    """IUIAutomation pela tabela de métodos (UIAutomationClient.h). Um objeto por thread (cada thread faz o seu CoInitialize).
    IUIAutomation: 7 ElementFromPoint, 8 GetFocusedElement, 14 ControlViewWalker. Elemento: 20 ProcessId, 21 ControlType,
    22 LocalizedControlType, 23 Name, 29 AutomationId, 30 ClassName, 35 IsPassword, 43 BoundingRectangle. Walker: 3 GetParent."""

    def __init__(self):
        ole32.CoInitializeEx(None, 0)          # MTA
        self.p = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(ctypes.byref(_guid("{FF48DBA4-60EF-4201-AA87-54103EEF594E}")), None, 1,
                                    ctypes.byref(_guid("{30CBE57D-D9D0-452A-AB13-7AC5AC4825EE}")), ctypes.byref(self.p))
        if hr != 0 or not self.p.value:
            raise OSError("UIA: CoCreateInstance = 0x%08X" % (hr & 0xFFFFFFFF))
        w = ctypes.c_void_p()
        self.walker = w if _metodo(self.p, 14, ctypes.POINTER(ctypes.c_void_p))(self.p, ctypes.byref(w)) == 0 and w.value else None

    @staticmethod
    def _solta(el):
        try:
            if el and el.value:
                _metodo(el, 2)(el)
        except Exception:
            pass

    @staticmethod
    def _bstr(el, idx):
        b = ctypes.c_void_p()
        if _metodo(el, idx, ctypes.POINTER(ctypes.c_void_p))(el, ctypes.byref(b)) != 0 or not b.value:
            return ""
        try:
            return ctypes.wstring_at(b.value)
        finally:
            oleaut32.SysFreeString(b)

    @staticmethod
    def _int(el, idx):
        v = ctypes.c_int()
        return v.value if _metodo(el, idx, ctypes.POINTER(ctypes.c_int))(el, ctypes.byref(v)) == 0 else None

    @staticmethod
    def _ret(el):
        r = wt.RECT()
        if _metodo(el, 43, ctypes.POINTER(wt.RECT))(el, ctypes.byref(r)) != 0:
            return None
        return [r.left, r.top, r.right, r.bottom]

    def _pai(self, el):
        if not self.walker:
            return None
        p = ctypes.c_void_p()
        if _metodo(self.walker, 3, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))(self.walker, el, ctypes.byref(p)) != 0:
            return None
        return p if p.value else None

    def em(self, x, y):
        """o elemento no ponto (x, y) da tela: {nome, controle, tipo_id, app, ret, [dentro_de], [senha]}"""
        el = ctypes.c_void_p()
        if _metodo(self.p, 7, wt.POINT, ctypes.POINTER(ctypes.c_void_p))(self.p, wt.POINT(int(x), int(y)), ctypes.byref(el)) != 0 \
                or not el.value:
            return None
        soltar = [el]
        try:
            senha = bool(self._int(el, 35))
            d = {"nome": "" if senha else self._bstr(el, 23).strip()[:200], "controle": self._bstr(el, 22),
                 "tipo_id": self._int(el, 21), "app": exe_do_pid(self._int(el, 20)), "ret": self._ret(el)}
            if senha:
                d["senha"] = True
            aid = self._bstr(el, 29)
            if aid and not senha:
                d["automation_id"] = aid[:80]
            # quem contém (o card, o item da lista, o botão): sobe até achar um nome, no máximo 4 níveis
            atual = el
            for _ in range(4):
                pai = self._pai(atual)
                if not pai:
                    break
                soltar.append(pai); atual = pai
                n = self._bstr(atual, 23).strip()
                if n and n != d["nome"]:
                    d["dentro_de"] = {"nome": n[:120], "controle": self._bstr(atual, 22)}
                    break
            return d
        finally:
            for e in soltar:
                self._solta(e)

    def foco_e_senha(self):
        el = ctypes.c_void_p()
        if _metodo(self.p, 8, ctypes.POINTER(ctypes.c_void_p))(self.p, ctypes.byref(el)) != 0 or not el.value:
            return False
        try:
            return bool(self._int(el, 35))
        finally:
            self._solta(el)


# ------------------------------------------------------------------ print nativo
class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]


user32.MonitorFromPoint.argtypes = [wt.POINT, wt.DWORD]
user32.MonitorFromPoint.restype = ctypes.c_void_p
user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]


def monitor_de(x, y):
    h = user32.MonitorFromPoint(wt.POINT(int(x), int(y)), 2)     # MONITOR_DEFAULTTONEAREST
    mi = MONITORINFO(); mi.cbSize = ctypes.sizeof(mi)
    if h and user32.GetMonitorInfoW(h, ctypes.byref(mi)):
        r = mi.rcMonitor
        return (r.left, r.top, r.right, r.bottom)
    return (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


def miniatura(im):
    return im.resize((96, 54)).convert("L")


def parecida(a, b):
    """duas miniaturas quase iguais (a tela não mudou)"""
    if a is None or b is None:
        return False
    from PIL import ImageChops, ImageStat
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0] < 1.5


def print_nativo(x, y):
    """(imagem do monitor inteiro em resolução nativa, retângulo do monitor). A marca do cursor entra no salvar_print."""
    from PIL import ImageGrab
    l, t, r, b = monitor_de(x, y)
    return ImageGrab.grab(bbox=(l, t, r, b), all_screens=True), (l, t, r, b)


def salvar_print(im, mon, x, y, base):
    """base.jpg = monitor inteiro com o cursor marcado; base_perto.jpg = recorte 800x500 em volta do cursor"""
    from PIL import ImageDraw
    l, t = mon[0], mon[1]
    cx, cy = int(x) - l, int(y) - t
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)
    # anel largo + ponto pequeno: marca onde está o cursor sem tampar a palavra que ele aponta
    for rad, larg, cor in ((52, 7, (0, 0, 0)), (49, 4, (255, 30, 46))):
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=cor, width=larg)
    d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(255, 30, 46), outline=(0, 0, 0))
    im.save(base + ".jpg", quality=82)
    W, H = im.size
    cl, ct = max(0, min(cx - 400, W - 800)), max(0, min(cy - 250, H - 500))
    im.crop((cl, ct, cl + min(800, W), ct + min(500, H))).save(base + "_perto.jpg", quality=90)


# ------------------------------------------------------------------ área de transferência (o que ele copiou)
CF_UNICODETEXT, CF_BITMAP, CF_DIB, CF_HDROP, CF_DIBV5 = 13, 2, 8, 15, 17
user32.GetClipboardData.restype = ctypes.c_void_p
user32.GetClipboardData.argtypes = [wt.UINT]
user32.EnumClipboardFormats.argtypes = [wt.UINT]
user32.EnumClipboardFormats.restype = wt.UINT
user32.GetClipboardSequenceNumber.restype = wt.DWORD
user32.RegisterClipboardFormatW.restype = wt.UINT
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]; kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalSize.argtypes = [ctypes.c_void_p]; kernel32.GlobalSize.restype = ctypes.c_size_t
# formatos que gerenciador de senha (KeePass, 1Password, Bitwarden...) põe pra ninguém ler/guardar o que ele copiou
F_EXCLUIR = user32.RegisterClipboardFormatW("ExcludeClipboardContentFromMonitorProcessing")
F_IGNORAR = user32.RegisterClipboardFormatW("Clipboard Viewer Ignore")
F_HISTORICO = user32.RegisterClipboardFormatW("CanIncludeInClipboardHistory")
F_NUVEM = user32.RegisterClipboardFormatW("CanUploadToCloudClipboard")
F_HTML = user32.RegisterClipboardFormatW("HTML Format")
GERENCIADORES = {"keepass.exe", "keepassxc.exe", "1password.exe", "bitwarden.exe", "lastpass.exe", "dashlane.exe", "nordpass.exe",
                 "enpass.exe", "roboform.exe", "keeper.exe", "keeperpasswordmanager.exe", "proton pass.exe", "protonpass.exe"}


def _dword(fmt):
    h = user32.GetClipboardData(fmt)
    p = kernel32.GlobalLock(h) if h else None
    if not p:
        return None
    try:
        return ctypes.c_uint32.from_address(p).value
    finally:
        kernel32.GlobalUnlock(h)


def ler_area():
    """{"protegido": True} | {"texto", "html_fonte", "html_img", "imagem": bool, "arquivos": bool} | None (não abriu)"""
    for _ in range(10):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return None
    try:
        fmts = set(); f = 0
        while True:
            f = user32.EnumClipboardFormats(f)
            if not f:
                break
            fmts.add(f)
        if F_EXCLUIR in fmts or F_IGNORAR in fmts:
            return {"protegido": True}
        for fp in (F_HISTORICO, F_NUVEM):
            if fp in fmts and _dword(fp) == 0:
                return {"protegido": True}
        r = {"imagem": bool(fmts & {CF_DIB, CF_DIBV5, CF_BITMAP}), "arquivos": CF_HDROP in fmts}
        if CF_UNICODETEXT in fmts:
            h = user32.GetClipboardData(CF_UNICODETEXT); p = kernel32.GlobalLock(h) if h else None
            if p:
                try:
                    r["texto"] = ctypes.wstring_at(p)
                finally:
                    kernel32.GlobalUnlock(h)
        if F_HTML in fmts:
            h = user32.GetClipboardData(F_HTML); p = kernel32.GlobalLock(h) if h else None
            if p:
                try:
                    raw = ctypes.string_at(p, min(kernel32.GlobalSize(h), 400000)).decode("utf-8", "replace")
                finally:
                    kernel32.GlobalUnlock(h)
                m = re.search(r"SourceURL:(\S+)", raw)
                if m:
                    r["html_fonte"] = m.group(1)
                m = re.search(r"<img[^>]+src=\"([^\"]+)\"", raw, re.I)
                if m:
                    r["html_img"] = html.unescape(m.group(1))[:500]
        return r
    finally:
        user32.CloseClipboard()


def pasta_capturas():
    """Imagens\\Capturas de Tela (onde a Ferramenta de Captura / Win+Shift+S salva sozinha)"""
    p = ctypes.c_void_p()
    try:
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(_guid("{B7BEDE81-DF94-4682-A7D8-57A52620B86F}")), 0, None,
                                                      ctypes.byref(p)) == 0 and p.value:
            s = ctypes.wstring_at(p.value); ole32.CoTaskMemFree(p)
            return s
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")


def hash_imagem(im):
    return hashlib.sha1(im.convert("RGB").tobytes()).hexdigest()


# Chrome, relógio da sessão, duracao e ler_wav: em comum.py (porte pro Mac)
from comum import (FFMPEG, FFPROBE, SEM_JANELA, CHROME_HIST, historico_chrome, UA, _baixar, og_image,  # noqa
                   imagem_do_pin, baixar_refs, t_da_sessao, fim_da_sessao, links_da_sessao, duracao, ler_wav)


# ------------------------------------------------------------------ áudio/vídeo: replay e junção
def gravar_wav(arq, dados, taxa, canais, larg=2):
    with wave.open(arq, "wb") as w:
        w.setnchannels(canais); w.setsampwidth(larg); w.setframerate(taxa); w.writeframes(dados)


def extrair_wav_fim(segs, segundos, saida):
    """junta os pedaços de wav (em ordem) e fica com os ÚLTIMOS 'segundos' (silêncio no começo se faltar)"""
    partes, fmt = [], None
    for s in segs:
        try:
            d, taxa, can, larg = ler_wav(s)
        except Exception:
            continue
        if fmt is None:
            fmt = (taxa, can, larg)
        if (taxa, can, larg) == fmt:
            partes.append(d)
    if fmt is None:
        return False
    taxa, can, larg = fmt
    tudo = b"".join(partes)
    n = int(round(segundos * taxa)) * can * larg
    tudo = tudo[-n:] if len(tudo) >= n else b"\0" * (n - len(tudo)) + tudo
    gravar_wav(saida, tudo, taxa, can, larg)
    return True


MUDO = 2       # pico de 16 bits abaixo disto = silêncio digital (< -85 dBFS; o microfone sem fio dele corta pra 0/±1 nas pausas)


def pico_fim(arqs, segundos):
    """maior |amostra| dos ÚLTIMOS 'segundos' da sequência de wavs (o último pode estar sendo gravado); None = sem dado"""
    picos, falta = [], segundos
    for arq in reversed(arqs):
        try:
            with open(arq, "rb") as f:
                cab = f.read(4096)
                i = cab.find(b"fmt "); j = cab.find(b"data", i)
                if i < 0 or j < 0:
                    continue
                taxa, can = int.from_bytes(cab[i + 12:i + 16], "little"), int.from_bytes(cab[i + 10:i + 12], "little")
                ini_dados = j + 8; tam = os.path.getsize(arq)
                n = min(tam - ini_dados, int(falta * taxa) * can * 2)
                if n <= 0:
                    continue
                f.seek(tam - n); b = f.read(n)
        except (OSError, ValueError):
            continue
        a = array.array("h"); a.frombytes(b[: len(b) // 2 * 2])
        if a:
            picos.append(max(max(a), -min(a)))
        falta -= len(a) / float(taxa * can)
        if falta <= 0.05:
            break
    return max(picos) if picos else None


def extrair_fala_fim(segs, segundos, saida):
    """como o extrair_wav_fim, mas sabendo que o microfone pode ter sido REABERTO no meio (P20): os pedaços
    fala_<geração>_<n>.wav de cada abertura são juntados em sequência e cada abertura é posta na linha do tempo pela
    hora em que o último pedaço dela fechou (mtime). A abertura mais nova termina no fim do buffer (igual ao de antes);
    buraco entre aberturas = silêncio. Uma abertura só = exatamente o extrair_wav_fim."""
    geracoes = {}
    for s in segs:
        m = re.search(r"fala_(\d+)_\d+\.wav$", s)
        geracoes.setdefault(m.group(1) if m else "", []).append(s)
    if len(geracoes) <= 1:
        return extrair_wav_fim(segs, segundos, saida)
    ordem = sorted(geracoes)
    blocos, fmt = [], None
    for g in ordem:
        partes = []
        for s in sorted(geracoes[g]):
            try:
                d, taxa, can, larg = ler_wav(s)
            except Exception:
                continue
            if fmt is None:
                fmt = (taxa, can, larg)
            if (taxa, can, larg) == fmt:
                partes.append(d)
        if partes:
            try:
                fecha = os.path.getmtime(sorted(geracoes[g])[-1])
            except OSError:
                continue
            blocos.append((fecha, b"".join(partes)))
    if fmt is None or not blocos:
        return False
    taxa, can, larg = fmt
    bpf = can * larg
    n = int(round(segundos * taxa))
    buf = bytearray(n * bpf)
    ultimo = blocos[-1][0]
    for fecha, d in blocos:                       # a mais nova por último (por cima, se encostar)
        fim_q = n - int(round((ultimo - fecha) * taxa))
        ini_q = fim_q - len(d) // bpf
        a, b = max(0, ini_q), min(n, fim_q)
        if b > a:
            buf[a * bpf:b * bpf] = d[(a - ini_q) * bpf:(b - ini_q) * bpf]
    gravar_wav(saida, bytes(buf), taxa, can, larg)
    return True


def extrair_pc(pecas, ini, fim, saida):
    """som do PC no intervalo [ini, fim] (epoch), montado pelos manifestos do gravar_pc.py (t0 de cada segmento); buraco = silêncio.
    P20: segmento de outra saída com outro formato (fone 44,1 kHz mono x monitor 48 kHz estéreo) é convertido, não fica de fora."""
    segs = []
    for man in pecas:
        try:
            m = json.load(open(man, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for s in m.get("segmentos", []):
            arq = os.path.join(os.path.dirname(man), s["arquivo"])
            if os.path.isfile(arq):
                segs.append((s["t0"], arq))
    if not segs:
        return False
    segs.sort()
    fmt = None
    for t0, arq in reversed(segs):
        try:
            _, taxa, can, larg = ler_wav(arq); fmt = (taxa, can, larg); break
        except Exception:
            continue
    if not fmt:
        return False
    taxa, can, larg = fmt
    bpf = can * larg
    n = int(round((fim - ini) * taxa))
    buf = bytearray(n * bpf)
    for t0, arq in segs:
        try:
            d, tx, c, lg = ler_wav(arq)
            if (tx, c, lg) != fmt:
                tmp = arq + ".conv.wav"
                subprocess.run([FFMPEG, "-v", "error", "-y", "-ignore_length", "1", "-i", arq, "-ar", str(taxa), "-ac", str(can), "-c:a", "pcm_s16le", tmp],
                               capture_output=True, timeout=300, creationflags=SEM_JANELA)
                d, tx, c, lg = ler_wav(tmp)
                os.remove(tmp)
                if (tx, c, lg) != fmt:
                    continue
        except Exception:
            continue
        ini_q = int(round((t0 - ini) * taxa))
        a, b = max(0, ini_q), min(n, ini_q + len(d) // bpf)
        if b > a:
            buf[a * bpf:b * bpf] = d[(a - ini_q) * bpf:(b - ini_q) * bpf]
    gravar_wav(saida, bytes(buf), taxa, can, larg)
    return True


VIDEO_ENC = ["-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency", "-crf", "30", "-g", "10", "-pix_fmt", "yuv420p"]


def extrair_video_fim(segs, segundos, saida, log=None):
    """últimos 'segundos' dos pedaços .ts do buffer → mp4 com os MESMOS parâmetros da gravação (pra juntar sem reencodar)"""
    segs = [s for s in segs if os.path.getsize(s) > 0]
    if not segs:
        return False
    lista = saida + ".txt"
    with open(lista, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '%s'\n" % s.replace("\\", "/").replace("'", "'\\''"))
    total = sum(duracao(s) for s in segs)
    ss = max(0.0, total - segundos)
    falta = max(0.0, segundos - total)
    vf = "fps=5,scale=1920:-2:flags=bilinear,format=yuv420p"
    if falta > 0.2:
        vf += ",tpad=start_duration=%.2f:color=black" % falta
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-ss", "%.3f" % ss,
           "-t", "%.3f" % segundos, "-vf", vf] + VIDEO_ENC + ["-threads", "2", "-an", "-y", saida]
    r = subprocess.run(cmd, capture_output=True, timeout=300, creationflags=SEM_JANELA)
    try:
        os.remove(lista)
    except OSError:
        pass
    if r.returncode != 0 and log:
        log("replay vídeo: %s" % r.stderr.decode("utf-8", "replace")[-300:])
    return r.returncode == 0 and os.path.isfile(saida)


def juntar_video(partes, saida, log=None):
    lista = saida + ".txt"
    with open(lista, "w", encoding="utf-8") as f:
        for s in partes:
            f.write("file '%s'\n" % s.replace("\\", "/").replace("'", "'\\''"))
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
                        "-movflags", "+faststart", "-y", saida], capture_output=True, timeout=900, creationflags=SEM_JANELA)
    try:
        os.remove(lista)
    except OSError:
        pass
    if r.returncode != 0 and log:
        log("juntar vídeo: %s" % r.stderr.decode("utf-8", "replace")[-300:])
    return r.returncode == 0


def juntar_wav(partes, saida):
    """concatena wavs (o formato do ÚLTIMO manda; os outros são convertidos pelo ffmpeg se diferirem)"""
    _, taxa, can, larg = ler_wav(partes[-1])
    blocos = []
    for p in partes:
        d, tx, c, lg = ler_wav(p)
        if (tx, c, lg) != (taxa, can, larg):
            tmp = p + ".conv.wav"
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", p, "-ar", str(taxa), "-ac", str(can), "-c:a", "pcm_s16le", tmp],
                           creationflags=SEM_JANELA)
            d, _, _, _ = ler_wav(tmp)
            os.remove(tmp)
        blocos.append(d)
    gravar_wav(saida, b"".join(blocos), taxa, can, larg)
    return True


def nivel_voz(arq, segundos=0.4):
    """RMS do fim do wav que está sendo gravado (fala ~ > 400)"""
    try:
        tam = os.path.getsize(arq)
        with open(arq, "rb") as f:
            f.seek(max(44, tam - int(48000 * 2 * segundos))); b = f.read()
        a = array.array("h"); a.frombytes(b[: len(b) // 2 * 2])
        if not a:
            return 0
        a = a[::4]
        return (sum(x * x for x in a) / len(a)) ** 0.5
    except Exception:
        return 0


# ------------------------------------------------------------------ Mac (porte de 02/11): as mesmas peças, pelo mac.py
if os.name != "nt":
    _salvar_print_windows = salvar_print
    UIA = mac.UIA
    ler_area = mac.ler_area
    pasta_capturas = mac.pasta_capturas
    monitor_de = mac.monitor_de
    print_nativo = mac.print_nativo
    GERENCIADORES = GERENCIADORES | mac.GERENCIADORES

    def salvar_print(im, mon, x, y, base):
        """no Mac o cursor vem em pontos e o print em pixels (Retina = 2x): converte e usa o mesmo desenho do Windows"""
        s = mac.escala(im, mon)
        _salvar_print_windows(im, (0, 0, im.width, im.height), (x - mon[0]) * s, (y - mon[1]) * s, base)
