# -*- coding: utf-8 -*-
"""KAKASHI da Fly no MAC — instala NA PRÓPRIA PASTA DO CLONE (git clone https://github.com/luancarvalho-fly/kakashi).
14/11/2026: até aqui o Mac era só à mão (MAC.md) e o painel do Premiere nunca chegava em quem não montava o .ccx sozinho (o Gu:
«não tenho acesso ao aplicativo do Kakashi no Mac, o painel»). O instalar.py chama este arquivo quando roda num Mac.

  python3 instalar.py                       → instala tudo (o mesmo comando do Windows)
  python3 instalar.py --atalho f1           → com o atalho que a pessoa escolheu (no teclado do Mac: fn+F1)
  python3 instalar.py --sem-premiere        → sem o painel do Premiere
  python3 instalar.py --sem-ligar           → não liga com o Mac (LaunchAgents) nem abre nada agora
  python3 instalar.py --desinstalar         → tira o app, os LaunchAgents, o painel e a skill; as gravações ficam
  python3 instalar.py --so-atualizar        → depois de um git pull: bibliotecas, painel, skill e reinicia (o atualizar.py chama)

O que faz, peça por peça:
 1. confere Python ≥ 3.10 com Tk, o ffmpeg e o swiftc (as Command Line Tools do Xcode);
 2. cria o Python só dele (.venv) com as bibliotecas do Mac (requirements.txt: as do Mac entram sozinhas);
 3. compila o som do Mac (som_mac/som_do_mac.swift → ScreenCaptureKit, sem driver);
 4. grava o atalho no config.json (padrão no Mac: f1);
 5. o PAINEL DO PREMIERE: monta o .ccx e instala pelo instalador de plugins da Adobe (UPIA do Mac); sem UPIA, abre o .ccx no
    Creative Cloud (dois cliques); o servidor do painel (porta 7815) liga junto;
 6. o APP «KAKASHI» em ~/Applications (Launchpad / Spotlight) e FIXADO NO DOCK uma vez (14/11): abre a janelinha do Kakashi;
    e o Kakashi, quando liga, põe o olho dele na BARRA DE MENU lá em cima (clique = a janelinha);
 7. liga com o Mac: dois LaunchAgents (com.flymedia.kakashi e com.flymedia.kakashi.premiere, só religam se caírem);
    os LaunchAgents antigos feitos à mão que apontam pra ESTA pasta são desligados e guardados com «.antes-instalador»;
 8. a skill /kakashi no Claude Code com os caminhos do Mac;
 9. lembra as permissões (Gravação de Tela, Acessibilidade, Microfone, Automação) — só a pessoa libera, nos Ajustes."""
import datetime, glob, hashlib, json, os, plistlib, re, shutil, subprocess, sys, tempfile, urllib.parse

UPIA_MAC = ("/Library/Application Support/Adobe/Adobe Desktop Common/RemoteComponents/UPI/UnifiedPluginInstallerAgent/"
            "UnifiedPluginInstallerAgent.app/Contents/MacOS/UnifiedPluginInstallerAgent")
ROTULOS = {"kakashi": "com.flymedia.kakashi", "premiere": "com.flymedia.kakashi.premiere"}
AGENTES = os.path.expanduser("~/Library/LaunchAgents")
APP = os.path.expanduser("~/Applications/KAKASHI.app")
LIBS_MAC = ["pillow", "psutil", "numpy", "pyobjc-framework-Quartz", "pyobjc-framework-Cocoa", "pyobjc-framework-ApplicationServices"]


def _uid():
    return str(os.getuid())


def _venv(dest):
    return os.path.join(dest, ".venv", "bin", "python")


def conferir_programas():
    if sys.version_info < (3, 10):
        sys.exit("Precisa do Python 3.10 ou mais novo:  brew install python@3.14 python-tk@3.14  e rode de novo com python3.14.")
    try:
        import tkinter
        tkinter.Tcl()
    except Exception:
        v = "%d.%d" % sys.version_info[:2]
        sys.exit("Este Python não tem o Tk (a barra e a janelinha do Kakashi):  brew install python-tk@%s  e rode de novo." % v)
    if not shutil.which("ffmpeg"):
        sys.exit("Falta o ffmpeg:  brew install ffmpeg  e rode de novo.")
    if not shutil.which("swiftc"):
        print("  AVISO: falta o swiftc (xcode-select --install): sem ele o SOM DO MAC não é gravado (a voz e a tela sim).")


def criar_venv(dest):
    py = _venv(dest)
    if not os.path.isfile(py):
        subprocess.run([sys.executable, "-m", "venv", os.path.join(dest, ".venv")], check=True)
    print("  instalando as bibliotecas do Mac (1 a 3 min)...")
    subprocess.run([py, "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", os.path.join(dest, "requirements.txt")],
                   check=True)
    subprocess.run([py, "-m", "pip", "install", "--disable-pip-version-check", "-q"] + LIBS_MAC, check=True)
    return py


def compilar_som(dest):
    src = os.path.join(dest, "som_mac", "som_do_mac.swift")
    exe = os.path.join(dest, "som_mac", "som_do_mac")
    if not os.path.isfile(src) or not shutil.which("swiftc"):
        return False
    # 14/11 (Claude do Gu): pela DATA, o clone novo (o .swift com a data do clone) recompilava à toa, e binário novo = o macOS pede
    # de novo a permissão de gravar o som. Agora pelo CONTEÚDO: o hash do .swift fica ao lado do binário.
    marca = exe + ".fonte.sha256"
    h = hashlib.sha256(open(src, "rb").read()).hexdigest()
    existia = os.path.isfile(exe)
    if existia:
        antes = open(marca, encoding="utf-8").read().strip() if os.path.isfile(marca) else None
        if antes == h:
            return True
        if antes is None:          # binário de antes desta regra (já liberado no macOS): vale como compilado deste fonte
            open(marca, "w", encoding="utf-8").write(h + "\n")
            print("  som do Mac: binário que já estava mantido (marquei o fonte; recompila só quando o .swift mudar)")
            return True
    r = subprocess.run(["swiftc", "-O", "-o", exe, src], capture_output=True, text=True)
    if r.returncode != 0:
        print("  AVISO: o som do Mac não compilou:", (r.stdout + r.stderr).strip()[-300:])
        return False
    open(marca, "w", encoding="utf-8").write(h + "\n")
    print("  som do Mac compilado (som_mac/som_do_mac)%s" % (" — o .swift mudou: o macOS pode pedir de novo a permissão de gravar o "
                                                            "som (Ajustes → Privacidade → Gravação de Tela e Áudio do Sistema)"
                                                            if existia else ""))
    return True


def ler_cfg(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gravar_cfg(p, c):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


def escolher_atalho(dest, pedido):
    cfgp = os.path.join(dest, "config.json")
    c = ler_cfg(cfgp)
    txt = pedido or c.get("atalho_mac") or "f1"           # no Mac não tem Page Down no teclado: padrão f1 (fn+F1)
    sys.path.insert(0, dest)
    try:
        import atalho
        a = atalho.ler(txt)
        txt, nome = a["texto"], a["nome"]
    except Exception as e:
        if pedido:
            sys.exit("O atalho «%s» não vale aqui: %s. Rode de novo com --atalho f1 (ou outra tecla)." % (txt, e))
        nome = txt.upper()
    c["atalho"] = txt; c["atalho_mac"] = txt; c.pop("atalho_cancelar", None)
    c.setdefault("replay", False)                           # o replay ainda não foi provado no Mac (MAC.md)
    gravar_cfg(cfgp, c)
    return nome


# ---------------------------------------------------------------- o painel do Premiere
def montar_ccx(dest, ccx):
    import zipfile
    painel = os.path.join(dest, "premiere", "painel")
    with zipfile.ZipFile(ccx, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ("manifest.json", "index.html", "main.js"):
            z.write(os.path.join(painel, n), n)
        for raiz, _, arqs in os.walk(os.path.join(painel, "icones")):
            for a in arqs:
                if a.endswith(".png"):
                    p = os.path.join(raiz, a)
                    z.write(p, os.path.relpath(p, painel).replace(os.sep, "/"))
    return ccx


def instalar_painel(dest):
    ccx = montar_ccx(dest, os.path.join(tempfile.gettempdir(), "KAKASHI-Fly.ccx"))
    if os.path.isfile(UPIA_MAC):
        # desinstalar antes: com o mesmo id+versão o instalador da Adobe PULA a troca e ainda diz que deu certo (lição do DUBX)
        subprocess.run([UPIA_MAC, "--remove", "KAKASHI"], capture_output=True)
        r = subprocess.run([UPIA_MAC, "--install", ccx], capture_output=True, text=True, errors="replace")
        saida = (r.stdout + r.stderr).strip()
        if r.returncode == 0 and "fail" not in saida.lower():
            print("  Premiere: painel KAKASHI instalado (Janela > Plugins > KAKASHI). Feche e abra o Premiere se ele estava aberto.")
            return True
        print("  Premiere: o instalador da Adobe recusou (%s). Tentando pelo Creative Cloud..." % saida[-200:])
    else:
        print("  Premiere: não achei o instalador de plugins da Adobe; abrindo o .ccx no Creative Cloud...")
    copia = ccx                             # fica na pasta temporária (nada novo dentro do clone)
    r = subprocess.run(["open", copia], capture_output=True, text=True)
    if r.returncode == 0:
        print("  Premiere: o Creative Cloud abriu o painel: clique em INSTALAR na janela dele (arquivo: %s)." % copia)
        return True
    print("  Premiere: não consegui instalar o painel. Instale à mão: dois cliques em %s, ou pelo UXP Developer Tool." % copia)
    return False


# ---------------------------------------------------------------- o app «KAKASHI» (a janelinha)
def criar_app(dest, py):
    """~/Applications/KAKASHI.app: um app de verdade (Launchpad, Spotlight, Dock) que abre a janelinha do Kakashi.
    Se o Kakashi já estiver ligado, só pede pra ele abrir a janelinha (o mesmo --painel do atalho do Windows)."""
    cont = os.path.join(APP, "Contents")
    if os.path.isdir(APP):
        shutil.rmtree(APP)
    os.makedirs(os.path.join(cont, "MacOS")); os.makedirs(os.path.join(cont, "Resources"))
    exe = os.path.join(cont, "MacOS", "KAKASHI")
    with open(exe, "w", encoding="utf-8") as f:
        f.write('#!/bin/sh\ncd "%s"\nexec "%s" "%s" --painel\n' % (dest, py, os.path.join(dest, "kakashi.pyw")))
    os.chmod(exe, 0o755)
    info = {"CFBundleName": "KAKASHI", "CFBundleDisplayName": "KAKASHI", "CFBundleIdentifier": "com.flymedia.kakashi.app",
            "CFBundleExecutable": "KAKASHI", "CFBundlePackageType": "APPL", "CFBundleVersion": "1", "CFBundleShortVersionString": "1",
            "CFBundleIconFile": "kakashi", "LSUIElement": False, "NSHighResolutionCapable": True,
            "NSMicrophoneUsageDescription": "O Kakashi grava a sua voz enquanto você mostra a correção."}
    with open(os.path.join(cont, "Info.plist"), "wb") as f:
        plistlib.dump(info, f)
    icones = os.path.join(dest, "painel", "icones")
    fonte = next((p for p in (os.path.join(icones, "olho.png"), os.path.join(icones, "icone_48@2x.png")) if os.path.isfile(p)), None)
    if fonte:
        subprocess.run(["sips", "-s", "format", "icns", fonte, "--out", os.path.join(cont, "Resources", "kakashi.icns")],
                       capture_output=True)
    subprocess.run(["touch", APP], capture_output=True)     # o Finder relê o ícone
    print("  app KAKASHI em ~/Applications (Launchpad / Spotlight: «KAKASHI»): abre a janelinha")


def fixar_no_dock(dest):
    """14/11 (o Luan: «pra pessoa ter acesso ao painel, igual fica na barra de tarefa»): o app KAKASHI fixado no Dock, UMA vez por
    instalação (config "dock_fixado"): se a pessoa tirar do Dock depois, a atualização não põe de volta. O olho na barra de menu lá
    em cima é o outro caminho (o Kakashi põe sozinho quando liga)."""
    cfgp = os.path.join(dest, "config.json")
    c = ler_cfg(cfgp)
    if c.get("dock_fixado") or c.get("dock") is False:
        return
    r = subprocess.run(["defaults", "read", "com.apple.dock", "persistent-apps"], capture_output=True, text=True)
    if "KAKASHI.app" not in (r.stdout or ""):
        url = "file://" + urllib.parse.quote(APP) + "/"
        entrada = ("<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>%s</string>"
                   "<key>_CFURLStringType</key><integer>15</integer></dict></dict></dict>" % url)
        w = subprocess.run(["defaults", "write", "com.apple.dock", "persistent-apps", "-array-add", entrada], capture_output=True, text=True)
        if w.returncode != 0:
            print("  AVISO: não fixei o KAKASHI no Dock (%s): arraste o app de ~/Applications pro Dock" % (w.stderr or "").strip()[-120:])
            return
        subprocess.run(["killall", "Dock"], capture_output=True)       # o Dock relê a lista (some e volta em 1 s)
        print("  app KAKASHI fixado no Dock (clique = abre o painel); o olho do Kakashi também fica na barra de menu, lá em cima")
    c["dock_fixado"] = True
    gravar_cfg(cfgp, c)


# ---------------------------------------------------------------- ligar com o Mac
def _plist(rotulo, py, script, pasta, log):
    return {"Label": rotulo, "ProgramArguments": [py, script], "WorkingDirectory": pasta, "RunAtLoad": True,
            "KeepAlive": {"SuccessfulExit": False}, "ThrottleInterval": 10,
            "ProcessType": "Interactive",       # 14/11 (Claude do Gu): os feitos à mão tinham; sem ele o macOS pode frear a gravação
            "EnvironmentVariables": {"PYTHONUTF8": "1", "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
            "StandardOutPath": log, "StandardErrorPath": log}


def _desligar(caminho, rotulo=None):
    alvo = ("gui/%s/%s" % (_uid(), rotulo)) if rotulo else None
    subprocess.run(["launchctl", "bootout", "gui/" + _uid(), caminho], capture_output=True)
    if alvo:
        subprocess.run(["launchctl", "bootout", alvo], capture_output=True)


def agentes_antigos(dest):
    """os LaunchAgents feitos à mão (antes do instalador) que rodam o kakashi.pyw ou o servidor.py DESTA pasta"""
    out = []
    for p in glob.glob(os.path.join(AGENTES, "*.plist")):
        try:
            d = plistlib.load(open(p, "rb"))
        except Exception:
            continue
        if d.get("Label") in ROTULOS.values():
            continue
        args = " ".join(d.get("ProgramArguments") or [d.get("Program", "")])
        if dest in args and ("kakashi.pyw" in args or "servidor.py" in args):
            out.append((p, d.get("Label")))
    return out


def ligar(dest, py, com_premiere):
    os.makedirs(AGENTES, exist_ok=True)
    data = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    for p, rot in agentes_antigos(dest):
        _desligar(p, rot)
        shutil.move(p, p + ".antes-instalador-" + data)
        print("  LaunchAgent antigo desligado e guardado: %s (.antes-instalador-%s)" % (os.path.basename(p), data))
    itens = [("kakashi", os.path.join(dest, "kakashi.pyw"), dest)]
    if com_premiere:
        itens.append(("premiere", os.path.join(dest, "premiere", "servidor.py"), os.path.join(dest, "premiere")))
    for chave, script, pasta in itens:
        rot = ROTULOS[chave]
        caminho = os.path.join(AGENTES, rot + ".plist")
        _desligar(caminho, rot)
        with open(caminho, "wb") as f:
            plistlib.dump(_plist(rot, py, script, pasta, os.path.join(pasta, chave + "-launchd.log")), f)
        r = subprocess.run(["launchctl", "bootstrap", "gui/" + _uid(), caminho], capture_output=True, text=True)
        print("  liga com o Mac: %s %s" % (rot, "OK" if r.returncode == 0 else "FALHOU (%s)" % (r.stderr.strip()[-160:])))


def plists_mudaram(dest, py, com_premiere):
    """algum LaunchAgent do pacote já instalado está diferente do que o ligar() escreveria agora? (instalação sem ligar = não cria)"""
    itens = [("kakashi", os.path.join(dest, "kakashi.pyw"), dest)]
    if com_premiere:
        itens.append(("premiere", os.path.join(dest, "premiere", "servidor.py"), os.path.join(dest, "premiere")))
    for chave, script, pasta in itens:
        rot = ROTULOS[chave]
        caminho = os.path.join(AGENTES, rot + ".plist")
        if not os.path.isfile(caminho):
            continue
        try:
            with open(caminho, "rb") as f:
                atual = plistlib.load(f)
        except Exception:
            return True
        if atual != _plist(rot, py, script, pasta, os.path.join(pasta, chave + "-launchd.log")):
            return True
    return False


def reiniciar(com_premiere):
    for chave in (("kakashi", "premiere") if com_premiere else ("kakashi",)):
        subprocess.run(["launchctl", "kickstart", "-k", "gui/%s/%s" % (_uid(), ROTULOS[chave])], capture_output=True)


# ---------------------------------------------------------------- a skill /kakashi
GUARDADAS = os.path.expanduser("~/.claude/skills-guardadas")     # 14/11 (Claude do Gu): guardar DENTRO de skills/ = 2 skills /kakashi


def _guardar(caminho):
    """skill antiga → ~/.claude/skills-guardadas/<nome>.antiga-<data> (fora de skills/: o Claude Code não vê duas /kakashi)"""
    os.makedirs(GUARDADAS, exist_ok=True)
    nome = os.path.basename(caminho)
    if ".antiga-" not in nome:                 # a que estava em uso ganha a data; a que já era antiga fica com o nome dela
        nome += ".antiga-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest, k = os.path.join(GUARDADAS, nome), 2
    while os.path.exists(dest):                # nunca dentro de outra (shutil.move numa pasta que existe = vai pra dentro)
        dest, k = os.path.join(GUARDADAS, "%s-%d" % (nome, k)), k + 1
    shutil.move(caminho, dest)
    return dest


def texto_mac(txt, dest, nome_at):
    """a skill do Windows com os caminhos e o jeito do Mac (14/11: antes só ia um aviso «troque \\ por /» no topo do SKILL.md)"""
    tecla = nome_at.upper()
    fn = ("fn+%s" % tecla) if re.fullmatch(r"F\d{1,2}", tecla) else tecla
    pares = [
        ("`%LOCALAPPDATA%\\Programs\\Kakashi-Fly\\`", "`%s/`" % dest),
        ("%LOCALAPPDATA%\\Programs\\Kakashi-Fly", dest),
        (".venv\\Scripts\\python.exe", ".venv/bin/python"),
        ("o padrão é Ctrl+Page Down, e cada um escolhe o seu",
         "neste Mac é %s (no teclado do Mac: %s; com Shift junto, cancela), e cada um escolhe o seu" % (tecla, fn)),
        ("botão ATUALIZAR na janelinha (atalho KAKASHI na área de trabalho)",
         "botão de atualizar na janelinha (app KAKASHI, no Launchpad/Spotlight) ou `.venv/bin/python atualizar.py --instalar` na pasta"),
        ("(atalho KAKASHI na área de trabalho)", "(app KAKASHI, no Launchpad/Spotlight)"),
        ("por cima de qualquer app (Windows).", "por cima de qualquer app (só no Windows por enquanto: no Mac a barra não desenha)."),
    ]
    for a, b in pares:
        txt = txt.replace(a, b)
    # o resto: caminho com \ dentro de crase vira / (só dentro das crases: fora delas o \ pode ser texto)
    txt = re.sub(r"`[^`\n]*\\[^`\n]*`", lambda m: m.group(0).replace("\\", "/"), txt)
    return txt


def instalar_skill(dest, trocar, marca, nome_at="F1"):
    """a pasta skill/ INTEIRA (SKILL.md cita GLOSSARIO.md e PROMPT-MOLDE.md «desta pasta da skill») com o texto do Mac em todo .md.
    A que já estava (mesmo a do pacote, que pode ter ajuste à mão) vai pra ~/.claude/skills-guardadas se mudar alguma coisa."""
    alvo = os.path.expanduser("~/.claude/skills/kakashi")
    base = os.path.dirname(alvo)
    for velha in [os.path.join(base, x) for x in (os.listdir(base) if os.path.isdir(base) else []) if x.startswith("kakashi.antiga-")]:
        print("  skill antiga que estava dentro de skills/ (o Claude Code via duas /kakashi) → %s" % _guardar(velha))
    if os.path.isdir(alvo) and not os.path.exists(os.path.join(alvo, marca)):
        if not trocar:
            print("  SKILL: já existe uma /kakashi neste Claude Code que NÃO veio deste pacote: deixei como está.\n"
                  "         Pra trocar pela do pacote: rode de novo com --trocar-skill (a antiga vai pra ~/.claude/skills-guardadas).")
            return False
    origem = os.path.join(dest, "skill")
    novos = {}
    for raiz, _, arqs in os.walk(origem):
        for n in arqs:
            if n.endswith((".pyc",)) or "__pycache__" in raiz:
                continue
            rel = os.path.relpath(os.path.join(raiz, n), origem)
            b = open(os.path.join(raiz, n), "rb").read()
            if n.endswith(".md"):
                b = texto_mac(b.decode("utf-8"), dest, nome_at).encode("utf-8")
            novos[rel] = b
    novos[marca] = (dest + "\n").encode("utf-8")
    if os.path.isdir(alvo):
        atuais = {}
        for raiz, _, arqs in os.walk(alvo):
            for n in arqs:
                atuais[os.path.relpath(os.path.join(raiz, n), alvo)] = open(os.path.join(raiz, n), "rb").read()
        if atuais == novos:
            print("  skill /kakashi já estava igual (caminhos do Mac)")
            return True
        print("  skill /kakashi anterior guardada em %s" % _guardar(alvo))
    for rel, b in novos.items():
        os.makedirs(os.path.dirname(os.path.join(alvo, rel)), exist_ok=True)
        open(os.path.join(alvo, rel), "wb").write(b)
    sobra = [rel for rel, b in novos.items() if rel.endswith(".md") and (b"%LOCALAPPDATA%" in b or b"Scripts\\python.exe" in b)]
    if sobra:
        print("  AVISO: ainda tem caminho do Windows em %s" % ", ".join(sobra))
    print("  skill /kakashi instalada no Claude Code: a pasta inteira (%d arquivos), caminhos do Mac" % (len(novos) - 1))
    return True


def lembrar_permissoes(py):
    real = os.path.realpath(py)
    print()
    print("PERMISSÕES (só você libera, uma vez): Ajustes do Sistema → Privacidade e Segurança → dê ao Python abaixo:")
    print("  Gravação de Tela e Áudio do Sistema · Acessibilidade · Microfone · Automação (pro link da aba da frente)")
    print("  Python:", real)
    print("  Se o Homebrew atualizar o Python, o macOS pede de novo.")
    try:
        subprocess.run([py, "-c", "import mac; mac.pedir_permissao()"], cwd=os.path.dirname(os.path.dirname(os.path.dirname(py))),
                       capture_output=True, timeout=20)
    except Exception:
        pass


# ---------------------------------------------------------------- os comandos
def desinstalar(dest, marca):
    for chave, rot in ROTULOS.items():
        caminho = os.path.join(AGENTES, rot + ".plist")
        _desligar(caminho, rot)
        if os.path.isfile(caminho):
            os.remove(caminho)
    if os.path.isdir(APP):
        shutil.rmtree(APP)
    alvo = os.path.expanduser("~/.claude/skills/kakashi")
    if os.path.exists(os.path.join(alvo, marca)):
        shutil.rmtree(alvo)
    if os.path.isfile(UPIA_MAC):
        subprocess.run([UPIA_MAC, "--remove", "KAKASHI"], capture_output=True)
    print("App, LaunchAgents, painel e skill removidos. As gravações continuam em %s (e a pasta do clone fica)." % os.path.join(dest, "sessoes"))


def main(a, marca, dest):
    """a = os argumentos do instalar.py (o mesmo argparse do Windows + --so-atualizar); dest = a pasta do clone (onde o instalar.py está)"""
    if a.desinstalar:
        return desinstalar(dest, marca)
    conferir_programas()
    print("KAKASHI da Fly no Mac → %s" % dest)
    for s in ("sessoes", os.path.join("premiere", "sessoes")):
        os.makedirs(os.path.join(dest, s), exist_ok=True)
    py = criar_venv(dest)
    compilar_som(dest)
    cfgp = os.path.join(dest, "config.json")
    c = ler_cfg(cfgp)
    if a.transcricao:
        c["transcricao"] = a.transcricao; gravar_cfg(cfgp, c)
    if c.get("transcricao") in ("tandera", "local"):
        t = a.tandera or c.get("tandera") or os.path.join(os.path.dirname(dest), "tandera")
        if os.path.isfile(os.path.join(t, "tandera", "manifesto.py")):
            c["tandera"] = os.path.abspath(t); gravar_cfg(cfgp, c)
            print("  transcrição pelo Tandera em %s" % c["tandera"])
        else:
            print("  AVISO: não achei a pasta do Tandera: escreva o caminho no config.json → \"tandera\"")
    nome_at = escolher_atalho(dest, a.atalho)
    c = ler_cfg(cfgp)
    if a.sem_premiere and not a.so_atualizar:
        c["premiere"] = False; gravar_cfg(cfgp, c)
    com_premiere = not (a.sem_premiere or c.get("premiere") is False)
    tem_painel = instalar_painel(dest) if com_premiere else False
    criar_app(dest, py)
    fixar_no_dock(dest)
    skill_ok = False if a.sem_skill else instalar_skill(dest, a.trocar_skill, marca, nome_at)
    if a.so_atualizar:
        # 14/11 (Claude do Gu: o ProcessType não voltou ao atualizar): LaunchAgent do pacote que existe e ficou diferente do que
        # esta versão escreveria = religa com o novo (o ligar já reinicia); igual = só reinicia, como antes
        if plists_mudaram(dest, py, com_premiere):
            print("  os LaunchAgents mudaram nesta versão: religando com o novo")
            ligar(dest, py, com_premiere)
        else:
            reiniciar(com_premiere)
        print("Atualizado e reiniciado.")
        return
    if not a.sem_ligar:
        ligar(dest, py, com_premiere)
    lembrar_permissoes(py)
    print()
    print("Pronto. %s começa e conclui uma gravação (no teclado do Mac, F1 = fn+F1); o botão direito na barra cancela." % nome_at)
    print("A janelinha: o app KAKASHI (Launchpad / Spotlight). Trocar o atalho: lá dentro, TROCAR O ATALHO.")
    print("Painel do Premiere: %s." % ("instalado" if tem_painel else "não instalado"))
    print("Depois de gravar, no Claude Code: /kakashi%s" % ("" if skill_ok or a.sem_skill else " (a skill não foi instalada: ver o aviso acima)"))
