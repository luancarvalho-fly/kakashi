# -*- coding: utf-8 -*-
"""MODO CAPTURA do Kakashi (12/11/2026) — o lugar do Lightshot.

Pedido dele (chat 12/11 ~17h05): «bora adaptar o Kakashi pra eu poder parar de usar o Light Shot... se só apertar Page Down, ele abre o
negocinho do Kakashi, eu consigo... escolher uma parte do print, desenhar, ou tudo que eu copiar enquanto tiver ativado esse modo... eu
ativo ele com Page Down e desativo com Page Down de novo... se eu copiar 7 coisas, quando eu terminar o Page Down de novo e colar, ele
vai colar em massa... Arquivo... eu mostrei um vídeo na internet, aí você pegou o link, ou um áudio do WhatsApp, aí baixou o áudio...
Já anexou na conversa... se eu quiser só tirar um print, pegar o link igual o Light Shot». Decisões dele na mesma hora: a tecla é o
PAGE DOWN SOZINHO (sabendo que ele deixa de rolar página enquanto o Kakashi está aberto); o print rápido SÓ COPIA a imagem (nada sobe
pra internet: o link do Lightshot é público); no fim COLA OS ARQUIVOS de uma vez (anexo) + os links/textos.

Peças:
- Recorte: a tela congela (print do monitor), escurece, ele arrasta a área; dentro dela desenha (caneta, marca-texto, linha, seta,
  quadrado, 4 cores, desfazer) e Enter / Ctrl+C / o ✓ copia a imagem (desenho liso, por cima do print intacto). Esc / botão direito
  = sai sem print.
- Coleta (enquanto o modo está ligado): o que ele copia (texto, link, imagem, arquivos; senha nunca), o que chega na pasta Downloads
  (o áudio do WhatsApp baixado, o arquivo salvo) e, no fim, as páginas que ele abriu no Chrome nesse intervalo.
- Fim: cola os ARQUIVOS (prints, imagens copiadas, arquivos, downloads) como anexo e depois os LINKS e TEXTOS como texto. Tudo fica
  também na pasta da captura (sessoes\\_capturas\\<data>) com um CAPTURA.md.
"""
import ctypes, ctypes.wintypes as wt, datetime, json, os, re, threading, time

from PIL import Image, ImageDraw, ImageGrab

import olho
import visual

_u32 = ctypes.WinDLL("user32", use_last_error=True)
_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.GlobalAlloc.restype = ctypes.c_void_p; _k32.GlobalAlloc.argtypes = (wt.UINT, ctypes.c_size_t)
_k32.GlobalLock.restype = ctypes.c_void_p; _k32.GlobalLock.argtypes = (ctypes.c_void_p,)
_k32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
_u32.OpenClipboard.argtypes = (wt.HWND,)
_u32.SetClipboardData.restype = ctypes.c_void_p; _u32.SetClipboardData.argtypes = (wt.UINT, ctypes.c_void_p)
_u32.GetClipboardSequenceNumber.restype = wt.DWORD
_u32.RegisterClipboardFormatW.restype = wt.UINT
CF_UNICODETEXT, CF_DIB, CF_HDROP = 13, 8, 15
CF_PNG = _u32.RegisterClipboardFormatW("PNG")
CORES = (("vermelho", "#ff3b5c"), ("amarelo", "#ffd60a"), ("verde", "#30d158"), ("azul", "#0a84ff"))
FERRS = (("caneta", "Caneta"), ("marca", "Marca-texto"), ("linha", "Linha"), ("seta", "Seta"), ("caixa", "Quadrado"))
_proprias = set()                        # números de sequência da área de transferência que EU pus (a coleta ignora)


# ------------------------------------------------------------------ área de transferência
def _por(formatos):
    """põe na área de transferência [(formato, bytes)] de uma vez"""
    for _ in range(40):
        if _u32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return False
    try:
        _u32.EmptyClipboard()
        for fmt, dados in formatos:
            h = _k32.GlobalAlloc(0x0002, len(dados))
            p = _k32.GlobalLock(h)
            ctypes.memmove(p, dados, len(dados))
            _k32.GlobalUnlock(h)
            _u32.SetClipboardData(fmt, h)
        return True
    finally:
        _u32.CloseClipboard()
        _proprias.add(int(_u32.GetClipboardSequenceNumber()))


def copiar_imagem(im):
    import io
    rgb = im.convert("RGB")
    b = io.BytesIO(); rgb.save(b, "BMP"); dib = b.getvalue()[14:]
    p = io.BytesIO(); im.save(p, "PNG")
    return _por([(CF_DIB, dib), (CF_PNG, p.getvalue())])


def copiar_arquivos(caminhos):
    """CF_HDROP: o Ctrl+V cola os arquivos (anexo), igual copiar no Explorador"""
    lista = ("\0".join(os.path.abspath(c) for c in caminhos) + "\0\0").encode("utf-16-le")
    cab = ctypes.c_uint32(20).value.to_bytes(4, "little") + (0).to_bytes(4, "little") * 2 + (0).to_bytes(4, "little") + (1).to_bytes(4, "little")
    return _por([(CF_HDROP, cab + lista)])


def copiar_texto(txt):
    return _por([(CF_UNICODETEXT, (txt + "\0").encode("utf-16-le"))])


def colar(espera=0.12):
    time.sleep(espera)
    _u32.keybd_event(0x11, 0, 0, 0); _u32.keybd_event(0x56, 0, 0, 0)
    _u32.keybd_event(0x56, 0, 2, 0); _u32.keybd_event(0x11, 0, 2, 0)


# ------------------------------------------------------------------ a coleta
def pasta_downloads():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as k:
            return winreg.QueryValueEx(k, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
    except OSError:
        return os.path.join(os.path.expanduser("~"), "Downloads")


class Captura:
    """o modo ligado: junta o que ele copia e o que chega no Downloads; os prints do recorte entram por adicionar_print"""

    def __init__(self, base, log=print):
        self.log = log
        self.t0 = time.time()
        self.pasta = os.path.join(base, datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_captura")
        os.makedirs(self.pasta, exist_ok=True)
        self.itens = []                   # {"tipo": print|imagem|arquivo|download|link|texto, "valor": caminho ou texto, "t"}
        self.parar = threading.Event()
        self.trava = threading.Lock()
        threading.Thread(target=self._area, daemon=True).start()
        threading.Thread(target=self._downloads, daemon=True).start()
        self.log("captura: ligada (%s)" % os.path.basename(self.pasta))

    def _add(self, tipo, valor):
        with self.trava:
            if any(i["tipo"] == tipo and i["valor"] == valor for i in self.itens):
                return
            self.itens.append({"tipo": tipo, "valor": valor, "t": round(time.time() - self.t0, 1)})
        self.log("captura: + %s %s" % (tipo, str(valor)[:80]))

    def n(self):
        return len(self.itens)

    def _salvar(self, im, nome):
        arq = os.path.join(self.pasta, "%02d_%s.png" % (len(self.itens) + 1, nome))
        im.save(arq)
        return arq

    def adicionar_print(self, im):
        self._add("print", self._salvar(im, "print"))

    def _area(self):
        seq = int(_u32.GetClipboardSequenceNumber())
        while not self.parar.wait(0.3):
            s = int(_u32.GetClipboardSequenceNumber())
            if s == seq:
                continue
            seq = s
            if s in _proprias:
                continue
            time.sleep(0.15)
            try:
                a = olho.ler_area()
                if not a or a.get("protegido"):
                    continue                  # gerenciador de senha marcou: nem lê
                if a["imagem"]:
                    im = ImageGrab.grabclipboard()
                    if isinstance(im, Image.Image):
                        self._add("imagem", self._salvar(im, "imagem"))
                elif a["arquivos"]:
                    lst = ImageGrab.grabclipboard()
                    for c in (lst or []) if isinstance(lst, list) else []:
                        if os.path.exists(str(c)):
                            self._add("arquivo", str(c))
                elif (a.get("texto") or "").strip():
                    t = a["texto"].strip()
                    self._add("link" if re.fullmatch(r"(https?://|www\.)\S+", t) else "texto", t)
            except Exception as e:
                self.log("captura/área: %r" % e)

    def _downloads(self):
        pasta = pasta_downloads()
        try:
            vistos = {n: os.path.getsize(os.path.join(pasta, n)) for n in os.listdir(pasta)}
        except OSError:
            return
        espera = {}
        while not self.parar.wait(1.0):
            try:
                atuais = os.listdir(pasta)
            except OSError:
                continue
            for n in atuais:
                if n in vistos or n.lower().endswith((".crdownload", ".tmp", ".part", ".partial", ".download")) or n.startswith("~"):
                    continue
                p = os.path.join(pasta, n)
                try:
                    tam = os.path.getsize(p)
                except OSError:
                    continue
                if espera.get(n) == tam and tam > 0:          # o tamanho parou: o download terminou
                    vistos[n] = tam; espera.pop(n, None)
                    self._add("download", p)
                else:
                    espera[n] = tam

    def concluir(self):
        """para a coleta, junta as páginas do Chrome do intervalo e escreve o CAPTURA.md; devolve (arquivos, texto)"""
        self.parar.set()
        fim = time.time()
        paginas = []
        try:
            for l in olho.historico_chrome(self.t0, fim):
                if l.get("url") and not any(p["url"] == l["url"] for p in paginas):
                    paginas.append(l)
        except Exception as e:
            self.log("captura/links: %r" % e)
        arquivos = [i["valor"] for i in self.itens if i["tipo"] in ("print", "imagem", "arquivo", "download")]
        links = [i["valor"] for i in self.itens if i["tipo"] == "link"]
        textos = [i["valor"] for i in self.itens if i["tipo"] == "texto"]
        linhas = []
        for u in links:
            linhas.append(u)
        extra = [p for p in paginas if p["url"] not in links][:15]
        if extra:
            linhas += ["", "Páginas que abri:"] + ["- %s — %s" % ((p.get("titulo") or "").strip()[:70], p["url"]) for p in extra]
        if textos:
            linhas += [""] + ["«%s»" % t[:1500] for t in textos]
        texto = "\n".join(linhas).strip()
        md = ["# CAPTURA · %s (%d s)" % (datetime.datetime.fromtimestamp(self.t0).strftime("%d/%m %H:%M"), int(fim - self.t0)), ""]
        md += ["- [%s] %s: %s" % (i["t"], i["tipo"], i["valor"]) for i in self.itens]
        md += ["", "## Páginas abertas no Chrome"] + ["- %s — %s" % ((p.get("titulo") or "")[:70], p["url"]) for p in paginas]
        open(os.path.join(self.pasta, "CAPTURA.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
        json.dump({"inicio_epoch": self.t0, "fim_epoch": fim, "itens": self.itens, "paginas": paginas},
                  open(os.path.join(self.pasta, "captura.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self.log("captura: desligada · %d arquivos, %d links, %d textos, %d páginas" % (len(arquivos), len(links), len(textos), len(paginas)))
        return arquivos, texto


# ------------------------------------------------------------------ o recorte (Tk)
class Recorte:
    """a tela congelada: arrasta a área, desenha dentro, Enter/Ctrl+C/✓ copia. Esc/botão direito sai sem print.
    pronto(im ou None) é chamado no fim (no thread do Tk)."""

    def __init__(self, tk, root, pronto, escala=1.0):
        self.tk, self.pronto, self.F = tk, pronto, escala
        x, y = _u32_cursor()
        self.mon = olho.monitor_de(x, y)
        l, t, r, b = self.mon
        self.tela = ImageGrab.grab(bbox=(l, t, r, b), all_screens=True).convert("RGBA")
        from PIL import ImageEnhance, ImageTk
        self.ImageTk = ImageTk
        escura = ImageEnhance.Brightness(self.tela.convert("RGB")).enhance(0.45)
        self.win = tk.Toplevel(root); self.win.overrideredirect(True); self.win.attributes("-topmost", True)
        self.win.geometry("%dx%d+%d+%d" % (r - l, b - t, l, t))
        self.cv = tk.Canvas(self.win, width=r - l, height=b - t, highlightthickness=0, bd=0, cursor="crosshair")
        self.cv.pack()
        self._fundo = ImageTk.PhotoImage(escura, master=self.win)
        self.cv.create_image(0, 0, image=self._fundo, anchor="nw")
        self.caixa = None; self.ini = None; self.ferr = "caneta"; self.cor = 0
        self.tracos = []; self.atual = None; self.barra = []; self.hover = None
        self.cv.create_text((r - l) // 2, int(40 * self.F), text="Arraste a área · Esc sai", fill="#FFFFFF",
                            font=("Segoe UI", int(13 * self.F)), tags="dica")
        for ev, f in (("<ButtonPress-1>", self._apertou), ("<B1-Motion>", self._arrastou), ("<ButtonRelease-1>", self._soltou),
                      ("<Button-3>", lambda e: self.fechar(None)), ("<Motion>", self._mexeu)):
            self.cv.bind(ev, f)
        for k in ("<Escape>",):
            self.win.bind(k, lambda e: self.fechar(None))
        for k in ("<Return>", "<Control-c>", "<Control-C>"):
            self.win.bind(k, lambda e: self.copiar())
        self.win.bind("<Control-z>", lambda e: self.desfazer())
        self.win.focus_force()

    # coordenadas: tudo no canvas (0,0 = canto do monitor)
    def _apertou(self, e):
        z = self._zona(e.x, e.y)
        if z is not None:
            return self._clique(z)
        if self.caixa is None:
            self.ini = (e.x, e.y)
            return
        x0, y0, x1, y1 = self.caixa
        if x0 <= e.x <= x1 and y0 <= e.y <= y1:                 # dentro da área: desenha
            self.atual = {"ferr": self.ferr, "cor": self.cor, "pts": [(e.x, e.y)], "itens": []}
        else:                                                    # fora: começa outra área
            self.caixa = None; self.tracos = []; self.cv.delete("area", "traco", "barra"); self.ini = (e.x, e.y)

    def _arrastou(self, e):
        if self.ini is not None:
            x0, y0 = self.ini
            self._mostrar_area(min(x0, e.x), min(y0, e.y), max(x0, e.x), max(y0, e.y))
        elif self.atual is not None:
            x0, y0, x1, y1 = self.caixa
            p = (min(max(e.x, x0), x1), min(max(e.y, y0), y1))
            pts = self.atual["pts"]
            if self.atual["ferr"] in ("caneta", "marca"):
                pts.append(p)
            elif len(pts) == 1:
                pts.append(p)
            else:
                pts[-1] = p
            self._desenhar_traco(self.atual)

    def _soltou(self, e):
        if self.ini is not None:
            x0, y0 = self.ini; self.ini = None
            if abs(e.x - x0) < 6 or abs(e.y - y0) < 6:
                return
            self._mostrar_area(min(x0, e.x), min(y0, e.y), max(x0, e.x), max(y0, e.y))
            self._barra()
        elif self.atual is not None:
            tr, self.atual = self.atual, None
            if len(tr["pts"]) >= 2:
                self.tracos.append(tr)
            else:
                for i in tr["itens"]:
                    self.cv.delete(i)

    def _mexeu(self, e):
        z = self._zona(e.x, e.y)
        if z != self.hover:
            self.hover = z
            if self.caixa:
                self._barra()

    def _mostrar_area(self, x0, y0, x1, y1):
        self.caixa = (x0, y0, x1, y1)
        self.cv.delete("area", "dica")
        crop = self.tela.crop((x0, y0, x1, y1))
        self._img_area = self.ImageTk.PhotoImage(crop, master=self.win)
        self.cv.create_image(x0, y0, image=self._img_area, anchor="nw", tags="area")
        self.cv.create_rectangle(x0 - 1, y0 - 1, x1 + 1, y1 + 1, outline="#FFFFFF", width=1, tags="area")
        self.cv.create_text(x0, y0 - 8, text="%d × %d" % (x1 - x0, y1 - y0), fill="#FFFFFF", anchor="sw",
                            font=("Segoe UI", int(10 * self.F)), tags="area")
        self.cv.tag_raise("traco")

    def _desenhar_traco(self, tr):
        for i in tr["itens"]:
            self.cv.delete(i)
        c = CORES[tr["cor"]][1]; w = max(2, int(3.5 * self.F))
        xy = [v for p in tr["pts"] for v in p]
        if len(xy) < 4:
            return
        f = tr["ferr"]
        if f == "caneta":
            tr["itens"] = [self.cv.create_line(*xy, fill=c, width=w, capstyle="round", joinstyle="round", smooth=True, tags="traco")]
        elif f == "marca":
            tr["itens"] = [self.cv.create_line(*xy, fill=c, width=int(18 * self.F), capstyle="butt", joinstyle="round",
                                               stipple="gray50", tags="traco")]
        elif f == "linha":
            tr["itens"] = [self.cv.create_line(*xy[:2], *xy[-2:], fill=c, width=w, capstyle="round", tags="traco")]
        elif f == "seta":
            tr["itens"] = [self.cv.create_line(*xy[:2], *xy[-2:], fill=c, width=w, capstyle="round", arrow="last",
                                               arrowshape=(int(15 * self.F), int(17 * self.F), int(6 * self.F)), tags="traco")]
        elif f == "caixa":
            x0, y0, x1, y1 = xy[0], xy[1], xy[-2], xy[-1]
            tr["itens"] = [self.cv.create_rectangle(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), outline=c, width=w, tags="traco")]

    def desfazer(self):
        if self.tracos:
            for i in self.tracos.pop()["itens"]:
                self.cv.delete(i)

    # a barrinha de ferramentas embaixo da área (desenhada pelo visual.py: a mesma cara da barra)
    def _barra(self):
        x0, y0, x1, y1 = self.caixa
        e = {"ferr": self.ferr, "cor": self.cor, "hover": self.hover}
        im, zonas = visual.barra_recorte(e, self.F)
        W, H = im.size
        bx = max(4, min(x1 - W, self.win.winfo_width() - W - 4))
        by = y1 + 8 if y1 + 8 + H < self.win.winfo_height() else y0 - H - 8
        if by < 0:
            by = y1 - H - 8
        self._img_barra = self.ImageTk.PhotoImage(im, master=self.win)
        self.cv.delete("barra")
        self.cv.create_image(bx, by, image=self._img_barra, anchor="nw", tags="barra")
        self.barra = [(bx + a, by, bx + b, by + H, z) for a, b, z, _ in zonas]

    def _zona(self, x, y):
        return next((z for x0, y0, x1, y1, z in self.barra if x0 <= x < x1 and y0 <= y < y1), None)

    def _clique(self, z):
        if isinstance(z, tuple) and z[0] == "ferr":
            self.ferr = z[1]
        elif isinstance(z, tuple) and z[0] == "cor":
            self.cor = z[1]
        elif z == "desfazer":
            self.desfazer()
        elif z == "copiar":
            return self.copiar()
        elif z == "sair":
            return self.fechar(None)
        self._barra()

    # o print final: a área intacta + o desenho liso por cima
    def imagem(self):
        x0, y0, x1, y1 = self.caixa
        base = self.tela.crop((x0, y0, x1, y1))
        K = 4
        camada = Image.new("RGBA", (base.width * K, base.height * K), (0, 0, 0, 0))
        marca = Image.new("RGBA", camada.size, (0, 0, 0, 0))
        d, dm = ImageDraw.Draw(camada), ImageDraw.Draw(marca)
        w = max(2, int(3.5 * self.F)) * K
        for tr in self.tracos:
            c = visual.rgba(CORES[tr["cor"]][1])
            pts = [((x - x0) * K, (y - y0) * K) for x, y in tr["pts"]]
            f = tr["ferr"]
            if f == "caneta":
                d.line(pts, fill=c, width=w, joint="curve")
                for x, y in (pts[0], pts[-1]):
                    d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=c)
            elif f == "marca":
                dm.line(pts, fill=c[:3] + (255,), width=int(18 * self.F) * K, joint="curve")
            elif f in ("linha", "seta"):
                (ax, ay), (bx, by) = pts[0], pts[-1]
                d.line([(ax, ay), (bx, by)], fill=c, width=w)
                for x, y in ((ax, ay), (bx, by)):
                    d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=c)
                if f == "seta":
                    import math
                    ang = math.atan2(by - ay, bx - ax); L, A = 16 * self.F * K, 0.42
                    d.polygon([(bx, by), (bx - L * math.cos(ang - A), by - L * math.sin(ang - A)),
                               (bx - L * math.cos(ang + A), by - L * math.sin(ang + A))], fill=c)
            elif f == "caixa":
                (ax, ay), (bx, by) = pts[0], pts[-1]
                d.rounded_rectangle((min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)), radius=4 * K, outline=c, width=w)
        camada = camada.resize(base.size, Image.LANCZOS)
        marca = marca.resize(base.size, Image.LANCZOS)
        a = marca.getchannel("A").point(lambda v: int(v * 0.42)); marca.putalpha(a)
        out = base.copy(); out.alpha_composite(marca); out.alpha_composite(camada)
        return out

    def copiar(self):
        if self.caixa is None:
            return
        im = self.imagem()
        copiar_imagem(im)
        self.fechar(im)

    def fechar(self, im):
        try:
            self.win.destroy()
        except Exception:
            pass
        self.pronto(im)


def _u32_cursor():
    pt = wt.POINT(); _u32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y
