# -*- coding: utf-8 -*-
"""O VISUAL do Kakashi 3.0 (12/11/2026) — barra e janelinha desenhadas em PIL, 4× maior e reduzidas (sem serrilhado).

Pedido dele (12/11 ~16h45, olhando a barra Grafite e a janelinha 8 bits): «esses ícones aí que você usou, não é pique iPhone não, mano,
e outra, a qualidade tá meio zoada, tá meio serrilhada... atualiza o próprio Kakashi... o painel dele, pensa no que você tem que
otimizar, o que tem que ter de botão novo ali, de controle... não é fazer só o rebranding na barra não, é fazer em tudo agora».

- Ícones no traço dos SF Symbols do iPhone (grade 24, traço ~1,75, pontas e cantos redondos), desenhados aqui — sem baixar nada.
- O Tk do Windows não suaviza borda: por isso a barra e a janelinha viram UMA imagem lisa (desenhada 4× e reduzida); o Tk só mostra
  a imagem e sabe onde cada botão está (as zonas que estas funções devolvem).
- O Sharingan (LEI de 14/10: o desenho que ele mandou, girando) é reduzido com filtro (LANCZOS), não pixel a pixel.
Tokens = o GRAFITE que ele escolheu (pins 331436853846619762 e 593771532153725227)."""
import math, os

from PIL import Image, ImageDraw, ImageFont

K = 4                                   # desenha 4× e reduz
_FONTES = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")
_INTER = {"r": os.path.join(_FONTES, "Inter-Regular.ttf"), "m": os.path.join(_FONTES, "Inter-Medium.ttf"),
          "sb": os.path.join(_FONTES, "Inter-SemiBold.ttf")}
_SISTEMA = {"r": r"C:\Windows\Fonts\segoeui.ttf", "m": r"C:\Windows\Fonts\segoeui.ttf", "sb": r"C:\Windows\Fonts\seguisb.ttf"}
COR = {"fundo": "#1C1C1E", "cartao": "#232325", "borda": "#3A3A3C", "seg": "#2C2C2E", "seg_sel": "#48484A", "hover": "#2C2C2E",
       "texto": "#FFFFFF", "texto2": "#8E8E93", "texto3": "#5A5A5E", "vermelho": "#FF453A", "amarelo": "#FFD60A", "verde": "#30D158",
       "azul": "#0A84FF", "preto": "#000000", "janela": "#161618"}
_cache_fonte = {}


def fonte(peso, px):
    k = (peso, px)
    if k not in _cache_fonte:
        arq = _INTER[peso] if os.path.isfile(_INTER[peso]) else _SISTEMA[peso]
        try:
            _cache_fonte[k] = ImageFont.truetype(arq, int(round(px * K)))
        except OSError:
            _cache_fonte[k] = ImageFont.load_default()
    return _cache_fonte[k]


def rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def largura_texto(txt, peso, px):
    return fonte(peso, px).getlength(txt) / K


# ------------------------------------------------------------------ ícones (grade 24, estilo SF Symbols)
def _traco(d, pts, w, cor, fechar=False):
    if fechar:
        pts = list(pts) + [pts[0]]
    d.line(pts, fill=cor, width=w, joint="curve")
    r = w / 2
    for x, y in pts:                     # pontas e cantos redondos
        d.ellipse((x - r, y - r, x + r, y + r), fill=cor)


def _ret_redondo(d, caixa, r, w=None, fill=None, outline=None):
    d.rounded_rectangle(caixa, radius=r, fill=fill, outline=outline, width=w or 0)


def icone(nome, px, cor="#FFFFFF", peso=1.75):
    """o ícone `nome` com `px` de lado, cor `cor`, pronto (já reduzido)"""
    S = 8                                 # supersample do ícone
    T = px * S
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = T / 24.0
    c = rgba(cor)
    w = max(1, int(round(peso * u)))
    P = lambda *xy: [(x * u, y * u) for x, y in zip(xy[::2], xy[1::2])]           # noqa: E731
    if nome == "cursor":
        _traco(d, P(6.5, 3.5, 6.5, 19.5, 10.4, 15.9, 13.1, 21.3, 15.5, 20.2, 12.9, 14.8, 18.2, 14.6), w, c, fechar=True)
    elif nome == "caneta":
        _traco(d, P(15.6, 4.6, 19.4, 8.4, 8.6, 19.2, 3.9, 20.1, 4.8, 15.4), w, c, fechar=True)
        _traco(d, P(13.4, 6.8, 17.2, 10.6), w, c)
    elif nome == "marca":
        _traco(d, P(13.8, 3.6, 20.4, 10.2, 14.1, 16.5, 7.5, 9.9), w, c, fechar=True)
        _traco(d, P(7.5, 9.9, 5.6, 17.6, 6.4, 18.4, 14.1, 16.5), w, c)
        _traco(d, P(3.6, 20.6, 8.8, 20.6), w, c)
    elif nome == "linha":
        _traco(d, P(5.5, 18.5, 18.5, 5.5), w, c)
    elif nome == "seta":
        _traco(d, P(6.2, 17.8, 17.6, 6.4), w, c)
        _traco(d, P(9.2, 6.2, 17.8, 6.2, 17.8, 14.8), w, c)
    elif nome == "caixa":
        _ret_redondo(d, (4.5 * u, 4.5 * u, 19.5 * u, 19.5 * u), 4 * u, w=w, outline=c)
    elif nome == "laser":
        d.ellipse((4 * u, 4 * u, 20 * u, 20 * u), outline=c, width=w)
        d.ellipse((8.6 * u, 8.6 * u, 15.4 * u, 15.4 * u), fill=c)
    elif nome == "desfazer":
        _traco(d, P(8.6, 4.8, 4.4, 9.2, 8.6, 13.6), w, c)
        _traco(d, P(4.6, 9.2, 14.2, 9.2), w, c)
        d.arc((9.2 * u, 9.2 * u, 19.4 * u, 19.6 * u), start=-90, end=90, fill=c, width=w)
        _traco(d, P(14.3, 19.6, 10.4, 19.6), w, c)
    elif nome == "limpar":
        _traco(d, P(4.2, 6.6, 19.8, 6.6), w, c)
        _traco(d, P(9.4, 6.6, 9.8, 4.2, 14.2, 4.2, 14.6, 6.6), w, c)
        _traco(d, P(6.2, 6.6, 7.2, 19.0, 8.4, 20.2, 15.6, 20.2, 16.8, 19.0, 17.8, 6.6), w, c)
        _traco(d, P(10.2, 10.4, 10.4, 16.6), w, c)
        _traco(d, P(13.8, 10.4, 13.6, 16.6), w, c)
    elif nome == "pausa":
        _ret_redondo(d, (6.6 * u, 4.8 * u, 10.4 * u, 19.2 * u), 1.6 * u, fill=c)
        _ret_redondo(d, (13.6 * u, 4.8 * u, 17.4 * u, 19.2 * u), 1.6 * u, fill=c)
    elif nome == "play":
        pts = P(7.4, 5.0, 19.0, 12.0, 7.4, 19.0)
        d.polygon(pts, fill=c)
        _traco(d, pts, w, c, fechar=True)
    elif nome == "gravar":
        d.ellipse((5.5 * u, 5.5 * u, 18.5 * u, 18.5 * u), fill=c)
    elif nome == "parar":
        _ret_redondo(d, (6.5 * u, 6.5 * u, 17.5 * u, 17.5 * u), 2.4 * u, fill=c)
    elif nome == "x":
        _traco(d, P(6.4, 6.4, 17.6, 17.6), w, c)
        _traco(d, P(17.6, 6.4, 6.4, 17.6), w, c)
    elif nome == "check":
        _traco(d, P(5.2, 12.6, 10.0, 17.4, 18.8, 6.8), w, c)
    elif nome == "pasta":
        _traco(d, P(3.6, 7.0, 3.6, 18.4, 4.8, 19.6, 19.2, 19.6, 20.4, 18.4, 20.4, 9.8, 19.2, 8.6, 11.6, 8.6, 9.6, 6.0, 4.8, 6.0),
               w, c, fechar=True)
    elif nome == "mic":
        _ret_redondo(d, (8.8 * u, 2.8 * u, 15.2 * u, 14.6 * u), 3.2 * u, w=w, outline=c)
        d.arc((5.4 * u, 6.0 * u, 18.6 * u, 18.0 * u), start=0, end=180, fill=c, width=w)
        _traco(d, P(12, 18.0, 12, 21.2), w, c)
    elif nome == "copiar":
        _ret_redondo(d, (8.4 * u, 8.4 * u, 19.6 * u, 19.6 * u), 2.6 * u, w=w, outline=c)
        _traco(d, P(15.6, 8.4, 15.6, 6.2, 14.4, 4.6, 6.0, 4.6, 4.6, 6.0, 4.6, 14.4, 6.0, 15.6, 8.4, 15.6), w, c)
    elif nome == "mais":
        _traco(d, P(12, 5.6, 12, 18.4), w, c)
        _traco(d, P(5.6, 12, 18.4, 12), w, c)
    elif nome == "menos":
        _traco(d, P(5.6, 12, 18.4, 12), w, c)
    elif nome == "canto":
        _ret_redondo(d, (3.6 * u, 5.0 * u, 20.4 * u, 19.0 * u), 3 * u, w=w, outline=c)
        _ret_redondo(d, (12.0 * u, 13.4 * u, 17.6 * u, 16.2 * u), 1.2 * u, fill=c)
    elif nome == "sair":
        d.arc((4.4 * u, 5.2 * u, 19.6 * u, 20.4 * u), start=-60, end=240, fill=c, width=w)
        _traco(d, P(12, 3.4, 12, 11.6), w, c)
    elif nome == "recorte":               # SF «crop»: as duas quinas do recorte
        _traco(d, P(7.0, 2.8, 7.0, 17.0, 21.2, 17.0), w, c)
        _traco(d, P(2.8, 7.0, 17.0, 7.0, 17.0, 21.2), w, c)
    elif nome == "colar":                 # SF «doc.on.clipboard»
        _ret_redondo(d, (5.2 * u, 4.6 * u, 18.8 * u, 21.0 * u), 2.6 * u, w=w, outline=c)
        _ret_redondo(d, (8.8 * u, 2.8 * u, 15.2 * u, 6.4 * u), 1.4 * u, fill=c)
        _traco(d, P(8.6, 11.4, 15.4, 11.4), w, c)
        _traco(d, P(8.6, 15.4, 13.0, 15.4), w, c)
    elif nome == "teclado":
        _ret_redondo(d, (2.8 * u, 6.0 * u, 21.2 * u, 18.0 * u), 2.6 * u, w=w, outline=c)
        _traco(d, P(7.6, 14.2, 16.4, 14.2), w, c)
    return im.resize((px, px), Image.LANCZOS)


# ------------------------------------------------------------------ o Sharingan, liso
_cache_olho = {}


def olho(pasta_icones, nome, px, cinza=False):
    k = (nome, px, cinza)
    if k not in _cache_olho:
        im = Image.open(os.path.join(pasta_icones, nome)).convert("RGBA")
        im = im.resize((px, px), Image.LANCZOS)
        if cinza:
            a = im.getchannel("A")
            im = im.convert("L").convert("RGBA"); im.putalpha(a)
        _cache_olho[k] = im
    return _cache_olho[k]


# ------------------------------------------------------------------ peças
class Tela4x:
    """uma imagem desenhada 4× com coordenadas em px da tela (1×)"""

    def __init__(self, w, h, fundo=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (int(w * K), int(h * K)), fundo)
        self.d = ImageDraw.Draw(self.im)
        self.zonas = []                   # (x0, y0, x1, y1, zona, dica)
        self.colas = []                   # (imagem 1×, x, y): ícones e olho colados depois de reduzir (nítidos)

    def ret(self, x0, y0, x1, y1, r, fill=None, outline=None, w=1):
        self.d.rounded_rectangle((x0 * K, y0 * K, x1 * K, y1 * K), radius=r * K, fill=rgba(fill) if fill else None,
                                 outline=rgba(outline) if outline else None, width=int(w * K) if outline else 0)

    def circ(self, cx, cy, r, fill=None, outline=None, w=1):
        self.d.ellipse(((cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K), fill=rgba(fill) if fill else None,
                       outline=rgba(outline) if outline else None, width=int(w * K) if outline else 0)

    def linha(self, x0, y0, x1, y1, cor, w=1):
        self.d.line((x0 * K, y0 * K, x1 * K, y1 * K), fill=rgba(cor), width=max(1, int(w * K)))

    def texto(self, x, y, txt, cor, peso="m", px=13, anchor="lm"):
        self.d.text((x * K, y * K), txt, font=fonte(peso, px), fill=rgba(cor), anchor=anchor)

    def ico(self, nome, cx, cy, px, cor):
        self.colas.append((icone(nome, px, cor), cx - px / 2, cy - px / 2))

    def cola(self, im, x, y):
        self.colas.append((im, x, y))

    def zona(self, x0, y0, x1, y1, zona, dica=None):
        self.zonas.append((x0, y0, x1, y1, zona, dica))

    def pronta(self):
        im = self.im.resize((int(self.w), int(self.h)), Image.LANCZOS)
        for c, x, y in self.colas:
            im.alpha_composite(c, (int(round(x)), int(round(y))))
        return im


def _botao_redondo(t, cx, cy, r, nome, px, cor, fundo=None, ativo=False, hover=False):
    if ativo:
        t.circ(cx, cy, r, fill=COR["texto"])
    elif hover:
        t.circ(cx, cy, r, fill="#3A3A3C" if fundo else COR["hover"])
    elif fundo:
        t.circ(cx, cy, r, fill=fundo)
    t.ico(nome, cx, cy, px, COR["preto"] if ativo else cor)


# ------------------------------------------------------------------ a BARRA
FERRAMENTAS = (("cursor", "Cursor: mexe no app"), ("caneta", "Caneta"), ("marca", "Marca-texto"), ("linha", "Linha"),
               ("seta", "Seta"), ("caixa", "Quadrado"), ("laser", "Laser: some sozinho"))
CORES_DESENHO = (("vermelho", "#ff3b5c"), ("amarelo", "#ffd60a"), ("verde", "#30d158"), ("azul", "#0a84ff"))


def barra(e, F=1.0):
    """e = {"modo": "grav"|"escolha", "tempo", "quem", "pausado", "mudo", "pedacos": [(n, est)], "ferr", "cor", "hover", "fila",
           "flash", "dica"} → (imagem RGBA 1×, zonas [(x0, x1, zona, dica)], x do centro do olho, tamanho do olho)"""
    H = 34 * F
    r_bt = 13 * F
    passo = 30 * F
    hv = e.get("hover")
    itens = []                             # (largura, função(t, x), zona, dica)
    add = lambda w, fn=None, z=None, dc=None: itens.append((w, fn, z, dc))     # noqa: E731
    add(16 * F, lambda t, x: [t.circ(x + 8 * F + dx * F, H / 2 + dy * F, 1.25 * F, fill="#5A5A5E") for dx in (-2.5, 2.5)
                              for dy in (-4.5, 0, 4.5)], "alca", "Arraste a barra")
    olho_x = None
    if e["modo"] == "grav":
        add(30 * F, None, "olho", "Concluir")                     # o Sharingan (o Tk põe por cima, animado)
        olho_x = 16 * F + 15 * F
        dica = e.get("dica")
        tempo, quem = e.get("tempo", "0:00"), e.get("quem", "PC")
        w_let = max(largura_texto("88:88", "sb", 14 * F) + largura_texto("Premiere · pausado", "r", 12 * F) + 16 * F,
                    largura_texto("Laser: some sozinho", "r", 12 * F) + 12 * F)

        def letreiro(t, x):
            if dica:
                t.texto(x + 6 * F, H / 2, dica, COR["texto2"], "r", 12 * F)
                return
            cor = COR["amarelo"] if e.get("pausado") else (COR["vermelho"] if e.get("mudo") else COR["texto"])
            t.texto(x + 6 * F, H / 2, ("Sem som " if e.get("mudo") else "") + tempo, cor, "sb", 14 * F)
            wt = largura_texto(("Sem som " if e.get("mudo") else "") + tempo, "sb", 14 * F)
            t.texto(x + 12 * F + wt, H / 2 + 0.5 * F, quem + (" · pausado" if e.get("pausado") else ""), COR["texto2"], "r", 12 * F)
        add(w_let, letreiro)
        if quem in ("PC", "Premiere"):
            add(passo + 2 * F, lambda t, x: _botao_redondo(t, x + passo / 2 + F, H / 2, r_bt, "play" if e.get("pausado") else "pausa",
                                                             int(15 * F), COR["texto"], fundo=COR["seg"], hover=hv == "pausa"),
                "pausa", "Continuar" if e.get("pausado") else "Pausar")
            ps = e.get("pedacos") or []
            if ps:
                add(4 * F)
                w1 = 22 * F

                def segs(t, x, ps=ps):
                    t.ret(x, H / 2 - 12 * F, x + len(ps) * w1 + 6 * F, H / 2 + 12 * F, 9 * F, fill=COR["seg"])
                    for i, (n, est) in enumerate(ps):
                        a = x + 3 * F + i * w1
                        if est == "gravando" or hv == ("ped", n):
                            t.ret(a + 1 * F, H / 2 - 9 * F, a + w1 - 1 * F, H / 2 + 9 * F, 7 * F, fill=COR["seg_sel"])
                        cor = {"gravando": COR["vermelho"], "vale": COR["texto"], "apagado": COR["texto3"]}[est]
                        t.texto(a + w1 / 2, H / 2, str(n), cor, "sb", 12 * F, "mm")
                        if est == "apagado":
                            t.linha(a + 6 * F, H / 2, a + w1 - 6 * F, H / 2, COR["texto3"], 1.2 * F)
                        t.zona(a, 0, a + w1, H, ("ped", n),
                               "Pedaço %d: %s" % (n, {"gravando": "gravando", "vale": "apagar", "apagado": "voltar"}[est]))
                add(len(ps) * w1 + 6 * F, segs)
        if e.get("desenho", True):          # sem desenho (Mac): a barra fica sem as ferramentas
            add(14 * F, lambda t, x: t.linha(x + 7 * F, H * .28, x + 7 * F, H * .72, COR["borda"], 1 * F))
            for nome, dc in FERRAMENTAS:
                add(passo, lambda t, x, nome=nome: _botao_redondo(t, x + passo / 2, H / 2, r_bt, nome, int(16 * F),
                                                                   COR["vermelho"] if nome == "laser" else COR["texto"],
                                                                   ativo=e.get("ferr") == nome, hover=hv == ("ferr", nome)),
                    ("ferr", nome), dc)
            add(4 * F)
            for i, (nome, hexa) in enumerate(CORES_DESENHO):
                def cor_fn(t, x, i=i, hexa=hexa):
                    cx = x + 10 * F
                    if e.get("cor") == i:
                        t.circ(cx, H / 2, 8.5 * F, outline=COR["texto"], w=1.5 * F)
                    elif hv == ("cor", i):
                        t.circ(cx, H / 2, 8.5 * F, outline=COR["texto3"], w=1 * F)
                    t.circ(cx, H / 2, 5.5 * F, fill=hexa)
                add(20 * F, cor_fn, ("cor", i), nome.capitalize())
            add(4 * F)
            add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "desfazer", int(16 * F), COR["texto"], hover=hv == "desfazer"),
                "desfazer", "Desfazer o último")
            add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "limpar", int(16 * F), COR["texto"], hover=hv == "limpar"),
                "limpar", "Limpar os desenhos")
        add(14 * F, lambda t, x: t.linha(x + 7 * F, H * .28, x + 7 * F, H * .72, COR["borda"], 1 * F))
        wc = largura_texto("Concluir", "sb", 13 * F) + 30 * F
        add(wc, lambda t, x: (t.ret(x + 2 * F, H / 2 - 12 * F, x + wc - 2 * F, H / 2 + 12 * F, 12 * F,
                                    fill="#E5E5EA" if hv == "concluir" else COR["texto"]),
                              t.texto(x + wc / 2, H / 2, "Concluir", COR["preto"], "sb", 13 * F, "mm")), "concluir", "Concluir (= o atalho)")
        add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "x", int(14 * F), COR["texto2"], hover=hv == "cancelar"),
            "cancelar", "Cancelar tudo")
    elif e["modo"] == "captura":           # 12/11: o modo captura (o lugar do Lightshot): ícone · «Captura · N» · Recorte · Colar tudo · X
        add(30 * F, lambda t, x: t.ico("recorte", x + 15 * F, H / 2, int(17 * F), COR["amarelo"]))
        txt = "Captura"
        n = e.get("n", 0)
        sub = "%d %s" % (n, "item" if n == 1 else "itens")
        wl = largura_texto(txt, "sb", 13 * F) + largura_texto("99 itens", "r", 12 * F) + 22 * F
        add(wl, lambda t, x: (t.texto(x + 4 * F, H / 2, txt, COR["texto"], "sb", 13 * F),
                              t.texto(x + 12 * F + largura_texto(txt, "sb", 13 * F), H / 2 + 0.5 * F, sub, COR["texto2"], "r", 12 * F)))
        wr = largura_texto("Recorte", "m", 12.5 * F) + 40 * F
        add(wr, lambda t, x: (t.ret(x + 2 * F, H / 2 - 12 * F, x + wr - 2 * F, H / 2 + 12 * F, 12 * F,
                                    fill="#3A3A3C" if hv == "recorte" else COR["seg"]),
                              t.ico("recorte", x + 17 * F, H / 2, int(14 * F), COR["texto"]),
                              t.texto(x + 28 * F, H / 2, "Recorte", COR["texto"], "m", 12.5 * F)), "recorte", "Recortar um pedaço da tela")
        add(6 * F)
        wc = largura_texto("Colar tudo", "sb", 13 * F) + 40 * F
        add(wc, lambda t, x: (t.ret(x + 2 * F, H / 2 - 12 * F, x + wc - 2 * F, H / 2 + 12 * F, 12 * F,
                                    fill="#E5E5EA" if hv == "colar" else COR["texto"]),
                              t.ico("colar", x + 17 * F, H / 2, int(14 * F), COR["preto"]),
                              t.texto(x + 28 * F, H / 2, "Colar tudo", COR["preto"], "sb", 13 * F)), "colar", "Colar tudo (= Page Down)")
        add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "x", int(14 * F), COR["texto2"], hover=hv == "sair_captura"),
            "sair_captura", "Sair sem colar")
    else:                                  # a escolha: «Como eu leio?» · Rápido | Profundo · +N · X
        add(6 * F)
        wq = largura_texto("Como eu leio?", "sb", 14 * F) + 16 * F
        add(wq, lambda t, x: t.texto(x + 4 * F, H / 2, "Como eu leio?", COR["texto"], "sb", 14 * F))
        wr, wp = largura_texto("Rápido", "sb", 13 * F) + 32 * F, largura_texto("Profundo", "sb", 13 * F) + 32 * F

        def seg_fn(t, x):
            t.ret(x, H / 2 - 13 * F, x + wr + wp + 6 * F, H / 2 + 13 * F, 10 * F, fill=COR["seg"])
            for i, (txt, w, z) in enumerate((("Rápido", wr, "rapido"), ("Profundo", wp, "profundo"))):
                a = x + 3 * F + (wr if i else 0)
                aceso = (z == "rapido" and hv != "profundo") or hv == z
                if aceso:
                    t.ret(a, H / 2 - 10 * F, a + w, H / 2 + 10 * F, 8 * F, fill=COR["seg_sel"])
                t.texto(a + w / 2, H / 2, txt, COR["texto"] if aceso else "#C7C7CC", "sb", 13 * F, "mm")
                t.zona(a, 0, a + w, H, z, "Coisa rápida" if z == "rapido" else "Análise profunda")
        add(wr + wp + 6 * F, seg_fn)
        if e.get("fila", 1) > 1:
            txt = "+%d" % (e["fila"] - 1)
            add(largura_texto(txt, "m", 12 * F) + 16 * F, lambda t, x: t.texto(x + 8 * F, H / 2, txt, COR["texto2"], "m", 12 * F))
        else:
            add(6 * F)
        add(passo + 2 * F, lambda t, x: _botao_redondo(t, x + passo / 2 + F, H / 2, r_bt, "x", int(14 * F), COR["texto2"], fundo=COR["seg"],
                                                         hover=hv == "descartar"), "descartar", "Descartar esta")
    add(8 * F)
    W = sum(w for w, _, _, _ in itens)
    t = Tela4x(W, H)
    borda = COR["texto"] if e.get("flash") else "#48484A"
    t.ret(0.5, 0.5, W - 0.5, H - 0.5, 12 * F, fill=COR["fundo"], outline=borda, w=(2 if e.get("flash") else 1))
    x = 0.0
    zonas = []
    for w, fn, z, dc in itens:
        if fn:
            fn(t, x)
        if z is not None:
            zonas.append((x, x + w, z, dc))
        x += w
    zonas = [(z[0], z[2], z[4], z[5]) for z in t.zonas] + zonas          # os pedaços (zona fina) antes do bloco
    return t.pronta(), zonas, olho_x, int(24 * F)


def barra_recorte(e, F=1.0):
    """a barrinha embaixo do recorte do modo captura: caneta, marca-texto, linha, seta, quadrado · 4 cores · desfazer · Copiar · X
    e = {"ferr", "cor", "hover"} → (imagem, zonas [(x0, x1, zona, dica)])"""
    H = 34 * F
    r_bt, passo, hv = 13 * F, 30 * F, e.get("hover")
    itens = []
    add = lambda w, fn=None, z=None, dc=None: itens.append((w, fn, z, dc))     # noqa: E731
    add(6 * F)
    for nome, dc in (("caneta", "Caneta"), ("marca", "Marca-texto"), ("linha", "Linha"), ("seta", "Seta"), ("caixa", "Quadrado")):
        add(passo, lambda t, x, nome=nome: _botao_redondo(t, x + passo / 2, H / 2, r_bt, nome, int(16 * F), COR["texto"],
                                                           ativo=e.get("ferr") == nome, hover=hv == ("ferr", nome)), ("ferr", nome), dc)
    add(4 * F)
    for i, (nome, hexa) in enumerate(CORES_DESENHO):
        def cor_fn(t, x, i=i, hexa=hexa):
            cx = x + 10 * F
            if e.get("cor") == i:
                t.circ(cx, H / 2, 8.5 * F, outline=COR["texto"], w=1.5 * F)
            t.circ(cx, H / 2, 5.5 * F, fill=hexa)
        add(20 * F, cor_fn, ("cor", i), nome.capitalize())
    add(4 * F)
    add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "desfazer", int(16 * F), COR["texto"], hover=hv == "desfazer"),
        "desfazer", "Desfazer")
    add(10 * F, lambda t, x: t.linha(x + 5 * F, H * .28, x + 5 * F, H * .72, COR["borda"], 1 * F))
    wc = largura_texto("Copiar", "sb", 13 * F) + 38 * F
    add(wc, lambda t, x: (t.ret(x + 2 * F, H / 2 - 12 * F, x + wc - 2 * F, H / 2 + 12 * F, 12 * F,
                                fill="#E5E5EA" if hv == "copiar" else COR["texto"]),
                          t.ico("check", x + 16 * F, H / 2, int(14 * F), COR["preto"]),
                          t.texto(x + 27 * F, H / 2, "Copiar", COR["preto"], "sb", 13 * F)), "copiar", "Copiar (Enter)")
    add(passo, lambda t, x: _botao_redondo(t, x + passo / 2, H / 2, r_bt, "x", int(14 * F), COR["texto2"], hover=hv == "sair"),
        "sair", "Sair (Esc)")
    add(6 * F)
    W = sum(w for w, _, _, _ in itens)
    t = Tela4x(W, H)
    t.ret(0.5, 0.5, W - 0.5, H - 0.5, 12 * F, fill=COR["fundo"], outline="#48484A", w=1)
    x, zonas = 0.0, []
    for w, fn, z, dc in itens:
        if fn:
            fn(t, x)
        if z is not None:
            zonas.append((x, x + w, z, dc))
        x += w
    return t.pronta(), zonas


# ------------------------------------------------------------------ a JANELINHA
def painel(e, F=1.0):
    """e = {"quem", "tempo", "estado_txt", "pausado", "mudo", "mic", "nivel" (0..1 ou None), "pedacos", "atalho", "cancela",
            "gravacoes": [{"quando","tipo","dur","modo","lida","extra"}], "hover", "escala_barra", "aviso"} → (imagem, zonas [(x0,y0,x1,y1,zona,dica)])
    Hierarquia (a regra dele de tela de ferramenta): o estado em cima → a ação principal SOZINHA → o que dá pra fazer com a gravação
    de agora → as gravações (cada uma com o modo e o que falta) → os ajustes no pé."""
    W = 420 * F
    hv = e.get("hover")
    grav = bool(e.get("quem"))
    lista = e.get("gravacoes") or []
    H_lista = 44 * F * max(1, len(lista))
    ext = e.get("extras") or []          # botões a mais no pé (o pacote do time: trocar o atalho, atualização)
    H = (24 + 92 + (58 if grav else 0) + 58 + 40 + H_lista + 26 + 52 + 20 + (38 * len(ext) if ext else 0)) * F
    t = Tela4x(W, H, rgba(COR["janela"]))
    y = 18 * F
    m = 18 * F
    # 1) ESTADO: cartão com o olho, o tempo grande, o estado e o microfone (com o nível ao vivo gravando)
    t.ret(m, y, W - m, y + 84 * F, 14 * F, fill=COR["cartao"], outline="#2C2C2E", w=1)
    olho_xy = (m + 14 * F, y + 14 * F, int(56 * F))
    tempo = e.get("tempo", "00:00")
    t.texto(m + 84 * F, y + 30 * F, tempo, COR["amarelo"] if e.get("pausado") else COR["texto"], "sb", 30 * F)
    t.texto(m + 84 * F, y + 58 * F, e.get("estado_txt", "Pronto · nada gravando"),
            COR["vermelho"] if e.get("mudo") else COR["texto2"], "r", 12.5 * F)
    # o microfone (nome curto) + barrinhas de nível
    mic = (e.get("mic") or "sem microfone")[:24]
    xm = W - m - 14 * F                    # tudo do microfone alinhado à direita do cartão
    t.texto(xm, y + 30 * F, mic, COR["texto2"], "r", 11 * F, "rm")
    t.ico("mic", xm - largura_texto(mic, "r", 11 * F) - 10 * F, y + 30 * F, int(14 * F), COR["texto2"])
    nivel = e.get("nivel")
    medidor = []
    if nivel is not None:                  # o nível da voz só existe gravando (parado, o microfone fica solto)
        for i in range(10):                # a janelinha acende por cima (muda 3×/s sem redesenhar tudo)
            aceso = i < int(round(nivel * 10))
            cor = (COR["verde"] if i < 7 else (COR["amarelo"] if i < 9 else COR["vermelho"])) if aceso else "#3A3A3C"
            x0 = xm - (10 - i) * 7 * F
            t.ret(x0, y + 51 * F, x0 + 5 * F, y + 59 * F, 1.5 * F, fill=cor)
            medidor.append((x0, y + 51 * F, x0 + 5 * F, y + 59 * F))
    y += 84 * F + 14 * F
    # 2) AÇÃO PRINCIPAL sozinha: Gravar (parado) | Pausar/Continuar (gravando)
    if not grav:
        t.ret(m, y, W - m, y + 44 * F, 22 * F, fill="#E5E5EA" if hv == "principal" else COR["texto"])
        t.ico("gravar", W / 2 - 44 * F, y + 22 * F, int(16 * F), COR["vermelho"])
        t.texto(W / 2 + 6 * F, y + 22 * F, "Gravar", COR["preto"], "sb", 15 * F, "mm")
        t.zona(m, y, W - m, y + 44 * F, "principal", "Começa a gravar (= o atalho)")
        y += 44 * F + 14 * F
    else:
        wb = (W - 2 * m - 10 * F) / 2
        rot = "Continuar" if e.get("pausado") else "Pausar"
        t.ret(m, y, m + wb, y + 44 * F, 22 * F, fill="#3A3A3C" if hv == "principal" else COR["seg"])
        t.ico("play" if e.get("pausado") else "pausa", m + wb / 2 - 40 * F, y + 22 * F, int(15 * F), COR["texto"])
        t.texto(m + wb / 2 + 8 * F, y + 22 * F, rot, COR["texto"], "sb", 15 * F, "mm")
        t.zona(m, y, m + wb, y + 44 * F, "principal", rot)
        x2 = m + wb + 10 * F
        t.ret(x2, y, W - m, y + 44 * F, 22 * F, fill="#E5E5EA" if hv == "concluir" else COR["texto"])
        t.ico("check", x2 + wb / 2 - 44 * F, y + 22 * F, int(16 * F), COR["preto"])
        t.texto(x2 + wb / 2 + 6 * F, y + 22 * F, "Concluir", COR["preto"], "sb", 15 * F, "mm")
        t.zona(x2, y, W - m, y + 44 * F, "concluir", "Concluir (= o atalho)")
        y += 44 * F + 10 * F
        # pedaços + cancelar
        ps = e.get("pedacos") or []
        t.texto(m + 2 * F, y + 16 * F, "Pedaços", COR["texto2"], "r", 12 * F)
        xs = m + 62 * F
        w1 = 26 * F
        t.ret(xs, y + 2 * F, xs + max(1, len(ps)) * w1 + 6 * F, y + 30 * F, 10 * F, fill=COR["seg"])
        for i, (n, est) in enumerate(ps[-9:]):
            a = xs + 3 * F + i * w1
            if est == "gravando" or hv == ("ped", n):
                t.ret(a + 1 * F, y + 5 * F, a + w1 - 1 * F, y + 27 * F, 8 * F, fill=COR["seg_sel"])
            cor = {"gravando": COR["vermelho"], "vale": COR["texto"], "apagado": COR["texto3"]}[est]
            t.texto(a + w1 / 2, y + 16 * F, str(n), cor, "sb", 12.5 * F, "mm")
            if est == "apagado":
                t.linha(a + 7 * F, y + 16 * F, a + w1 - 7 * F, y + 16 * F, COR["texto3"], 1.2 * F)
            t.zona(a, y, a + w1, y + 32 * F, ("ped", n), "Pedaço %d: clique apaga / volta" % n)
        wcan = largura_texto("Cancelar", "m", 12.5 * F) + 34 * F
        t.ret(W - m - wcan, y + 2 * F, W - m, y + 30 * F, 14 * F, fill="#3A1517" if hv == "cancelar" else COR["seg"])
        t.ico("x", W - m - wcan + 15 * F, y + 16 * F, int(12 * F), COR["vermelho"])
        t.texto(W - m - wcan + 26 * F, y + 16 * F, "Cancelar", COR["vermelho"], "m", 12.5 * F)
        t.zona(W - m - wcan, y, W - m, y + 32 * F, "cancelar", "Cancelar (vai pras descartadas)")
        y += 32 * F + 26 * F
    if grav:
        pass
    else:
        y += 0
    # 3) GRAVADAS
    t.texto(m + 2 * F, y + 10 * F, "Gravadas", COR["texto"], "sb", 14 * F)
    t.texto(W - m, y + 10 * F, "%d" % len(lista), COR["texto3"], "r", 12 * F, "rm")
    y += 28 * F
    t.ret(m, y, W - m, y + H_lista, 12 * F, fill=COR["cartao"], outline="#2C2C2E", w=1)
    for i, g in enumerate(lista):
        yy = y + i * 44 * F
        if i:
            t.linha(m + 14 * F, yy, W - m - 14 * F, yy, "#2C2C2E", 1 * F)
        cy = yy + 22 * F
        t.texto(m + 14 * F, cy - 7 * F, g["quando"], COR["texto"], "m", 12.5 * F)
        t.texto(m + 14 * F, cy + 9 * F, "%s · %s%s" % (g["tipo"], g["dur"], (" · " + g["extra"]) if g.get("extra") else ""),
                COR["texto2"], "r", 11 * F)
        # o modo: chip (ou os 2 botões quando falta)
        xr = W - m - 12 * F
        # abrir pasta / descartar (ícones)
        for nome, z, cor in (("limpar", ("descartar", i), COR["texto2"]), ("pasta", ("abrir", i), COR["texto2"])):
            _botao_redondo(t, xr - 12 * F, cy, 12 * F, nome, int(15 * F), cor, hover=hv == z)
            t.zona(xr - 24 * F, yy, xr, yy + 44 * F, z, "Descartar (Ctrl+Z volta)" if z[0] == "descartar" else "Abrir a pasta")
            xr -= 28 * F
        xr -= 4 * F
        if g.get("modo"):
            txt = "Rápido" if g["modo"] == "rapido" else "Profundo"
            wchip = largura_texto(txt, "m", 11 * F) + 18 * F
            t.ret(xr - wchip, cy - 10 * F, xr, cy + 10 * F, 10 * F, fill=COR["seg"])
            t.texto(xr - wchip / 2, cy, txt, COR["texto"], "m", 11 * F, "mm")
            xr -= wchip + 6 * F
            if g.get("lida"):
                t.ico("check", xr - 8 * F, cy, int(13 * F), COR["verde"])
                t.zona(xr - 16 * F, yy, xr, yy + 44 * F, ("lida", i), "O Claude já leu")
                xr -= 20 * F
        else:                               # sem modo: escolhe aqui e manda pro Claude (cola /kakashi rápido|profundo)
            for txt, z in (("Profundo", ("profundo", i)), ("Rápido", ("rapido", i))):
                wchip = largura_texto(txt, "m", 11 * F) + 18 * F
                t.ret(xr - wchip, cy - 11 * F, xr, cy + 11 * F, 11 * F, fill=COR["seg_sel"] if hv == z else COR["seg"],
                      outline="#48484A", w=1)
                t.texto(xr - wchip / 2, cy, txt, COR["texto"], "m", 11 * F, "mm")
                t.zona(xr - wchip, yy, xr, yy + 44 * F, z, "Ler no modo %s (cola /kakashi)" % txt.lower())
                xr -= wchip + 6 * F
    y += H_lista + 18 * F
    # 4) PÉ: ajustes (atalho, tamanho da barra, barra pro canto, pasta, fechar)
    t.ico("teclado", m + 9 * F, y + 12 * F, int(16 * F), COR["texto2"])
    t.texto(m + 24 * F, y + 12 * F, e.get("legenda") or "Ctrl+PgDn grava · +Shift cancela", COR["texto2"], "r", 11.5 * F)
    y += 30 * F
    bts = (("canto", "Barra no canto", "canto"), ("menos", "", "barra_menor"), ("mais", "", "barra_maior"),
           ("pasta", "Pasta", "pasta"), ("sair", "Fechar", "fechar"))
    x = m
    for ico, txt, z in bts:
        w = (largura_texto(txt, "m", 12 * F) + 40 * F) if txt else 32 * F
        cor = COR["vermelho"] if z == "fechar" else COR["texto"]
        if z == "fechar":
            x = W - m - w
        t.ret(x, y, x + w, y + 30 * F, 15 * F, fill="#3A3A3C" if hv == z else COR["seg"])
        t.ico(ico, x + (16 * F if txt else w / 2), y + 15 * F, int(14 * F), cor)
        if txt:
            t.texto(x + 29 * F, y + 15 * F, txt, cor, "m", 12 * F)
        dica = {"canto": "A barra volta pro canto do olho", "barra_menor": "Barra menor", "barra_maior": "Barra maior",
                "pasta": "Abrir a pasta das gravações", "fechar": "Fechar o Kakashi"}[z]
        t.zona(x, y, x + w, y + 30 * F, z, dica)
        if z == "barra_maior":
            t.texto(x + w + 6 * F, y + 15 * F, "%d%%" % int(round(e.get("escala_barra", 1.0) * 100)), COR["texto3"], "r", 11 * F)
            x += 36 * F
        x += w + 8 * F
    for z, txt, ico in ext:                # um por linha, largura inteira (o rótulo muda: «procurando...», «em dia»)
        y += 38 * F
        t.ret(m, y, W - m, y + 30 * F, 15 * F, fill="#3A3A3C" if hv == z else COR["seg"])
        t.ico(ico, m + 16 * F, y + 15 * F, int(14 * F), COR["texto"])
        t.texto(m + 29 * F, y + 15 * F, txt, COR["texto"], "m", 12 * F)
        t.zona(m, y, W - m, y + 30 * F, z, txt)
    if e.get("aviso"):
        t.texto(W / 2, H - 10 * F, e["aviso"], COR["amarelo"], "r", 11 * F, "mm")
    return t.pronta(), t.zonas, {"olho": olho_xy, "medidor": medidor}
