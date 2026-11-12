# -*- coding: utf-8 -*-
"""KAKASHI ÚNICO — fase 1 (19/10/2026). Desenho: apps\\CORRETOR\\DESENHO-KAKASHI-UNICO.md (aprovado por ele: "Pode").

Pedido dele: "um atalho pra eu poder começar a gravar, sem ter que clicar em nada, tipo o Whisper... aperto o atalho de novo pra parar"
+ "fica aqui o Whisper do lado, você coloca o Sharinganzinho do Kakashi rodando, pra eu saber que tá rodando".

- Ctrl+Page Down   = começa / conclui.      Ctrl+Shift+Page Down = cancela (vai pra _descartadas, nunca apaga).
  (era Ctrl+Alt+K; ele trocou em 19/10: "coloca Ctrl + Page Down")
- Sharingan no canto (do lado da bolinha do Whisper): parado e apagado = pronto; vermelho girando + relógio = gravando.
  Clique = começa/conclui. Arrastar = muda de lugar (fica lembrado). Botão direito = cancelar / sair.
- O TIPO sai da janela da frente na hora do atalho:
    Premiere (com o painel do KAKASHI aberto) → manda o painel gravar (CORRETOR 7815, o rastro da timeline é dele)
    AppPessoal                                    → o gravador do AppPessoal (7798, rastro dos cartões e do quiz)
    qualquer outra coisa                      → grava aqui: microfone + som do PC + tela + janela da frente + cliques
- Gravação esquecida (o caso dos 47 min de 19/10): 10 min sem voz → o Sharingan pisca amarelo.
- OLHO DE DEUS (P3, 21/10, aprovado por ele; peças em olho.py), no tipo "pc", sem tecla nenhuma a mais:
    caminho do mouse (~0,25 s, só quando mexe) · elemento debaixo do mouse (UI Automation) na pausa >0,8 s e em todo clique ·
    card do AppPessoal sob o mouse (o AppPessoal manda pra porta 7816) · print NATIVO + recorte 800x500 na pausa, na fala e a cada página nova ·
    o que ele copia (texto, link, imagem, Win+Shift+S; senha nunca) · links do Chrome no fim (+ imagem dos pins) ·
    REPLAY: DESLIGADO desde 02/11 (ele: "a partir do momento que eu ligo o Kakashi, que eu desligo, esse é o timestamp exato da
    gravação... não é pra você pegar coisa anterior ou coisa depois"). Ligado, os últimos 2 min (tela + voz + som do PC) ficavam
    num disco rotativo e entravam no começo da gravação (config "replay": true religa; só com ele pedindo)
- GRAVAÇÃO MUDA (P20, 21/10): voz do buffer em silêncio digital 60 s → reabre só o microfone · no atalho, buffer mudo →
  o microfone dele fecha antes da captura nova + "replay_sem_voz" · gravando mudo 20 s → Sharingan cinza + "SEM SOM" ·
  saída de som trocada no meio → um pc.wav só · ffmpeg órfão de buffer antigo é encerrado (LEIA-ME, seção P20)
- TROCA SOZINHA PRO PREMIERE (23/10; ele: "Sim, óbvio", depois de "Eu não tô no PC, ó. Aí como é que eu faço? É difícil, né?"):
    gravando como PC e o Premiere fica na frente 1,5 s com o painel do KAKASHI vivo → o painel começa a gravar e, SÓ depois de
    ele estar gravando, a parte PC fecha (sessao.json: continua_em = "premiere", troca_epoch). As duas são UMA correção:
    Ctrl+Page Down conclui a do Premiere; Ctrl+Shift+Page Down cancela as duas. Config "troca_premiere": false desliga.
- OLHO NO PREMIERE (23/10 noite; ele: "faz o Kakashi ser o mais completo possível... É o olho de Deus, mano, é minha tela"):
    enquanto o painel do Premiere grava (7815 gravando/pausado), o olho do PC (mouse, elemento sob o mouse, print nativo, cópias,
    links do Chrome) grava junto em <sessão do CORRETOR>\\_olho, no RELÓGIO do painel (t_gravacao, pausas tiradas). Pausado = não
    grava nada. No fim liga fala.wav/tela.mp4/pc.wav do painel (hardlink) e escreve sessao.json (tipo pc, olho_premiere) → o
    resumo_pc.py lê a _olho como uma sessão PC. Abre/fecha o arquivo a cada evento: o painel pode mover a pasta (descartada).
    Gravação PC ativa tem prioridade (alvo = PC). Config "olho_premiere": false desliga.
- MICROFONE MORTO NO FONE (P40, 30/10; ele: "se não tiver nenhum ruidinho, bota o barulho do Sharingan no meu ouvido"):
    gravando PC ou AppPessoal, quando o "SEM SOM" acende (20 s em silêncio digital) → sons\\sharingan.wav 2x na saída padrão.
    Uma vez por queda (de novo só se a voz voltar e morrer de novo). No Premiere quem toca é o CORRETOR. Config "alerta_som": false desliga.
- Porta 7816: GET /status (estado: gravando/parado — o Claude confere antes de reiniciar) · POST /app_pessoal (card sob o mouse)
    · POST /chrome (04/11: a extensão chrome\\ manda o ELEMENTO DA PÁGINA sob o mouse, pelo código: tag, seletor, texto, link,
    imagem, componente e arquivo:linha em app local; vira o evento "chrome" no eventos.jsonl)
- KAKASHI 3.0 (12/11/2026, chat; ele: «em vez de ter aquela caixinha com pausar e tudo mais, seria maneiro ter uma... barrinha no
  meio... você apaga os fragmentos que você não quer» · «o atalho tem que ser um só... esse nível... eu que tenho que colocar ali...
  coisa rápida, ou coisa mais profunda» · «pode começar tudo logo, já faz tudo»):
    BARRA no meio da tela (arrasta e fica lembrada; NÃO aparece na gravação nem nos prints: SetWindowDisplayAffinity) no lugar do
    olho do canto: Sharingan + tempo + pausar + os PEDAÇOS (clique = apagar/voltar, PC e Premiere) + DESENHO (cursor, caneta,
    seta, caixa, laser; 4 cores; desfazer; limpar) + concluir/cancelar.
    O atalho continua UM só. Ao concluir, a barra pergunta RÁPIDO ou PROFUNDO: o clique grava MODO.json na pasta da sessão e cola
    "/kakashi rápido" ou "/kakashi profundo". A skill lê o modo (rápido = PROMPT + conferidor; profundo = tudo, com sabotador).
    Desenho (classe Desenho, só Windows): cada traço = evento "traco" com o elemento debaixo da ponta (UIA) + print logo depois;
    no Chrome, a extensão manda o elemento pelo código (status.pedido_chrome → motivo "traco"). Ideia do bug reporter do Rolf (12/11).
Só CPU. Som só o do aviso de microfone morto (P40).
"""
import array, collections, ctypes, ctypes.wintypes as wt, datetime, glob, json, os, queue, re, shutil, subprocess, sys, threading, time
import tkinter as tk
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import olho  # noqa: E402
import atalho  # noqa: E402   # pacote da Fly (27/10): o atalho que a pessoa escolher
import atualizar  # noqa: E402   # pacote da Fly (27/10): versão nova no GitHub da Fly
SESSOES = os.path.join(AQUI, "sessoes")
PORTA = 7816
CFG = os.path.join(AQUI, "config.json")
CORRETOR = AQUI   # pacote da Fly: gravar_pc.py, config.json e painel\icones vêm junto, na mesma pasta
PY = (os.path.join(os.path.dirname(sys.executable), "python.exe")
      if os.path.isfile(os.path.join(os.path.dirname(sys.executable), "python.exe")) else sys.executable)
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
MAC = sys.platform == "darwin"      # porte pro Mac (02/11/2026): as peças do sistema vêm do mac.py; a lógica é a mesma
SEM_JANELA = 0x08000000 if not MAC else 0
LOG = os.path.join(AQUI, "kakashi.log")

if not MAC:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
else:
    import mac  # noqa: E402
    user32 = kernel32 = mac.SemWindows()


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(datetime.datetime.now().strftime("%d/%m %H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def cfg():
    try:
        return json.load(open(CFG, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def salvar_cfg(c):
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


def http(url, corpo=None, t=3):
    try:
        req = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo is not None else None,
                                     headers={"Content-Type": "application/json"}, method="POST" if corpo is not None else "GET")
        return json.load(urllib.request.urlopen(req, timeout=t))
    except Exception:
        return None


# ---------- janela da frente ----------
def janela_frente(hwnd=None):
    hwnd = hwnd or user32.GetForegroundWindow()
    n = user32.GetWindowTextLengthW(hwnd)
    b = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, b, n + 1)
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    exe = ""
    h = kernel32.OpenProcess(0x1000, False, pid.value)   # PROCESS_QUERY_LIMITED_INFORMATION
    if h:
        buf = ctypes.create_unicode_buffer(520); tam = wt.DWORD(520)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(tam)):
            exe = os.path.basename(buf.value)
        kernel32.CloseHandle(h)
    return {"app": exe, "titulo": b.value}


def _pid_da_janela(hwnd):
    pid = wt.DWORD()
    if hwnd:
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def tipo_da_frente():
    j = janela_frente()
    if j["app"].lower() == "pythonw.exe" and j["titulo"] in ("tk", ""):     # a própria bolinha: pega a janela de baixo dela
        hw = user32.GetWindow(user32.GetForegroundWindow(), 2)   # GW_HWNDNEXT
        while hw and not (user32.IsWindowVisible(hw) and user32.GetWindowTextLengthW(hw)):
            hw = user32.GetWindow(hw, 2)
        if hw:
            j = janela_frente(hw)
    if "premiere" in j["app"].lower():
        st = http("http://127.0.0.1:7815/status")
        if st and st.get("painel_visto_ha_s") is not None and st["painel_visto_ha_s"] < 10:
            return "premiere", j
    if re.search(r"\bAppPessoal\b", j["titulo"]) and http("http://127.0.0.1:7798/api/app_pessoal/gravacao") is not None:
        return "app_pessoal", j
    return "pc", j


# ---------- "/kakashi" no Ctrl+V e colado onde está o cursor (21/10, pedido dele) ----------
# "quando terminar a gravação, ele já deixar copiado automaticamente ... e ele já colar automático também ... aonde tiver o
# cursor ... Exatamente como o Whisper faz ... mesmo se colou em algum outro lugar, eu posso apertar um Ctrl V que vai tá lá"
# DLLs próprias: os argtypes daqui não mexem nas funções do user32 que o resto do arquivo (e o olho.py) usa.
_u32 = ctypes.WinDLL("user32", use_last_error=True) if not MAC else mac.SemWindows()
_k32 = ctypes.WinDLL("kernel32", use_last_error=True) if not MAC else mac.SemWindows()
_k32.GlobalAlloc.restype = ctypes.c_void_p; _k32.GlobalAlloc.argtypes = (wt.UINT, ctypes.c_size_t)
_k32.GlobalLock.restype = ctypes.c_void_p; _k32.GlobalLock.argtypes = (ctypes.c_void_p,)
_k32.GlobalUnlock.argtypes = (ctypes.c_void_p,)
_u32.OpenClipboard.argtypes = (wt.HWND,)
_u32.SetClipboardData.restype = ctypes.c_void_p; _u32.SetClipboardData.argtypes = (wt.UINT, ctypes.c_void_p)
TEXTO_COLAR = "/kakashi"


def _copiar(texto):
    dados = (texto + "\0").encode("utf-16-le")
    for _ in range(20):                       # outro programa pode estar com a área de transferência aberta
        if _u32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return False
    try:
        _u32.EmptyClipboard()
        h = _k32.GlobalAlloc(0x0002, len(dados))            # GMEM_MOVEABLE
        ptr = _k32.GlobalLock(h)
        ctypes.memmove(ptr, dados, len(dados))
        _k32.GlobalUnlock(h)
        return bool(_u32.SetClipboardData(13, h))           # CF_UNICODETEXT
    finally:
        _u32.CloseClipboard()


def colar_kakashi(colar=True, texto=None):
    """Copia "/kakashi" e (se colar) aperta Ctrl+V na janela da frente. Espera ele soltar o Ctrl/Shift/Page Down do atalho,
    senão o Ctrl+V sai como Ctrl+Shift+V. No Premiere só copia: lá Ctrl+V cola clipe na timeline.
    3.0 (12/11): texto = "/kakashi rápido" ou "/kakashi profundo" (o que ele escolheu na barra)."""
    texto = texto or TEXTO_COLAR
    try:
        fim = time.time() + 3
        while time.time() < fim and any(_u32.GetAsyncKeyState(vk) & 0x8000 for vk in atalho.teclas_soltar()):
            time.sleep(0.03)
        if not _copiar(texto):
            log("colar: área de transferência ocupada"); return
        if colar and "premiere" not in janela_frente()["app"].lower():
            time.sleep(0.08)
            _u32.keybd_event(0x11, 0, 0, 0); _u32.keybd_event(0x56, 0, 0, 0)          # Ctrl down, V down
            _u32.keybd_event(0x56, 0, 2, 0); _u32.keybd_event(0x11, 0, 2, 0)          # V up, Ctrl up
        log("colar: %s %s" % (texto, "copiado e colado" if colar else "copiado"))
    except Exception as e:
        log("colar: %s" % e)

if MAC:
    janela_frente = mac.janela_frente
    _copiar = mac.copiar

    def colar_kakashi(colar=True, texto=None):
        """Mac: copia "/kakashi" e (se colar) aperta Cmd+V na janela da frente, depois que ele soltar as teclas do atalho.
        No Premiere só copia (lá Cmd+V cola clipe na timeline). 3.0: texto = "/kakashi rápido" ou "/kakashi profundo"."""
        texto = texto or TEXTO_COLAR
        try:
            teclas = [c for c in [mac.VK_MAC.get(v) for v in atalho.teclas_soltar()] if c is not None] + mac.TECLAS_MOD
            fim = time.time() + 3
            while time.time() < fim and any(mac.tecla_apertada(c) for c in teclas):
                time.sleep(0.03)
            if not _copiar(texto):
                log("colar: área de transferência ocupada"); return
            if colar and "premiere" not in janela_frente()["app"].lower():
                time.sleep(0.08)
                mac.colar()
            log("colar: %s %s" % (texto, "copiado e colado" if colar else "copiado"))
        except Exception as e:
            log("colar: %s" % e)


# ---------- microfone (mesma escolha do CORRETOR / AppPessoal) ----------
def microfone():
    for arq, chave in ((os.path.join(CORRETOR, "config.json"), "dispositivo_audio"),):
        try:
            v = json.load(open(arq, encoding="utf-8")).get(chave)
            if v:
                return v
        except (OSError, ValueError):
            pass
    try:
        r = subprocess.run([FFMPEG, "-hide_banner", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                           capture_output=True, timeout=15, creationflags=SEM_JANELA)
        for m in re.finditer(r'"([^"]+)"\s+\((audio|video|none)\)', (r.stderr or b"").decode("utf-8", "replace")):
            if m.group(2) == "audio":
                return m.group(1)
    except Exception:
        pass
    return ""


# de onde vêm a voz, a tela e o som do PC (o teste do P20 troca por fonte nula do ffmpeg / --falso, sem tocar som nenhum)
def entrada_mic(dev):
    return ["-f", "dshow", "-audio_buffer_size", "50", "-i", "audio=" + dev]


ENTRADA_TELA = ["-f", "gdigrab", "-framerate", "5", "-draw_mouse", "1", "-i", "desktop"]
GRAVAR_PC_EXTRA = []
if MAC:
    def microfone():
        """Mac: o "dispositivo_audio" do config.json do Kakashi ou do Premiere (o mesmo microfone); senão o 1º do avfoundation"""
        for arq in (CFG, os.path.join(AQUI, "premiere", "config.json")):
            try:
                v = json.load(open(arq, encoding="utf-8")).get("dispositivo_audio")
                if v:
                    return v
            except (OSError, ValueError):
                pass
        try:
            r = subprocess.run([FFMPEG, "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
                               capture_output=True, timeout=15)
            txt = (r.stderr or b"").decode("utf-8", "replace")
            m = re.search(r"AVFoundation audio devices:.*?\] \[\d+\] ([^\n]+)", txt, re.S)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
        return ""

    def entrada_mic(dev):
        return ["-f", "avfoundation", "-i", ":" + dev]

    ENTRADA_TELA = ["-f", "avfoundation", "-framerate", "5", "-capture_cursor", "1", "-i", "Capture screen 0:none"]
# P20: gravando, tanto tempo em silêncio digital → o olho fica cinza e o "SEM SOM" pisca (+ P40: o som do Sharingan no fone).
# Era 15; P40 (30/10) subiu pra 20 = o mesmo do CORRETOR (mic_morto_s): o mic sem fio dele corta pra ZERO em toda pausa
# (29/10: pausa normal de até 17,5 s em 57 min; 20 s não deu alarme falso em 2h47). config.json "mudo_aviso_s" muda.
MUDO_AVISO_S = 20
SOM_ALERTA = os.path.join(AQUI, "sons", "sharingan.wav")


def mudo_aviso_s():
    try:
        return float(cfg().get("mudo_aviso_s", MUDO_AVISO_S))
    except (TypeError, ValueError):
        return MUDO_AVISO_S


def tocar_alerta():
    """P40 (30/10, ele: "se não tiver nenhum ruidinho, bota o barulho do Sharingan no meu ouvido"): o sharingan.wav 2x na
    saída padrão do Windows (o fone), igual o CORRETOR faz no modo Premiere. config.json "alerta_som": false desliga;
    "alerta_som_arquivo" troca o som. Num fio: não segura o olho."""
    c = cfg()
    som = str(c.get("alerta_som_arquivo") or SOM_ALERTA)
    if c.get("alerta_som", True) is False or not os.path.isfile(som):
        log("alerta: som não tocado (alerta_som=%s, arquivo=%r)" % (c.get("alerta_som", True), som))
        return

    def _toca():
        try:
            for _ in range(2):
                if MAC:
                    subprocess.Popen(["afplay", som])
                else:
                    import winsound
                    winsound.PlaySound(som, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                time.sleep(2.2)     # JUIZ 30/10: espera depois dos DOIS (igual o CORRETOR): o fio não morre com o 2º ainda tocando
            log("alerta: toquei o som do Sharingan 2x (%s)" % os.path.basename(som))
        except Exception as e:
            log("alerta: não toquei o som: %r" % e)
    threading.Thread(target=_toca, daemon=True).start()


class VozViva:
    """P20: há quanto tempo o wav da gravação está em SILÊNCIO DIGITAL (< -85 dB). O microfone sem fio dele corta pra zero
    nas pausas (até 17,5 s em 29/10), por isso o aviso só vem depois de mudo_aviso_s() (20 s).
    'faltando_e_mudo': o wav nem existir conta como mudo (PC: o ffmpeg do microfone não abriu); no AppPessoal, não sabe.
    'quem': "pc" ou "app_pessoal" → P40: o aviso toca o som do Sharingan 1 vez (só de novo se a voz voltar e morrer de novo).
    "premiere" ou nada = sem som (no Premiere quem toca é o CORRETOR)."""

    def __init__(self, arq, ini, faltando_e_mudo=True, quem=None):
        self.arq, self.ini, self.faltando_e_mudo, self.quem = arq, ini, faltando_e_mudo, quem
        self.ult_som = ini; self.avisou = False; self.trechos = []

    def medir(self, agora):
        if not os.path.isfile(self.arq) and not self.faltando_e_mudo:
            self.ult_som = agora
        else:
            p = olho.pico_fim([self.arq], 1.5)
            if p is not None and p >= olho.MUDO:
                if self.avisou:
                    log("a voz voltou na gravação (%.0f s em silêncio digital)" % (agora - self.ult_som))
                    self.trechos.append((self.ult_som, agora))
                self.ult_som = agora; self.avisou = False
        mudo = agora - self.ult_som
        if mudo > mudo_aviso_s() and not self.avisou:
            self.avisou = True
            log("gravação MUDA há %.0f s (%s): o olho ficou cinza" % (mudo, os.path.basename(os.path.dirname(self.arq))))
            if self.quem in ("pc", "app_pessoal"):
                try:
                    tocar_alerta()
                except Exception as e:
                    log("alerta: %r" % e)
        return mudo

    def trechos_mudos(self, t0, agora):
        """[[de, até], ...] no relógio da sessão (t0 = 0:00) dos trechos que passaram do aviso, o aberto fecha em 'agora'"""
        tr = self.trechos + ([(self.ult_som, agora)] if self.avisou else [])
        return [[round(a - t0, 1), round(b - t0, 1)] for a, b in tr]


# ---------- gravação própria (tipo "pc") ----------
class GravacaoPC:
    def __init__(self, janela, k=None, replay=None):
        """replay = o que o Replay.parar() devolveu ({fim, segundos}): o relógio da sessão começa 'segundos' antes do atalho,
        os eventos desses 2 min (que o Vigia guardou na memória) entram já, e os arquivos do replay entram no começo no concluir"""
        agora = datetime.datetime.now()
        self.k = k
        self.pasta = os.path.join(SESSOES, agora.strftime("%Y-%m-%d_%H%M%S") + "_pc")
        os.makedirs(self.pasta, exist_ok=True)
        self.t_grav = time.time()                       # o atalho (a gravação de agora em diante)
        self.replay_s = round(replay["segundos"], 2) if replay and replay.get("segundos", 0) >= 1 else 0.0
        self.t0 = (replay["fim"] - self.replay_s) if self.replay_s else self.t_grav     # 0:00 da sessão
        self.replay_arqs = None; self.replay_pronto = threading.Event()
        if not self.replay_s:
            self.replay_pronto.set()
        self.meta = {"tipo": "pc", "inicio_local": datetime.datetime.fromtimestamp(self.t0).replace(microsecond=0).isoformat(),
                     "inicio_epoch": self.t0, "gravacao_epoch": self.t_grav, "replay_s": self.replay_s,
                     "janela_inicial": janela, "erros": []}
        if replay and "sem_voz" in replay:          # P20: a voz do buffer estava em silêncio digital nos últimos ~10 s
            self.meta.update(replay_sem_voz=replay["sem_voz"], replay_voz_muda_s=replay.get("voz_muda_s"))
        self.procs = []
        self.parar_ev = threading.Event()
        self.concluida = threading.Event()              # o concluir terminou (a troca pro Premiere espera isso pra descartar junto)
        self.ev = open(os.path.join(self.pasta, "eventos.jsonl"), "a", encoding="utf-8")
        self.ev_trava = threading.Lock()
        self.hashes = set()                             # imagens já salvas (área de transferência x pasta de capturas)
        self.flog = open(os.path.join(self.pasta, "ffmpeg.log"), "ab")
        # 03/11 (Kakashi PC 09:52, ele: «coloca o Kakashi aqui com os mesmos controles do Premiere... Pausar, aí excluir a parte»): a
        # gravação é feita em PEDAÇOS, igual ao painel do Premiere — cada Pausar fecha um (fala/tela/som do PC), Continuar abre o próximo,
        # e o pedaço pode ser apagado (e voltado) no trilho da janelinha. Sem pausa = um pedaço só = os mesmos arquivos de sempre.
        self.pedacos = [{"n": 1, "ini": round(self.t_grav - self.t0, 2), "epoch": self.t_grav, "dur": None, "apagado": False}]
        self.pausado, self.pausa_epoch, self.pausado_s = False, None, 0.0
        self.p_trava = threading.Lock()
        self._abrir_pedaco(1, self.t_grav)
        if k is not None and self.replay_s:            # mouse/janela/cliques dos 2 min do replay (só estavam na memória)
            for quando, e in k.vigia.desde(self.t0):
                self._evento(e, quando)
        self._evento({"tipo": "janela", **janela, "atalho": True})
        threading.Thread(target=self._area, daemon=True).start()
        threading.Thread(target=self._capturas, daemon=True).start()
        self._salvar_meta()

    def _arq(self, base, ext, n):
        """o arquivo do pedaço n: o 1º tem o nome de sempre (fala.wav, tela.mp4); os outros, fala_p02.wav, tela_p02.mp4…"""
        return os.path.join(self.pasta, base + ext if n == 1 else "%s_p%02d%s" % (base, n, ext))

    def _abrir_pedaco(self, n, epoch):
        dev = microfone()
        if n == 1:
            self.meta["microfone"] = dev
        if dev:
            self._abrir("fala", [FFMPEG, "-hide_banner", "-nostats", "-loglevel", "warning"] + entrada_mic(dev) + ["-ac", "1", "-ar", "48000",
                                 "-c:a", "pcm_s16le", "-flush_packets", "1", "-y", self._arq("fala", ".wav", n)])
        else:
            self.meta["erros"].append("nenhum microfone encontrado" + ("" if n == 1 else " (pedaço %d)" % n))
        self._abrir("tela", [FFMPEG, "-hide_banner", "-nostats", "-loglevel", "warning"] + ENTRADA_TELA +
                            ["-vf", "scale=1920:-2:flags=bilinear,format=yuv420p",
                             "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency", "-crf", "30", "-g", "10",
                             "-threads", "2", "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
                             "-frag_duration", "2000000", "-flush_packets", "1", "-y", self._arq("tela", ".mp4", n)])
        gp = os.path.join(CORRETOR, "gravar_pc.py")
        if os.path.isfile(gp):      # no Mac o gravar_pc.py lê o som do Mac pelo som_mac/som_do_mac (ScreenCaptureKit)
            self._abrir("som_pc", [PY, gp, "--pasta", self.pasta, "--parte", str(n), "--inicio", "%.3f" % epoch] + GRAVAR_PC_EXTRA,
                        stdout=subprocess.DEVNULL, stderr=open(os.path.join(self.pasta, "som_pc.log"), "ab"))

    def _fechar(self, procs):
        for nome, p in procs:
            try:
                p.stdin.write(b"q"); p.stdin.flush()
            except Exception:
                pass
        for nome, p in procs:
            try:
                p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                p.kill(); self.meta["erros"].append(nome + ": não fechou em 15 s, foi encerrado")

    def valendo(self):
        """o tempo que VALE (sem as pausas e sem os pedaços apagados) — o relógio da janelinha e do olho, igual ao painel"""
        t = self.pedacos[0]["ini"]                  # o replay (0 desde 02/11)
        for p in self.pedacos:
            if p["apagado"]:
                continue
            t += p["dur"] if p["dur"] is not None else max(0.0, time.time() - p["epoch"])
        return t

    def pausar(self):
        with self.p_trava:
            if self.pausado or self.parar_ev.is_set():
                return False
            agora = time.time()
            self._evento({"tipo": "pausa", "pedaco": self.pedacos[-1]["n"]}, agora)
            self.pausado, self.pausa_epoch = True, agora
            p = self.pedacos[-1]; p["dur"] = round(agora - p["epoch"], 2)
            procs, self.procs = self.procs, []
        self._fechar(procs)
        log("pausou %s (pedaço %d, %.1f s)" % (os.path.basename(self.pasta), p["n"], p["dur"]))
        self.meta["pedacos"] = self.pedacos; self._salvar_meta()
        return True

    def continuar(self):
        with self.p_trava:
            if not self.pausado or self.parar_ev.is_set():
                return False
            agora = time.time()
            self.pausado_s += agora - self.pausa_epoch
            n = self.pedacos[-1]["n"] + 1
            self.pedacos.append({"n": n, "ini": round(agora - self.t0 - self.pausado_s, 2), "epoch": agora, "dur": None, "apagado": False})
            self.pausado, self.pausa_epoch = False, None
            self._abrir_pedaco(n, agora)
            self._evento({"tipo": "continua", "pedaco": n}, agora)
        log("continuou %s (pedaço %d)" % (os.path.basename(self.pasta), n))
        return True

    def alternar_pedaco(self, n):
        """apaga ou volta um pedaço (o que está gravando agora não: pausa antes). Nada some: no concluir o apagado vai pra _pedacos"""
        with self.p_trava:
            for p in self.pedacos:
                if p["n"] == n and p["dur"] is not None:
                    p["apagado"] = not p["apagado"]
                    self._evento({"tipo": "pedaco_apagado" if p["apagado"] else "pedaco_voltou", "pedaco": n, "marca": True})
                    return True
        return False

    def _abrir(self, nome, cmd, stdout=subprocess.DEVNULL, stderr=None):
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr or self.flog, creationflags=SEM_JANELA)
            self.procs.append((nome, p))
        except Exception as e:
            self.meta["erros"].append("%s: %s" % (nome, e))

    def _evento(self, d, quando=None):
        """uma linha no eventos.jsonl, no relógio da sessão (t = segundos desde o 0:00, que inclui o replay). 03/11: pausado = nada
        entra (a não ser a marca de pedaço apagado/voltou); o relógio não conta as pausas (igual ao painel do Premiere)"""
        if getattr(self, "pausado", False) and not d.get("marca"):
            return
        d = dict(d); d.pop("marca", None)
        if getattr(self, "pedacos", None) and "pedaco" not in d:
            d["pedaco"] = self.pedacos[-1]["n"]
        d["t"] = round((quando or time.time()) - self.t0 - getattr(self, "pausado_s", 0.0), 2)
        with self.ev_trava:
            if not self.ev.closed:
                self.ev.write(json.dumps(d, ensure_ascii=False) + "\n"); self.ev.flush()

    def _rotulo(self, quando, nome):
        s = max(0, int(quando - self.t0 - getattr(self, "pausado_s", 0.0)))
        return "%02d%02d_%s" % (s // 60, s % 60, nome)

    def _salvar_imagem(self, im, quando, nome):
        os.makedirs(os.path.join(self.pasta, "_copias"), exist_ok=True)
        base = os.path.join("_copias", self._rotulo(quando, nome)); rel = base + ".png"; i = 2
        while os.path.exists(os.path.join(self.pasta, rel)):
            rel = "%s_%d.png" % (base, i); i += 1
        im.save(os.path.join(self.pasta, rel))
        return rel

    def _area(self):
        """o que ele copia (Ctrl+C, print, Win+Shift+S) entra no log com a hora. SENHA NUNCA: conteúdo marcado por
        gerenciador de senha, gerenciador na frente, janela de senha ou campo de senha em foco = nem é lido."""
        try:
            uia = olho.UIA()
        except Exception as e:
            uia = None; log("área/uia: %r" % e)
        contagem = mac.area_contagem if MAC else olho.user32.GetClipboardSequenceNumber
        seq = contagem()
        while not self.parar_ev.wait(0.3):
            s = contagem()
            if s == seq:
                continue
            seq = s; quando = time.time(); time.sleep(0.15)
            try:
                j = janela_frente()
                dono = j["app"] if MAC else (olho.exe_do_pid(_pid_da_janela(user32.GetClipboardOwner())) or j["app"])
                if {j["app"].lower(), dono.lower()} & olho.GERENCIADORES or re.search(r"senha|password|passkey", j["titulo"], re.I):
                    continue
                if uia is not None and uia.foco_e_senha():
                    continue
                a = olho.ler_area()
                if not a or a.get("protegido"):
                    continue
                ev = {"tipo": "copiou", "app": dono, "janela": j["titulo"][:90]}
                if a.get("html_fonte"):
                    ev["de"] = a["html_fonte"][:300]
                from PIL import ImageGrab
                if a["imagem"]:
                    im = ImageGrab.grabclipboard()
                    if im is None or isinstance(im, list):
                        continue
                    h = olho.hash_imagem(im)
                    if h in self.hashes:
                        continue
                    self.hashes.add(h)
                    captura = dono.lower() in ("snippingtool.exe", "screenclippinghost.exe", "screensketch.exe", "screencaptureui",
                                               "captura de tela", "screenshot")
                    ev.update(o_que="captura" if captura else "imagem", arquivo=self._salvar_imagem(im, quando, "captura" if captura else "imagem"),
                              tamanho=list(im.size))
                    if a.get("html_img"):
                        ev["url_imagem"] = a["html_img"]
                elif a["arquivos"]:
                    lst = a.get("lista") if MAC else ImageGrab.grabclipboard()
                    ev.update(o_que="arquivos", arquivos=[str(x) for x in (lst or [])][:30])
                elif a.get("texto", "").strip():
                    t = a["texto"].strip()
                    ev["o_que"] = "link" if re.fullmatch(r"(https?://|www\.)\S+", t) else "texto"
                    ev["texto"] = t[:2000]
                    if len(t) > 2000:
                        os.makedirs(os.path.join(self.pasta, "_copias"), exist_ok=True)
                        rel = os.path.join("_copias", self._rotulo(quando, "texto") + ".txt")
                        open(os.path.join(self.pasta, rel), "w", encoding="utf-8").write(t); ev["arquivo"] = rel
                else:
                    continue
                self._evento(ev, quando)
            except Exception as e:
                log("área: %r" % e)

    def _capturas(self):
        """Win+Shift+S / Ferramenta de Captura salvam sozinhas em Imagens\\Capturas de Tela: cada nova vem pra sessão"""
        from PIL import Image
        pasta = olho.pasta_capturas()
        try:
            vistos = set(os.listdir(pasta))
        except OSError:
            vistos = set()
        while not self.parar_ev.wait(2.0):
            try:
                novos = [n for n in os.listdir(pasta) if n not in vistos]
            except OSError:
                continue
            for n in novos:
                vistos.add(n)
                if not n.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                src = os.path.join(pasta, n)
                try:
                    time.sleep(0.4)
                    quando = os.path.getmtime(src)
                    im = Image.open(src); im.load()
                    h = olho.hash_imagem(im)
                    if h in self.hashes:
                        continue
                    self.hashes.add(h)
                    self._evento({"tipo": "copiou", "o_que": "captura", "arquivo": self._salvar_imagem(im, quando, "captura"),
                                  "origem": src, "tamanho": list(im.size)}, quando)
                except Exception as e:
                    log("capturas: %r" % e)

    def fala_wav(self):
        return self._arq("fala", ".wav", self.pedacos[-1]["n"])

    def _salvar_meta(self):
        with open(os.path.join(self.pasta, "sessao.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)

    def concluir(self, cancelar=False):
        try:
            self._concluir(cancelar)
        finally:
            self.concluida.set()

    def _concluir(self, cancelar=False):
        self.parar_ev.set()
        with self.p_trava:
            procs, self.procs = self.procs, []
            if not self.pausado:
                p = self.pedacos[-1]; p["dur"] = round(time.time() - p["epoch"], 2)
        self._fechar(procs)
        try:
            with self.ev_trava:
                self.ev.close()
            self.flog.close()
        except Exception:
            pass
        fim = time.time()
        em_pedacos = len(self.pedacos) > 1 or any(p["apagado"] for p in self.pedacos)
        if em_pedacos and not cancelar:
            self._juntar_pedacos()
        else:
            # som do PC: o gravar_pc.py do CORRETOR deixa pc01*.wav; um só vira pc.wav
            pcs = sorted(f for f in os.listdir(self.pasta) if re.match(r"pc\d+.*\.wav$", f))
            if len(pcs) == 1:
                os.replace(os.path.join(self.pasta, pcs[0]), os.path.join(self.pasta, "pc.wav"))
            elif len(pcs) > 1:
                self._juntar_pc(pcs)
        dur = round(self.valendo(), 1) if em_pedacos else round(fim - self.t0, 1)
        self.meta.update(fim_local=datetime.datetime.now().replace(microsecond=0).isoformat(), duracao_s=dur)
        if em_pedacos:
            self.meta["pedacos"] = [{k: p[k] for k in ("n", "ini", "dur", "apagado")} for p in self.pedacos]
            if all(p["apagado"] for p in self.pedacos):
                cancelar = True; self.meta["erros"].append("todos os pedaços apagados: foi pra descartadas")
        if cancelar:
            self.meta["descartada"] = True
        self._salvar_meta()
        if cancelar:
            dest = os.path.join(SESSOES, "_descartadas"); os.makedirs(dest, exist_ok=True)
            try:
                shutil.move(self.pasta, dest)
            except OSError as e:
                log("cancelar: %s" % e)
            log("cancelada " + self.pasta)
            return
        if self.replay_s:
            self._juntar_replay()
            self._salvar_meta()
        log("concluída " + self.pasta)
        # links do Chrome: o History só vai pro disco alguns segundos depois da visita
        time.sleep(12)
        try:
            n = len(olho.links_da_sessao(self.pasta, self.meta))
            self.meta["links"] = n
        except Exception as e:
            self.meta["erros"].append("links do Chrome: %s" % e)
        self._salvar_meta()

    def _juntar_pedacos(self):
        """03/11: os pedaços que valem viram UM tela.mp4 / fala.wav / pc.wav (o relógio sem as pausas e sem os apagados) e o
        eventos.jsonl perde o que caiu nos apagados e encosta o resto. Os arquivos de cada pedaço vão pra pasta _pedacos (nunca apaga)."""
        P = lambda x: os.path.join(self.pasta, x)          # noqa: E731
        guarda = P("_pedacos"); os.makedirs(guarda, exist_ok=True)
        # o 1º pedaço tem o nome final: vira _p01 antes de juntar
        for base, ext in (("tela", ".mp4"), ("fala", ".wav")):
            if os.path.isfile(P(base + ext)):
                os.replace(P(base + ext), P("%s_p01%s" % (base, ext)))
        # som do PC de cada pedaço pelo relógio (o gravar_pc abre um pouco depois: vira silêncio no começo; troca de saída = junta)
        for p in self.pedacos:
            man = P("pc%02d.json" % p["n"])
            if os.path.isfile(man) and p["dur"]:
                try:
                    if not olho.extrair_pc([man], p["epoch"], p["epoch"] + p["dur"], P("pc_p%02d.wav" % p["n"])):
                        self.meta["erros"].append("som do PC: pedaço %d sem som" % p["n"])
                except Exception as e:
                    self.meta["erros"].append("som do PC: pedaço %d: %s" % (p["n"], e))
        validos = [p for p in self.pedacos if not p["apagado"] and (p["dur"] or 0) > 0.2]
        for p in validos:
            fw = P("fala_p%02d.wav" % p["n"])
            if os.path.isfile(fw):
                try:
                    d, tx, can, lg = olho.ler_wav(fw)
                    corte = int(p["dur"] * tx) * can * lg
                    if len(d) > corte:
                        os.replace(fw, fw + ".inteiro.wav"); olho.gravar_wav(fw, d[:corte], tx, can, lg)
                except Exception as e:
                    self.meta["erros"].append("pedaços: cortar a fala %d: %s" % (p["n"], e))
            tv = P("tela_p%02d.mp4" % p["n"])
            if os.path.isfile(tv) and olho.duracao(tv) > p["dur"] + 0.25:
                r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", tv, "-t", "%.3f" % p["dur"], "-c:v", "libx264",
                                    "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-y", tv + ".cortado.mp4"],
                                   capture_output=True, timeout=600, creationflags=SEM_JANELA)
                if r.returncode == 0:
                    os.replace(tv, tv + ".inteiro.mp4"); os.replace(tv + ".cortado.mp4", tv)
                else:
                    self.meta["erros"].append("pedaços: cortar a tela %d: %s" % (p["n"], r.stderr.decode("utf-8", "replace")[-200:]))
        for base, ext, video in (("tela", ".mp4", True), ("fala", ".wav", False), ("pc", ".wav", False)):
            partes = [P("%s_p%02d%s" % (base, p["n"], ext)) for p in validos]
            partes = [x for x in partes if os.path.isfile(x) and os.path.getsize(x) > 1000]
            if not partes:
                continue
            try:
                ok = olho.juntar_video(partes, P(base + ext), log) if video else olho.juntar_wav(partes, P(base + ext))
                if not ok:
                    self.meta["erros"].append("pedaços: %s não juntou" % (base + ext))
            except Exception as e:
                self.meta["erros"].append("pedaços: %s: %s" % (base + ext, e))
        for f in os.listdir(self.pasta):
            if re.match(r"(tela|fala|pc)_p\d\d\.(mp4|wav)(\.inteiro\.(mp4|wav))?$", f) or re.match(r"pc\d\d(_\d+)?\.(wav|json)$", f):
                try:
                    shutil.move(P(f), os.path.join(guarda, f))
                except OSError as e:
                    log("pedaços: guardar %s: %s" % (f, e))
        # eventos: o que caiu num pedaço apagado sai; o resto encosta (tira a duração dos apagados de antes)
        apag = [p for p in self.pedacos if p["apagado"] and p["dur"]]
        if apag:
            try:
                linhas = open(P("eventos.jsonl"), encoding="utf-8").read().splitlines()
                out = []
                for l in linhas:
                    try:
                        e = json.loads(l)
                    except ValueError:
                        continue
                    t, n = e.get("t"), e.get("pedaco")
                    if isinstance(t, (int, float)):
                        marca = e.get("tipo") in ("pedaco_apagado", "pedaco_voltou")
                        if isinstance(n, int) and not marca:
                            if any(p["n"] == n for p in apag):
                                continue
                            e["t"] = round(t - sum(p["dur"] for p in apag if p["n"] < n), 2)
                        else:
                            e["t"] = round(t - sum(p["dur"] for p in apag if p["ini"] + p["dur"] <= t), 2)
                    out.append(json.dumps(e, ensure_ascii=False))
                shutil.copy(P("eventos.jsonl"), os.path.join(guarda, "eventos.com-apagados.jsonl"))
                open(P("eventos.jsonl"), "w", encoding="utf-8").write("\n".join(out) + "\n")
            except Exception as e:
                self.meta["erros"].append("pedaços: eventos: %s" % e)
        log("pedaços juntados em %s: %d de %d valem" % (os.path.basename(self.pasta), len(validos), len(self.pedacos)))

    def _juntar_pc(self, pcs):
        """P20: a saída de som trocou no meio (fone, monitor...): o gravar_pc.py deixou um pc01_N.wav por saída. Antes ficavam
        soltos (sem pc.wav o resumo não lia o som do PC e o replay não juntava); agora viram um pc.wav na linha do tempo
        (t0 de cada segmento no pc01.json; buraco da troca = silêncio; formato diferente é convertido)."""
        man = os.path.join(self.pasta, "pc01.json")
        try:
            m = json.load(open(man, encoding="utf-8"))
            segs = m.get("segmentos") or []
            ini = m.get("inicio") or self.t_grav       # o atalho (o --inicio): a abertura atrasada vira silêncio no começo
            fim = m.get("fim") or max(s["t0"] + s.get("dur", 0) for s in segs)
            if olho.extrair_pc([man], ini, fim, os.path.join(self.pasta, "pc.wav")):
                for f in pcs:
                    os.remove(os.path.join(self.pasta, f))
                self.meta["pc_saidas"] = [s.get("dispositivo") for s in segs]
            else:
                self.meta["erros"].append("som do PC: %d pedaços (%s) não juntaram" % (len(pcs), ", ".join(pcs)))
        except Exception as e:
            self.meta["erros"].append("som do PC: juntar %s: %s" % (", ".join(pcs), e))

    def _juntar_replay(self):
        """replay_*.(mp4|wav) + o gravado → tela.mp4 / fala.wav / pc.wav, tudo no relógio da sessão (0:00 = começo do replay)"""
        if not self.replay_pronto.wait(90):
            self.meta["erros"].append("replay: a extração não terminou em 90 s (ficou de fora)"); return
        r = self.replay_arqs or {}
        p = lambda n: os.path.join(self.pasta, n)
        feitos = []
        for chave, final, tipo in (("tela", "tela.mp4", "v"), ("fala", "fala.wav", "a"), ("pc", "pc.wav", "a")):
            rep = r.get(chave)
            if not rep or not os.path.isfile(p(final)):
                continue
            meio = p("_gravacao_" + final)
            try:
                os.replace(p(final), meio)
                ok = olho.juntar_video([rep, meio], p(final), log) if tipo == "v" else olho.juntar_wav([rep, meio], p(final))
                d_rep, d_meio, d_fim = olho.duracao(rep), olho.duracao(meio), olho.duracao(p(final)) if ok else 0
                if ok and d_fim >= d_rep + d_meio - 1.5:
                    os.remove(rep); os.remove(meio); feitos.append(chave)
                else:
                    if os.path.isfile(p(final)):
                        os.remove(p(final))
                    os.replace(meio, p(final))
                    self.meta["erros"].append("replay %s: não juntou (%.1f + %.1f → %.1f s); ficou separado em %s" %
                                              (chave, d_rep, d_meio, d_fim, os.path.basename(rep)))
            except Exception as e:
                self.meta["erros"].append("replay %s: %s" % (chave, e))
                if os.path.isfile(meio) and not os.path.isfile(p(final)):
                    os.replace(meio, p(final))
        self.meta["replay_juntado"] = feitos


class OlhoPremiere(GravacaoPC):
    """23/10 (ele: "faz o Kakashi ser o mais completo possível pra não ter mais problema, tá ligado? É o olho de Deus, mano, é minha
    tela"): enquanto o painel do Premiere grava (começou lá ou trocou do PC), o olho do PC continua — janela, mouse, elemento sob o
    mouse, print do "aqui", o que ele copia — numa pasta _olho DENTRO da sessão do Premiere, no MESMO relógio da gravação do painel
    (sem as pausas: o relógio sai do t_gravacao do 7815/status). Sem ffmpeg nenhum: a tela, a voz e o som do PC continuam sendo do
    painel. No fim, a fala.wav e a tela.mp4 do painel são ligadas na _olho e ela vira uma sessão "pc" que o resumo_pc.py lê igual.
    Arquivo nenhum fica aberto (abre, escreve, fecha): o painel pode descartar/mover a pasta da sessão a qualquer hora."""

    def __init__(self, pasta_premiere, k, t_gravacao=0.0, gravando=True):
        self.k = k
        self.pasta_premiere = pasta_premiere
        self.pasta = os.path.join(pasta_premiere, "_olho")
        os.makedirs(self.pasta, exist_ok=True)
        self.t0 = self.t_grav = time.time()
        self.replay_s = 0.0; self.replay_arqs = None
        self.replay_pronto = threading.Event(); self.replay_pronto.set()
        self.relogio = (float(t_gravacao or 0.0), self.t0, bool(gravando))
        j = janela_frente()
        self.meta = {"tipo": "pc", "olho_premiere": True, "sessao_premiere": os.path.basename(pasta_premiere),
                     "inicio_local": datetime.datetime.fromtimestamp(self.t0).replace(microsecond=0).isoformat(),
                     "inicio_epoch": self.t0, "gravacao_epoch": self.t0, "replay_s": 0.0, "t_gravacao_inicio": round(self.relogio[0], 2),
                     "janela_inicial": j, "erros": []}
        # 04/11 (queda de luz): o Kakashi reabriu e o olho voltou numa sessão que já tinha começo; reescrever o começo pra 17:17 jogava
        # fora os links do Chrome e o rastro dos outros apps de 16:51–17:15 na leitura. Sessão já começada = o começo antigo fica.
        try:
            velho = json.load(open(os.path.join(self.pasta, "sessao.json"), encoding="utf-8"))
            if velho.get("sessao_premiere") == self.meta["sessao_premiere"] and velho.get("inicio_epoch"):
                for c in ("inicio_local", "inicio_epoch", "gravacao_epoch", "t_gravacao_inicio", "janela_inicial", "erros"):
                    if c in velho:
                        self.meta[c] = velho[c]
                self.meta.setdefault("reaberto", []).extend(velho.get("reaberto", []))
                self.meta["reaberto"].append(datetime.datetime.fromtimestamp(self.t0).replace(microsecond=0).isoformat())
        except (OSError, ValueError):
            pass
        self.procs = []
        self.parar_ev = threading.Event()
        self.concluida = threading.Event()
        self.ev_trava = threading.Lock()
        self.hashes = set()
        self._evento({"tipo": "janela", **j, "atalho": True})
        threading.Thread(target=self._area, daemon=True).start()
        threading.Thread(target=self._capturas, daemon=True).start()
        self._salvar_meta()

    def sincronizar(self, t_gravacao, gravando):
        """o vigia chama a cada ~0,5 s com o t_gravacao do painel: o relógio do olho anda junto (parado na pausa)"""
        self.relogio = (float(t_gravacao or 0.0), time.time(), bool(gravando))

    def t_rec(self, quando):
        t, e, grav = self.relogio
        return max(0.0, t + (max(0.0, quando - e) if grav else 0.0))

    def viva(self):
        return not self.parar_ev.is_set() and os.path.isdir(self.pasta_premiere)

    def _evento(self, d, quando=None):
        quando = quando or time.time()
        if not self.relogio[2] or not self.viva():      # pausado (o painel não grava) ou a sessão já saiu do lugar
            return
        d = dict(d); d["t"] = round(self.t_rec(quando), 2); d["epoch"] = round(quando, 2)
        with self.ev_trava:
            try:
                with open(os.path.join(self.pasta, "eventos.jsonl"), "a", encoding="utf-8") as f:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
            except OSError:
                pass

    def _rotulo(self, quando, nome):
        s = int(self.t_rec(quando))
        return "%02d%02d_%s" % (s // 60, s % 60, nome)

    def _salvar_imagem(self, im, quando, nome):
        if not self.viva():
            raise OSError("a sessão do Premiere saiu do lugar")
        if not self.relogio[2]:                         # 04/11: pausado = a imagem copiada também não entra
            raise OSError("o painel do Premiere está pausado")
        return GravacaoPC._salvar_imagem(self, im, quando, nome)

    def fala_wav(self):
        """a voz que o painel está gravando agora (parteNN.wav da sessão): o print do 'aqui' sai enquanto ele fala.
        Pausado ou terminando = nada (nem abre o arquivo: o painel vai juntar/apagar os pedaços)."""
        if not self.relogio[2] or not self.viva() or time.time() - self.relogio[1] > 1.0:
            return ""
        try:
            ps = sorted(f for f in os.listdir(self.pasta_premiere) if re.match(r"parte\d+\.wav$", f))
        except OSError:
            return ""
        return os.path.join(self.pasta_premiere, ps[-1]) if ps else ""

    def _salvar_meta(self):
        if os.path.isdir(self.pasta):
            GravacaoPC._salvar_meta(self)

    def _recontar(self, mp):
        """o relógio FINAL do painel (sessao.json dele, depois do Concluir): as partes que ficaram (t0 recontado quando ele apaga
        um pedaço) viram relogio_trechos e cada evento do olho ganha o t de novo pelo epoch (o ao vivo fica em t_bruto quando muda);
        evento de pedaço apagado sai pra eventos_dos_pedacos_apagados.jsonl — igual o CORRETOR faz com os eventos dele."""
        partes = sorted([p for p in (mp.get("partes") or []) if p.get("inicio") and p.get("fim")], key=lambda p: p["inicio"])
        if not partes:
            return
        tre = [[round(p["inicio"], 3), round(float(p.get("t0") or 0.0), 3), round(p["fim"], 3)] for p in partes]
        apag = [(p["inicio"], p["fim"]) for p in (mp.get("pedacos_apagados") or []) if p.get("inicio") and p.get("fim")]
        self.meta["relogio_trechos"] = tre
        arq = os.path.join(self.pasta, "eventos.jsonl")
        with self.ev_trava:
            try:
                evs = [json.loads(l) for l in open(arq, encoding="utf-8") if l.strip()]
            except (OSError, ValueError):
                return
            ficam, saem = [], []
            for e in evs:
                q = e.get("epoch")
                if q is not None and any(a - 0.3 <= q <= b + 0.3 for a, b in apag) and not any(a <= q <= b for a, _, b in tre):
                    saem.append(e); continue
                if q is not None:
                    t = round(olho.t_da_sessao(q, self.meta), 2)
                    if abs(t - e.get("t", t)) > 0.05:
                        e["t_bruto"] = e.get("t"); e["t"] = t
                ficam.append(e)
            try:
                with open(arq, "w", encoding="utf-8") as f:
                    f.writelines(json.dumps(e, ensure_ascii=False) + "\n" for e in ficam)
                if saem:
                    with open(os.path.join(self.pasta, "eventos_dos_pedacos_apagados.jsonl"), "w", encoding="utf-8") as f:
                        f.writelines(json.dumps(e, ensure_ascii=False) + "\n" for e in saem)
            except OSError as ex:
                self.meta["erros"].append("recontar o relógio: %s" % ex); return
        self.meta["eventos_recontados"] = sum(1 for e in ficam if "t_bruto" in e)
        if saem:
            self.meta["eventos_de_pedaco_apagado"] = len(saem)

    def _concluir(self, cancelar=False):
        self.parar_ev.set()
        fim = time.time()
        t_fim = self.t_rec(fim)
        if not os.path.isdir(self.pasta):               # descartada: o painel levou a pasta inteira pro _descartadas
            log("olho do Premiere: a sessão %s saiu do lugar (descartada?)" % os.path.basename(self.pasta_premiere)); return
        for _ in range(360):                            # o painel junta audio.wav / tela.mp4 depois do concluir (até 3 min)
            st = http("http://127.0.0.1:7815/status", t=1) or {}
            if not os.path.isdir(self.pasta):
                return
            if not st.get("finalizando") and os.path.isfile(os.path.join(self.pasta_premiere, "audio.wav")):
                break
            time.sleep(0.5)
        try:
            mp = json.load(open(os.path.join(self.pasta_premiere, "sessao.json"), encoding="utf-8"))
        except Exception:
            mp = {}
        self._recontar(mp)
        for src, dst in (("audio.wav", "fala.wav"), ("tela.mp4", "tela.mp4"), ("pc.wav", "pc.wav")):
            a, b = os.path.join(self.pasta_premiere, src), os.path.join(self.pasta, dst)
            if os.path.isfile(a) and not os.path.exists(b):
                try:
                    os.link(a, b)                       # link no mesmo disco: não duplica os 4K
                except OSError:
                    if dst != "tela.mp4":
                        shutil.copy2(a, b)
        tre = self.meta.get("relogio_trechos")
        self.meta.update(fim_local=datetime.datetime.now().replace(microsecond=0).isoformat(), fim_epoch=round(tre[-1][2] if tre else fim, 3),
                         duracao_s=round(float(mp.get("t_gravado") or t_fim), 1), microfone=mp.get("dispositivo"),
                         estado_premiere=mp.get("estado"))
        if cancelar or mp.get("estado") == "descartada":
            self.meta["descartada"] = True
        self._salvar_meta()
        log("olho do Premiere concluído: %s (%.0f s)" % (self.pasta, t_fim))
        time.sleep(12)                                  # links do Chrome: o History só vai pro disco uns segundos depois
        try:
            self.meta["links"] = len(olho.links_da_sessao(self.pasta, self.meta))
        except Exception as e:
            self.meta["erros"].append("links do Chrome: %s" % e)
        self._salvar_meta()


# ---------- o olho sempre aberto (P3) ----------
class Vigia:
    """Lê o Windows 20x/s: janela da frente, cliques e o caminho do mouse (amostra a cada ~0,25 s, só quando mexe).
    Parado (sem gravação): os eventos ficam SÓ na memória, os últimos ~2 min, pra entrar no replay. Gravando o tipo "pc":
    vão pro eventos.jsonl e, na pausa do mouse (>0,8 s depois de andar) e em todo clique, o elemento debaixo do mouse (UIA);
    print nativo na pausa, enquanto ele fala (o "aqui"), e ~1,5 s depois de cada janela/página nova."""
    PAUSA, PASSO, MEMORIA = 0.8, 0.25, 140

    def __init__(self, k):
        self.k = k
        self.anel = collections.deque(); self.trava = threading.Lock()
        self.jobs = queue.Queue(maxsize=12)
        self.ult_print = {"t": 0.0, "pos": None, "mini": None}
        threading.Thread(target=self._laco, daemon=True).start()
        threading.Thread(target=self._trabalhador, daemon=True).start()

    def emitir(self, ev, quando=None):
        quando = quando or time.time()
        g = self.k.alvo()                  # a gravação do PC, ou o olho do Premiere quando o painel grava (23/10)
        if g is not None and quando >= g.t0:
            g._evento(ev, quando); return
        rep = getattr(self.k, "replay", None)    # o vigia sobe antes do Replay existir
        if rep is None or not rep.rodando():    # 02/11: sem replay, nada de antes do atalho fica guardado ("é pra ser exatamente do que eu quero falar")
            with self.trava:
                self.anel.clear()
            return
        with self.trava:
            self.anel.append((quando, ev))
            while self.anel and self.anel[0][0] < quando - self.MEMORIA:
                self.anel.popleft()

    def desde(self, t0):
        with self.trava:
            return [(q, e) for q, e in self.anel if q >= t0]

    def pedir(self, *job):
        try:
            self.jobs.put_nowait(job)
        except queue.Full:
            pass

    def _laco(self):
        pt = wt.POINT(); ult_j = None; botoes = {0x01: False, 0x02: False}
        ant = amostra = None; t_amostra = t_mexeu = t_voz = 0.0; andou = 0.0; print_janela = None
        while True:
            agora = time.time()
            try:
                g = self.k.alvo()
                j = janela_frente()
                if (j["app"], j["titulo"]) != ult_j:
                    ult_j = (j["app"], j["titulo"]); self.emitir({"tipo": "janela", **j}, agora)
                    print_janela = agora + 1.5            # página/janela nova: print nativo quando assentar
                if MAC:
                    pos = mac.mouse()
                else:
                    user32.GetCursorPos(ctypes.byref(pt)); pos = (pt.x, pt.y)
                if ant is not None and pos != ant:
                    andou += abs(pos[0] - ant[0]) + abs(pos[1] - ant[1]); t_mexeu = agora
                ant = pos
                if agora - t_amostra >= self.PASSO:
                    t_amostra = agora
                    if amostra is None or abs(pos[0] - amostra[0]) + abs(pos[1] - amostra[1]) > 3:
                        amostra = pos; self.emitir({"tipo": "mouse", "x": pos[0], "y": pos[1]}, agora)
                # 3.0 (12/11): com uma ferramenta de desenho escolhida o mouse está no pegador do Desenho: clique e pausa são DESENHO
                # (o evento «traco» já leva o elemento debaixo da ponta) — não vira «clique» nem «mouse parou» no app de baixo
                desenhando = self.k.desenhando()
                if andou > 25 and agora - t_mexeu >= self.PAUSA:
                    andou = 0.0
                    self.emitir({"tipo": "parou", "x": pos[0], "y": pos[1]}, t_mexeu)
                    if g is not None and not desenhando:
                        self.pedir("uia", "parou", pos, t_mexeu); self.pedir("print", "parou", pos, t_mexeu)
                for vk in botoes:
                    baixo = mac.botao(vk - 1) if MAC else bool(user32.GetAsyncKeyState(vk) & 0x8000)
                    if baixo and not botoes[vk] and desenhando:
                        botoes[vk] = baixo; continue
                    if baixo and not botoes[vk]:
                        alvo = mac.janela_em(*pos) if MAC else janela_frente(user32.GetAncestor(user32.WindowFromPoint(pt), 2))
                        self.emitir({"tipo": "clique" if vk == 1 else "clique_direito", "x": pos[0], "y": pos[1], **alvo}, agora)
                        if g is not None:
                            self.pedir("uia", "clique", pos, agora)
                    botoes[vk] = baixo
                if g is None:
                    print_janela = None
                elif print_janela and agora >= print_janela:
                    print_janela = None; self.pedir("print", "pagina", pos, agora)
                if g is not None and agora - t_voz >= 0.5:          # falando = o "aqui" pode vir a qualquer hora
                    t_voz = agora
                    if olho.nivel_voz(g.fala_wav()) > 400:
                        self.pedir("print", "fala", pos, agora)
            except Exception as e:
                log("vigia: %r" % e)
            time.sleep(0.05)

    def _trabalhador(self):
        uia = None
        while True:
            tipo, motivo, pos, quando = self.jobs.get()
            g = self.k.alvo()
            if g is None:
                continue
            try:
                if tipo == "uia":
                    if uia is None:
                        uia = olho.UIA()
                    d = uia.em(*pos)
                    if d:
                        self.emitir({"tipo": "sob_mouse", "motivo": motivo, "x": pos[0], "y": pos[1], **d}, quando)
                else:
                    self._print(g, motivo, pos, quando)
            except Exception as e:
                log("olho %s: %r" % (tipo, e))

    def _print(self, g, motivo, pos, quando):
        u = self.ult_print; agora = time.time()
        perto = u["pos"] is not None and abs(pos[0] - u["pos"][0]) + abs(pos[1] - u["pos"][1]) < 40
        if motivo == "fala" and (agora - u["t"] < 3.0 or (perto and agora - u["t"] < 8.0)):
            return
        im, mon = olho.print_nativo(*pos)
        mini = olho.miniatura(im)
        if perto and motivo != "traco" and olho.parecida(mini, u["mini"]):
            return                                      # mesma tela, cursor no mesmo lugar: nada novo (o desenho sempre vale)
        os.makedirs(os.path.join(g.pasta, "_prints"), exist_ok=True)
        base = rel = os.path.join("_prints", g._rotulo(quando, motivo)); i = 2
        while os.path.exists(os.path.join(g.pasta, rel + ".jpg")):
            rel = "%s_%d" % (base, i); i += 1
        olho.salvar_print(im, mon, pos[0], pos[1], os.path.join(g.pasta, rel))
        u.update(t=agora, pos=pos, mini=mini)
        self.emitir({"tipo": "print", "motivo": motivo, "x": pos[0], "y": pos[1], "arquivo": rel + ".jpg",
                     "perto": rel + "_perto.jpg", "monitor": list(mon)}, quando)


class Replay:
    """Os últimos 2 min de tela + voz + som do PC num disco rotativo (sessoes\\_replay), pra entrarem no começo da gravação.
    Tela e voz: ffmpeg em pedaços de 10 s; som do PC: o gravar_pc.py do CORRETOR em peças de 60 s com 2 s de sobra
    (cada segmento tem o t0 no relógio do PC). Pedaço com mais de ~2,5 min é apagado. Liga sozinho quando nada grava;
    para quando qualquer Kakashi começa a gravar. config.json "replay": false = desligado; "replay_s": 120 = quanto.
    P20 (21/10): o buffer ficou 3 h ligado e a voz virou silêncio digital sem erro nenhum (o receptor do microfone sem fio
    dormiu/reconectou). Agora a voz é vigiada: MUDO_S em silêncio digital → reabre SÓ o microfone (fala_<geração>_<n>.wav);
    a saída de som do PC trocada vai pro kakashi.log (quem troca o loopback é o gravar_pc.py, a cada 2 s)."""
    PECA_PC = 60.0
    MUDO_S, MUDO_MAX = 60.0, 600.0      # 1ª reabertura depois de 60 s mudo; mudo de novo, espera o dobro (até 10 min)
    MUDO_ATALHO_S = 10.0                # no atalho: a voz dos últimos 10 s em silêncio digital = replay_sem_voz

    def __init__(self):
        self.base = os.path.join(SESSOES, "_replay")
        self.trava = threading.RLock()
        self.procs, self.pecas, self.pasta, self.ini = [], [], None, None
        self.flog = None; self.falhou_em = 0.0
        self.proc_fala = None; self.geracao = 0; self.voz = {}; self.saida = None
        self._limpar_orfaos()

    def _limpar_orfaos(self):
        """P20: ffmpeg / gravar_pc.py de um buffer de ANTES (Kakashi morto sem parar o replay) ficavam vivos segurando o
        microfone e a tela — em 21/10 dois do teste do P3 rodaram 13 h (8,8 GB; o microfone deles travou às 06:39 e seguiu
        aberto). Só existe um Kakashi (mutex): o que escreve nesta pasta de buffer e não é filho meu é sobra."""
        try:
            import psutil
        except ImportError:
            return
        meu, base = os.getpid(), self.base.lower()
        for p in psutil.process_iter(["pid", "ppid", "cmdline"]):
            try:
                cl = " ".join(p.info["cmdline"] or []).lower()
                if base in cl and p.info["pid"] != meu and p.info["ppid"] != meu:
                    p.kill(); log("replay: processo de buffer antigo encerrado (pid %d): ...%s" % (p.info["pid"], cl[-70:]))
            except Exception:
                pass

    @staticmethod
    def ligado_no_config():
        return bool(cfg().get("replay", False))     # 02/11: sem a chave = desligado (só grava do atalho ao atalho)

    @staticmethod
    def segundos():
        return float(cfg().get("replay_s", 120))

    def rodando(self):
        return bool(self.procs)

    def info(self):
        return {"ligado_no_config": self.ligado_no_config(), "rodando": self.rodando(),
                "segundos_guardados": round(min(self.segundos(), time.time() - self.ini), 1) if self.procs and self.ini else 0}

    def ligar(self):
        with self.trava:
            if self.procs or not self.ligado_no_config() or time.time() - self.falhou_em < 30:
                return
            os.makedirs(self.base, exist_ok=True)
            for n in os.listdir(self.base):          # sobras de antes (Kakashi fechado no meio): nunca é sessão, só buffer
                d = os.path.join(self.base, n)
                if os.path.isdir(d) and time.time() - os.path.getmtime(d) > 600:
                    shutil.rmtree(d, ignore_errors=True)
            self.pasta = os.path.join(self.base, "%d" % (time.time() * 1000)); os.makedirs(self.pasta)
            self.ini = time.time()
            self.flog = open(os.path.join(self.pasta, "ffmpeg.log"), "ab")
            self._abrir(self.BASE + ENTRADA_TELA + ["-vf", "scale=1920:-2:flags=bilinear,format=yuv420p"] + olho.VIDEO_ENC +
                        ["-threads", "2"] + self.SEG + ["-segment_format", "mpegts", os.path.join(self.pasta, "tela_%05d.ts")])
            self.geracao = 0; self.saida = None
            self._abrir_fala()
            self._peca_pc()
            threading.Thread(target=self._zelador, args=(self.pasta,), daemon=True).start()
            # JUIZ 30/10: antes ligava calado sem microfone (03:06 o buffer subiu só com tela + som do PC e nada no log)
            log("replay ligado" + ("" if self.proc_fala is not None else " SEM microfone (nenhum dispositivo de captura encontrado: só tela + som do PC)"))

    BASE = [FFMPEG, "-hide_banner", "-nostats", "-loglevel", "warning"]
    SEG = ["-f", "segment", "-segment_time", "10", "-reset_timestamps", "1"]

    def _abrir(self, cmd):
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=self.flog, creationflags=SEM_JANELA)
            self.procs.append(p)
            return p
        except Exception as e:
            log("replay: %s" % e)

    def _abrir_fala(self):
        """o microfone do buffer: um ffmpeg por abertura (geração), pedaços fala_<geração>_<n>.wav de 10 s"""
        dev = microfone()
        self.proc_fala = None
        if dev:
            self.proc_fala = self._abrir(self.BASE + entrada_mic(dev) + ["-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le"] + self.SEG +
                                         ["-segment_format", "wav", os.path.join(self.pasta, "fala_%03d_%%05d.wav" % self.geracao)])
        agora = time.time()
        self.voz = {"ult_som": self.voz.get("ult_som", agora) if self.geracao else agora, "aberto": agora,
                    "espera": self.voz.get("espera", self.MUDO_S) if self.geracao else self.MUDO_S,
                    "reaberturas": self.voz.get("reaberturas", 0) if self.geracao else 0}

    def _fechar_fala(self, espera=2.0):
        """fecha o microfone do buffer e ESPERA ele soltar o aparelho (21/10 12:55: a captura nova aberta com o ffmpeg velho
        ainda segurando o microfone também veio zerada; a de 12:57, com tudo fechado, veio com som)"""
        p = self.proc_fala; self.proc_fala = None
        if p is None:
            return
        if p in self.procs:
            self.procs.remove(p)
        self._q(p)
        try:
            p.wait(timeout=espera)
        except subprocess.TimeoutExpired:
            p.kill()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                log("replay: o ffmpeg do microfone não fechou nem com kill")
        try:
            p.stdin.close()
        except Exception:
            pass

    def _falas(self, pasta):
        return sorted(glob.glob(os.path.join(pasta, "fala_*.wav")))

    def _vigiar_voz(self, pasta, agora):
        """P20: voz do buffer em silêncio digital há MUDO_S → reabre só o microfone. Ele calado também dá silêncio digital
        (o microfone sem fio corta pra zero nas pausas): mudo de novo, a próxima espera o dobro (60, 120, 240... até 600 s)."""
        if self.proc_fala is None or not self.voz:
            return
        v = self.voz
        p = olho.pico_fim(self._falas(pasta)[-2:], 2.5)
        if p is not None and p >= olho.MUDO:
            if v["reaberturas"]:
                log("replay: a voz voltou (%.0f s em silêncio digital, %d reabertura(s) do microfone)" % (agora - v["ult_som"], v["reaberturas"]))
            v.update(ult_som=agora, espera=self.MUDO_S, reaberturas=0)
            return
        if agora - max(v["ult_som"], v["aberto"]) < v["espera"]:
            return
        log("replay: voz em silêncio digital há %.0f s (pico < %d) — reabrindo o microfone (%dª vez)" %
            (agora - v["ult_som"], olho.MUDO, v["reaberturas"] + 1))
        self._fechar_fala()
        self.geracao += 1
        v["reaberturas"] += 1; v["espera"] = min(self.MUDO_MAX, v["espera"] * 2)
        self._abrir_fala()
        if self.proc_fala is None:
            log("replay: o microfone não reabriu (nenhum microfone encontrado)")

    def _vigiar_saida(self):
        """a saída de som do PC trocou (fone, monitor...): o gravar_pc.py já reabre o loopback na nova; aqui só vai pro log"""
        if not self.pecas:
            return
        try:
            m = json.load(open(os.path.join(self.pecas[-1][1], "pc01.json"), encoding="utf-8"))
            atual = (m.get("segmentos") or [{}])[-1].get("dispositivo")
        except (OSError, ValueError, IndexError, AttributeError):
            return
        if atual and atual != self.saida:
            if self.saida is not None:
                log("replay: som do PC agora de '%s' (era '%s')" % (atual, self.saida))
            self.saida = atual

    def _peca_pc(self):
        gp = os.path.join(CORRETOR, "gravar_pc.py")
        if not os.path.isfile(gp):
            return
        d = os.path.join(self.pasta, "pc_%d" % (time.time() * 1000)); os.makedirs(d)
        try:
            p = subprocess.Popen([PY, gp, "--pasta", d, "--parte", "1", "--inicio", "%.3f" % time.time()] + GRAVAR_PC_EXTRA, stdin=subprocess.PIPE,
                                 stdout=subprocess.DEVNULL, stderr=open(os.path.join(d, "som_pc.log"), "ab"), creationflags=SEM_JANELA)
            self.pecas.append([p, d, time.time()])
        except Exception as e:
            log("replay pc: %s" % e)

    @staticmethod
    def _q(p):
        try:
            p.stdin.write(b"q"); p.stdin.flush()
        except Exception:
            pass

    def _zelador(self, pasta):
        """troca a peça do som do PC a cada 60 s, apaga pedaço velho, religa se um ffmpeg morrer"""
        while True:
            time.sleep(2)
            with self.trava:
                if self.pasta != pasta:
                    return
                agora = time.time(); guardar = self.segundos() + 30
                if any(p.poll() is not None for p in self.procs):
                    log("replay: um ffmpeg parou sozinho; religando em 30 s")
                    self.falhou_em = agora; self._parar_procs(); shutil.rmtree(pasta, ignore_errors=True); return
                vivas = [x for x in self.pecas if x[0].poll() is None]
                if vivas and agora - vivas[-1][2] >= self.PECA_PC:
                    self._peca_pc()
                elif len(vivas) >= 2 and agora - vivas[-1][2] >= 2:
                    for x in vivas[:-1]:
                        self._q(x[0])
                for x in list(self.pecas):
                    if x[0].poll() is not None and agora - x[2] > self.PECA_PC + guardar:
                        shutil.rmtree(x[1], ignore_errors=True); self.pecas.remove(x)
                for padrao in ("tela_*.ts", "fala_*.wav"):
                    for f in sorted(glob.glob(os.path.join(pasta, padrao)))[:-2]:
                        try:
                            if agora - os.path.getmtime(f) > guardar:
                                os.remove(f)
                        except OSError:
                            pass
                try:
                    self._vigiar_voz(pasta, agora)
                    self._vigiar_saida()
                except Exception as e:
                    log("replay vigia: %r" % e)

    def _parar_procs(self):
        for p in self.procs + [x[0] for x in self.pecas]:
            self._q(p)
        procs = self.procs + [x[0] for x in self.pecas]
        self.procs, self.pecas = [], []
        return procs

    def parar(self):
        """para o buffer AGORA e devolve {fim, segundos, pasta, procs} (None se não estava rodando)"""
        with self.trava:
            if not self.procs:
                return None
            fim = time.time()
            info = {"fim": fim, "segundos": max(0.0, min(self.segundos(), fim - self.ini - 2.0)), "pasta": self.pasta}
            # P20: voz dos últimos ~10 s em silêncio digital = não confia no buffer: o microfone dele fecha JÁ (e solta o
            # aparelho) antes de a gravação abrir a captura nova; a sessão fica marcada com replay_sem_voz
            if self.proc_fala is not None:
                p10 = olho.pico_fim(self._falas(self.pasta)[-3:], self.MUDO_ATALHO_S)
                info["sem_voz"] = p10 is None or p10 < olho.MUDO
                info["voz_muda_s"] = round(fim - self.voz.get("ult_som", fim), 1) if info["sem_voz"] else 0.0
                if info["sem_voz"]:
                    p = self.proc_fala
                    self._fechar_fala(espera=0.0)        # kill na hora (o fim dele é silêncio mesmo); devolve no info["procs"]
                    self.procs.append(p)
            info["procs"] = self._parar_procs()
            self.pasta = None; self.proc_fala = None
            try:
                self.flog.close()
            except Exception:
                pass
            log("replay parado (%.0f s guardados)" % info["segundos"] +
                (" — voz dos últimos %.0f s em silêncio digital (mudo há %.0f s): microfone do buffer fechado antes da captura nova"
                 % (self.MUDO_ATALHO_S, info["voz_muda_s"]) if info.get("sem_voz") else ""))
            return info

    @staticmethod
    def _esperar(info):
        for p in info["procs"]:
            try:
                p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                p.kill()
            try:
                p.stdin.close()
            except Exception:
                pass

    def descartar(self, info):
        if info:
            self._esperar(info); shutil.rmtree(info["pasta"], ignore_errors=True)

    def extrair(self, info, g):
        """os últimos 'segundos' do buffer → replay_tela.mp4 / replay_fala.wav / replay_pc.wav na pasta da sessão"""
        out = {}
        try:
            self._esperar(info)
            R, fim, pasta = info["segundos"], info["fim"], info["pasta"]
            if R >= 1:
                alvo = lambda n: os.path.join(g.pasta, n)
                if olho.extrair_video_fim(sorted(glob.glob(os.path.join(pasta, "tela_*.ts"))), R, alvo("replay_tela.mp4"), log):
                    out["tela"] = alvo("replay_tela.mp4")
                if olho.extrair_fala_fim(self._falas(pasta), R, alvo("replay_fala.wav")):
                    out["fala"] = alvo("replay_fala.wav")
                if olho.extrair_pc(sorted(glob.glob(os.path.join(pasta, "pc_*", "pc01.json"))), fim - R, fim, alvo("replay_pc.wav")):
                    out["pc"] = alvo("replay_pc.wav")
            shutil.rmtree(pasta, ignore_errors=True)
        except Exception as e:
            log("replay extrair: %r" % e)
        g.replay_arqs = out
        g.replay_pronto.set()


# ---------- o controle (qual gravação está ligada, de quem) ----------
class Kakashi:
    def __init__(self):
        self.pc = None          # GravacaoPC
        self.fora = None        # "premiere" | "app_pessoal" quando fui eu que mandei gravar lá
        self.inicio = None
        self.ultima_voz = None
        self.aviso = ""
        self.quem_cache = None
        self.voz_viva = None    # P20: VozViva da gravação de agora (PC ou AppPessoal)
        self.mudo = 0.0
        self.trava = threading.Lock()
        self.troca_pedida = None  # troca PC → Premiere em andamento: {"g", "t", "janela"} (o painel ainda não começou)
        self.troca_pc = None      # a parte PC da correção que continuou no Premiere (pra cancelar junto)
        self.troca_desistiu = None  # a GravacaoPC em que o painel não começou: não tenta trocar de novo nela
        self.olho_prem = None       # 23/10: OlhoPremiere — o olho do PC dentro da sessão do painel enquanto ele grava
        # 3.0 (12/11): a escolha RÁPIDO × PROFUNDO depois de concluir (uma por correção, na ordem), o desenho e o pedido pro Chrome
        self.esc_trava = threading.Lock()
        self.escolhas = self._carregar_escolhas()
        self.esc_vistas = {os.path.normcase(p) for e in self.escolhas for p in e["pastas"]}
        self.ult_fora = None        # (quem, pasta) da gravação de fora (Premiere/app de cartões): concluiu lá = a escolha aparece igual
        self.prem_pedacos = []      # os pedaços do painel do Premiere (7815/status), pra barra
        self.desenho = None         # a Tela põe aqui o Desenho (só Windows)
        self.pedido_chrome = None   # {id, x, y, escala, t}: a extensão do Chrome descreve o elemento na ponta do traço
        self.n_pedido = 0
        self.vigia = Vigia(self)
        self.replay = Replay()
        threading.Thread(target=self._cuidar_replay, daemon=True).start()
        threading.Thread(target=self._vigiar_troca, daemon=True).start()
        threading.Thread(target=self._vigiar_olho_premiere, daemon=True).start()

    def alvo(self):
        """onde o olho escreve agora: a gravação do PC (tem prioridade, inclusive no ~1 s da troca) ou o olho do Premiere.
        03/11: PC pausado = o olho não guarda nada (nem print).
        04/11 (queda de luz no meio de uma correção do Premiere): Premiere pausado também não — o CORRETOR reabriu a sessão PAUSADA
        e o olho seguiu salvando print («2320_parou_*.jpg») enquanto nada gravava"""
        if self.pc is not None:
            return None if self.pc.pausado else self.pc
        o = self.olho_prem
        return o if o is not None and o.relogio[2] else None

    def pausar_continuar(self):
        """03/11: o PAUSAR/CONTINUAR do painel do Premiere, aqui no PC.
        04/11 (depois da queda de luz; ele: «o Kakashi é o Kakashi, é meu computador... não tem que entrar no Premiere para poder parar
        a pausa»): a gravação do Premiere também pausa/continua daqui — direto no CORRETOR, com ou sem o painel aberto. Sem o painel,
        a voz e a tela seguem (o CORRETOR grava) e o olho do PC registra o resto; a timeline volta quando o painel abrir."""
        g = self.pc
        if g is not None:
            return g.continuar() if g.pausado else g.pausar()
        st = http("http://127.0.0.1:7815/status", t=2)
        if st and st.get("estado") == "pausado":
            r = http("http://127.0.0.1:7815/retomar", {}, t=30) or {}
            log("Premiere: CONTINUAR pelo Kakashi → %s" % (r.get("estado") or r.get("erro") or r))
            return r.get("estado") == "gravando"
        if st and st.get("estado") == "gravando":
            r = http("http://127.0.0.1:7815/pausar", {}, t=30) or {}
            log("Premiere: PAUSAR pelo Kakashi → %s" % (r.get("estado") or r.get("erro") or r))
            return r.get("estado") == "pausado"
        return False

    def _vigiar_olho_premiere(self):
        """23/10 (ele: "faz o Kakashi ser o mais completo possível... É o olho de Deus, mano, é minha tela"): o painel do Premiere
        gravando (começou lá ou trocou do PC) → o olho do PC continua dentro da sessão dele (OlhoPremiere), no relógio da gravação
        do painel. O painel parou/terminou → o olho fecha na hora (antes de o painel juntar os pedaços)."""
        while True:
            time.sleep(0.25)
            try:
                if cfg().get("olho_premiere", True) is False:
                    if self.olho_prem is not None:
                        o = self.olho_prem; self.olho_prem = None; threading.Thread(target=o.concluir, daemon=True).start()
                    continue
                st = http("http://127.0.0.1:7815/status", t=1)
                if st is None:
                    continue
                est, pasta = st.get("estado"), st.get("pasta")
                o = self.olho_prem
                if est in ("gravando", "pausado") and pasta and os.path.isdir(pasta):
                    if o is not None and o.pasta_premiere != pasta:        # outra sessão: fecha a velha
                        self.olho_prem = None; threading.Thread(target=o.concluir, daemon=True).start(); o = None
                    if o is None:
                        self.olho_prem = o = OlhoPremiere(pasta, self, st.get("t_gravacao"), est == "gravando")
                        log("olho do Premiere: começou em %s (t_gravacao %.1f)" % (os.path.basename(pasta), st.get("t_gravacao") or 0))
                    o.sincronizar(st.get("t_gravacao"), est == "gravando")
                elif o is not None:
                    self.olho_prem = None
                    threading.Thread(target=o.concluir, daemon=True).start()
            except Exception as e:
                log("olho do Premiere: %r" % e)

    def estado(self):
        """quem está gravando agora (vale também se ele ligou pelo botão do AppPessoal ou do painel)"""
        if self.pc:
            self.quem_cache = "pc"
            return "pc", time.time() - self.pc.valendo()      # 03/11: o relógio do que VALE (pausa não conta)
        lu = http("http://127.0.0.1:7798/api/app_pessoal/gravacao", t=1)
        if lu and lu.get("gravando"):
            self.quem_cache = "app_pessoal"
            self.ult_fora = (self.quem_cache, lu.get("pasta"), None)        # 3.0: pra escolha, se ele concluir pelo botão de lá
            return "app_pessoal", time.time() - (lu.get("segundos") or 0)
        st = http("http://127.0.0.1:7815/status", t=1)
        if st and st.get("estado") in ("gravando", "pausado"):
            self.quem_cache = "premiere"
            self.prem_pausado = st.get("estado") == "pausado"      # 04/11: a janela dizia «GRAVANDO» com o painel pausado
            self.prem_painel_s = st.get("painel_visto_ha_s")
            self.prem_pedacos = st.get("pedacos") or []             # 3.0: os pedaços do painel na barra (clique = apagar/voltar)
            self.ult_fora = ("premiere", st.get("pasta"), self.troca_pc.pasta if self.troca_pc is not None else None)
            return "premiere", time.time() - (st.get("t_gravacao") or 0)
        self.quem_cache = None
        if st is not None:        # nada gravando (ele concluiu pelo botão do painel): a parte PC de uma troca não é mais "a atual"
            self.troca_pc = None; self.fora = None
        uf = self.ult_fora
        if uf is not None and ((st if uf[0] == "premiere" else lu) is not None):   # app fora do ar não é «concluiu»: espera voltar
            # 3.0: concluiu pelo botão do painel do Premiere ou do app de cartões (não pelo atalho): a barra pergunta igual, só não cola
            # (repetida = ignorada: o atalho já pediu a escolha dessa pasta; cancelada = a pasta já está nas vistas)
            self.ult_fora = None
            self._pedir_escolha(uf[0], [uf[1], uf[2]], False)
        return None, None

    def status(self):
        """GET 127.0.0.1:7816/status — o Claude confere aqui antes de reiniciar o Kakashi"""
        quem = "pc" if self.pc else self.quem_cache
        d = {"ok": True, "app": "kakashi", "porta": PORTA, "pid": os.getpid(), "estado": "gravando" if quem else "parado", "quem": quem,
             "replay": self.replay.info()}
        if self.pc:
            d.update(pasta=self.pc.pasta, t=round(time.time() - self.pc.t_grav, 1), replay_s=self.pc.replay_s,
                     pausado=self.pc.pausado, t_valendo=round(self.pc.valendo(), 1),
                     pedacos=[{k: p[k] for k in ("n", "ini", "dur", "apagado")} for p in self.pc.pedacos])
        if quem:
            d["mudo_s"] = round(self.mudo, 1)      # P20: segundos em silêncio digital (> 20 = o olho está cinza)
        if self.olho_prem is not None:             # 23/10: o olho do PC dentro da sessão do Premiere
            d["olho_premiere"] = self.olho_prem.pasta
        d["ferramenta"] = self.desenho.ferr if self.desenho is not None else "cursor"      # 3.0
        d["escolha_pendente"] = len(self.escolhas)
        pc_ = self.pedido_chrome
        if pc_ is not None and time.time() - pc_["t"] < 4:  # 3.0: a extensão descreve o elemento do Chrome debaixo da ponta do traço
            d["pedido_chrome"] = {c: pc_[c] for c in ("id", "x", "y", "escala")}
        return d

    # ---------- 3.0 (12/11/2026): RÁPIDO × PROFUNDO, escolhido por ELE na barra depois de concluir ----------
    ESCOLHAS = os.path.join(AQUI, "escolhas_pendentes.json")

    def _carregar_escolhas(self):
        """as escolhas que ficaram esperando quando o Kakashi fechou (pasta que ainda existe e ainda sem MODO.json)"""
        try:
            es = json.load(open(self.ESCOLHAS, encoding="utf-8"))
        except (OSError, ValueError):
            return []
        return [e for e in es if any(os.path.isdir(p) and not os.path.isfile(os.path.join(p, "MODO.json")) for p in e.get("pastas", []))]

    def _salvar_escolhas(self):
        try:
            with open(self.ESCOLHAS, "w", encoding="utf-8") as f:
                json.dump(self.escolhas, f, ensure_ascii=False, indent=1)
        except OSError as e:
            log("escolha: não salvei a lista: %r" % e)

    def _pedir_escolha(self, quem, pastas, colar):
        pastas = [p for p in pastas if p]
        if not pastas:
            return
        with self.esc_trava:
            if any(os.path.normcase(p) in self.esc_vistas for p in pastas):
                return
            self.esc_vistas.update(os.path.normcase(p) for p in pastas)
            self.escolhas.append({"quem": quem, "pastas": pastas, "colar": bool(colar), "t": round(time.time(), 2)})
            self._salvar_escolhas()
        log("escolha: %s %s esperando RÁPIDO ou PROFUNDO" % (quem, ", ".join(os.path.basename(p) for p in pastas)))

    def _nao_perguntar(self, *pastas):
        """cancelou: essas pastas nunca pedem escolha (vão pro _descartadas)"""
        with self.esc_trava:
            self.esc_vistas.update(os.path.normcase(p) for p in pastas if p)

    @staticmethod
    def _sumiu(p):
        """a pasta saiu do lugar (cancelada/descartada) ou está marcada descartada"""
        if not os.path.isdir(p):
            return True
        try:
            return bool(json.load(open(os.path.join(p, "sessao.json"), encoding="utf-8")).get("descartada"))
        except (OSError, ValueError):
            return False

    def escolha_atual(self):
        """a escolha da vez (a mais velha), já sem as que foram canceladas/descartadas por fora"""
        with self.esc_trava:
            antes = len(self.escolhas)
            self.escolhas = [e for e in self.escolhas if not all(self._sumiu(p) for p in e["pastas"])]
            if len(self.escolhas) != antes:
                self._salvar_escolhas()
            return dict(self.escolhas[0], fila=len(self.escolhas)) if self.escolhas else None

    def escolher(self, modo):
        """o clique em RÁPIDO ou PROFUNDO: MODO.json em cada pasta da correção e cola "/kakashi rápido|profundo" (o atalho cola onde está o
        cursor; no Premiere e quando ele concluiu pelo botão de lá, só copia)"""
        with self.esc_trava:
            if not self.escolhas:
                return
            e = self.escolhas.pop(0)
            self._salvar_escolhas()
        quando = datetime.datetime.now().replace(microsecond=0).isoformat()
        for p in e["pastas"]:
            if not os.path.isdir(p):
                log("escolha: %s saiu do lugar, sem MODO.json" % p); continue
            try:
                with open(os.path.join(p, "MODO.json"), "w", encoding="utf-8") as f:
                    json.dump({"modo": modo, "escolhido_em": quando, "quem": e["quem"], "pastas": e["pastas"]}, f, ensure_ascii=False, indent=1)
            except OSError as ex:
                log("escolha: MODO.json em %s: %r" % (p, ex))
        log("escolha: %s → %s" % (", ".join(os.path.basename(p) for p in e["pastas"]), modo.upper()))
        colar_kakashi(e["colar"], "/kakashi " + ("rápido" if modo == "rapido" else "profundo"))

    def descartar_escolha(self):
        """o X da escolha: a correção vai pro _descartadas (nunca apaga); espera o Kakashi/painel terminar de juntar os arquivos"""
        with self.esc_trava:
            if not self.escolhas:
                return
            e = self.escolhas.pop(0)
            self._salvar_escolhas()
        for p in e["pastas"]:
            for _ in range(360):                    # até 3 min: o concluir (juntar pedaços, links do Chrome) ainda pode estar rodando
                st = http("http://127.0.0.1:7815/status", t=1) or {}
                try:
                    sj = os.path.join(p, "sessao.json")
                    m = json.load(open(sj, encoding="utf-8"))
                    # PC: o "links" é a última coisa que o concluir grava (depois dos 12 s do histórico do Chrome); painel/app de
                    # cartões: a duração gravada e o sessao.json parado há 15 s (teste_modo 12/11: mover antes quebrava o concluir)
                    pronta = "links" in m or (("duracao_s" in m or "t_gravado" in m) and time.time() - os.path.getmtime(sj) > 15)
                except (OSError, ValueError):
                    pronta = False
                if not os.path.isdir(p) or (pronta and not st.get("finalizando")):
                    break
                time.sleep(0.5)
            if os.path.isdir(p):
                ok = descartar({"pasta": p, "base": os.path.dirname(p)})
                log("escolha: DESCARTOU %s (%s)" % (p, "foi pro _descartadas" if ok else "NÃO moveu"))

    def alternar_pedaco(self, n):
        """3.0: o clique num pedaço da barra = apaga ou volta (PC aqui; Premiere no painel, POST /apagar_pedaco | /voltar_pedaco).
        O que está gravando não: pausa antes."""
        if self.pc is not None:
            return self.pc.alternar_pedaco(n)
        st = http("http://127.0.0.1:7815/status", t=2) or {}
        p = next((x for x in st.get("pedacos") or [] if x.get("n") == n), None)
        if p is None or p.get("gravando"):
            return False
        r = http("http://127.0.0.1:7815/%s" % ("voltar_pedaco" if p.get("apagado") else "apagar_pedaco"), {"n": n}, t=30) or {}
        log("Premiere: pedaço %d %s pela barra → %s" % (n, "VOLTAR" if p.get("apagado") else "APAGAR", r.get("erro") or "ok"))
        self.prem_pedacos = r.get("pedacos") or self.prem_pedacos
        return not r.get("erro")

    def desenhando(self):
        """uma ferramenta de desenho escolhida (o mouse está no pegador do Desenho, não no app de baixo)"""
        d = self.desenho
        return d is not None and d.ferr != "cursor"

    def pedir_chrome(self, x, y):
        self.n_pedido += 1
        self.pedido_chrome = {"id": self.n_pedido, "x": int(x), "y": int(y), "escala": ESC, "t": time.time()}
        return self.n_pedido

    def _cuidar_replay(self):
        """buffer ligado só quando NADA grava (o painel do Premiere e o AppPessoal gravam por conta própria)"""
        time.sleep(5)
        while True:
            try:
                with self.trava:
                    quem = "pc" if self.pc else self.quem_cache
                    if quem is None and not self.replay.rodando():
                        self.replay.ligar()
                    elif quem in ("app_pessoal", "premiere") and self.replay.rodando():
                        info = self.replay.parar()
                        threading.Thread(target=self.replay.descartar, args=(info,), daemon=True).start()
                    elif quem is None and self.replay.rodando() and not self.replay.ligado_no_config():
                        info = self.replay.parar()
                        threading.Thread(target=self.replay.descartar, args=(info,), daemon=True).start()
            except Exception as e:
                log("cuidar replay: %r" % e)
            time.sleep(2)

    TROCA_S = 1.5             # o Premiere tem que ficar na frente esse tempo seguido (alt+tab de passagem não troca)
    TROCA_ESPERA_S = 15.0     # o painel pega o "iniciar" no próximo GET /comando; sem começar até aqui = painel morto, segue PC

    def _vigiar_troca(self):
        """23/10 (ele: "Sim, óbvio"): gravando como PC e ele entra no Premiere → troca sozinho pro modo Premiere (o rastro da
        timeline só vem de lá). Primeiro o painel começa; só com ele GRAVANDO a parte PC fecha (sem buraco de voz: ~1 s gravado
        nos dois). Não volta pro PC quando ele sai do Premiere: a sessão do Premiere grava a tela inteira e a voz do mesmo jeito,
        e o OlhoPremiere (_vigiar_olho_premiere) segue com mouse/elemento/prints/cópias dentro de <sessão>\\_olho."""
        frente_desde = None
        while True:
            time.sleep(0.3)
            try:
                g = self.pc
                if g is None or g.pausado:           # 03/11: pausado não troca pro Premiere
                    frente_desde = None; continue
                pedida = self.troca_pedida
                if pedida is not None:                        # já pedi: espera o painel começar
                    st = http("http://127.0.0.1:7815/status", t=1)
                    with self.trava:
                        if self.pc is not g or self.troca_pedida is not pedida:
                            continue
                        if st and st.get("estado") == "gravando":
                            self._fechar_parte_pc(g, pedida)
                        elif time.time() - pedida["t"] > self.TROCA_ESPERA_S:
                            self.troca_pedida = None; self.troca_desistiu = g     # nesta gravação não tenta de novo (não enche a fila do painel)
                            log("troca: o painel do Premiere não começou em %.0f s; segue gravando como PC" % self.TROCA_ESPERA_S)
                            g._evento({"tipo": "troca_falhou", "para": "premiere"})
                            threading.Thread(target=self._cancelar_troca_atrasada, args=(pedida["t"],), daemon=True).start()
                    continue
                if self.troca_desistiu is g:
                    continue
                j = janela_frente()
                if "premiere" not in j["app"].lower():
                    frente_desde = None; continue
                agora = time.time()
                frente_desde = frente_desde or agora
                if agora - frente_desde < self.TROCA_S or cfg().get("troca_premiere", True) is False:
                    continue
                st = http("http://127.0.0.1:7815/status", t=1)
                if not (st and st.get("painel_visto_ha_s") is not None and st["painel_visto_ha_s"] < 10 and st.get("estado") == "parado"):
                    continue
                with self.trava:
                    if self.pc is not g or self.troca_pedida is not None:
                        continue
                    r = http("http://127.0.0.1:7815/comando", {"acao": "iniciar"})
                    if not (r and r.get("ok")):
                        log("troca: o Premiere não aceitou o iniciar (%r)" % (r,)); frente_desde = None; continue
                    self.troca_pedida = {"g": g, "t": time.time(), "janela": j}
                    log("troca: Premiere na frente %.1f s → pedi o iniciar ao painel (%s)" % (self.TROCA_S, j["titulo"][:60]))
                frente_desde = None
            except Exception as e:
                log("troca: %r" % e)

    def _fechar_parte_pc(self, g, pedida):
        """(com a trava) o Premiere já está gravando: a parte PC fecha e fica marcada como o começo da mesma correção"""
        t = time.time()
        self.troca_pedida = None
        self.pc = None; self.inicio = None
        self.fora = "premiere"; self.quem_cache = "premiere"; self.troca_pc = g
        vv = self.voz_viva
        if vv is not None and vv.arq == g.fala_wav():
            tr = vv.trechos_mudos(g.t0, t)
            if tr:
                g.meta["voz_muda"] = tr
        g.meta.update(continua_em="premiere", troca_epoch=round(t, 2), troca_s=round(t - g.t0, 2),
                      troca_janela=pedida["janela"], troca_pedida_epoch=round(pedida["t"], 2))
        g._evento({"tipo": "troca", "para": "premiere", **pedida["janela"]}, t)
        threading.Thread(target=g.concluir, args=(False,), daemon=True).start()
        log("troca: PC → Premiere em %.1f s da sessão (%s)" % (t - g.t0, g.pasta))

    def _descartar_parte_pc(self, g):
        """cancelou depois da troca: a parte PC (já concluída ou concluindo) vai junto pro _descartadas"""
        g.concluida.wait(60)
        ok = descartar({"pasta": g.pasta, "base": SESSOES})
        log("troca: parte PC %s %s" % (g.pasta, "descartada junto" if ok else "NÃO foi pro _descartadas"))

    def _cancelar_troca_atrasada(self, t0):
        """concluiu a PC com o "iniciar" ainda na fila do painel: se o Premiere começar mesmo assim, cancela essa sobra"""
        while time.time() - t0 < self.TROCA_ESPERA_S + 5:
            st = http("http://127.0.0.1:7815/status", t=1)
            if st and st.get("estado") == "gravando":
                http("http://127.0.0.1:7815/cancelar", {}); log("troca: o Premiere começou depois do fim da PC → cancelei essa sobra")
                return
            time.sleep(0.5)

    def alternar(self, cancelar=False):
        with self.trava:
            self._alternar(cancelar)

    def _alternar(self, cancelar=False):
        quem, _ = self.estado()
        if quem == "pc":
            g = self.pc; self.pc = None; self.inicio = None; self.quem_cache = None
            if self.troca_pedida is not None:         # apertou o atalho no meio da troca: a PC é a correção inteira
                threading.Thread(target=self._cancelar_troca_atrasada, args=(self.troca_pedida["t"],), daemon=True).start()
                self.troca_pedida = None
            vv = self.voz_viva
            if vv is not None and vv.arq == g.fala_wav():
                tr = vv.trechos_mudos(g.t0, time.time())
                if tr:
                    g.meta["voz_muda"] = tr        # P20: trechos em silêncio digital > 20 s (relógio da sessão)
            threading.Thread(target=g.concluir, args=(cancelar,), daemon=True).start()
            # 3.0 (12/11): concluiu = a barra pergunta RÁPIDO ou PROFUNDO; o clique cola "/kakashi rápido|profundo" (era colar na hora)
            if cancelar or all(p["apagado"] for p in g.pedacos):        # tudo apagado = vai pro _descartadas sozinha
                self._nao_perguntar(g.pasta)
            else:
                self._pedir_escolha("pc", [g.pasta], True)
            return
        if quem == "app_pessoal":
            uf, self.ult_fora = self.ult_fora, None
            if cancelar:      # 03/11 (revisão do AppPessoal, task «cancelar do Kakashi»): cancelar mandava «concluir»; agora vai pro _descartadas
                self._nao_perguntar(uf[1] if uf else None)
                http("http://127.0.0.1:7798/api/app_pessoal/gravacao", {"acao": "descartar", "motivo": "cancelada pelo atalho (Ctrl+Shift+Page Down)"}, t=20)
                self.fora = None; return
            http("http://127.0.0.1:7798/api/app_pessoal/gravacao", {"acao": "concluir"}, t=20); self.fora = None
            self._pedir_escolha(quem, [uf[1] if uf else None], True); return
        if quem == "premiere":
            uf, self.ult_fora = self.ult_fora, None
            if cancelar:
                self._nao_perguntar(*(uf[1:] if uf else ()))
                http("http://127.0.0.1:7815/cancelar", {})
                if self.troca_pc is not None:        # começou como PC e trocou: as duas partes são uma correção só
                    threading.Thread(target=self._descartar_parte_pc, args=(self.troca_pc,), daemon=True).start()
            else:
                self._pedir_escolha("premiere", list(uf[1:]) if uf else [], False)     # no Premiere só copia (Ctrl+V lá cola clipe)
                # 04/11 (queda de luz): o PC voltou com a sessão PAUSADA e o Premiere fechado; cada aperto virava um «concluir» na fila
                # do painel, que não estava lá (8 na fila). Agora: aperto repetido em 15 s não conta, e sem o painel (nada há 5 s) o
                # próprio CORRETOR conclui.
                if time.time() - getattr(self, "ult_concluir_prem", 0) < 15:
                    log("atalho: concluir do Premiere repetido em menos de 15 s, ignorado")
                    self.fora = None; self.troca_pc = None; return
                self.ult_concluir_prem = time.time()
                visto = getattr(self, "prem_painel_s", None)
                if visto is None or visto > 5:
                    def _direto():
                        r = http("http://127.0.0.1:7815/concluir", {}, t=300) or {}
                        log("atalho: painel do Premiere fechado, o CORRETOR concluiu direto: %s" % (r.get("sessao") or r.get("erro") or r))
                    threading.Thread(target=_direto, daemon=True).start()
                else:
                    http("http://127.0.0.1:7815/comando", {"acao": "concluir"})
            self.fora = None; self.troca_pc = None; return
        if cancelar:
            return
        tipo, j = tipo_da_frente()
        log("começar: %s (%s · %s)" % (tipo, j["app"], j["titulo"][:60]))
        self.ultima_voz = time.time()
        info = self.replay.parar()            # o buffer solta o microfone/tela antes de a gravação abrir
        if tipo == "premiere":
            threading.Thread(target=self.replay.descartar, args=(info,), daemon=True).start()
            http("http://127.0.0.1:7815/comando", {"acao": "iniciar"}); self.fora = "premiere"; self.quem_cache = "premiere"
        elif tipo == "app_pessoal":
            threading.Thread(target=self.replay.descartar, args=(info,), daemon=True).start()
            http("http://127.0.0.1:7798/api/app_pessoal/gravacao", {"acao": "iniciar"}, t=20); self.fora = "app_pessoal"; self.quem_cache = "app_pessoal"
        else:
            g = GravacaoPC(j, self, info)
            self.pc = g; self.inicio = g.t_grav; self.quem_cache = "pc"
            if info:
                threading.Thread(target=self.replay.extrair, args=(info, g), daemon=True).start()

    def medir_voz(self):
        """1x/s (o olho chama): (voz_recente, segundos em silêncio digital). Só dá pra medir na gravação própria e na do AppPessoal."""
        g = self.pc; arq = None
        if g and g.pausado:                         # 03/11: pausado não é «sem som»
            self.voz_viva = None; self.mudo = 0.0; self.ultima_voz = time.time()
            return True, 0.0
        if g:
            arq, ini, pc, quem = g.fala_wav(), g.pedacos[-1]["epoch"], True, "pc"
        else:
            lu = http("http://127.0.0.1:7798/api/app_pessoal/gravacao", t=1)
            if lu and lu.get("gravando") and lu.get("pasta"):
                arq, ini, pc, quem = os.path.join(lu["pasta"], "fala.wav"), time.time(), False, "app_pessoal"
        if not arq:
            self.voz_viva = None; self.mudo = 0.0
            return True, 0.0
        if self.voz_viva is None or self.voz_viva.arq != arq:
            self.voz_viva = VozViva(arq, ini, faltando_e_mudo=pc, quem=quem)
        self.mudo = self.voz_viva.medir(time.time())
        return self.voz_recente(arq), self.mudo

    def voz_recente(self, arq):
        """10 min sem voz no microfone → aviso.
        Voz = os últimos 5 s bem acima do mais baixo que ESTA gravação já esteve (o piso): 3× o piso, entre 15 e 60 de RMS
        (~ -67 a -55 dBFS). 04/11: era um número fixo, 400 (~ -38 dBFS), da época (19/10) em que o microfone sem fio dava ~2000;
        em 04/11 a mesma voz dava 20–270 e o anel amarelo piscou com ele falando (Kakashi 16:15 [10:15] «por que tá piscando isso
        aqui?»). Conferido nas 46 gravações de 01–04/11: o maior trecho «sem voz» caiu de 612 s pra 137 s; silêncio digital e
        ruído de sala (30–45) por 12 min ainda avisam. O microfone sem fio corta pra zero nas pausas, então o piso dele é ~0."""
        if not arq or not os.path.isfile(arq):
            return True
        try:
            tam = os.path.getsize(arq)
            with open(arq, "rb") as f:
                f.seek(max(44, tam - 48000 * 2 * 5)); b = f.read()
            a = array.array("h"); a.frombytes(b[: len(b) // 2 * 2])
            if a:
                rms = (sum(x * x for x in a[::8]) / len(a[::8])) ** 0.5
                if getattr(self, "voz_piso_arq", None) != arq:
                    self.voz_piso_arq, self.voz_piso = arq, rms
                self.voz_piso = min(self.voz_piso, rms)
                if rms > max(15.0, min(self.voz_piso * 3, 60.0)):
                    self.ultima_voz = time.time()
        except Exception:
            return True
        return time.time() - (self.ultima_voz or time.time()) < 600


# ---------- porta 7816 (status + o card do AppPessoal sob o mouse) ----------
ORIGENS = {"http://localhost:7798", "http://127.0.0.1:7798"}


def servidor(k):
    class H(BaseHTTPRequestHandler):
        def _cab(self, cod, n=0):
            self.send_response(cod)
            o = self.headers.get("Origin")
            if o in ORIGENS:                     # só o AppPessoal (outro site aberto no Chrome não lê nem escreve aqui)
                self.send_header("Access-Control-Allow-Origin", o)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(n))

        def _json(self, cod, obj):
            b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self._cab(cod, len(b)); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
            self.wfile.write(b)

        def do_OPTIONS(self):
            self._cab(204); self.end_headers()

        def do_GET(self):
            if self.path.split("?")[0] == "/status":
                return self._json(200, k.status())
            self._json(404, {"ok": False})

        def do_POST(self):
            if self.path.split("?")[0] == "/chrome":
                return self._chrome()
            if self.path.split("?")[0] != "/app_pessoal":
                return self._json(404, {"ok": False})
            o = self.headers.get("Origin")
            if o and o not in ORIGENS:
                return self._json(403, {"ok": False})
            try:
                d = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 20000)).decode("utf-8") or "{}")
            except ValueError:
                return self._json(400, {"ok": False})
            if k.pc is None:
                return self._json(200, {"ok": False, "motivo": "o Kakashi do PC não está gravando"})
            ev = {"tipo": "app_pessoal", "acao": str(d.get("acao") or "")[:20]}
            for c in ("id", "k", "titulo", "aba", "url"):
                if d.get(c) not in (None, ""):
                    ev[c] = str(d[c])[:200]
            for c in ("sx", "sy"):
                if isinstance(d.get(c), (int, float)):
                    ev[c] = int(d[c])
            k.vigia.emitir(ev)
            self._json(200, {"ok": True})

        def _chrome(self):
            """04/11 (ele: «colocasse o mouse do Kakashi nas coisas do PC, do Chrome, pelo código... pelo código fonte, pra saber o
            elemento»): a extensão chrome\\ manda o elemento da página debaixo do mouse (tag, seletor, texto, link, imagem e, em app
            local, componente + arquivo:linha) na pausa e no clique. Só a extensão (origem chrome-extension://) escreve aqui."""
            o = self.headers.get("Origin") or ""
            if o and not o.startswith("chrome-extension://"):
                return self._json(403, {"ok": False})
            try:
                d = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 40000)).decode("utf-8") or "{}")
            except ValueError:
                return self._json(400, {"ok": False})
            if k.alvo() is None:
                return self._json(200, {"ok": False, "motivo": "o Kakashi não está gravando"})
            ev = {"tipo": "chrome", "motivo": str(d.get("motivo") or "")[:20]}
            for c, n in (("url", 500), ("titulo", 120), ("tag", 30), ("id", 120), ("classes", 160), ("html", 300), ("seletor", 300),
                         ("texto", 200), ("texto_pai", 160), ("rotulo", 120), ("papel", 40), ("link", 500), ("imagem", 400)):
                if d.get(c) not in (None, ""):
                    ev[c] = str(d[c])[:n]
            for c in ("cx", "cy", "sx", "sy", "aba", "frame"):
                if isinstance(d.get(c), (int, float)):
                    ev[c] = int(d[c])
            if isinstance(d.get("ret"), list):
                ev["ret"] = [int(v) for v in d["ret"][:4] if isinstance(v, (int, float))]
            if isinstance(d.get("dpr"), (int, float)):
                ev["dpr"] = round(float(d["dpr"]), 2)
            if d.get("topo") is False:
                ev["iframe"] = True
            if d.get("senha"):
                ev["senha"] = True
            if isinstance(d.get("pedido"), int):       # 3.0: a resposta ao pedido_chrome = o elemento na ponta do traço
                ev["pedido"] = d["pedido"]
                pc_ = k.pedido_chrome
                if pc_ is not None and pc_["id"] == d["pedido"]:
                    k.pedido_chrome = None
            f = d.get("fonte")
            if isinstance(f, dict):
                ev["fonte"] = {"framework": str(f.get("framework") or "")[:20], "arquivo": str(f.get("arquivo") or "")[:300],
                               "componentes": [str(x)[:60] for x in (f.get("componentes") or [])[:5]]}
                if isinstance(f.get("marcas"), dict):
                    ev["fonte"]["marcas"] = {str(a)[:40]: str(b)[:160] for a, b in list(f["marcas"].items())[:6]}
            k.vigia.emitir(ev)
            self._json(200, {"ok": True})

        def log_message(self, *a):
            pass

    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORTA), H)
    except OSError as e:
        log("porta %d ocupada: %s" % (PORTA, e)); return
    srv.daemon_threads = True
    log("porta %d no ar" % PORTA)
    srv.serve_forever()


# ---------- atalho global ----------
MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_NOREPEAT = 0x1, 0x2, 0x4, 0x4000
WM_HOTKEY = 0x0312


def thread_atalhos_mac(fila):
    """Mac: o mesmo config.json e as mesmas regras do atalho.py, ouvidos por um CGEventTap (mac.Atalho)"""
    def registrar():
        a = atalho.do_config(cfg()); g, c = a["gravar"], a["cancelar"]
        ok = mac.ATALHO.registrar(g, c)
        if a["erro"]:
            fila.put(("erro", a["erro"]))
        if not ok:
            fila.put(("erro", "%s não existe no teclado do Mac: troque na janelinha do KAKASHI (TROCAR O ATALHO)" % g["nome"]))
        log("atalhos (Mac): %s=%s %s" % (g["nome"], ok, c["nome"] if c else "-"))
        atalho.ATIVO = a if ok else None

    mac.ATALHO = mac.Atalho(lambda acao: fila.put((acao, None)), lambda msg: (log("atalho: " + msg), fila.put(("erro", msg))))
    atalho.RECARREGAR_MAC = registrar
    registrar()
    mac.ATALHO.rodar()


def thread_atalhos(fila):
    """pacote da Fly (27/10): o atalho sai do config.json ("atalho" / "atalho_cancelar"; padrão Ctrl+Page Down, o do Luan) e
    a janelinha troca sem reiniciar: ela manda WM_RECARREGAR (registrar de novo) ou WM_SOLTAR (enquanto a pessoa aperta o novo)."""
    msg = wt.MSG()
    user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)        # cria a fila de mensagens desta thread antes de alguém postar
    atalho.THREAD_ID = kernel32.GetCurrentThreadId()

    def registrar():
        user32.UnregisterHotKey(None, 1); user32.UnregisterHotKey(None, 2)
        a = atalho.do_config(cfg()); g, c = a["gravar"], a["cancelar"]
        ok1 = bool(user32.RegisterHotKey(None, 1, g["mods"] | MOD_NOREPEAT, g["vk"]))
        ok2 = bool(c and user32.RegisterHotKey(None, 2, c["mods"] | MOD_NOREPEAT, c["vk"]))
        if a["erro"]:
            fila.put(("erro", a["erro"]))
        if not ok1:
            fila.put(("erro", "%s já é de outro programa: troque na janelinha do KAKASHI (TROCAR O ATALHO)" % g["nome"]))
        log("atalhos: %s=%s %s=%s" % (g["nome"], ok1, c["nome"] if c else "-", ok2))
        atalho.ATIVO = a if ok1 else None

    registrar()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == WM_HOTKEY:
            fila.put(("cancelar" if msg.wParam == 2 else "alternar", None))
        elif msg.message == atalho.WM_RECARREGAR:
            registrar()
        elif msg.message == atalho.WM_SOLTAR:
            user32.UnregisterHotKey(None, 1); user32.UnregisterHotKey(None, 2)


# ---------- o Sharingan ----------
TRANSP = "#010203"
try:
    ESC = user32.GetDpiForSystem() / 96.0 if not MAC else 1.0      # tela 4K com zoom do Windows: tudo cresce junto (o Mac já escala)
except Exception:
    ESC = 1.0
# o olho é o do painel do Premiere: arte de 40x40 ampliada 4x nos PNGs (160) → aqui 1 bloco = 1 px (40), ou 2 px (80) no config "olho": 80
ICONES = os.path.join(CORRETOR, "painel", "icones")
OLHO = int(cfg().get("olho", 40))
def _tamanho_barra():
    """3.0: o tamanho da barra acompanha a tela: 1 = 1080p a 100%; a 4K dele sem zoom do Windows (2160 lógicos) = 1,5"""
    # 12/11 15:52 (ele, vendo o teste na tela: «abriu aqui na minha tela e ta muito grande cara»): era 1,5× na 4K; agora o tamanho
    # dos outros apps dele (100%), e config.json "barra_escala" (ex.: 0.85) ajusta sem mexer no código
    try:
        esc = float(cfg().get("barra_escala", 1.0))
    except (TypeError, ValueError):
        esc = 1.0
    return ESC * max(0.6, min(esc, 2.0))


# KAKASHI 3.0 (12/11/2026) — a BARRA no meio da tela no lugar do olho do canto. Ele (chat): «em vez de ter aquela caixinha com pausar
# e tudo mais, seria maneiro ter uma... barrinha no meio, que você mexe nela... você apaga os fragmentos que você não quer».
F = _tamanho_barra()
# 12/11 16h (ele, no preview das 3 roupagens: «eu prefiro grafite» · «tira esse ícone de raio e lupa» · «tira esse olho do lado do como eu
# leio» · «substitui a bolinha vermelha de rec pelo olho do Kakashi girando... quando ele tiver pausado... o olho com sangue» · «faltou
# uma ferramenta de linha... um marca-texto ficaria maneiro também, igual tem no Lightshot») → GRAFITE (pins 331436853846619762 e
# 593771532153725227): corpo grafite de cantos redondos, botões redondos, a ferramenta escolhida num círculo branco, pedaços e a
# escolha em controle segmentado, «Concluir» em pílula branca.
BH = int(32 * F)                    # altura da barra
CEL = int(28 * F)                   # largura de cada botão de ícone
MARGEM = max(3, int(4 * F))         # o respiro em cima/embaixo dos botões
COR = {"fundo": "#1C1C1E", "borda": "#2C2C2E", "hover": "#2C2C2E", "ativo": "#3A3A3C", "seg": "#2C2C2E", "seg_sel": "#48484A",
       "texto": "#FFFFFF", "texto2": "#8E8E93", "texto3": "#5A5A5E", "vermelho": "#FF453A", "amarelo": "#FFD60A",
       "preto": "#000000"}          # grafite (iOS escuro)
FONTE = "Inter"                     # a da UI V2 do Flynder (instalada); sem ela, a do sistema
ICONE = {"cursor": "", "caneta": "", "seta": "", "linha": "", "caixa": "", "marca": "",
         "laser": "", "desfazer": "", "limpar": "", "pausa": "", "play": "", "cancelar": ""}
ICONE_TXT = {"cursor": "↖", "caneta": "✎", "seta": "↑", "linha": "／", "caixa": "▢", "marca": "▮", "laser": "●", "desfazer": "↶",
             "limpar": "⌫", "pausa": "❚❚", "play": "▶", "cancelar": "✕"}     # sem a fonte de ícones (Mac, Windows 10)
CORES_DESENHO = (("vermelho", "#ff3b5c"), ("amarelo", "#ffd60a"), ("verde", "#30d158"), ("azul", "#0a84ff"))   # as do bug reporter do Rolf
FERRAMENTAS = (("cursor", "Cursor: mexe no app"), ("caneta", "Caneta"), ("marca", "Marca-texto"), ("linha", "Linha"), ("seta", "Seta"),
               ("caixa", "Quadrado"), ("laser", "Laser: some sozinho"))
LASER_S = 1.1                       # o rastro do laser some em 1,1 s (o número do Rolf)


def _estilo_ex(win, mais=0, menos=0):
    """liga/desliga bits do estilo estendido da janela de topo de um Toplevel do Tk (Windows). Devolve o HWND."""
    try:
        win.update_idletasks()
        hw = user32.GetParent(win.winfo_id()) or win.winfo_id()
        est = user32.GetWindowLongW(hw, -20)
        user32.SetWindowLongW(hw, -20, (est | mais) & ~menos)
        return hw
    except Exception as e:
        log("estilo da janela: %r" % e)
        return None


def desenhar_trilho(cv, x, y, w, h, ps, sel):
    """os pedaços da gravação do PC (o da janelinha e o de cima do olho): vermelho = vale, vazado = apagado, vivo = gravando,
    contorno amarelo = selecionado. Devolve [(x0, x1, pedaço)] pro clique."""
    cv.create_rectangle(x, y, x + w, y + h, fill="#121217", outline="")
    blocos = []
    if not ps:
        return blocos
    agora = time.time()
    durs = [p["dur"] if p["dur"] is not None else max(0.5, agora - p["epoch"]) for p in ps]
    tot = sum(durs) or 1; xx = x + 2; livre = w - 4 - 3 * (len(ps) - 1)
    for p, d in zip(ps, durs):
        bw = max(6, int(livre * d / tot)); x1 = min(x + w - 2, xx + bw)
        if p["apagado"]:
            cv.create_rectangle(xx, y + 4, x1, y + h - 4, fill="#1a1a20", outline="#3a3a44")
        else:
            cv.create_rectangle(xx, y + 4, x1, y + h - 4, fill="#ff1e2e" if p["dur"] is None else "#d6001c", outline="")
        if sel == p["n"]:
            cv.create_rectangle(xx - 1, y + 2, x1 + 1, y + h - 2, outline="#FFE600", width=2)
        blocos.append((xx, x1, p)); xx = x1 + 3
    return blocos


def botao_8bits(cv, x0, y0, x1, y1, fundo, claro, escuro):
    """a borda com relevo do painel (claro em cima/esquerda, escuro embaixo/direita), desenhada num canvas"""
    cv.create_rectangle(x0, y0, x1, y1, fill=fundo, outline="")
    cv.create_rectangle(x0, y0, x1, y0 + 3, fill=claro, outline=""); cv.create_rectangle(x0, y0, x0 + 3, y1, fill=claro, outline="")
    cv.create_rectangle(x0, y1 - 3, x1, y1, fill=escuro, outline=""); cv.create_rectangle(x1 - 3, y0, x1, y1, fill=escuro, outline="")


def olho_cinza_pil(arq, k):
    """P20: o quadro do olho em CINZA (mesmo tamanho do subsample(k) do Tk: pega 1 pixel a cada k). Transparência mantida."""
    from PIL import Image, ImageEnhance
    im = Image.open(arq).convert("RGBA")
    im = im.resize((max(1, -(-im.width // k)), max(1, -(-im.height // k))), Image.NEAREST)
    a = im.getchannel("A")
    g = ImageEnhance.Brightness(im.convert("L")).enhance(0.85).convert("RGBA")
    g.putalpha(a)
    return g


def olho_cinza(arq, k, master):
    from PIL import ImageTk
    return ImageTk.PhotoImage(olho_cinza_pil(arq, k), master=master)


class Desenho:
    """KAKASHI 3.0 (12/11/2026) — desenhar POR CIMA DE QUALQUER APP enquanto grava: caneta, seta, caixa e laser, 4 cores, desfazer e
    limpar (a ideia e os números vêm do bug reporter do Fly Studio que o Rolf mandou em 12/11; lá é só dentro do site, aqui é a tela).
    Ele (chat 12/11): «é só desenho na tela e o próprio código fonte lá, de onde eu passo o mouse... já resolveria».
    Duas janelas do tamanho do monitor:
      tinta   = onde o desenho aparece. Cor-chave transparente e o clique SEMPRE passa (WS_EX_LAYERED|WS_EX_TRANSPARENT). Entra no
                tela.mp4 (o gdigrab copia janela layered) e no print nativo.
      pegador = quase invisível (alpha ~1%); só aparece com uma ferramenta de desenho escolhida — é ele que recebe o mouse.
                Botão direito nele = volta pro cursor.
    Cada traço vira o evento «traco» (ferramenta, cor, caixa, ponta, pontos com o tempo, e o elemento do app DEBAIXO da ponta pela
    UIA) + um print logo depois; no Chrome, a extensão descreve o elemento pelo código (Kakashi.pedido_chrome). O laser vira evento
    quando para de mexer (0,6 s). Desfazer não apaga o evento (o traço apareceu no vídeo): vira «traco_desfeito». Só Windows."""

    def __init__(self, tela):
        self.tela, self.k = tela, tela.k
        root = tela.root
        self.ferr, self.cor = "cursor", 0
        self.tracos = []            # {n, ferr, cor, pts: [(x, y, t)], itens: [ids do canvas]}
        self.atual = None
        self.laser, self.laser_seg, self.laser_mexeu, self.hover = [], [], 0.0, None
        self.n = 0
        self.fila = queue.Queue()   # o trabalho de cada traço (UIA, evento, print) fora do Tk: a UIA não roda na thread das janelas
        self.reabrir = False        # o trabalhador terminou: o pegador volta (o Tk que faz)
        self.mon = olho.monitor_de(*tela.centro())
        l, t, r, b = self.mon
        geo = "%dx%d+%d+%d" % (r - l, b - t, l, t)
        self.tinta = tk.Toplevel(root); self.tinta.overrideredirect(True); self.tinta.attributes("-topmost", True)
        self.tinta.configure(bg=TRANSP); self.tinta.attributes("-transparentcolor", TRANSP); self.tinta.geometry(geo)
        self.cv = tk.Canvas(self.tinta, width=r - l, height=b - t, bg=TRANSP, highlightthickness=0, bd=0)
        self.cv.pack()
        # 12/11 16h (ele: «um marca-texto ficaria maneiro também, igual tem no Lightshot»): o marca-texto mora numa janela própria,
        # translúcida de verdade (alpha 42% + cor-chave), pra o texto de baixo continuar legível
        self.marca = tk.Toplevel(root); self.marca.overrideredirect(True); self.marca.attributes("-topmost", True)
        self.marca.configure(bg=TRANSP); self.marca.attributes("-transparentcolor", TRANSP); self.marca.geometry(geo)
        self.marca.attributes("-alpha", 0.42)
        self.cvm = tk.Canvas(self.marca, width=r - l, height=b - t, bg=TRANSP, highlightthickness=0, bd=0)
        self.cvm.pack()
        self.peg = tk.Toplevel(root); self.peg.overrideredirect(True); self.peg.attributes("-topmost", True)
        self.peg.configure(bg="#000000", cursor="crosshair"); self.peg.geometry(geo)
        self.peg.attributes("-alpha", 0.01)
        for ev, f in (("<ButtonPress-1>", self._apertou), ("<B1-Motion>", self._arrastou), ("<ButtonRelease-1>", self._soltou),
                      ("<Motion>", self._mexeu), ("<Button-3>", lambda e: self.ferramenta("cursor"))):
            self.peg.bind(ev, f)
        self.EX_TINTA = 0x00080000 | 0x00000020 | 0x08000000 | 0x00000080    # layered | transparent (clique passa) | noactivate | toolwindow
        self.EX_PEG = 0x08000000 | 0x00000080                                 # noactivate | toolwindow (recebe o mouse)
        _estilo_ex(self.tinta, mais=self.EX_TINTA); _estilo_ex(self.marca, mais=self.EX_TINTA); _estilo_ex(self.peg, mais=self.EX_PEG)
        self.tinta.withdraw(); self.marca.withdraw(); self.peg.withdraw()
        self.tinta_vis = self.peg_vis = self.marca_vis = False
        threading.Thread(target=self._trabalhador, daemon=True).start()

    # ---- estado
    def ferramenta(self, nome):
        if nome not in dict(FERRAMENTAS):
            return
        if self.atual is not None:
            self._apagar_itens(self.atual); self.atual = None
        self.ferr = nome
        self.peg.configure(cursor={"caneta": "pencil", "marca": "pencil", "laser": "none"}.get(nome, "crosshair"))
        self._mostrar()

    def escolher_cor(self, i):
        self.cor = i
        if self.ferr in ("cursor", "laser"):         # escolheu cor = quer desenhar: vai pra caneta
            self.ferramenta("caneta")

    def tem_algo(self):
        return bool(self.tracos or self.laser or self.ferr != "cursor")

    def _mostrar(self):
        quer_peg = self.ferr != "cursor"
        quer_tinta = quer_peg or bool(self.tracos) or bool(self.laser)
        quer_marca = self.ferr == "marca" or any(t["ferr"] == "marca" for t in self.tracos)
        if quer_marca != self.marca_vis:         # o marca-texto fica embaixo da tinta (a seta por cima do grifado)
            self.marca_vis = quer_marca
            if quer_marca:
                self.marca.deiconify(); self.marca.attributes("-topmost", True); _estilo_ex(self.marca, mais=self.EX_TINTA)
            else:
                self.marca.withdraw()
        if quer_tinta != self.tinta_vis:
            self.tinta_vis = quer_tinta
            if quer_tinta:
                self.tinta.deiconify(); self.tinta.attributes("-topmost", True); _estilo_ex(self.tinta, mais=self.EX_TINTA)
            else:
                self.tinta.withdraw()
        if quer_peg != self.peg_vis:
            self.peg_vis = quer_peg
            if quer_peg:
                self.peg.deiconify(); self.peg.attributes("-topmost", True); _estilo_ex(self.peg, mais=self.EX_PEG)
            else:
                self.peg.withdraw()
        self.tela.topo()

    def parar(self):
        """a gravação acabou: tudo some, sem evento (não tem mais onde gravar)"""
        self.cv.delete("all"); self.cvm.delete("all"); self.tracos, self.laser, self.laser_seg, self.atual = [], [], [], None
        self.ferr = "cursor"; self._mostrar()

    # ---- mouse no pegador
    def _apertou(self, e):
        if self.ferr in ("cursor", "laser"):
            return
        self.atual = {"ferr": self.ferr, "cor": self.cor, "pts": [(e.x_root, e.y_root, time.time())], "itens": []}
        self._redesenhar(self.atual)

    def _arrastou(self, e):
        tr = self.atual
        if tr is None:
            return self._mexeu(e)
        pts, ponto = tr["pts"], (e.x_root, e.y_root, time.time())
        if tr["ferr"] in ("caneta", "marca"):          # mão livre; linha, seta e caixa = só o ponto final
            if abs(ponto[0] - pts[-1][0]) + abs(ponto[1] - pts[-1][1]) >= 2:
                pts.append(ponto)
        elif len(pts) == 1:
            pts.append(ponto)
        else:
            pts[-1] = ponto
        self._redesenhar(tr)

    def _soltou(self, e):
        tr, self.atual = self.atual, None
        if tr is None:
            return
        pts = tr["pts"]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if tr["ferr"] in ("caneta", "marca"):
            pequeno = len(pts) < 2 or max(max(xs) - min(xs), max(ys) - min(ys)) < 4
        else:
            pequeno = len(pts) < 2 or max(abs(pts[-1][0] - pts[0][0]), abs(pts[-1][1] - pts[0][1])) < 6
        if pequeno:                                   # clique sem arrastar: não é desenho
            self._apagar_itens(tr); return
        self.n += 1; tr["n"] = self.n; self.tracos.append(tr)
        if tr["ferr"] == "caixa":
            ponta = ((pts[0][0] + pts[-1][0]) // 2, (pts[0][1] + pts[-1][1]) // 2)     # a caixa aponta pro que está dentro
        else:
            ponta = (pts[-1][0], pts[-1][1])
        self._registrar(tr["ferr"], tr["cor"], list(pts), tr["n"], ponta)

    def _mexeu(self, e):
        self.hover = (e.x_root, e.y_root)
        if self.ferr != "laser":
            return
        agora = time.time()
        p = (e.x_root, e.y_root, agora)
        if self.laser_seg:
            ult = self.laser_seg[-1]
            self.laser_mov += abs(p[0] - ult[0]) + abs(p[1] - ult[1])
        else:
            self.laser_mov = 0.0
        self.laser.append(p); self.laser_seg.append(p); self.laser_mexeu = agora
        if not self.tinta_vis:
            self._mostrar()

    # ---- tinta
    def _apagar_itens(self, tr):
        cv = self.cvm if tr.get("ferr") == "marca" else self.cv
        for i in tr.get("itens", []):
            cv.delete(i)
        tr["itens"] = []

    def _redesenhar(self, tr):
        self._apagar_itens(tr)
        l, t = self.mon[0], self.mon[1]
        # 12/11 16h20 (ele: «os elementos na tela, tipo, seta, risco... condizentes com design também... não coloca uns bagulho
        # quadradão, bruto... pique iPhone... retângulo, bota uma bordinha de leve, não precisa ser ultra boleado... só um bagulho
        # sofisticado»): traço fino de ponta redonda, sem o contorno preto; seta de cabeça fina; quadrado só com a borda, canto de leve
        c, cv = CORES_DESENHO[tr["cor"]][1], self.cv
        larg = max(2, int(3.5 * F))
        xy = [v for x, y, _ in tr["pts"] for v in (x - l, y - t)]
        ferr = tr["ferr"]
        if ferr == "caneta":
            if len(xy) == 2:
                xy = xy + [xy[0] + 1, xy[1]]
            tr["itens"] = [cv.create_line(*xy, fill=c, width=larg, capstyle="round", joinstyle="round", smooth=len(xy) > 4)]
        elif ferr == "marca":     # marca-texto (Lightshot): faixa larga, ponta reta, na janela translúcida
            if len(xy) == 2:
                xy = xy + [xy[0] + 1, xy[1]]
            tr["itens"] = [self.cvm.create_line(*xy, fill=c, width=int(20 * F), capstyle="butt", joinstyle="round")]
            if not self.marca_vis:
                self._mostrar()
        elif len(xy) >= 4:
            a, b = xy[:2], xy[-2:]
            if ferr == "linha":
                tr["itens"] = [cv.create_line(*a, *b, fill=c, width=larg, capstyle="round")]
            elif ferr == "seta":
                tr["itens"] = [cv.create_line(*a, *b, fill=c, width=larg, arrow="last", capstyle="round",
                                              arrowshape=(int(15 * F), int(17 * F), int(6 * F)))]
            elif ferr == "caixa":     # só a borda, canto levemente redondo (4 arcos + 4 lados)
                x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1]))
                r = max(2, min(int(8 * F), (x1 - x0) // 2, (y1 - y0) // 2)); d = 2 * r
                kw = dict(outline=c, width=larg, style="arc")
                tr["itens"] = [cv.create_arc(x0, y0, x0 + d, y0 + d, start=90, extent=90, **kw),
                               cv.create_arc(x1 - d, y0, x1, y0 + d, start=0, extent=90, **kw),
                               cv.create_arc(x1 - d, y1 - d, x1, y1, start=270, extent=90, **kw),
                               cv.create_arc(x0, y1 - d, x0 + d, y1, start=180, extent=90, **kw),
                               cv.create_line(x0 + r, y0, x1 - r, y0, fill=c, width=larg),
                               cv.create_line(x1, y0 + r, x1, y1 - r, fill=c, width=larg),
                               cv.create_line(x0 + r, y1, x1 - r, y1, fill=c, width=larg),
                               cv.create_line(x0, y0 + r, x0, y1 - r, fill=c, width=larg)]
        if not self.tinta_vis:
            self._mostrar()

    def desfazer(self):
        if not self.tracos:
            return
        tr = self.tracos.pop()
        self._apagar_itens(tr)
        self.k.vigia.emitir({"tipo": "traco_desfeito", "n": tr["n"], "ferramenta": tr["ferr"]})
        self._mostrar()

    def limpar(self):
        n = len(self.tracos)
        for tr in self.tracos:
            self._apagar_itens(tr)
        self.tracos, self.laser, self.laser_seg = [], [], []
        self.cv.delete("laser")
        if n:
            self.k.vigia.emitir({"tipo": "tracos_limpos", "quantos": n})
        self._mostrar()

    def tique(self):
        """a cada 50 ms (o laço da barra): o rastro do laser apagando, o laser parado vira evento, o pegador volta"""
        agora = time.time()
        if self.reabrir:
            self.reabrir = False
            if self.ferr != "cursor" and self.peg_vis:
                self.peg.deiconify(); self.peg.attributes("-topmost", True); _estilo_ex(self.peg, mais=self.EX_PEG); self.tela.topo()
        if self.ferr == "laser" and len(self.laser_seg) > 1 and self.laser_mov > 40 and agora - self.laser_mexeu > 0.6:
            pts, self.laser_seg, self.laser_mov = self.laser_seg, [], 0.0
            self.n += 1
            self._registrar("laser", 0, pts, self.n, (pts[-1][0], pts[-1][1]))
        elif self.ferr != "laser":
            self.laser_seg = []
        if self.laser or (self.ferr == "laser" and self.hover):
            self._desenhar_laser(agora)

    def _desenhar_laser(self, agora):
        cv = self.cv; cv.delete("laser")
        self.laser = [p for p in self.laser if agora - p[2] < LASER_S]
        l, t = self.mon[0], self.mon[1]
        for (x0, y0, _), (x1, y1, t1) in zip(self.laser, self.laser[1:]):
            vida = max(0.0, 1 - (agora - t1) / LASER_S)
            r, g, b = (int(0x5a + (0xff - 0x5a) * vida), int(0x00 + 0x3b * vida), int(0x10 + (0x5c - 0x10) * vida))
            cv.create_line(x0 - l, y0 - t, x1 - l, y1 - t, fill="#%02x%02x%02x" % (r, g, b), width=max(1, int(8 * F * max(0.3, vida))),
                           capstyle="round", tags="laser")
        if self.ferr == "laser" and self.hover:       # o ponteiro do laser desenhado (o cursor do Windows fica escondido)
            x, y = self.hover[0] - l, self.hover[1] - t; rr = int(7 * F)
            cv.create_oval(x - rr - 3, y - rr - 3, x + rr + 3, y + rr + 3, fill="#ffffff", outline="", tags="laser")
            cv.create_oval(x - rr, y - rr, x + rr, y + rr, fill="#ff1e2e", outline="", tags="laser")
        if not self.laser and self.ferr != "laser":
            self._mostrar()

    # ---- o traço vira evento (fora do Tk)
    def _registrar(self, ferr, cor, pts, n, ponta):
        if self.k.alvo() is None:                     # pausado: o desenho fica na tela mas não entra na correção
            return
        if self.peg_vis:                              # a UIA precisa ver o app de baixo: o pegador sai do caminho um instante
            self.peg.withdraw()
        self.fila.put((ferr, cor, pts, n, ponta))

    def _trabalhador(self):
        uia = None
        while True:
            ferr, cor, pts, n, ponta = self.fila.get()
            try:
                time.sleep(0.03)                      # o Windows tirar o pegador da tela
                if uia is None:
                    uia = olho.UIA()
                try:
                    alvo = uia.em(*ponta)
                except Exception as e:
                    alvo = None; log("desenho/uia: %r" % e)
                if alvo and str(alvo.get("app", "")).lower() in ("pythonw.exe", "python.exe"):
                    alvo = None                       # pegou a própria tinta/barra: sem elemento
            finally:
                self.reabrir = True
            try:
                t0, quando = pts[0][2], pts[-1][2]
                passo = max(1, len(pts) // 120)
                amostra = pts[::passo] + ([pts[-1]] if (len(pts) - 1) % passo else [])
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                ev = {"tipo": "traco", "n": n, "ferramenta": ferr, "cor": CORES_DESENHO[cor][0] if ferr != "laser" else "laser",
                      "caixa": [min(xs), min(ys), max(xs), max(ys)], "ponta": [int(ponta[0]), int(ponta[1])],
                      "dur": round(quando - t0, 2), "pontos": [[int(p[0]), int(p[1]), int((p[2] - t0) * 1000)] for p in amostra]}
                if alvo:
                    ev["alvo"] = alvo
                    if str(alvo.get("app", "")).lower() == "chrome.exe":
                        ev["pedido_chrome"] = self.k.pedir_chrome(*ponta)
                self.k.vigia.emitir(ev, quando)
                self.k.vigia.pedir("print", "traco", (int(ponta[0]), int(ponta[1])), quando)
                log("desenho: %s %d (%s) → %s" % (ferr, n, ev["cor"], (alvo or {}).get("nome", "?")[:60]))
            except Exception as e:
                log("desenho: %r" % e)


class Tela:
    """3.0 (12/11/2026): a BARRA do Kakashi, no meio da tela (em cima, centralizada; arrasta pela alça e fica lembrada em
    config.json barra_cx/barra_y). Aparece só gravando ou esperando a escolha; fica FORA da gravação e dos prints
    (SetWindowDisplayAffinity WDA_EXCLUDEFROMCAPTURE). Gravando: alça · Sharingan (clique = concluir) · letreiro (tempo, ou a dica do
    botão debaixo do mouse) · pausar · pedaços (clique = apagar/voltar) · cursor/caneta/seta/caixa/laser · 4 cores · desfazer ·
    limpar · CONCLUIR · cancelar. Concluiu: «COMO EU LEIO?» · RÁPIDO · PROFUNDO · descartar.
    Antes (19/10–11/11) era o olho no canto, do lado da bolinha do Whisper, com a barra dos pedaços só pausado."""

    def __init__(self, k, fila):
        self.k, self.fila = k, fila
        self.root = tk.Tk(); self.root.overrideredirect(True); self.root.attributes("-topmost", True)
        if MAC:      # o Tk do Mac não tem -transparentcolor: a janela inteira é transparente e o fundo é "systemTransparent"
            self.root.attributes("-transparent", True); self.root.configure(bg="systemTransparent")
        else:
            self.root.configure(bg=TRANSP); self.root.attributes("-transparentcolor", TRANSP)
        c = cfg()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        # 12/11 16:37 (ele, depois de não ver a barra em cima do site escuro: «onde ficava o olho»): padrão = o canto de baixo, onde o
        # olho ficava (do lado da bolinha do Whisper; config olho_x/olho_y de antes). A barra cresce PRA ESQUERDA a partir dali (a
        # ponta direita fica fixa, a largura muda entre gravando e a escolha). Arrastou = vale o lugar dele (barra_cx/barra_y, pelo meio).
        self.dir = None
        if "barra_cx" in c:
            self.cx, self.y = int(c["barra_cx"]), int(c.get("barra_y", int(64 * F)))
        else:
            ox, oy = int(c.get("olho_x", sw - int(83 * ESC))), int(c.get("olho_y", sh - int(76 * ESC)))
            self.dir = min(sw - int(6 * F), ox + int(22 * F)); self.y = oy - BH // 2; self.cx = self.dir - 50
        self.W = 100
        self.cv = tk.Canvas(self.root, width=self.W, height=BH, bg="systemTransparent" if MAC else TRANSP, highlightthickness=0)
        self.cv.pack()
        self._geo()
        self.olho = self._carregar_olho(); self.modo = "escondido"; self.quadro = 0; self.prox = 0.0; self.visivel = True
        self.painel = None
        self.quem = None; self.desde = None; self.aviso = None; self.pisca = False; self.mudo = False; self.ult_estado = 0
        self.pausado = False; self.escolha = None
        self.zonas = []; self.hover = None; self.arr = None; self._z = None; self._dicas = []
        from tkinter import font as tkfont
        fams = set(tkfont.families(self.root))
        fam = FONTE if FONTE in fams else ("Segoe UI Variable Text" if "Segoe UI Variable Text" in fams else "Segoe UI")
        self.f_txt = tkfont.Font(root=self.root, family=fam, size=-int(13 * F))
        semi = FONTE + " SemiBold"
        self.f_bold = tkfont.Font(root=self.root, family=semi if semi in fams else fam, size=-int(13 * F),
                                  weight="normal" if semi in fams else "bold")
        self.f_peq = tkfont.Font(root=self.root, family=semi if semi in fams else fam, size=-int(11 * F))
        self.tem_icones = "Segoe Fluent Icons" in fams
        self.f_ico = tkfont.Font(root=self.root, family="Segoe Fluent Icons" if self.tem_icones else fam, size=-int(15 * F))
        self.w_txt = max(self.f_txt.measure(s) for s in ("Premiere pausado 00:00", "Laser: some sozinho", "Cursor: mexe no app",
                                                         "Concluir (= o atalho)", "Análise profunda")) + int(26 * F)
        self.cv.bind("<ButtonPress-1>", self._apertou); self.cv.bind("<B1-Motion>", self._arrastou)
        self.cv.bind("<ButtonRelease-1>", self._soltou); self.cv.bind("<Button-3>", self._menu)
        self.cv.bind("<Motion>", lambda e: setattr(self, "hover", self._zona_em(e.x)))
        self.cv.bind("<Leave>", lambda e: setattr(self, "hover", None))
        if MAC:
            self.cv.bind("<Button-2>", self._menu); self.cv.bind("<Control-Button-1>", self._menu)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Pausar / continuar", command=self._pausa)
        self.menu.add_command(label="Cancelar a gravação (vai pra descartadas)", command=lambda: self._acao(True))
        self.menu.add_command(label="Abrir o painel do Kakashi", command=lambda: self.abrir_painel())
        self.menu.add_command(label="Barra de volta pro canto", command=self._centralizar)
        self.menu.add_separator(); self.menu.add_command(label="Fechar o Kakashi", command=self._sair)
        # a barra NUNCA pega o foco (senão a "janela da frente" vira ela mesma e o /kakashi cola nela): ferramenta + não-ativa
        self.root.update_idletasks()
        self.hw = None
        if not MAC:
            self.hw = _estilo_ex(self.root, mais=0x08000000 | 0x00000080)       # WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
            try:   # fora da gravação e dos prints (Windows 10 2004+): o vídeo mostra o app, não a barra
                ok = user32.SetWindowDisplayAffinity(self.hw, 0x11)
                log("barra fora da gravação (WDA_EXCLUDEFROMCAPTURE): %s" % bool(ok))
            except Exception as e:
                log("barra fora da gravação: %r" % e)
        if MAC:     # porte pro Mac: a barra em toda mesa (Space), sem o Mac pular de mesa quando ela aparece
            try: mac.olho_em_toda_mesa()
            except Exception as e: log("mesa: %r" % e)
        self.desenho = None
        if not MAC:
            try:
                self.desenho = Desenho(self); k.desenho = self.desenho
            except Exception as e:
                log("desenho: não montou (%r) — a barra segue sem as ferramentas" % e)
        self._mostrar(False)
        self.root.after(50, self._tique)

    # ---- lugar
    def _geo(self):
        if self.dir is not None:                     # presa pela ponta direita (o canto do olho)
            self.cx = self.dir - self.W // 2
        self.root.geometry("%dx%d+%d+%d" % (self.W, BH, self.cx - self.W // 2, self.y))

    def centro(self):
        return self.cx, self.y + BH // 2

    def _centralizar(self):
        """botão direito → «Barra de volta pro canto»: esquece o lugar arrastado e volta pro canto do olho"""
        c = cfg(); c.pop("barra_cx", None); c.pop("barra_y", None); salvar_cfg(c)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ox, oy = int(c.get("olho_x", sw - int(83 * ESC))), int(c.get("olho_y", sh - int(76 * ESC)))
        self.dir = min(sw - int(6 * F), ox + int(22 * F)); self.y = oy - BH // 2; self._geo()

    def topo(self):
        """a barra por cima de tudo (inclusive do pegador do desenho), sem pegar o foco"""
        try:
            if MAC:
                self.root.attributes("-topmost", True); self.root.lift(); return
            hw = self.hw or user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            user32.SetWindowPos(hw, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)   # HWND_TOPMOST; SWP_NOSIZE|NOMOVE|NOACTIVATE
        except Exception as e:
            log("topo: %r" % e)

    # ---- o olho (os mesmos quadros e tempos do painel do Premiere)
    def _carregar_olho(self):
        # main.js do painel: ligar 55 ms, giro 90 ms em loop, desligar 45 ms ao contrário
        k = max(1, round(160 / max(16, BH - 6 * F)))
        abre = lambda n: tk.PhotoImage(file=os.path.join(ICONES, n)).subsample(k)    # noqa: E731
        nomes = {"olho": "olho.png",
                 "ligar": ["ligar_%02d.png" % i for i in range(18) if os.path.isfile(os.path.join(ICONES, "ligar_%02d.png" % i))],
                 "giro": ["giro_%02d.png" % i for i in range(12)]}
        olho_ = {c: abre(v) if isinstance(v, str) else [abre(n) for n in v] for c, v in nomes.items()}
        try:     # P20: os mesmos quadros em cinza = gravando MUDO (silêncio digital > 20 s) ou pausado
            cinza = lambda n: olho_cinza(os.path.join(ICONES, n), k, self.root)          # noqa: E731
            self.olho_cinza = {c: cinza(v) if isinstance(v, str) else [cinza(n) for n in v] for c, v in nomes.items()}
        except Exception as e:
            log("olho cinza: %r" % e); self.olho_cinza = olho_
        return olho_

    def _animar(self):
        agora = time.time()
        if agora < self.prox:
            return
        # 12/11 16h (ele: «substitui a bolinha vermelha de rec pelo olho do Kakashi girando... quando ele tiver pausado, não tiver
        # girando, vai ficar... o olho com sangue... aquela animaçãozinha»): gira = gravando e não pausado; pausou = a animação de
        # desligar até o olho com sangue, e volta a ligar ao continuar
        grav = bool(self.quem) and not self.pausado
        fica = bool(self.quem) or bool(self.escolha)  # 3.0: esperando a escolha a barra fica
        n_lig = len(self.olho["ligar"])
        if self.modo == "escondido":
            if fica:
                self._mostrar(True); self.modo = "olho_ini" if grav else "olho"; self.prox = agora + 0.25
            return
        if self.modo == "olho_ini":
            self.modo, self.quadro = ("ligando", 0) if grav else ("olho", 0)
        elif self.modo == "olho":
            if grav:
                self.modo, self.quadro = "ligando", 0
            elif not fica:
                self.modo = "escondido"; self._mostrar(False)
        elif self.modo == "ligando":
            if not grav: self.modo = "desligando"
            elif self.quadro >= n_lig - 1: self.modo, self.quadro = "giro", 0
            else: self.quadro += 1
        elif self.modo == "giro":
            if not grav: self.modo, self.quadro = "desligando", n_lig - 1
            else: self.quadro = (self.quadro + 1) % len(self.olho["giro"])
        elif self.modo == "desligando":
            if grav: self.modo = "ligando"
            elif self.quadro <= 0: self.modo = "olho"; self.prox = agora + 0.3; return
            else: self.quadro -= 1
        self.prox = agora + {"ligando": 0.055, "giro": 0.090, "desligando": 0.045}.get(self.modo, 0.2)

    def _img_olho(self):
        o = self.olho_cinza if (self.mudo and self.quem and not self.pausado) else self.olho   # cinza = microfone mudo (P20)
        if self.modo in ("ligando", "desligando"):
            return o["ligar"][max(0, min(self.quadro, len(o["ligar"]) - 1))]
        if self.modo == "giro":
            return o["giro"][self.quadro]
        return o["olho"]

    def _mostrar(self, sim):
        if sim == self.visivel: return
        self.visivel = sim
        if sim:
            self.root.deiconify(); self.root.attributes("-topmost", True)
            if MAC:
                try: mac.olho_em_toda_mesa()
                except Exception as e: log("mesa: %r" % e)
        else:
            self.root.withdraw()

    # ---- ações
    def _acao(self, cancelar=False):
        threading.Thread(target=lambda: (self.k.alternar(cancelar), self._forcar()), daemon=True).start()

    def _forcar(self):
        self.ult_estado = 0

    def _pausa(self):
        threading.Thread(target=lambda: (self.k.pausar_continuar(), self._forcar()), daemon=True).start()

    def _escolher(self, modo):
        self.escolha = None
        threading.Thread(target=lambda: (self.k.escolher(modo), self._forcar()), daemon=True).start()

    def _descartar_escolha(self):
        self.escolha = None
        threading.Thread(target=lambda: (self.k.descartar_escolha(), self._forcar()), daemon=True).start()

    def _clicou(self, zona):
        d = self.desenho
        if zona in ("olho", "concluir"):
            self._acao(False)
        elif zona == "cancelar":
            self._acao(True)
        elif zona == "pausa":
            self._pausa()
        elif zona in ("rapido", "profundo"):
            self._escolher(zona)
        elif zona == "descartar":
            self._descartar_escolha()
        elif isinstance(zona, tuple) and zona[0] == "ped":
            threading.Thread(target=lambda: (self.k.alternar_pedaco(zona[1]), self._forcar()), daemon=True).start()
        elif d is not None and isinstance(zona, tuple) and zona[0] == "ferr":
            d.ferramenta(zona[1])
        elif d is not None and isinstance(zona, tuple) and zona[0] == "cor":
            d.escolher_cor(zona[1])
        elif d is not None and zona == "desfazer":
            d.desfazer()
        elif d is not None and zona == "limpar":
            d.limpar()

    def _apertou(self, e):
        self.arr = (e.x_root, e.y_root, self.cx, self.y, False, self._zona_em(e.x))

    def _arrastou(self, e):
        if not self.arr: return
        x0, y0, cx, cy, _, zona = self.arr
        if zona not in (None, "alca"):              # arrastar começa na alça ou num pedaço vazio da barra
            return
        if abs(e.x_root - x0) + abs(e.y_root - y0) > 5:
            self.arr = (x0, y0, cx, cy, True, zona)
            self.dir = None                          # arrastou: vale o lugar dele, pelo meio
            self.cx, self.y = cx + e.x_root - x0, cy + e.y_root - y0
            self._geo()

    def _soltou(self, e):
        if self.arr and self.arr[4]:
            c = cfg(); c["barra_cx"], c["barra_y"] = int(self.cx), int(self.y); salvar_cfg(c)
        elif self.arr and self.arr[5] is not None and self._zona_em(e.x) == self.arr[5]:
            self._clicou(self.arr[5])
        self.arr = None

    def abrir_painel(self):
        if self.painel and self.painel.vivo():
            self.painel.win.deiconify(); self.painel.win.lift(); self.painel.win.focus_force(); return
        self.painel = Painel(self)

    def _menu(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

    def _sair(self):
        if self.k.pc:
            self.k.alternar()
            time.sleep(1)
        try:        # P20: o buffer fecha junto (antes os ffmpeg dele ficavam órfãos segurando o microfone)
            self.k.replay.descartar(self.k.replay.parar())
        except Exception as e:
            log("sair/replay: %r" % e)
        self.root.destroy(); os._exit(0)

    # ---- o laço (50 ms)
    def _tique(self):
        # 19/10: o laço NUNCA pode morrer (um erro aqui congelava o olho e o atalho parava de responder)
        try:
            self._tique_corpo()
        except Exception as e:
            log("tique: %r" % e)
        self.root.after(50, self._tique)

    def _tique_corpo(self):
        try:
            while True:
                tipo, info = self.fila.get_nowait()
                if tipo == "erro": self.aviso = info; log(info)
                else: self._acao(tipo == "cancelar")
        except queue.Empty:
            pass
        agora = time.time()
        if agora - self.ult_estado > 1.0:        # quem está gravando (1x por segundo, em segundo plano)
            self.ult_estado = agora
            threading.Thread(target=self._ler_estado, daemon=True).start()
        d = self.desenho
        if d is not None:
            try:
                if not self.quem and d.tem_algo():
                    d.parar()                        # acabou a gravação: o desenho some junto
                elif self.pausado and d.ferr != "cursor":
                    d.ferramenta("cursor")           # pausado: nada grava, o mouse volta pro app
                d.tique()
            except Exception as e:
                log("desenho/tique: %r" % e)
        self._animar()
        if self.visivel: self._desenhar()
        self._aviso_grande()
        if self.visivel and agora - getattr(self, "_ult_topo", 0) > 2.0:
            # 22/10: o "-topmost" do tk se perde depois de outra janela "sempre na frente" (ex.: o Lightshot); reafirma a cada 2 s
            self._ult_topo = agora
            if d is not None and not MAC:
                for w, vis in ((d.marca, d.marca_vis), (d.tinta, d.tinta_vis), (d.peg, d.peg_vis)):
                    if vis:
                        try:
                            hw = user32.GetParent(w.winfo_id()) or w.winfo_id()
                            user32.SetWindowPos(hw, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
                        except Exception:
                            pass
            self.topo()
        if agora - getattr(self, "_ult_flag", 0) > 0.5:      # o atalho da área de trabalho pediu a janelinha?
            self._ult_flag = agora
            if os.path.exists(FLAG_PAINEL):
                try: os.remove(FLAG_PAINEL)
                except OSError: pass
                self.abrir_painel()
        if self.painel: self.painel.tique()

    def _aviso_grande(self):
        """07/11 (Kakashi PC 17:51, ~50 s sem microfone sem ele perceber; no chat: «um aviso GRANDE piscando no meio da tela quando o
        microfone/som falhar»): gravando e mudo (o mesmo «SEM SOM» do olho, 20 s em silêncio digital) → uma faixa vermelha grande no
        meio da tela, piscando, que não pega clique (passa pro que está embaixo); some quando a voz volta ou a gravação para/pausa."""
        quer = bool(self.quem) and self.mudo and not self.pausado
        av = getattr(self, "_av", None)
        if not quer:
            if av is not None:
                av.withdraw()
            return
        if av is None:
            av = tk.Toplevel(self.root); av.overrideredirect(True); av.attributes("-topmost", True)
            try:
                av.attributes("-alpha", 0.9)
            except Exception:
                pass
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            w, h = int(sw * 0.62), int(sh * 0.16)
            av.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2))
            av.configure(bg="#B00020")
            self._av_txt = tk.Label(av, text="MICROFONE MUDO", font=("Segoe UI Black", max(28, int(h * 0.30)), "bold"), fg="#FFFFFF", bg="#B00020")
            self._av_txt.pack(expand=True, fill="both")
            self._av_sub = tk.Label(av, text="", font=("Segoe UI", max(12, int(h * 0.11)), "bold"), fg="#FFE600", bg="#B00020")
            self._av_sub.pack(fill="x", pady=(0, int(h * 0.08)))
            if not MAC:
                try:   # não pega clique: WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
                    av.update_idletasks()
                    hwnd = ctypes.windll.user32.GetParent(av.winfo_id()) or av.winfo_id()
                    est = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                    ctypes.windll.user32.SetWindowLongW(hwnd, -20, est | 0x00080000 | 0x00000020 | 0x08000000)
                except Exception as e:
                    log("aviso grande: não deixei passar o clique: %r" % e)
            self._av = av
            log("aviso grande: MICROFONE MUDO no meio da tela")
        mudo_s = int(self.k.mudo or 0)
        self._av_sub.config(text="o Kakashi não está ouvindo você há %d s · confira o microfone" % mudo_s)
        aceso = int(time.time() * 2) % 2 == 0
        cor = "#B00020" if aceso else "#3A0008"
        for wdg in (av, self._av_txt, self._av_sub):
            wdg.configure(bg=cor)
        av.deiconify(); av.lift()

    def _ler_estado(self):
        q, d = self.k.estado()
        if q and not self.quem:
            # 12/11 16:31 (ele: «o atalho não funcionou... eu tive que abrir o Kakashi e mexer lá»): o atalho FUNCIONOU (16:31:12
            # começou com o Chrome na frente), mas a barra cinza em cima do site escuro não foi vista; ele apertou de novo (concluiu
            # 10 s depois). Agora, ao começar, a barra pisca a borda branca 2 s e aparece mais embaixo da borda da tela.
            self.flash_ate = time.time() + 2.0
        self.quem, self.desde = q, d
        self.pausado = (q == "pc" and self.k.pc is not None and self.k.pc.pausado) or (q == "premiere" and getattr(self.k, "prem_pausado", False))
        recente, mudo = self.k.medir_voz() if q else (True, 0.0)
        if not q:
            self.k.voz_viva = None; self.k.mudo = 0.0
        self.pisca = bool(q) and not recente
        self.mudo = bool(q) and mudo > mudo_aviso_s()
        self.escolha = None if q else self.k.escolha_atual()     # 3.0: gravando, a escolha da anterior espera

    # ---- o desenho da barra
    def _pedacos(self):
        """[(n, estado)] estado: gravando | vale | apagado — PC (daqui) ou Premiere (do painel, pelo 7815/status)"""
        if self.quem == "pc" and self.k.pc is not None:
            return [(p["n"], "gravando" if p["dur"] is None else ("apagado" if p["apagado"] else "vale")) for p in self.k.pc.pedacos]
        if self.quem == "premiere":
            return [(p.get("n"), "gravando" if p.get("gravando") else ("apagado" if p.get("apagado") else "vale"))
                    for p in self.k.prem_pedacos if p.get("n") is not None]
        return []

    def _letreiro(self):
        """(texto grande, texto pequeno, cor): a dica do botão debaixo do mouse, ou o estado. O «gravando» é o Sharingan girando
        (12/11 16h, ele: «substitui a bolinha vermelha de rec pelo olho do Kakashi girando»)"""
        if self.escolha and not self.quem:          # na escolha o letreiro é a pergunta (as dicas não cabem ali)
            return "Como eu leio?", "", COR["texto"]
        z = self.hover
        dica = next((dc for _, _, zz, dc in self._dicas if zz == z), None) if z is not None else None
        if dica:
            return dica, "", COR["texto2"]
        if self.quem:
            s = int(time.time() - self.desde) if self.desde else 0
            tempo = "%d:%02d" % (s // 60, s % 60)
            nome = {"pc": "PC", "app_pessoal": "AppPessoal", "premiere": "Premiere"}.get(self.quem, "")
            if self.mudo:            # P20: gravação muda há > 20 s: «Sem som» piscando (vermelho / apagado a cada 0,5 s)
                return "Sem som " + tempo, "", (COR["vermelho"] if int(time.time() * 2) % 2 == 0 else COR["texto3"])
            if self.pausado:
                return tempo, nome + " · pausado", COR["amarelo"]
            amarelo = self.pisca and int(time.time() * 2) % 2 == 0      # 10 min sem voz
            return tempo, nome, (COR["amarelo"] if amarelo else COR["texto"])
        if self.escolha:
            return "Como eu leio?", "", COR["texto"]
        return (self.aviso or "")[:40], "", COR["amarelo"]

    def _itens(self):
        """[(largura, zona, dica, função de desenho(cv, x0, x1))] da esquerda pra direita"""
        it = []
        sep = lambda w: it.append((w, None, None, None))                                # noqa: E731
        risco = lambda: it.append((int(13 * F), None, None, self._d_risco))              # noqa: E731
        it.append((int(14 * F), "alca", "Arraste a barra", self._d_alca))
        if self.quem:
            it.append((BH, "olho", "Concluir", self._d_olho))
            it.append((self.w_txt, None, None, self._d_letreiro))
            if self.quem in ("pc", "premiere"):
                it.append((CEL + int(2 * F), "pausa", "Continuar" if self.pausado else "Pausar",
                           lambda cv, a, b: self._d_redondo(cv, a, b, "play" if self.pausado else "pausa", fundo=COR["seg"])))
                ps = self._pedacos()[-12:]
                if ps:
                    sep(int(4 * F))
                    w1 = int(21 * F)
                    def segs(cv, a, b, ps=ps, w1=w1):
                        self._capsula(cv, a, MARGEM, b, BH - MARGEM, int(8 * F), COR["seg"])
                        for i, (n, est) in enumerate(ps):
                            self._d_pedaco(cv, a + int(3 * F) + i * w1, a + int(3 * F) + (i + 1) * w1, n, est)
                    it.append((len(ps) * w1 + int(6 * F), None, None, segs))
                    # as zonas de clique de cada pedaço (por cima do mesmo lugar: largura zero na fila, só a zona)
                    base = sum(w for w, _, _, _ in it) - (len(ps) * w1 + int(6 * F)) + int(3 * F)
                    self._zonas_ped = [(base + i * w1, base + (i + 1) * w1, ("ped", n),
                                        "Pedaço %d: %s" % (n, {"gravando": "gravando", "vale": "apagar", "apagado": "voltar"}[est]))
                                       for i, (n, est) in enumerate(ps)]
                else:
                    self._zonas_ped = []
            else:
                self._zonas_ped = []
            if self.desenho is not None:
                risco()
                for nome, dica in FERRAMENTAS:
                    it.append((CEL, ("ferr", nome), dica, lambda cv, a, b, nome=nome: self._d_ferr(cv, a, b, nome)))
                sep(int(4 * F))
                for i, (nome, _) in enumerate(CORES_DESENHO):
                    it.append((int(18 * F), ("cor", i), nome.capitalize(), lambda cv, a, b, i=i: self._d_cor(cv, a, b, i)))
                sep(int(4 * F))
                it.append((CEL, "desfazer", "Desfazer o último", lambda cv, a, b: self._d_redondo(cv, a, b, "desfazer")))
                it.append((CEL, "limpar", "Limpar os desenhos", lambda cv, a, b: self._d_redondo(cv, a, b, "limpar")))
            risco()
            it.append((self.f_bold.measure("Concluir") + int(30 * F), "concluir", "Concluir (= o atalho)", self._d_concluir))
            it.append((CEL, "cancelar", "Cancelar tudo", lambda cv, a, b: self._d_redondo(cv, a, b, "cancelar", COR["texto2"])))
        elif self.escolha:
            self._zonas_ped = []
            sep(int(4 * F))
            it.append((self.f_bold.measure("Como eu leio?") + int(18 * F), None, None, self._d_letreiro))
            wr, wp = self.f_bold.measure("Rápido") + int(30 * F), self.f_bold.measure("Profundo") + int(30 * F)
            it.append((int(4 * F), None, None, lambda cv, a, b, w=wr + wp: self._capsula(cv, a, MARGEM, a + w + int(8 * F), BH - MARGEM,
                                                                                       int(10 * F), COR["seg"])))
            it.append((wr, "rapido", "Coisa rápida", lambda cv, a, b: self._d_segmento(cv, a, b, "Rápido", True)))
            it.append((wp, "profundo", "Análise profunda", lambda cv, a, b: self._d_segmento(cv, a, b, "Profundo", False)))
            it.append((int(4 * F), None, None, None))
            fila = self.escolha.get("fila", 1)
            if fila > 1:
                txt = "+%d" % (fila - 1)
                it.append((self.f_txt.measure(txt) + int(16 * F), None, None,
                           lambda cv, a, b, t=txt: cv.create_text((a + b) // 2, BH // 2, text=t, fill=COR["texto2"], font=self.f_txt)))
            else:
                sep(int(4 * F))
            it.append((CEL + int(2 * F), "descartar", "Descartar esta",
                       lambda cv, a, b: self._d_redondo(cv, a, b, "cancelar", COR["texto2"], fundo=COR["seg"])))
        it.append((int(8 * F), None, None, None))
        return it

    def _glifo(self, nome):
        return (ICONE if self.tem_icones else ICONE_TXT)[nome]

    def _zona_em(self, x):
        z = next((z for x0, x1, z, _ in getattr(self, "_zonas_ped", []) if x0 <= x < x1), None)
        return z if z is not None else next((z for x0, x1, z in self.zonas if x0 <= x < x1), None)

    def _assinatura(self, itens, W):
        """tudo que aparece na barra, menos o quadro do Sharingan: igual = não redesenha (só troca a imagem do olho)"""
        d = self.desenho
        return (W, tuple(z for _, z, _, _ in itens), self.hover, self._letreiro(), self.pausado, self.mudo, self._borda(),
                (d.ferr, d.cor) if d is not None else None, tuple(self._pedacos()), self.pisca and int(time.time() * 2) % 2 == 0)

    def _borda(self):
        """a cor da borda da barra: branca piscando nos 2 s depois de começar (pra ele ver que o atalho pegou); depois, cinza visível
        em cima de site escuro (#48484A; o #2C2C2E sumia no Fly X-tudo)"""
        if time.time() < getattr(self, "flash_ate", 0) and int(time.time() * 4) % 2 == 0:
            return COR["texto"]
        return "#48484A"

    def _desenhar(self):
        itens = self._itens()
        W = sum(w for w, _, _, _ in itens)
        if W != self.W:
            self.W = W; self.cv.configure(width=W); self._geo()
        ass = self._assinatura(itens, W)
        if ass == getattr(self, "_ass", None):      # nada mudou: só o Sharingan anda (antes refazia a barra inteira a cada 50 ms)
            if getattr(self, "_id_olho", None) is not None:
                self.cv.itemconfigure(self._id_olho, image=self._img_olho())
            return
        self._ass = ass
        cv = self.cv; cv.delete("all"); self.zonas = []; self._id_olho = None
        self._dicas = [(x0, x1, z, dc) for x0, x1, z, dc in getattr(self, "_zonas_ped", [])]
        borda = self._borda()
        if borda == COR["texto"]:                   # piscando ao começar: borda de 2 px
            self._capsula(cv, 0, 0, W - 1, BH - 1, int(11 * F), borda)
            self._capsula(cv, 2, 2, W - 3, BH - 3, int(11 * F) - 2, COR["fundo"])
        else:
            self._capsula(cv, 0, 0, W - 1, BH - 1, int(11 * F), COR["fundo"], borda)
        x = 0
        for w, zona, dica, f in itens:
            self._z = zona
            if f is not None:
                f(cv, x, x + w)
            if zona is not None:
                self.zonas.append((x, x + w, zona))
                if dica:
                    self._dicas.append((x, x + w, zona, dica))
            x += w

    # peças
    @staticmethod
    def _capsula(cv, x0, y0, x1, y1, r, fill, outline=""):
        """retângulo de cantos redondos: 4 círculos + 2 retângulos (o polígono «smooth» do Tk afundava a borda e vazava o fundo);
        a borda = a mesma forma 1 px maior por baixo"""
        def forma(x0, y0, x1, y1, r, cor):
            if not cor:
                return
            d = 2 * r
            for cx, cy in ((x0, y0), (x1 - d, y0), (x0, y1 - d), (x1 - d, y1 - d)):
                cv.create_oval(cx, cy, cx + d, cy + d, fill=cor, outline=cor)
            cv.create_rectangle(x0 + r, y0, x1 - r, y1, fill=cor, outline=cor)
            cv.create_rectangle(x0, y0 + r, x1, y1 - r, fill=cor, outline=cor)
        r = max(1, min(r, (y1 - y0) // 2, (x1 - x0) // 2))
        if outline:
            forma(x0, y0, x1, y1, r, outline)
            if fill:
                forma(x0 + 1, y0 + 1, x1 - 1, y1 - 1, max(1, r - 1), fill)
        else:
            forma(x0, y0, x1, y1, r, fill)

    def _d_alca(self, cv, a, b):
        cx, cy, p = (a + b) // 2 + int(2 * F), BH // 2, max(1, int(1.3 * F))
        for dy in (-4, 0, 4):
            for dx in (-2, 2):
                x, y = cx + int(dx * F), cy + int(dy * F)
                cv.create_oval(x - p, y - p, x + p, y + p, fill="#48484A", outline="")

    def _d_olho(self, cv, a, b):
        self._id_olho = cv.create_image((a + b) // 2, BH // 2, image=self._img_olho())

    def _d_letreiro(self, cv, a, b):
        grande, pequeno, cor = self._letreiro()
        x = a + int(6 * F)
        if grande:
            cv.create_text(x, BH // 2, text=grande, fill=cor, font=self.f_bold if self.quem or self.escolha else self.f_txt, anchor="w")
        if pequeno:
            cv.create_text(x + self.f_bold.measure(grande) + int(8 * F), BH // 2, text=pequeno, fill=COR["texto2"], font=self.f_txt,
                           anchor="w")

    def _d_risco(self, cv, a, b):
        cx = (a + b) // 2
        cv.create_line(cx, int(BH * 0.3), cx, int(BH * 0.7), fill="#38383A", width=max(1, int(F)))

    def _circulo(self, cv, cx, cor):
        r = (BH - 2 * MARGEM) // 2
        cv.create_oval(cx - r, BH // 2 - r, cx + r, BH // 2 + r, fill=cor, outline=cor)

    def _d_redondo(self, cv, a, b, ico, cor=None, fundo=None, ativo=False):
        """botão redondo (pin 1): fundo cinza (ou nada), branco quando é a ferramenta escolhida"""
        cx = (a + b) // 2
        if ativo:
            self._circulo(cv, cx, COR["texto"])
        elif self.hover == self._z:
            self._circulo(cv, cx, COR["ativo"] if fundo else COR["hover"])
        elif fundo:
            self._circulo(cv, cx, fundo)
        c = COR["preto"] if ativo else (cor or COR["texto"])
        cv.create_text(cx, BH // 2, text=self._glifo(ico), fill=c, font=self.f_ico,
                       angle=-45 if (ico in ("seta", "linha") and self.tem_icones) else 0)

    def _d_pedaco(self, cv, a, b, n, est):
        """um pedaço dentro do segmentado (pin 3): o que grava fica destacado com o número vermelho; apagado = cinza riscado"""
        z = ("ped", n)
        if est == "gravando" or self.hover == z:
            self._capsula(cv, a + 1, MARGEM + int(3 * F), b - 1, BH - MARGEM - int(3 * F), int(6 * F), COR["seg_sel"])
        cor = {"gravando": COR["vermelho"], "vale": COR["texto"], "apagado": COR["texto3"]}[est]
        cv.create_text((a + b) // 2, BH // 2, text=str(n), fill=cor, font=self.f_peq)
        if est == "apagado":
            cv.create_line(a + int(5 * F), BH // 2, b - int(5 * F), BH // 2, fill=COR["texto3"], width=max(1, int(F)))

    def _d_ferr(self, cv, a, b, nome):
        d = self.desenho
        ativo = d is not None and d.ferr == nome
        cor = COR["vermelho"] if nome == "laser" else COR["texto"]
        self._d_redondo(cv, a, b, nome, cor, ativo=ativo)

    def _d_cor(self, cv, a, b, i):
        d = self.desenho
        cx, cy, r = (a + b) // 2, BH // 2, max(4, int(5 * F))
        rr = r + max(3, int(3 * F))
        if d is not None and d.cor == i:
            cv.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, outline=COR["texto"], width=max(1, int(1.5 * F)))
        elif self.hover == self._z:
            cv.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, outline=COR["texto3"], width=max(1, int(F)))
        cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=CORES_DESENHO[i][1], outline="")

    def _d_concluir(self, cv, a, b):
        """«Concluir» em pílula branca (pin 1)"""
        y0, y1 = MARGEM, BH - MARGEM
        self._capsula(cv, a + int(2 * F), y0, b - int(2 * F), y1, (y1 - y0) // 2, "#E5E5EA" if self.hover == self._z else COR["texto"])
        cv.create_text((a + b) // 2, BH // 2, text="Concluir", fill=COR["preto"], font=self.f_bold)

    def _d_segmento(self, cv, a, b, txt, principal):
        """uma opção do segmentado da escolha (pin 3): a principal (Rápido) fica destacada; a outra acende com o mouse"""
        if principal or self.hover == self._z:
            self._capsula(cv, a + int(1 * F), MARGEM + int(3 * F), b - int(1 * F), BH - MARGEM - int(3 * F), int(7 * F), COR["seg_sel"])
        cv.create_text((a + b) // 2, BH // 2, text=txt, fill=COR["texto"] if (principal or self.hover == self._z) else "#C7C7CC",
                       font=self.f_bold)


FLAG_PAINEL = os.path.join(AQUI, "abrir_painel.flag")
APP_PESSOAL_COR = os.path.join(AQUI, "_sem_app_pessoal")   # pacote da Fly: o AppPessoal é do Luan, aqui não existe
PREMIERE_SES = os.path.join(AQUI, "premiere", "sessoes")   # pacote da Fly: o servidor do painel mora em premiere\


def gravacoes(n=12):
    """as últimas correções dos 3 Kakashis (PC, AppPessoal, Premiere), mais nova primeiro"""
    out = []
    for base, tipo in ((SESSOES, "PC"), (APP_PESSOAL_COR, "AppPessoal"), (PREMIERE_SES, "Premiere")):
        if not os.path.isdir(base):
            continue
        for nome in os.listdir(base):
            pasta = os.path.join(base, nome)
            if not re.match(r"20\d\d-", nome) or not os.path.isdir(pasta):
                continue
            try:
                m = json.load(open(os.path.join(pasta, "sessao.json"), encoding="utf-8"))
            except (OSError, ValueError):
                m = {}
            dur = m.get("duracao_s")
            if dur is None and m.get("fim") and m.get("inicio"):
                dur = m["fim"] - m["inicio"]
            quando = (m.get("inicio_local") or m.get("inicio_iso") or nome)[:16].replace("T", " ")
            extra = m.get("sequencia") or (m.get("janela_inicial") or {}).get("titulo") or ""
            out.append({"pasta": pasta, "base": base, "tipo": tipo, "quando": quando, "dur": dur, "extra": extra[:40],
                        "descartada": bool(m.get("descartada"))})
    out.sort(key=lambda x: x["quando"], reverse=True)
    return out[:n]


def descartar(g):
    """vai pra <origem>/_descartadas (nunca apaga) e marca descartada no sessao.json"""
    arq = os.path.join(g["pasta"], "sessao.json")
    try:
        m = json.load(open(arq, encoding="utf-8"))
    except (OSError, ValueError):
        m = {}
    m["descartada"] = True; m["descartada_em"] = datetime.datetime.now().replace(microsecond=0).isoformat()
    try:
        json.dump(m, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except OSError:
        pass
    dest = os.path.join(g["base"], "_descartadas"); os.makedirs(dest, exist_ok=True)
    try:
        shutil.move(g["pasta"], dest); return True
    except OSError as e:
        log("descartar: %s" % e); return False


class Painel:
    """Janelinha do KAKASHI em 8 bits — mesma estética do painel do Premiere (CORRETOR\\painel\\index.html: fundo #0b0b0e, canto
    reto, borda grossa com relevo claro em cima/esquerda e escuro embaixo/direita, fonte pixel 5x7 em caixa alta, título titulo.png,
    relógio d_*.png). 19/10, ele: "o Kakashi todo é pra tá na estética do plugin do Premiere, todo 8 bits... Esse nome aqui".
    Não pisca: a lista só é refeita quando muda."""
    FUNDO = "#0b0b0e"
    EST = {   # (fundo, claro, escuro, cor da letra)
        "vermelho": ("#d6001c", "#ff6a6a", "#5e000c", "branco"),
        "concluir": ("#15151a", "#34343e", "#050507", "vermelho"),
        "neutro":   ("#2a2a33", "#4a4a56", "#0a0a0d", "amarelo"),
        "mini":     ("#15151a", "#34343e", "#050507", "branco"),
        "perigo":   ("#2a0006", "#6a0a16", "#0a0002", "vermelho"),
        "off":      ("#1a1a20", "#24242b", "#0a0a0d", "apagado"),
    }

    def __init__(self, tela):
        import pixel
        from PIL import Image, ImageTk
        self.px, self.Image, self.ImageTk = pixel, Image, ImageTk
        self.tela = tela; self.cache = {}
        self.win = tk.Toplevel(tela.root); self.win.title("KAKASHI"); self.win.configure(bg=self.FUNDO)
        self.win.resizable(False, False)
        self.win.geometry("+%d+%d" % (tela.root.winfo_screenwidth() // 2 - 300, tela.root.winfo_screenheight() // 2 - 330))
        self.win.attributes("-topmost", True)
        try:
            self.win.iconphoto(False, tk.PhotoImage(file=os.path.join(ICONES, "icone_48.png")))
        except Exception:
            pass
        self.win.protocol("WM_DELETE_WINDOW", self.fechar)
        self.win.update_idletasks()
        try:    # barra de título escura (Windows 11)
            hw = user32.GetParent(self.win.winfo_id())
            v = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hw, 20, ctypes.byref(v), ctypes.sizeof(v))
        except Exception:
            pass
        self.olho_g = {"olho": tk.PhotoImage(file=os.path.join(ICONES, "olho.png")).subsample(2),
                       "giro": [tk.PhotoImage(file=os.path.join(ICONES, "giro_%02d.png" % i)).subsample(2) for i in range(12)]}
        app = tk.Frame(self.win, bg=self.FUNDO); app.pack(padx=12, pady=(12, 14))
        topo = tk.Frame(app, bg=self.FUNDO); topo.pack(fill="x", pady=(0, 12))
        self.lb_olho = tk.Label(topo, bg=self.FUNDO, image=self.olho_g["olho"], bd=0); self.lb_olho.pack(side="left", padx=(0, 10))
        marca = tk.Frame(topo, bg=self.FUNDO); marca.pack(side="left", fill="x")
        self.img_tit = tk.PhotoImage(file=os.path.join(ICONES, "titulo.png"))
        tk.Label(marca, image=self.img_tit, bg=self.FUNDO, bd=0).pack(anchor="w")
        self.lb_sub = tk.Label(marca, bg=self.FUNDO, bd=0); self.lb_sub.pack(anchor="w", pady=(4, 0))
        self._texto(self.lb_sub, atalho.legenda(cfg()), "vermelho")
        # relógio + status (igual ao painel)
        self.lb_crono = tk.Label(app, bg=self.FUNDO, bd=0); self.lb_crono.pack(pady=(2, 0))
        lin = tk.Frame(app, bg=self.FUNDO); lin.pack(pady=(6, 0))
        self.ponto = tk.Frame(lin, width=8, height=8, bg="#5b5b63"); self.ponto.pack(side="left", padx=(0, 8))
        self.lb_status = tk.Label(lin, bg=self.FUNDO, bd=0); self.lb_status.pack(side="left")
        # 03/11 (ele: «coloca o Kakashi aqui com os mesmos controles do Premiere... Pausar, aí excluir a parte»): o mesmo do painel do
        # Premiere — TRILHO com os pedaços (clique seleciona; APAGAR N / VOLTAR N), o botão grande PAUSAR/CONTINUAR, CONCLUIR e CANCELAR
        lt = tk.Frame(app, bg=self.FUNDO); lt.pack(fill="x", pady=(10, 0))
        self.trilho = tk.Canvas(lt, width=392, height=26, bg=self.FUNDO, highlightthickness=0, bd=0, cursor="hand2")
        self.trilho.pack(side="left"); self.trilho.bind("<Button-1>", self._clicou_trilho)
        self.bt_ped = self._botao(lt, 120, 26, self._acao_pedaco); self.bt_ped.pack(side="right")
        self.ped_sel = None; self.ult_trilho = 0
        self.bt_grav = self._botao(app, 520, 44, self._principal); self.bt_grav.pack(pady=(8, 0))
        lc = tk.Frame(app, bg=self.FUNDO); lc.pack(fill="x", pady=(6, 0))
        self.bt_conc = self._botao(lc, 386, 30, lambda: self.tela._acao(False)); self.bt_conc.pack(side="left")
        self.bt_canc = self._botao(lc, 128, 30, lambda: self.tela._acao(True)); self.bt_canc.pack(side="right")
        # gravações
        self.lb_tit_lista = tk.Label(app, bg=self.FUNDO, bd=0); self.lb_tit_lista.pack(anchor="w", pady=(16, 6))
        self._texto(self.lb_tit_lista, "GRAVADAS", "amarelo", 3)
        self.lista = tk.Frame(app, bg=self.FUNDO); self.lista.pack(fill="x")
        pe = tk.Frame(app, bg=self.FUNDO); pe.pack(fill="x", pady=(12, 0))
        b1 = self._botao(pe, 256, 30, lambda: os.startfile(SESSOES)); b1.pack(side="left")
        self._pintar(b1, "mini", "ABRIR A PASTA DO PC")
        b2 = self._botao(pe, 256, 30, tela._sair); b2.pack(side="right")
        self._pintar(b2, "perigo", "FECHAR O KAKASHI")
        pe2 = tk.Frame(app, bg=self.FUNDO); pe2.pack(fill="x", pady=(6, 0))     # pacote da Fly: trocar o atalho
        self.bt_atalho = self._botao(pe2, 520, 30, self.trocar_atalho); self.bt_atalho.pack()
        self._pintar(self.bt_atalho, "mini", "TROCAR O ATALHO")
        pe3 = tk.Frame(app, bg=self.FUNDO); pe3.pack(fill="x", pady=(6, 0))     # pacote da Fly: atualização
        self.bt_atual = self._botao(pe3, 520, 30, self.atualizacao); self.bt_atual.pack()
        self._nova_pintada = "?"; self._pintar_atual()
        self.giro_i = 0; self.ult_giro = 0; self.ult_lista = 0; self.assinatura = None; self.estado_bt = None
        self.montar_lista(forcar=True)

    # ---- peças 8 bits
    def _img(self, txt, cor, E=2):
        k = (txt, cor, E)
        if k not in self.cache:
            self.cache[k] = self.ImageTk.PhotoImage(self.px.render(txt, E, cor), master=self.win)
        return self.cache[k]

    def _texto(self, label, txt, cor, E=2):
        label.configure(image=self._img(txt, cor, E))

    def _botao(self, pai, w, h, cmd):
        cv = tk.Canvas(pai, width=w, height=h, bg=self.FUNDO, highlightthickness=0, bd=0, cursor="hand2")
        cv._cmd = cmd; cv._est = None
        cv.bind("<Button-1>", lambda e: cv._cmd() if cv._est != "off" else None)
        return cv

    def _pintar(self, cv, est, txt, E=2):
        chave = (est, txt, E)
        if getattr(cv, "_chave", None) == chave:
            return
        cv._chave = chave; cv._est = est
        w, h = int(cv["width"]), int(cv["height"]); b = 4 if h >= 40 else 3
        f, cl, es, cor = self.EST[est]
        cv.delete("all")
        cv.create_rectangle(0, 0, w, h, fill=f, outline="")
        cv.create_rectangle(0, 0, w, b, fill=cl, outline=""); cv.create_rectangle(0, 0, b, h, fill=cl, outline="")
        cv.create_rectangle(0, h - b, w, h, fill=es, outline=""); cv.create_rectangle(w - b, 0, w, h, fill=es, outline="")
        cv.create_image(w // 2, h // 2 + 1, image=self._img(txt, cor, E))
        cv.configure(cursor="arrow" if est == "off" else "hand2")

    def _principal(self):
        """parado = INICIAR; gravando no PC ou no Premiere = PAUSAR/CONTINUAR (04/11: o Premiere também, sem abrir o painel); AppPessoal = CONCLUIR"""
        if self.tela.quem in ("pc", "premiere"):
            self.tela._pausa()
        else:
            self.tela._acao(False)

    def _pedacos(self):
        g = self.tela.k.pc
        return list(g.pedacos) if g is not None else []

    def _clicou_trilho(self, e):
        for x0, x1, p in getattr(self, "_blocos", []):
            if x0 <= e.x <= x1:
                if p["dur"] is None:            # o que está gravando não se apaga (pausa antes)
                    return
                self.ped_sel = None if self.ped_sel == p["n"] else p["n"]; self.ult_trilho = 0; return

    def _acao_pedaco(self):
        g = self.tela.k.pc
        if g is not None and self.ped_sel is not None:
            g.alternar_pedaco(self.ped_sel); self.ult_trilho = 0

    def _desenhar_trilho(self):
        cv = self.trilho; cv.delete("all")
        ps = self._pedacos(); w, h = int(cv["width"]), int(cv["height"])
        self._blocos = desenhar_trilho(cv, 0, 0, w, h, ps, self.ped_sel)
        if not ps:
            self._pintar(self.bt_ped, "off", "APAGAR"); return
        sel = next((p for p in ps if p["n"] == self.ped_sel), None)
        if sel is None:
            self.ped_sel = None; self._pintar(self.bt_ped, "off", "APAGAR")
        else:
            self._pintar(self.bt_ped, "mini" if sel["apagado"] else "perigo", ("VOLTAR %d" if sel["apagado"] else "APAGAR %d") % sel["n"])

    def trocar_atalho(self):
        """pacote da Fly (27/10): aperta o botão, aperta o atalho novo (Esc cancela); grava no config.json e vale na hora."""
        if self.tela.quem:
            self._pintar(self.bt_atalho, "mini", "CONCLUA A GRAVACAO ANTES")
            self.win.after(2500, lambda: self.vivo() and self._pintar(self.bt_atalho, "mini", "TROCAR O ATALHO")); return
        if getattr(self, "_capturando", False):
            return
        self._capturando = True; self._cap_r = None
        atalho.soltar()                       # o atalho de agora não dispara enquanto a pessoa aperta o novo
        self._pintar(self.bt_atalho, "neutro", "APERTE O ATALHO NOVO · ESC CANCELA")
        threading.Thread(target=lambda: setattr(self, "_cap_r", atalho.capturar()), daemon=True).start()

    def _fim_troca(self, r):
        self._capturando = False
        if r.get("ok"):
            c = cfg(); c["atalho"] = r["texto"]; c.pop("atalho_cancelar", None); salvar_cfg(c)
            log("atalho trocado na janelinha: " + r["texto"])
        atalho.recarregar()                   # registra o novo (ou devolve o antigo, se cancelou)
        self._texto(self.lb_sub, atalho.legenda(cfg()), "vermelho")
        self._pintar(self.bt_atalho, "mini", r["msg"])
        self.win.after(3500, lambda: self.vivo() and self._pintar(self.bt_atalho, "mini", "TROCAR O ATALHO"))

    def _pintar_atual(self):
        """pacote da Fly (27/10): o botão de atualização mostra a versão nova assim que o vigia (atualizar.py) acha."""
        self._nova_pintada = atualizar.NOVA
        if atualizar.NOVA:
            self._pintar(self.bt_atual, "neutro", "ATUALIZAR PRA " + atualizar.NOVA)
        else:
            self._pintar(self.bt_atual, "mini", "PROCURAR ATUALIZACAO · VERSAO " + atualizar.versao_local())

    def atualizacao(self):
        if getattr(self, "_procurando", False):
            return
        if atualizar.NOVA:
            if self.tela.quem:
                self._pintar(self.bt_atual, "mini", "CONCLUA A GRAVACAO ANTES")
                self.win.after(2500, lambda: self.vivo() and self._pintar_atual()); return
            atualizar.abrir_instalador_em_janela()     # janela preta à parte: ela fecha e reabre o Kakashi no fim
            log("atualização: o botão abriu o atualizador (%s)" % atualizar.NOVA)
            self._pintar(self.bt_atual, "neutro", "ATUALIZANDO · ACOMPANHE NA JANELA PRETA"); return
        self._procurando = True; self._atual_r = None
        self._pintar(self.bt_atual, "neutro", "PROCURANDO...")
        threading.Thread(target=lambda: setattr(self, "_atual_r", atualizar.checar()), daemon=True).start()

    def _fim_procura(self, r):
        self._procurando = False
        if r["estado"] == "erro":
            self._pintar(self.bt_atual, "mini", "SEM INTERNET OU GITHUB FORA")
            self.win.after(3500, lambda: self.vivo() and self._pintar_atual())
        elif r["estado"] == "em_dia":
            self._pintar(self.bt_atual, "mini", "EM DIA · VERSAO " + r["local"])
            self.win.after(3500, lambda: self.vivo() and self._pintar_atual())
        else:
            self._pintar_atual()

    def vivo(self):
        try:
            return bool(self.win.winfo_exists())
        except Exception:
            return False

    def fechar(self):
        self.win.destroy(); self.tela.painel = None

    def montar_lista(self, forcar=False):
        gs = gravacoes(10)
        grav_pasta = os.path.normcase(self.tela.k.pc.pasta) if (self.tela.k.pc) else None
        ass = tuple((g["pasta"], g["dur"]) for g in gs) + (grav_pasta,)
        self.ult_lista = time.time()
        if ass == self.assinatura and not forcar:
            return          # nada mudou: não refaz (era isso que fazia piscar)
        self.assinatura = ass
        for w in self.lista.winfo_children():
            w.destroy()
        if not gs:
            l = tk.Label(self.lista, bg=self.FUNDO, bd=0); l.pack(anchor="w"); self._texto(l, "NENHUMA AINDA", "cinza")
        for g in gs:
            ln = tk.Frame(self.lista, bg="#121217", highlightthickness=0); ln.pack(fill="x", pady=2)
            d = g["dur"]; dur = "%d:%02d" % (int(d) // 60, int(d) % 60) if d else "GRAVANDO"
            q = g["quando"]      # 2026-10-19 15:31 → 19/10 15:31
            q = "%s/%s %s" % (q[8:10], q[5:7], q[11:16]) if len(q) >= 16 else q
            l = tk.Label(ln, bg="#121217", bd=0); l.pack(side="left", padx=8, pady=6)
            self._texto(l, "%s · %s · %s" % (q, g["tipo"], dur), "branco")
            esta = grav_pasta and os.path.normcase(g["pasta"]) == grav_pasta
            if not esta:
                b = self._botao(ln, 120, 26, lambda g=g: (descartar(g), self.montar_lista(forcar=True))); b.pack(side="right", padx=(4, 4), pady=3)
                self._pintar(b, "perigo", "DESCARTAR")
            b = self._botao(ln, 80, 26, lambda g=g: os.startfile(g["pasta"])); b.pack(side="right", pady=3)
            self._pintar(b, "mini", "ABRIR")

    def tique(self):
        if not self.vivo():
            self.tela.painel = None; return
        if getattr(self, "_capturando", False) and getattr(self, "_cap_r", None) is not None:
            r, self._cap_r = self._cap_r, None; self._fim_troca(r)
        if getattr(self, "_procurando", False) and getattr(self, "_atual_r", None) is not None:
            r, self._atual_r = self._atual_r, None; self._fim_procura(r)
        elif not getattr(self, "_procurando", False) and getattr(self, "_nova_pintada", "?") != atualizar.NOVA:
            self._pintar_atual()            # o vigia achou versão nova enquanto a janelinha estava aberta
        grav = bool(self.tela.quem); agora = time.time()
        if grav and agora - self.ult_giro > 0.09:
            self.ult_giro = agora; self.giro_i = (self.giro_i + 1) % 12
            self.lb_olho.configure(image=self.olho_g["giro"][self.giro_i])
        elif not grav and getattr(self, "_olho_parado", False) is False:
            self.lb_olho.configure(image=self.olho_g["olho"])
        self._olho_parado = not grav
        s_ = int(agora - self.tela.desde) if (grav and self.tela.desde) else 0
        crono = "%02d:%02d" % (s_ // 60 % 100, s_ % 60)
        if getattr(self, "_crono", None) != crono:
            self._crono = crono; self._texto(self.lb_crono, crono, "branco", 5)
        quem = {"pc": "PC", "app_pessoal": "APP_PESSOAL", "premiere": "PREMIERE"}.get(self.tela.quem, "")
        mudo = grav and self.tela.mudo
        pausa = grav and self.tela.pausado
        est = ("gravando", quem, mudo, pausa) if grav else ("parado",)
        if est != self.estado_bt:
            self.estado_bt = est
            self.ponto.configure(bg=("#FFE600" if pausa else "#5b5b63" if mudo else "#ff1e2e") if grav else "#39d353")
            self._texto(self.lb_status, ("PAUSADO · " + quem if pausa else "GRAVANDO · " + quem + (" · SEM SOM" if mudo else "")) if grav
                        else "PRONTO · NADA GRAVANDO", ("amarelo" if pausa else "vermelho" if mudo else "branco") if grav else "cinza")
            if grav and self.tela.quem in ("pc", "premiere"):     # 04/11: o Premiere também pausa/continua daqui
                self._pintar(self.bt_grav, "vermelho" if pausa else "neutro", "CONTINUAR" if pausa else "PAUSAR", 3)
                self._pintar(self.bt_conc, "concluir", "CONCLUIR")
            else:
                self._pintar(self.bt_grav, "concluir" if grav else "vermelho", "CONCLUIR" if grav else "INICIAR", 3)
                self._pintar(self.bt_conc, "off", "CONCLUIR")
            self._pintar(self.bt_canc, "mini" if grav else "off", "CANCELAR")
        if agora - self.ult_trilho > 0.25:
            self.ult_trilho = agora; self._desenhar_trilho()
        if agora - self.ult_lista > 3:
            self.montar_lista()


def main():
    painel = "--painel" in sys.argv
    if MAC:      # um Kakashi só: trava num arquivo (some sozinha quando o processo fecha)
        import fcntl
        global _TRAVA
        _TRAVA = open(os.path.join(AQUI, "kakashi.trava"), "w")
        try:
            fcntl.flock(_TRAVA, fcntl.LOCK_EX | fcntl.LOCK_NB); ja_tem = False
        except OSError:
            ja_tem = True
    else:
        kernel32.CreateMutexW(None, False, "Global\\KakashiUnicoLuan")
        ja_tem = kernel32.GetLastError() == 183
    if ja_tem:      # já tem um aberto: só pede pra ele abrir a janelinha
        if painel:
            open(FLAG_PAINEL, "w").close()
        return
    if painel:
        open(FLAG_PAINEL, "w").close()
    os.makedirs(SESSOES, exist_ok=True)
    fila = queue.Queue()
    threading.Thread(target=thread_atalhos_mac if MAC else thread_atalhos, args=(fila,), daemon=True).start()
    if not MAC:     # a atualização pelo GitHub ainda não foi portada pro Mac (porte do Gu, 02/11)
        threading.Thread(target=atualizar.vigia, args=(FLAG_PAINEL, cfg, salvar_cfg, log), daemon=True).start()   # pacote da Fly
    log("ligado")
    k = Kakashi()
    threading.Thread(target=servidor, args=(k,), daemon=True).start()
    Tela(k, fila).root.mainloop()


if __name__ == "__main__":
    main()
