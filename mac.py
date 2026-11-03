# -*- coding: utf-8 -*-
"""O que o Kakashi do PC precisa do sistema, no jeito do Mac (porte de 02/11/2026). O kakashi.pyw, o olho.py e o atalho.py
continuam com o código do Windows; no Mac eles trocam as peças do sistema pelas daqui (o resto da lógica é a mesma).

- janela_frente / janela_em ....... o app da frente (NSWorkspace) e o título da janela (CGWindowList: precisa de Gravação de Tela)
- mouse / botao ................... onde está o cursor e se o botão está apertado (Quartz, consulta periódica: sem gancho)
- area_contagem / ler_area ........ o que foi copiado (NSPasteboard); conteúdo marcado por gerenciador de senha NUNCA é lido
- copiar / colar .................. "/kakashi" na área de transferência e Cmd+V (precisa de Acessibilidade)
- Atalho .......................... o atalho global (CGEventTap: Acessibilidade ou Monitoramento de Entrada); some com a tecla
- print_nativo / salvar_print ..... print da tela principal em resolução nativa (Retina = 2x os pontos do cursor)
- foco_e_senha .................... campo de senha em foco (AXSecureTextField), pra não ler o que foi copiado dele
- UIA.em .......................... o elemento debaixo do mouse (Acessibilidade), no mesmo formato do UI Automation do Windows
- olho_em_toda_mesa ............... a bolinha do Sharingan em toda mesa (Space), sem ícone no Dock
Só lê. Nada aqui grava som nem mexe em ajuste do sistema.
"""
import os, re, subprocess, threading, time

import AppKit
import Quartz


class SemWindows:
    """no lugar do ctypes.windll no Mac: as linhas de preparo do Windows que rodam no carregar (argtypes, formatos) viram nada"""
    def __getattr__(self, nome):
        return SemWindows()

    def __call__(self, *a, **k):
        return 0


# ------------------------------------------------------------------ janela da frente
def _janelas():
    op = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    return Quartz.CGWindowListCopyWindowInfo(op, Quartz.kCGNullWindowID) or []


def _do_pid(pid):
    """a janela mais da frente (camada 0) desse app: {app, titulo}"""
    for w in _janelas():
        if w.get("kCGWindowOwnerPID") == pid and w.get("kCGWindowLayer", 0) == 0:
            return {"app": str(w.get("kCGWindowOwnerName") or ""), "titulo": str(w.get("kCGWindowName") or "")}
    return None


def _ax(el, atr):
    """um atributo de acessibilidade (None se não tem / sem permissão)"""
    try:
        import ApplicationServices as AS
        err, v = AS.AXUIElementCopyAttributeValue(el, atr, None)
        return None if err else v
    except Exception:
        return None


def titulo_ax(pid):
    """o título da janela em foco do app, pela Acessibilidade (não precisa da Gravação de Tela como o CGWindowList)"""
    try:
        import ApplicationServices as AS
        w = _ax(AS.AXUIElementCreateApplication(pid), AS.kAXFocusedWindowAttribute)
        v = _ax(w, AS.kAXTitleAttribute) if w is not None else None
        return str(v) if v else ""
    except Exception:
        return ""


# o endereço da aba da frente, perguntado ao próprio navegador (Automação: o Mac pergunta uma vez "Python quer controlar o Safari").
# Só quando a janela/aba muda (cache pelo app + título): o vigia chama janela_frente 20x/s.
NAVEGADORES = {"Safari": 'tell application "Safari" to get URL of front document',
               "Google Chrome": 'tell application "Google Chrome" to get URL of active tab of front window',
               "Arc": 'tell application "Arc" to get URL of active tab of front window',
               "Brave Browser": 'tell application "Brave Browser" to get URL of active tab of front window'}
_URL = {"chave": None, "url": ""}


def url_da_frente(app, titulo):
    if app not in NAVEGADORES:
        return ""
    if _URL["chave"] == (app, titulo):
        return _URL["url"]
    url = ""
    try:
        r = subprocess.run(["osascript", "-e", NAVEGADORES[app]], capture_output=True, text=True, timeout=2)
        if r.returncode == 0 and re.match(r"https?://", r.stdout.strip()):
            url = r.stdout.strip()
    except Exception:
        pass
    _URL.update(chave=(app, titulo), url=url)
    return url


def janela_frente(_=None):
    """{app, titulo}. A própria bolinha do Kakashi (este Python) na frente → a janela do app de baixo dela"""
    app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
    pid = app.processIdentifier() if app else 0
    if pid == os.getpid():
        for w in _janelas():
            if w.get("kCGWindowLayer", 0) == 0 and w.get("kCGWindowOwnerPID") != pid:
                return {"app": str(w.get("kCGWindowOwnerName") or ""), "titulo": str(w.get("kCGWindowName") or "")}
    j = _do_pid(pid) if pid else None
    nome = str(app.localizedName() or "") if app else ""
    titulo = (j or {}).get("titulo", "") or (titulo_ax(pid) if pid else "")
    d = {"app": nome or (j or {}).get("app", ""), "titulo": titulo}
    url = url_da_frente(d["app"], titulo)
    if url:
        d["url"] = url
    return d


def janela_em(x, y):
    """a janela debaixo do ponto (o clique): {app, titulo}"""
    for w in _janelas():
        if w.get("kCGWindowLayer", 0) != 0 or w.get("kCGWindowOwnerPID") == os.getpid():
            continue
        b = w.get("kCGWindowBounds") or {}
        if b.get("X", 0) <= x < b.get("X", 0) + b.get("Width", 0) and b.get("Y", 0) <= y < b.get("Y", 0) + b.get("Height", 0):
            return {"app": str(w.get("kCGWindowOwnerName") or ""), "titulo": str(w.get("kCGWindowName") or "")}
    return janela_frente()


# ------------------------------------------------------------------ mouse
def mouse():
    p = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return (int(p.x), int(p.y))


def botao(n):
    """n = 0 (esquerdo) / 1 (direito)"""
    return bool(Quartz.CGEventSourceButtonState(Quartz.kCGEventSourceStateCombinedSessionState, n))


# ------------------------------------------------------------------ área de transferência
# tipos que gerenciador de senha (1Password, Bitwarden, KeePassXC, Senhas do macOS...) põe pra ninguém ler/guardar (nspasteboard.org)
PROTEGIDOS = {"org.nspasteboard.ConcealedType", "org.nspasteboard.TransientType", "org.nspasteboard.AutoGeneratedType",
              "com.agilebits.onepassword"}
GERENCIADORES = {"1password", "1password 7", "bitwarden", "keepassxc", "lastpass", "dashlane", "nordpass", "enpass",
                 "proton pass", "keeper password manager", "senhas", "passwords", "acesso às chaves", "keychain access"}


def area_contagem():
    return AppKit.NSPasteboard.generalPasteboard().changeCount()


def ler_area():
    """o mesmo formato do olho.ler_area do Windows: {imagem, arquivos, texto?, html_fonte?} ou {protegido: True}"""
    pb = AppKit.NSPasteboard.generalPasteboard()
    tipos = set(str(t) for t in (pb.types() or []))
    if tipos & PROTEGIDOS:
        return {"protegido": True}
    r = {"imagem": bool(tipos & {"public.png", "public.tiff"}), "arquivos": "public.file-url" in tipos}
    s = pb.stringForType_(AppKit.NSPasteboardTypeString)
    if s:
        r["texto"] = str(s)
    fonte = pb.stringForType_("org.chromium.source-url")
    if fonte:
        r["html_fonte"] = str(fonte)
    if r["arquivos"]:
        r["lista"] = [str(u.path()) for u in (pb.readObjectsForClasses_options_([AppKit.NSURL], None) or []) if u.isFileURL()]
    return r


def imagem_da_area():
    """a imagem copiada como PIL.Image (o ImageGrab.grabclipboard do Pillow também lê no Mac)"""
    from PIL import ImageGrab
    im = ImageGrab.grabclipboard()
    return None if im is None or isinstance(im, list) else im


def copiar(texto):
    pb = AppKit.NSPasteboard.generalPasteboard()
    pb.clearContents()
    return bool(pb.setString_forType_(texto, AppKit.NSPasteboardTypeString))


def _tecla(codigo, baixo, flags=0):
    e = Quartz.CGEventCreateKeyboardEvent(None, codigo, baixo)
    if flags:
        Quartz.CGEventSetFlags(e, flags)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)


def colar():
    """Cmd+V na janela da frente (Acessibilidade)"""
    _tecla(9, True, Quartz.kCGEventFlagMaskCommand); _tecla(9, False, Quartz.kCGEventFlagMaskCommand)


def tecla_apertada(codigo):
    return bool(Quartz.CGEventSourceKeyState(Quartz.kCGEventSourceStateCombinedSessionState, codigo))


def foco_e_senha():
    """o campo em foco é de senha? (AXSecureTextField; sem Acessibilidade = não sabe = False)"""
    try:
        import ApplicationServices as AS
        sis = AS.AXUIElementCreateSystemWide()
        err, el = AS.AXUIElementCopyAttributeValue(sis, AS.kAXFocusedUIElementAttribute, None)
        if err or el is None:
            return False
        for atr in (AS.kAXSubroleAttribute, AS.kAXRoleAttribute):
            err, v = AS.AXUIElementCopyAttributeValue(el, atr, None)
            if not err and v and "SecureTextField" in str(v):
                return True
    except Exception:
        pass
    return False


def _ret(el):
    """[esquerda, topo, direita, baixo] em pontos"""
    try:
        import ApplicationServices as AS
        pos, tam = _ax(el, AS.kAXPositionAttribute), _ax(el, AS.kAXSizeAttribute)
        ok1, p = AS.AXValueGetValue(pos, AS.kAXValueCGPointType, None)
        ok2, s = AS.AXValueGetValue(tam, AS.kAXValueCGSizeType, None)
        if ok1 and ok2:
            return [int(p.x), int(p.y), int(p.x + s.width), int(p.y + s.height)]
    except Exception:
        pass
    return None


def _nome(el):
    import ApplicationServices as AS
    for atr in (AS.kAXTitleAttribute, AS.kAXDescriptionAttribute, AS.kAXValueAttribute, AS.kAXHelpAttribute):
        v = _ax(el, atr)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


class UIA:
    """o elemento debaixo do mouse pela Acessibilidade do Mac, no MESMO formato do UI Automation do Windows:
    {nome, controle, app, ret, [dentro_de], [senha], [automation_id]}. Campo de senha: o nome (o que está escrito) nunca sai."""
    def em(self, x, y):
        try:
            import ApplicationServices as AS
            err, el = AS.AXUIElementCopyElementAtPosition(AS.AXUIElementCreateSystemWide(), float(x), float(y), None)
            if err or el is None:
                return None
            papel = str(_ax(el, AS.kAXRoleAttribute) or "")
            sub = str(_ax(el, AS.kAXSubroleAttribute) or "")
            senha = "SecureTextField" in papel + sub
            err, pid = AS.AXUIElementGetPid(el, None)
            app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid) if not err else None
            d = {"nome": "" if senha else _nome(el)[:200], "controle": str(_ax(el, AS.kAXRoleDescriptionAttribute) or papel),
                 "app": str(app.localizedName()) if app else "", "ret": _ret(el)}
            if senha:
                d["senha"] = True
            ident = _ax(el, "AXIdentifier")
            if ident and not senha:
                d["automation_id"] = str(ident)[:80]
            atual = el
            for _ in range(4):          # quem contém (o card, a linha, o botão): sobe até achar um nome
                atual = _ax(atual, AS.kAXParentAttribute)
                if atual is None:
                    break
                n = _nome(atual)
                if n and n != d["nome"]:
                    d["dentro_de"] = {"nome": n[:120], "controle": str(_ax(atual, AS.kAXRoleDescriptionAttribute) or "")}
                    break
            return d
        except Exception:
            return None

    def foco_e_senha(self):
        return foco_e_senha()


def pasta_capturas():
    """onde o Cmd+Shift+3/4/5 salva (padrão: a Mesa)"""
    try:
        r = subprocess.run(["defaults", "read", "com.apple.screencapture", "location"], capture_output=True, text=True, timeout=5)
        p = os.path.expanduser(r.stdout.strip())
        if r.returncode == 0 and os.path.isdir(p):
            return p
    except Exception:
        pass
    return os.path.expanduser("~/Desktop")


# ------------------------------------------------------------------ o Sharingan em toda mesa
def olho_em_toda_mesa():
    """o Kakashi não vira app da frente (sem ícone no Dock) e a bolinha sem borda aparece na mesa (Space) em que a pessoa está, por
    cima de tudo, sem o Mac pular pra outra mesa. Chamar na thread do Tk, depois de a janela existir e a cada vez que ela aparece."""
    app = AppKit.NSApplication.sharedApplication()
    if app.activationPolicy() != AppKit.NSApplicationActivationPolicyAccessory:
        app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
    todas = (AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces | AppKit.NSWindowCollectionBehaviorStationary |
             AppKit.NSWindowCollectionBehaviorFullScreenAuxiliary | AppKit.NSWindowCollectionBehaviorIgnoresCycle)
    for w in app.windows():
        if w.styleMask() == AppKit.NSWindowStyleMaskBorderless:          # a bolinha (overrideredirect)
            w.setCollectionBehavior_(todas)
            w.setLevel_(AppKit.NSStatusWindowLevel)
            w.setHidesOnDeactivate_(False)
        else:                                                              # a janelinha: abre na mesa de agora
            w.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorMoveToActiveSpace)


# ------------------------------------------------------------------ print
def monitor_de(x, y):
    """a tela principal, em pontos (o print da 1ª versão é só dela)"""
    f = AppKit.NSScreen.mainScreen().frame()
    return (0, 0, int(f.size.width), int(f.size.height))


def print_nativo(x, y):
    """(imagem da tela principal em pixels nativos, retângulo em pontos)"""
    from PIL import ImageGrab
    return ImageGrab.grab(), monitor_de(x, y)


def escala(im, mon):
    return im.width / float(max(1, mon[2] - mon[0]))


# ------------------------------------------------------------------ atalho
# a tecla de cada vk do Windows (os nomes e as regras do atalho.py valem iguais) → o código da tecla no Mac
_F = [122, 120, 99, 118, 96, 97, 98, 100, 101, 109, 103, 111, 105, 107, 113, 106, 64, 79, 80, 90]
VK_MAC = {0x70 + i: c for i, c in enumerate(_F)}                                    # f1–f20
VK_MAC.update({0x22: 121, 0x21: 116, 0x23: 119, 0x24: 115, 0x2E: 117, 0x20: 49, 0x25: 123, 0x26: 126, 0x27: 124, 0x28: 125})
_LETRAS = {"a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9, "b": 11, "q": 12, "w": 13, "e": 14,
           "r": 15, "y": 16, "t": 17, "o": 31, "u": 32, "i": 34, "p": 35, "l": 37, "j": 38, "k": 40, "n": 45, "m": 46}
VK_MAC.update({ord(l.upper()): c for l, c in _LETRAS.items()})
VK_MAC.update({0x30 + n: c for n, c in enumerate([29, 18, 19, 20, 21, 23, 22, 26, 28, 25])})   # 0–9
MAC_VK = {c: v for v, c in VK_MAC.items()}
# MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN do atalho.py → flags do Mac (win = Command)
MODS_MAC = ((0x1, Quartz.kCGEventFlagMaskAlternate), (0x2, Quartz.kCGEventFlagMaskControl),
            (0x4, Quartz.kCGEventFlagMaskShift), (0x8, Quartz.kCGEventFlagMaskCommand))
TECLAS_MOD = [56, 60, 59, 62, 58, 61, 55, 54]        # shift, control, option, command (esquerda e direita)


def mods_de(flags):
    m = 0
    for mod, f in MODS_MAC:
        if flags & f:
            m |= mod
    return m


def pedir_permissao():
    """sem Acessibilidade / Monitoramento de Entrada, o macOS mostra o pedido (e põe o app na lista dos Ajustes); quem libera é a pessoa"""
    try:
        import ApplicationServices as AS
        if not AS.AXIsProcessTrustedWithOptions({AS.kAXTrustedCheckOptionPrompt: True}):
            Quartz.CGRequestListenEventAccess()
    except Exception:
        pass


class Atalho:
    """o atalho global por um CGEventTap. Ativo (com Acessibilidade): a tecla do atalho NÃO chega no app da frente (o F1 do
    Premiere é a Ajuda). Sem permissão pra ativo, tenta só ouvir (Monitoramento de Entrada). Nenhum dos dois = erro na fila."""

    def __init__(self, ao_apertar, ao_erro):
        self.ao_apertar, self.ao_erro = ao_apertar, ao_erro
        self.teclas = {}            # (codigo, mods) → "alternar" / "cancelar"
        self.solto = False          # a janelinha está capturando um atalho novo
        self.captura = None         # (codigo, mods) da última tecla (pro TROCAR O ATALHO)
        self.tap = None

    def registrar(self, gravar, cancelar):
        self.teclas = {}
        for a, acao in ((gravar, "alternar"), (cancelar, "cancelar")):
            if a and a["vk"] in VK_MAC:
                self.teclas[(VK_MAC[a["vk"]], a["mods"])] = acao
        return bool(gravar and (VK_MAC.get(gravar["vk"]), gravar["mods"]) in self.teclas)

    def _cb(self, proxy, tipo, ev, ref):
        if tipo in (Quartz.kCGEventTapDisabledByTimeout, Quartz.kCGEventTapDisabledByUserInput):
            Quartz.CGEventTapEnable(self.tap, True)
            return ev
        codigo = Quartz.CGEventGetIntegerValueField(ev, Quartz.kCGKeyboardEventKeycode)
        mods = mods_de(Quartz.CGEventGetFlags(ev))
        if self.solto:
            if tipo == Quartz.kCGEventKeyDown and codigo not in TECLAS_MOD:
                self.captura = (codigo, mods)
            return ev
        acao = self.teclas.get((codigo, mods))
        if acao is None:
            return ev
        if tipo == Quartz.kCGEventKeyDown and not Quartz.CGEventGetIntegerValueField(ev, Quartz.kCGKeyboardEventAutorepeat):
            self.ao_apertar(acao)
        return None if self.ativo else ev

    def rodar(self):
        """na thread do atalho: fica rodando pra sempre"""
        pedir_permissao()
        mascara = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
        for opcao, ativo in ((Quartz.kCGEventTapOptionDefault, True), (Quartz.kCGEventTapOptionListenOnly, False)):
            self.tap = Quartz.CGEventTapCreate(Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap, opcao, mascara, self._cb, None)
            if self.tap:
                self.ativo = ativo
                break
        if not self.tap:
            self.ao_erro("o Mac não deixou o Kakashi ouvir o teclado: libere em Ajustes do Sistema → Privacidade e Segurança → "
                         "Acessibilidade (e Monitoramento de Entrada) e abra o Kakashi de novo")
            return
        fonte = Quartz.CFMachPortCreateRunLoopSource(None, self.tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), fonte, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(self.tap, True)
        Quartz.CFRunLoopRun()

    def capturar(self, limite=15.0):
        """espera a próxima tecla (com os modificadores). Volta (vk do Windows, mods) / "esc" / None"""
        self.captura = None; self.solto = True
        try:
            fim = time.time() + limite
            while time.time() < fim:
                if self.captura:
                    codigo, mods = self.captura
                    if codigo == 53:
                        return "esc"
                    fim_solta = time.time() + 3
                    while time.time() < fim_solta and (tecla_apertada(codigo) or any(tecla_apertada(m) for m in TECLAS_MOD)):
                        time.sleep(0.02)
                    return (MAC_VK.get(codigo), mods)
                time.sleep(0.015)
            return None
        finally:
            self.solto = False


ATALHO = None       # o Atalho rodando (o kakashi.pyw cria)
