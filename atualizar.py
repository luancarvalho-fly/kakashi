# -*- coding: utf-8 -*-
"""ATUALIZAÇÃO do KAKASHI da Fly (27/10/2026; 03/11: o Kakashi e o Tandera viraram repositórios separados).

Ele (27/10): «conforme eu for atualizando o Kakashi e o Tandera, tem como ir mandando notificação ou subindo atualização para as pessoas
que estão usando...?» e «melhor colocar no da fly publico pra galera». O pacote mora num repositório PÚBLICO do GitHub da Fly; cada
versão é uma etiqueta vAAAA.MM.DD (ou vAAAA.MM.DD.N). Não precisa de conta, login nem Git: só internet.

  python atualizar.py --checar     → EM DIA (versão) | NOVA: <versão> (você tem <versão>) | ERRO: <motivo>
  python atualizar.py --instalar   → baixa a versão nova e roda o instalador dela (atalho, config e gravações ficam)
O Kakashi confere sozinho (vigia()) 1,5 min depois de ligar e a cada 12 h; achou versão nova, abre a janelinha UMA vez com o botão
ATUALIZAR. A skill /kakashi (e a /tandera) também confere no passo 0.
"""
import json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile

# 03/11 (ele: «Uma coisa Kakashi, outra [Tandera]»): o Kakashi mora em luancarvalho-fly/kakashi; o Tandera em luancarvalho-fly/tandera
# (atualiza por git pull). Quem instalou pelo kakashi-tandera de outubro recebe lá uma última versão com ESTE arquivo e passa a vir daqui.
REPO = "luancarvalho-fly/kakashi"
AQUI = os.path.dirname(os.path.abspath(__file__))
ETIQUETA = re.compile(r"^v(\d{4})\.(\d{2})\.(\d{2})(?:\.(\d+))?$")
NOVA = None             # versão nova achada pela última conferência (a janelinha lê daqui)


def versao_local():
    try:
        return open(os.path.join(AQUI, "VERSAO.txt"), encoding="utf-8").read().strip()
    except OSError:
        return "0000.00.00"


def _num(v):
    m = ETIQUETA.match("v" + v.lstrip("v"))
    return tuple(int(x or 0) for x in m.groups()) if m else (0,)


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "kakashi-atualizar", "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(req, timeout=timeout)


def checar():
    """{"estado": "nova" | "em_dia" | "erro", "versao": a mais nova do GitHub, "local": a instalada, "msg": ...}"""
    global NOVA
    local = versao_local()
    try:
        tags = json.load(_get("https://api.github.com/repos/%s/tags?per_page=100" % REPO))
    except Exception as e:
        return {"estado": "erro", "local": local, "msg": "sem internet ou GitHub fora do ar (%s)" % str(e)[:80]}
    versoes = [t["name"].lstrip("v") for t in tags if ETIQUETA.match(t.get("name", ""))]
    if not versoes:
        return {"estado": "erro", "local": local, "msg": "nenhuma versão publicada ainda"}
    mais = max(versoes, key=_num)
    if _num(mais) > _num(local):
        NOVA = mais
        return {"estado": "nova", "versao": mais, "local": local}
    NOVA = None
    return {"estado": "em_dia", "versao": mais, "local": local}


def _gravando():
    for porta in (7816, 7815):
        try:
            if json.load(urllib.request.urlopen("http://127.0.0.1:%d/status" % porta, timeout=2)).get("estado") in ("gravando", "pausado"):
                return True
        except Exception:
            pass
    return False


def vigia(flag_painel, cfg, salvar_cfg, log):
    """roda numa thread do kakashi.pyw: confere e, achando versão nova (e ninguém gravando), abre a janelinha UMA vez por versão."""
    time.sleep(90)
    while True:
        try:
            r = checar()
            if r["estado"] == "nova":
                c = cfg()
                if c.get("atualizacao_avisada") != r["versao"] and not _gravando():
                    c["atualizacao_avisada"] = r["versao"]; salvar_cfg(c)
                    open(flag_painel, "w").close()
                    log("atualização: versão nova %s (instalada %s) → abri a janelinha" % (r["versao"], r["local"]))
        except Exception as e:
            log("atualização: %s" % e)
        time.sleep(12 * 3600)


def abrir_instalador_em_janela():
    """a janelinha chama isto: o atualizador roda numa janela preta à parte (ele fecha e reabre o Kakashi no fim)."""
    if sys.platform == "darwin":       # 04/11 (Mac do Gu): sem janela de console no Mac — roda escondido e escreve em atualizar.log
        with open(os.path.join(AQUI, "atualizar.log"), "a", encoding="utf-8") as log:
            subprocess.Popen([sys.executable, os.path.join(AQUI, "atualizar.py"), "--instalar"], cwd=AQUI,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        return
    py = os.path.join(os.path.dirname(sys.executable), "python.exe")
    subprocess.Popen([py if os.path.isfile(py) else sys.executable, os.path.join(AQUI, "atualizar.py"), "--instalar"], cwd=AQUI,
                     creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))


def instalar_mac():
    """04/11 (Mac do Gu): no Mac o Kakashi é um CLONE do repositório (o instalar.py é só do Windows) — atualizar = git pull.
    Os arquivos do Gu (config.json, premiere/config.json, lidas.json) ficam fora do git (skip-worktree), então o pull não mexe neles."""
    if not os.path.isdir(os.path.join(AQUI, ".git")):
        print("No Mac o Kakashi atualiza pelo git, e esta pasta não é um clone do repositório. Siga o MAC.md (instalação à mão).")
        return 1
    r = subprocess.run(["git", "-C", AQUI, "pull", "--ff-only"], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    if r.returncode == 0:
        print("Atualizado (%s). Feche e abra o Kakashi pra valer o código novo." % versao_local())
    return r.returncode


def instalar(teste=False):
    r = checar()
    if sys.platform == "darwin" and r["estado"] == "nova":
        return instalar_mac()
    if r["estado"] != "nova":
        print("Nada pra atualizar:", r.get("msg") or "você já está na versão %s." % r["local"])
        return 0
    v = r["versao"]
    print("Baixando a versão %s (você tem %s)..." % (v, r["local"]))
    tmp = tempfile.mkdtemp(prefix="kakashi-%s-" % v)
    zp = os.path.join(tmp, "pacote.zip")
    with _get("https://github.com/%s/archive/refs/tags/v%s.zip" % (REPO, v), timeout=120) as resp, open(zp, "wb") as f:
        shutil.copyfileobj(resp, f)
    with zipfile.ZipFile(zp) as z:
        z.extractall(tmp)
    pastas = [os.path.join(tmp, d) for d in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, d))]
    antigo = [d for d in pastas if os.path.isfile(os.path.join(d, "instalar_tudo.py"))]       # o kakashi-tandera de outubro
    if antigo:
        cmd = [sys.executable, os.path.join(antigo[0], "instalar_tudo.py"), "--atualizar"]
        if os.path.isfile(os.path.join(AQUI, "kakashi.pyw")):           # este atualizador é o do Kakashi: atualiza ESTA instalação
            cmd += ["--destino-kakashi", AQUI]
        if teste:
            cmd.append("--teste")
        raiz = antigo[0]
    else:                                                             # 03/11: o repositório do Kakashi (o instalar.py na raiz)
        raiz = next(d for d in pastas if os.path.isfile(os.path.join(d, "kakashi.pyw")) and os.path.isfile(os.path.join(d, "instalar.py")))
        cmd = [sys.executable, os.path.join(raiz, "instalar.py"), "--destino", AQUI]
        if teste:
            cmd += ["--sem-ligar", "--sem-skill", "--sem-premiere"]
    cod = subprocess.run(cmd, cwd=raiz).returncode
    shutil.rmtree(tmp, ignore_errors=True)
    return cod


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    if "--checar" in sys.argv:
        r = checar()
        print({"nova": "NOVA: %s (você tem %s)" % (r.get("versao"), r["local"]), "em_dia": "EM DIA (%s)" % r["local"],
               "erro": "ERRO: %s" % r.get("msg")}[r["estado"]])
    elif "--instalar" in sys.argv:
        cod = instalar(teste="--teste" in sys.argv)
        if "--teste" not in sys.argv and sys.stdin and sys.stdin.isatty():      # 04/11: no Mac roda sem janela (sem teclado)
            input("\nPode fechar esta janela (Enter).")
        sys.exit(cod)
    else:
        print(__doc__)
