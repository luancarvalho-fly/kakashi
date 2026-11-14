# -*- coding: utf-8 -*-
"""O VISUAL 8 BITS do Kakashi 3.0 — a barra, a barrinha do recorte e a janelinha na estética do painel do Premiere.

14/11/2026, ele: «bota aquela [UI] 8-bits original do jeito que tava» → escolheu «Barra 3.0 em 8 bits» (a primeira barra do 3.0, de
12/11, antes do iOS/Grafite: `_antes-3.0-2026-11-12\\kakashi.3.0-8bits.pyw`). Aqui está aquele desenho — corpo #0b0b0e, botões com
relevo (claro em cima/esquerda, escuro embaixo/direita), fonte pixel 5x7 em caixa alta (pixel.py, a MESMA do painel do Premiere),
ícones 9x9 com sombra, Sharingan reduzido pixel a pixel — com TUDO que o 3.0 ganhou depois (modo captura, Rápido/Profundo na lista,
trocar o modo, nível da voz, − / + da barra, botões do pacote do time).

Mesma interface do visual.py (o Grafite), que continua aí: config "visual": "grafite" volta pra ele (tema.py escolhe).
Bônus pro Mac: o 8 bits não usa fonte do sistema (o Grafite procurava Inter/Segoe do Windows e no Mac caía na fonte de emergência)."""
import os

from PIL import Image, ImageDraw, ImageEnhance

import pixel

OLHO_PX = 34                      # o Sharingan da barra (em px a 1×; a barra tem 40)
ICONES = None                     # a pasta dos ícones do painel (titulo.png); o kakashi.pyw diz qual
COR = {"fundo": "#0b0b0e", "janela": "#0b0b0e", "linha": "#121217", "texto": "#FFFFFF", "texto2": "#8E8E96", "vermelho": "#FF1E2E",
       "amarelo": "#FFE600", "verde": "#39D353", "preto": "#000000", "risco": "#2a2a33"}
# (fundo, claro, escuro, cor da letra) — os do painel do Premiere / da janelinha 8 bits de 19/10
EST = {
    "vermelho": ("#d6001c", "#ff6a6a", "#5e000c", "branco"),
    "concluir": ("#15151a", "#34343e", "#050507", "vermelho"),
    "neutro":   ("#2a2a33", "#4a4a56", "#0a0a0d", "amarelo"),
    "mini":     ("#15151a", "#34343e", "#050507", "branco"),
    "perigo":   ("#2a0006", "#6a0a16", "#0a0002", "vermelho"),
    "off":      ("#1a1a20", "#24242b", "#0a0a0d", "apagado"),
    "corpo":    ("#0b0b0e", "#34343e", "#050507", "branco"),
}
_MAIS_CLARO = {"#2a2a33": "#3a3a46", "#15151a": "#24242c", "#d6001c": "#ff1e2e", "#2a0006": "#4a0010"}
FERRAMENTAS = (("cursor", "CURSOR: MEXE NO APP"), ("caneta", "CANETA"), ("marca", "MARCA-TEXTO"), ("linha", "LINHA"),
               ("seta", "SETA"), ("caixa", "QUADRADO"), ("laser", "LASER: SOME SOZINHO"))
CORES_DESENHO = (("vermelho", "#ff3b5c"), ("amarelo", "#ffd60a"), ("verde", "#30d158"), ("azul", "#0a84ff"))
LIMITE_TXT = 19                   # o letreiro tem largura fixa (a barra não pula quando a dica troca)

# os ícones 9x9 (X = aceso) — os 11 da barra 8 bits de 12/11 + os que o 3.0 pediu depois, na mesma grade
ICONES_8 = {
    "cursor": ["X........", "XX.......", "XXX......", "XXXX.....", "XXXXX....", "XXXXXX...", "XXXXXXX..", "XX.XX....", "X...XX..."],
    "caneta": ["......XX.", ".....XXXX", "....XXXX.", "...XXXX..", "..XXXX...", ".XXXX....", ".XXX.....", "X.X......", "XX......."],
    "marca":  [".....XXX.", "....XXXXX", "...XXXXX.", "..XXXXX..", ".XXXXX...", ".XXXX....", "..XX.....", ".X.......", "XXXXX...."],
    "linha":  ["........X", ".......X.", "......X..", ".....X...", "....X....", "...X.....", "..X......", ".X.......", "X........"],
    "seta":   ["...XXXXXX", "......XXX", ".....XX.X", "....XX..X", "...XX....", "..XX.....", ".XX......", "XX.......", "X........"],
    "caixa":  ["XXXXXXXXX", "X.......X", "X.......X", "X.......X", "X.......X", "X.......X", "X.......X", "X.......X", "XXXXXXXXX"],
    "laser":  [".........", "...XXX...", "..XXXXX..", ".XXXXXXX.", ".XXXXXXX.", ".XXXXXXX.", "..XXXXX..", "...XXX...", "........."],
    "desfazer": ["...X.....", "..XX.....", ".XXXXXXX.", "XXXXXXXXX", ".XX.....X", "..X.....X", "........X", ".......X.", "..XXXXX.."],
    "limpar": ["X.......X", "XX.....XX", ".XX...XX.", "..XX.XX..", "...XXX...", "..XX.XX..", ".XX...XX.", "XX.....XX", "X.......X"],
    "pausa":  [".........", ".XX...XX.", ".XX...XX.", ".XX...XX.", ".XX...XX.", ".XX...XX.", ".XX...XX.", ".XX...XX.", "........."],
    "play":   [".X.......", ".XX......", ".XXX.....", ".XXXX....", ".XXXXX...", ".XXXX....", ".XXX.....", ".XX......", ".X......."],
    "raio":   [".....XXX.", "....XXX..", "...XXX...", "..XXXXXX.", ".....XX..", "....XX...", "...XX....", "..XX.....", ".X......."],
    "lupa":   [".XXXX....", "X....X...", "X....X...", "X....X...", "X....X...", ".XXXXX...", ".....XX..", "......XX.", ".......XX"],
    "check":  [".........", "........X", ".......XX", "......XX.", "X....XX..", "XX..XX...", ".XXXX....", "..XX.....", "........."],
    "recorte": ["..X......", "..X......", "XXXXXXX..", "..X...X..", "..X...X..", "..X...X..", "..XXXXXXX", "......X..", "......X.."],
    "colar":  ["..XXXXX..", "XXX...XXX", "X.XXXXX.X", "X.......X", "X.XXXXX.X", "X.......X", "X.XXX...X", "X.......X", "XXXXXXXXX"],
    "pasta":  [".........", "XXXX.....", "X...X....", "X....XXXX", "X.......X", "X.......X", "X.......X", "X.......X", "XXXXXXXXX"],
    "mic":    ["...XXX...", "..XXXXX..", "..XXXXX..", "..XXXXX..", "X.XXXXX.X", "X..XXX..X", ".X.....X.", "..XXXXX..", "....X...."],
    "teclado": [".........", "XXXXXXXXX", "X.X.X.X.X", "X.......X", "XX.X.X.XX", "X.......X", "X.XXXXX.X", "XXXXXXXXX", "........."],
    "mais":   [".........", "....X....", "....X....", "....X....", ".XXXXXXX.", "....X....", "....X....", "....X....", "........."],
    "menos":  [".........", ".........", ".........", ".........", ".XXXXXXX.", ".........", ".........", ".........", "........."],
    "canto":  ["XXXXXXXXX", "X.......X", "X.......X", "X.......X", "X.......X", "X...XXX.X", "X...XXX.X", "X.......X", "XXXXXXXXX"],
    "sair":   ["....X....", ".X..X..X.", "X...X...X", "X...X...X", "X.......X", "X.......X", "X.......X", ".X.....X.", "..XXXXX.."],
    "gravar": [".........", "...XXX...", "..XXXXX..", ".XXXXXXX.", ".XXXXXXX.", ".XXXXXXX.", "..XXXXX..", "...XXX...", "........."],
    "x":      [".........", ".X.....X.", "..X...X..", "...X.X...", "....X....", "...X.X...", "..X...X..", ".X.....X.", "........."],
}


def rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def escala(F):
    """o tamanho do bloco da fonte e dos ícones (2 = a letra miúda do painel do Premiere)"""
    return max(2, int(round(2 * F)))


def largura_texto(txt, E):
    return pixel.render(txt, E, "branco").width


_cache_ico = {}


def icone(nome, cor, E):
    """o ícone 9x9 com a sombra escura de 1 bloco (igual a fonte pixel)"""
    k = (nome, cor, E)
    if k in _cache_ico:
        return _cache_ico[k]
    g = ICONES_8[nome]
    rgb = rgba(cor)
    im = Image.new("RGBA", ((len(g[0]) + 1) * E, (len(g) + 1) * E), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for camada, c in ((0, (10, 10, 13, 255)), (1, rgb)):
        for y, lin in enumerate(g):
            for x, v in enumerate(lin):
                if v == "X":
                    ox, oy = (x + 1, y + 1) if camada == 0 else (x, y)
                    d.rectangle((ox * E, oy * E, ox * E + E - 1, oy * E + E - 1), fill=c)
    _cache_ico[k] = im
    return im


# ------------------------------------------------------------------ o Sharingan, pixel a pixel (como o subsample do Tk de antes)
_cache_olho = {}


def olho(pasta_icones, nome, px, cinza=False):
    k = (nome, px, cinza)
    if k not in _cache_olho:
        im = Image.open(os.path.join(pasta_icones, nome)).convert("RGBA").resize((px, px), Image.NEAREST)
        if cinza:          # P20: gravando MUDO
            a = im.getchannel("A")
            im = ImageEnhance.Brightness(im.convert("L")).enhance(0.85).convert("RGBA")
            im.putalpha(a)
        _cache_olho[k] = im
    return _cache_olho[k]


# ------------------------------------------------------------------ a tela (1×, sem suavizar)
class Tela8:
    def __init__(self, w, h, fundo=(0, 0, 0, 0)):
        self.w, self.h = int(round(w)), int(round(h))
        self.im = Image.new("RGBA", (self.w, self.h), fundo)
        self.d = ImageDraw.Draw(self.im)
        self.zonas = []

    def ret(self, x0, y0, x1, y1, fill):
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        if x1 > x0 and y1 > y0:
            self.d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=rgba(fill))

    def borda(self, x0, y0, x1, y1, cor, b):
        for r in ((x0, y0, x1, y0 + b), (x0, y1 - b, x1, y1), (x0, y0, x0 + b, y1), (x1 - b, y0, x1, y1)):
            self.ret(*r, cor)

    def botao(self, x0, y0, x1, y1, est, hover=False, b=None):
        """o botão com relevo do painel"""
        f, cl, es, cor = EST[est]
        if hover:
            f = _MAIS_CLARO.get(f, f)
        b = b or (4 if (y1 - y0) >= 40 else 3)
        self.ret(x0, y0, x1, y1, f)
        self.ret(x0, y0, x1, y0 + b, cl); self.ret(x0, y0, x0 + b, y1, cl)
        self.ret(x0, y1 - b, x1, y1, es); self.ret(x1 - b, y0, x1, y1, es)
        return cor

    def cola(self, im, x, y):
        self.im.alpha_composite(im, (int(round(x)), int(round(y))))

    def texto(self, x, y, txt, cor, E, anchor="lm"):
        """anchor: l/m/r na horizontal, sempre centrado na vertical em y"""
        im = pixel.render(txt, E, cor)
        if anchor[0] == "m":
            x -= im.width / 2
        elif anchor[0] == "r":
            x -= im.width
        self.cola(im, x, y - im.height / 2 + E / 2)
        return im.width

    def ico(self, nome, cx, cy, cor, E):
        im = icone(nome, cor, E)
        self.cola(im, cx - im.width / 2 + E / 2, cy - im.height / 2 + E / 2)
        return im.width

    def zona(self, x0, y0, x1, y1, zona, dica=None):
        self.zonas.append((x0, y0, x1, y1, zona, dica))


_HEX_PIXEL = {"branco": "#FFFFFF", "amarelo": "#FFD60A", "vermelho": "#E8101E", "cinza": "#78788A", "apagado": "#4E4E58"}


def _cor_hex(nome):
    return _HEX_PIXEL.get(nome, nome)


# ------------------------------------------------------------------ a BARRA
def barra(e, F=1.0):
    """mesmo contrato do visual.barra: e = {"modo": "grav"|"escolha"|"captura", "tempo", "quem", "pausado", "mudo", "pedacos",
    "ferr", "cor", "hover", "fila", "flash", "dica", "desenho", "n"} → (imagem RGBA, zonas [(x0, x1, zona, dica)], x do olho, px do olho)"""
    E = escala(F)
    BH = int(40 * F)
    CEL = int(30 * F)
    M = max(4, int(5 * F))                 # respiro em cima/embaixo dos botões
    hv = e.get("hover")
    itens = []                             # (largura, função(t, x0, x1), zona, dica)
    add = lambda w, fn=None, z=None, dc=None: itens.append((int(w), fn, z, dc))     # noqa: E731

    def risco(t, a, b):
        cx = (a + b) // 2
        t.ret(cx - 1, M, cx + 1, BH - M, COR["risco"])

    def bt_ico(nome, cor, est="neutro", ativo=False, zona=None):
        def fn(t, a, b):
            t.botao(a + 2, M, b - 2, BH - M, est, hover=(zona is not None and hv == zona))
            if ativo:
                t.borda(a + 2, M, b - 2, BH - M, COR["amarelo"], max(2, int(2 * F)))
            t.ico(nome, (a + b) / 2, BH / 2, cor, E)
        return fn

    def w_rotulo(txt, com_icone=False):
        return largura_texto(txt, E) + int(24 * F) + ((9 + 2) * E if com_icone else 0)

    def bt_txt(txt, est, zona, ico=None, cor_ico=None):
        def fn(t, a, b):
            cor = t.botao(a + 2, M, b - 2, BH - M, est, hover=hv == zona)
            wt = largura_texto(txt, E)
            if ico:
                wi = (9 + 1) * E
                x0 = (a + b - wi - int(6 * F) - wt) / 2
                t.ico(ico, x0 + wi / 2, BH / 2, cor_ico, E)
                t.texto(x0 + wi + int(6 * F), BH / 2, txt, cor, E)
            else:
                t.texto((a + b) / 2, BH / 2, txt, cor, E, "mm")
        return fn

    w_let = (LIMITE_TXT * 6 + 2) * E

    def letreiro(txt, cor):
        def fn(t, a, b):
            t.ret(a + 2, M, b - 2, BH - M, COR["linha"])
            if txt:
                t.texto(a + int(8 * F), BH / 2, txt[:LIMITE_TXT].upper(), cor, E)
        return fn

    olho_x = None
    add(16 * F, lambda t, a, b: [t.ret((a + b) // 2 + dx - p, BH // 2 + i * p * 3 - p, (a + b) // 2 + dx + p, BH // 2 + i * p * 3 + p, "#4a4a56")
                                 for p in (max(2, int(2 * F)),) for i in range(-2, 3) for dx in (-p * 2, p * 2)], "alca", "ARRASTE A BARRA")
    if e["modo"] == "grav":
        olho_x = sum(w for w, _, _, _ in itens) + BH / 2
        add(BH, None, "olho", "CONCLUIR")
        dica = e.get("dica")
        tempo, quem = e.get("tempo", "0:00"), e.get("quem", "PC")
        if dica:
            txt, cor = dica, "amarelo"
        elif e.get("mudo"):
            txt, cor = "SEM SOM " + tempo, "vermelho"
        elif e.get("pausado"):
            txt, cor = "%s PAUSA %s" % ("PR" if quem == "Premiere" else quem, tempo), "amarelo"
        else:
            txt, cor = "%s %s" % (quem, tempo), "branco"
        add(w_let, letreiro(txt, cor))
        if quem in ("PC", "Premiere"):
            add(CEL, bt_ico("play", "#ffffff", "vermelho", zona="pausa") if e.get("pausado") else bt_ico("pausa", "#FFD60A", "neutro", zona="pausa"),
                "pausa", "CONTINUAR" if e.get("pausado") else "PAUSAR")
            ps = e.get("pedacos") or []
            if ps:
                add(4 * F)
                for n, est in ps:
                    def ped(t, a, b, n=n, est=est):
                        f = {"gravando": "#ff1e2e", "vale": "#d6001c", "apagado": "#1a1a20"}[est]
                        if hv == ("ped", n) and est != "gravando":
                            f = "#3a3a46" if est == "vale" else "#5a1a24"
                        t.ret(a + 2, M + 2, b - 2, BH - M - 2, f)
                        if est == "apagado":
                            t.borda(a + 2, M + 2, b - 2, BH - M - 2, "#3a3a44", 1)
                            t.d.line((a + 5, M + 5, b - 6, BH - M - 6), fill=rgba("#5b5b63"), width=max(1, int(2 * F)))
                        t.texto((a + b) / 2, BH / 2, str(n), "apagado" if est == "apagado" else "branco", max(2, E - 1), "mm")
                    add(24 * F, ped, ("ped", n), "PEDACO %d: %s" % (n, {"gravando": "GRAVANDO", "vale": "APAGAR", "apagado": "VOLTAR"}[est]))
        if e.get("desenho", True):          # sem desenho (Mac): a barra fica sem as ferramentas
            add(14 * F, risco)
            for nome, dc in FERRAMENTAS:
                ativo = e.get("ferr") == nome
                cor = "#ff1e2e" if nome == "laser" else (CORES_DESENHO[e.get("cor") or 0][1] if nome != "cursor" else "#ffffff")
                add(CEL, bt_ico(nome, cor, "mini" if ativo else "neutro", ativo=ativo, zona=("ferr", nome)), ("ferr", nome), dc)
            add(6 * F)
            for i, (nome, hexa) in enumerate(CORES_DESENHO):
                def cor_fn(t, a, b, i=i, hexa=hexa):
                    m = int(4 * F) + M // 2
                    t.ret(a + m // 2 - 2, M + m // 2 - 2, b - m // 2 + 2, BH - M - m // 2 + 2, "#0a0a0d")
                    t.ret(a + m // 2, M + m // 2, b - m // 2, BH - M - m // 2, hexa)
                    if e.get("cor") == i:
                        t.borda(a + 1, M, b - 1, BH - M, "#ffffff", max(2, int(2 * F)))
                    elif hv == ("cor", i):
                        t.borda(a + 1, M, b - 1, BH - M, "#5b5b63", max(1, int(F)))
                add(22 * F, cor_fn, ("cor", i), nome.upper())
            add(6 * F)
            add(CEL, bt_ico("desfazer", "#ffffff", zona="desfazer"), "desfazer", "DESFAZER O ULTIMO")
            add(CEL, bt_ico("limpar", "#ffffff", zona="limpar"), "limpar", "LIMPAR OS DESENHOS")
        add(14 * F, risco)
        add(w_rotulo("CONCLUIR"), bt_txt("CONCLUIR", "concluir", "concluir"), "concluir", "CONCLUIR = O ATALHO")
        add(4 * F)
        add(CEL, bt_ico("x", "#ff5c5c", "perigo", zona="cancelar"), "cancelar", "CANCELAR TUDO")
    elif e["modo"] == "captura":           # 12/11: o modo captura (o lugar do Lightshot)
        n = e.get("n", 0)
        add(CEL, lambda t, a, b: t.ico("recorte", (a + b) / 2, BH / 2, "#FFD60A", E))
        add(w_let, letreiro("CAPTURA · %d %s" % (n, "ITEM" if n == 1 else "ITENS"), "branco"))
        add(w_rotulo("RECORTE", True), bt_txt("RECORTE", "neutro", "recorte", "recorte", "#ffffff"), "recorte", "RECORTAR UM PEDACO DA TELA")
        add(6 * F)
        add(w_rotulo("COLAR TUDO", True), bt_txt("COLAR TUDO", "vermelho", "colar", "colar", "#ffffff"), "colar", "COLAR TUDO")
        add(4 * F)
        add(CEL, bt_ico("x", "#ff5c5c", "perigo", zona="sair_captura"), "sair_captura", "SAIR SEM COLAR")
    else:                                  # a escolha: olho parado · «COMO EU LEIO?» · RÁPIDO | PROFUNDO · +N · X
        olho_x = sum(w for w, _, _, _ in itens) + BH / 2
        add(BH)
        add(w_let, letreiro(e.get("dica") or "COMO EU LEIO?", "amarelo" if e.get("dica") else "branco"))
        add(w_rotulo("RAPIDO", True), bt_txt("RAPIDO", "neutro", "rapido", "raio", "#ffd60a"), "rapido", "COISA RAPIDA")
        add(6 * F)
        add(w_rotulo("PROFUNDO", True), bt_txt("PROFUNDO", "vermelho", "profundo", "lupa", "#ffffff"), "profundo", "ANALISE PROFUNDA")
        fila = e.get("fila", 1)
        if fila > 1:
            add(w_rotulo("+%d" % (fila - 1)), lambda t, a, b, f=fila: t.texto((a + b) / 2, BH / 2, "+%d" % (f - 1), "cinza", E, "mm"))
        add(6 * F)
        add(CEL, bt_ico("x", "#ff5c5c", "perigo", zona="descartar"), "descartar", "DESCARTAR ESTA")
    add(6 * F)
    W = sum(w for w, _, _, _ in itens)
    t = Tela8(W, BH)
    t.botao(0, 0, W, BH, "corpo")          # o corpo da barra, com o relevo do painel
    if e.get("flash"):
        t.borda(0, 0, W, BH, "#ffffff", max(2, int(2 * F)))
    x, zonas = 0, []
    for w, fn, z, dc in itens:
        if fn:
            fn(t, x, x + w)
        if z is not None:
            zonas.append((x, x + w, z, dc))
        x += w
    return t.im, zonas, (int(olho_x) if olho_x is not None else None), int(OLHO_PX * F)


def barra_recorte(e, F=1.0):
    """a barrinha embaixo do recorte do modo captura (mesmo contrato do visual.barra_recorte) → (imagem, zonas)"""
    E = escala(F)
    BH, CEL, M = int(40 * F), int(30 * F), max(4, int(5 * F))
    hv = e.get("hover")
    itens = []
    add = lambda w, fn=None, z=None, dc=None: itens.append((int(w), fn, z, dc))     # noqa: E731
    add(6 * F)
    for nome, dc in (("caneta", "Caneta"), ("marca", "Marca-texto"), ("linha", "Linha"), ("seta", "Seta"), ("caixa", "Quadrado")):
        def fn(t, a, b, nome=nome):
            ativo = e.get("ferr") == nome
            t.botao(a + 2, M, b - 2, BH - M, "mini" if ativo else "neutro", hover=hv == ("ferr", nome))
            if ativo:
                t.borda(a + 2, M, b - 2, BH - M, COR["amarelo"], max(2, int(2 * F)))
            t.ico(nome, (a + b) / 2, BH / 2, CORES_DESENHO[e.get("cor") or 0][1], E)
        add(CEL, fn, ("ferr", nome), dc)
    add(6 * F)
    for i, (nome, hexa) in enumerate(CORES_DESENHO):
        def cor_fn(t, a, b, i=i, hexa=hexa):
            m = int(4 * F) + M // 2
            t.ret(a + m // 2 - 2, M + m // 2 - 2, b - m // 2 + 2, BH - M - m // 2 + 2, "#0a0a0d")
            t.ret(a + m // 2, M + m // 2, b - m // 2, BH - M - m // 2, hexa)
            if e.get("cor") == i:
                t.borda(a + 1, M, b - 1, BH - M, "#ffffff", max(2, int(2 * F)))
        add(22 * F, cor_fn, ("cor", i), nome.capitalize())
    add(6 * F)

    def desf(t, a, b):
        t.botao(a + 2, M, b - 2, BH - M, "neutro", hover=hv == "desfazer")
        t.ico("desfazer", (a + b) / 2, BH / 2, "#ffffff", E)
    add(CEL, desf, "desfazer", "Desfazer")
    add(14 * F, lambda t, a, b: t.ret((a + b) // 2 - 1, M, (a + b) // 2 + 1, BH - M, COR["risco"]))
    wc = largura_texto("COPIAR", E) + (9 + 2) * E + int(30 * F)

    def copiar(t, a, b):
        cor = t.botao(a + 2, M, b - 2, BH - M, "vermelho", hover=hv == "copiar")
        t.ico("check", a + int(14 * F) + 4 * E, BH / 2, "#ffffff", E)
        t.texto(a + int(20 * F) + 10 * E, BH / 2, "COPIAR", cor, E)
    add(wc, copiar, "copiar", "Copiar (Enter)")
    add(4 * F)

    def sair(t, a, b):
        t.botao(a + 2, M, b - 2, BH - M, "perigo", hover=hv == "sair")
        t.ico("x", (a + b) / 2, BH / 2, "#ff5c5c", E)
    add(CEL, sair, "sair", "Sair (Esc)")
    add(6 * F)
    W = sum(w for w, _, _, _ in itens)
    t = Tela8(W, BH)
    t.botao(0, 0, W, BH, "corpo")
    x, zonas = 0, []
    for w, fn, z, dc in itens:
        if fn:
            fn(t, x, x + w)
        if z is not None:
            zonas.append((x, x + w, z, dc))
        x += w
    return t.im, zonas


# ------------------------------------------------------------------ a JANELINHA (a de 19/10, com as peças do 3.0)
def painel(e, F=1.0):
    """mesmo contrato do visual.painel → (imagem, zonas [(x0, y0, x1, y1, zona, dica)], {"olho": (x, y, px), "medidor": [ret]})
    A ordem é a da janelinha 8 bits de 19/10 (olho + título, relógio grande, status, PAUSAR/INICIAR grande, CONCLUIR | CANCELAR,
    GRAVADAS, o pé) + o que o 3.0 trouxe (pedaços clicáveis, nível da voz, modo de cada gravação, − / + da barra)."""
    E = escala(F)
    W = 640 * F
    m = 12 * F
    hv = e.get("hover")
    grav = bool(e.get("quem"))
    lista = e.get("gravacoes") or []
    ext = e.get("extras") or []
    LIN = 48 * F
    H_lista = LIN * max(1, len(lista)) + 2 * F * max(0, len(lista) - 1)
    H = 2000 * F + H_lista                 # desenha numa folha alta e corta no fim (a altura certa sai do próprio desenho)
    t = Tela8(W, H, rgba(COR["janela"]))
    y = 12 * F
    # 1) TOPO: o Sharingan + o título (titulo.png do painel do Premiere) + a legenda do atalho em vermelho
    opx = int(64 * F)
    olho_xy = (m, y, opx)
    xt = m + opx + 12 * F
    if ICONES and os.path.isfile(os.path.join(ICONES, "titulo.png")):
        tit = Image.open(os.path.join(ICONES, "titulo.png")).convert("RGBA")
        k = max(1, int(round(F)))
        tit = tit.resize((tit.width * k, tit.height * k), Image.NEAREST)
        t.cola(tit, xt, y + 6 * F)
    else:
        t.texto(xt, y + 6 * F + 12 * F, "KAKASHI", "vermelho", E * 2)
    t.ico("teclado", xt + 6 * E, y + 52 * F, "#8E8E96", E)
    t.texto(xt + 14 * E, y + 52 * F, (e.get("legenda") or "CTRL+PGDN GRAVA · +SHIFT CANCELA").upper(), "vermelho", E)
    # o microfone e o nível da voz, à direita do topo
    mic = (e.get("mic") or "SEM MICROFONE").upper()
    xm = W - m - 4 * F
    while len(mic) > 4 and largura_texto(mic, E) > W * 0.36:
        mic = mic[:-1]
    t.texto(xm, y + 14 * F, mic, "cinza", E, "rm")
    t.ico("mic", xm - largura_texto(mic, E) - 8 * E, y + 14 * F, "#8E8E96", E)
    medidor = []
    if e.get("nivel") is not None:
        for i in range(10):
            x0 = xm - (10 - i) * 9 * F
            t.ret(x0, y + 28 * F, x0 + 7 * F, y + 38 * F, "#3A3A3C")
            medidor.append((int(x0), int(y + 28 * F), int(x0 + 7 * F), int(y + 38 * F)))
    y += 64 * F + 12 * F
    # 2) o RELÓGIO grande + o status com o pontinho
    t.texto(W / 2, y + 23 * F, e.get("tempo", "00:00"), "amarelo" if e.get("pausado") else "branco", 5 * E // 2, "mm")
    y += 46 * F
    pausa, mudo = e.get("pausado"), e.get("mudo")
    txt = (e.get("estado_txt") or "Pronto · nada gravando").upper()
    cor_txt = ("amarelo" if pausa else "vermelho" if mudo else "branco") if grav else "cinza"
    ponto = ("#FFE600" if pausa else "#5b5b63" if mudo else "#ff1e2e") if grav else "#39d353"
    wtx = largura_texto(txt, E)
    x0 = W / 2 - (wtx + 16 * F) / 2
    t.ret(x0, y + 13 * F - 4 * F, x0 + 8 * F, y + 13 * F + 4 * F, ponto)
    t.texto(x0 + 16 * F, y + 13 * F, txt, cor_txt, E)
    y += 26 * F + 12 * F
    # 3) a AÇÃO PRINCIPAL sozinha e grande: INICIAR (parado) | PAUSAR / CONTINUAR (gravando no PC ou Premiere) | CONCLUIR (o app de cartões)
    if not grav:
        est, rot = "vermelho", "INICIAR"
    elif e.get("quem") in ("pc", "premiere"):
        est, rot = ("vermelho", "CONTINUAR") if pausa else ("neutro", "PAUSAR")
    else:
        est, rot = "concluir", "CONCLUIR"
    cor = t.botao(m, y, W - m, y + 44 * F, est, hover=hv == "principal")
    t.texto(W / 2, y + 22 * F, rot, cor, E + 1, "mm")
    t.zona(m, y, W - m, y + 44 * F, "principal", "Começa a gravar (= o atalho)" if not grav else rot.capitalize())
    y += 44 * F + 6 * F
    # 4) CONCLUIR | CANCELAR (apagados parado)
    wcan = 128 * F
    est_c = "concluir" if (grav and e.get("quem") in ("pc", "premiere")) else "off"
    cor = t.botao(m, y, W - m - wcan - 6 * F, y + 30 * F, est_c, hover=hv == "concluir" and est_c != "off")
    t.texto((m + W - m - wcan - 6 * F) / 2, y + 15 * F, "CONCLUIR", cor, E, "mm")
    if est_c != "off":
        t.zona(m, y, W - m - wcan - 6 * F, y + 30 * F, "concluir", "Concluir (= o atalho)")
    est_x = "perigo" if grav else "off"
    cor = t.botao(W - m - wcan, y, W - m, y + 30 * F, est_x, hover=hv == "cancelar" and grav)
    t.texto(W - m - wcan / 2, y + 15 * F, "CANCELAR", cor, E, "mm")
    if grav:
        t.zona(W - m - wcan, y, W - m, y + 30 * F, "cancelar", "Cancelar (vai pras descartadas)")
    y += 30 * F
    # 5) os PEDAÇOS (gravando): o trilho do painel do Premiere, clique apaga / volta
    if grav:
        y += 10 * F
        t.texto(m, y + 15 * F, "PEDACOS", "cinza", E)
        xs = m + largura_texto("PEDACOS", E) + 10 * F
        t.ret(xs, y, W - m, y + 30 * F, COR["linha"])
        w1 = 30 * F
        for i, (n, est) in enumerate((e.get("pedacos") or [])[-14:]):
            a = xs + 3 * F + i * (w1 + 3 * F)
            f = {"gravando": "#ff1e2e", "vale": "#d6001c", "apagado": "#1a1a20"}[est]
            if hv == ("ped", n) and est != "gravando":
                f = "#3a3a46" if est == "vale" else "#5a1a24"
            t.ret(a, y + 4 * F, a + w1, y + 26 * F, f)
            if est == "apagado":
                t.borda(a, y + 4 * F, a + w1, y + 26 * F, "#3a3a44", 1)
            t.texto(a + w1 / 2, y + 15 * F, str(n), "apagado" if est == "apagado" else "branco", E, "mm")
            if est != "gravando":
                t.zona(a, y, a + w1, y + 30 * F, ("ped", n), "Pedaço %d: clique apaga / volta" % n)
        y += 30 * F
    y += 16 * F
    # 6) GRAVADAS
    t.texto(m, y + 12 * F, "GRAVADAS", "amarelo", E + 1)
    t.texto(W - m, y + 12 * F, "%d" % len(lista), "cinza", E, "rm")
    y += 24 * F + 8 * F
    if not lista:
        t.texto(m + 8 * F, y + LIN / 2, "NENHUMA AINDA", "cinza", E)
    for i, g in enumerate(lista):
        yy = y + i * (LIN + 2 * F)
        t.ret(m, yy, W - m, yy + LIN, COR["linha"])
        cy = yy + LIN / 2
        # da direita pra esquerda: DESCARTAR · ABRIR · o modo (ou RAPIDO/PROFUNDO pra escolher) · ✓ lida
        xr = W - m - 4 * F
        for rot, z, est, dica in (("DESCARTAR", ("descartar", i), "perigo", "Descartar (Ctrl+Z volta)"),
                                  ("ABRIR", ("abrir", i), "mini", "Abrir a pasta")):
            wb = largura_texto(rot, E) + 16 * F
            cor = t.botao(xr - wb, cy - 13 * F, xr, cy + 13 * F, est, hover=hv == z)
            t.texto(xr - wb / 2, cy, rot, cor, E, "mm")
            t.zona(xr - wb, yy, xr, yy + LIN, z, dica)
            xr -= wb + 4 * F
        xr -= 6 * F
        if g.get("modo"):
            # o seletor de dois lados (13/11): o escolhido aceso, o outro clicável (troca o MODO.json, não cola nada)
            for txt_, z_ in (("PROFUNDO", "profundo"), ("RAPIDO", "rapido")):
                wb = largura_texto(txt_, E) + 14 * F
                if g["modo"] == z_:
                    cor = t.botao(xr - wb, cy - 13 * F, xr, cy + 13 * F, "vermelho" if z_ == "profundo" else "neutro")
                else:
                    zz = ("trocamodo", i, z_)
                    cor = t.botao(xr - wb, cy - 13 * F, xr, cy + 13 * F, "off", hover=False)
                    if hv == zz:
                        t.borda(xr - wb, cy - 13 * F, xr, cy + 13 * F, "#8E8E96", max(1, int(F)))
                        cor = "branco"
                    t.zona(xr - wb, yy, xr, yy + LIN, zz, "Trocar pra %s (se apertou o outro sem querer)" % txt_.lower())
                t.texto(xr - wb / 2, cy, txt_, cor, E, "mm")
                xr -= wb
            xr -= 6 * F
            if g.get("lida"):
                t.ico("check", xr - 5 * E, cy, "#39D353", E)
                t.zona(xr - 10 * E, yy, xr, yy + LIN, ("lida", i), "O Claude já leu")
                xr -= 12 * E
        else:                              # sem modo: escolhe aqui e manda pro Claude (cola /kakashi rápido|profundo)
            for txt_, z_, est in (("PROFUNDO", ("profundo", i), "mini"), ("RAPIDO", ("rapido", i), "mini")):   # sem modo: os dois neutros, pra escolher
                wb = largura_texto(txt_, E) + 14 * F
                cor = t.botao(xr - wb, cy - 13 * F, xr, cy + 13 * F, est, hover=hv == z_)
                t.texto(xr - wb / 2, cy, txt_, cor, E, "mm")
                t.zona(xr - wb, yy, xr, yy + LIN, z_, "Ler no modo %s (cola /kakashi)" % txt_.lower())
                xr -= wb + 4 * F
        # à esquerda, em duas linhas: quando · e o tipo, a duração e o resto (cortado no que couber)
        livre = xr - (m + 8 * F) - 6 * F
        l1 = g["quando"]
        while l1 and largura_texto(l1, E) > livre:
            l1 = l1[:-1]
        l2 = "%s · %s%s" % (g["tipo"], g["dur"], (" · " + g["extra"]) if g.get("extra") else "")
        l2 = l2.upper()
        while l2 and largura_texto(l2, E) > livre:
            l2 = l2[:-1]
        t.texto(m + 8 * F, cy - 9 * F, l1, "branco", E)
        t.texto(m + 8 * F, cy + 9 * F, l2, "cinza", E)
    y += H_lista + 14 * F
    # 7) o PÉ: BARRA NO CANTO · − · + · NN% · PASTA ......... FECHAR
    bts = (("BARRA NO CANTO", "canto", "mini", "A barra volta pro canto do olho"), ("-", "barra_menor", "mini", "Barra menor"),
           ("+", "barra_maior", "mini", "Barra maior"), ("PASTA", "pasta", "mini", "Abrir a pasta das gravações"),
           ("FECHAR", "fechar", "perigo", "Fechar o Kakashi"))
    x = m
    for rot, z, est, dica in bts:
        wb = max(30 * F, largura_texto(rot, E) + 20 * F)
        if z == "fechar":
            x = W - m - wb
        cor = t.botao(x, y, x + wb, y + 30 * F, est, hover=hv == z)
        t.texto(x + wb / 2, y + 15 * F, rot, cor, E, "mm")
        t.zona(x, y, x + wb, y + 30 * F, z, dica)
        if z == "barra_maior":
            pc = "%d%%" % int(round(e.get("escala_barra", 1.0) * 100))
            t.texto(x + wb + 6 * F, y + 15 * F, pc, "cinza", E)
            x += largura_texto(pc, E) + 10 * F
        x += wb + 6 * F
    y += 30 * F
    for z, rot, _ico in ext:               # os botões do pacote do time, um por linha
        y += 8 * F
        cor = t.botao(m, y, W - m, y + 30 * F, "mini", hover=hv == z)
        t.texto(W / 2, y + 15 * F, rot.upper(), cor, E, "mm")
        t.zona(m, y, W - m, y + 30 * F, z, rot)
        y += 30 * F
    if e.get("aviso"):
        t.texto(W / 2, y + 16 * F, e["aviso"].upper(), "amarelo", E, "mm")
        y += 24 * F
    y += 14 * F
    return t.im.crop((0, 0, t.w, int(round(y)))), t.zonas, {"olho": olho_xy, "medidor": medidor}
