# KAKASHI no Mac

**Estado (03/11/2026): o código do Mac ESTÁ neste repositório.** Portado e provado pelo Gu (Fly) em 02/11 num MacBook Pro com chip
Apple (macOS 27, Premiere 26.5) e juntado no Kakashi do Luan em 03/11. É o MESMO código do Windows: cada arquivo troca só as peças do
sistema pelas do `mac.py` (`MAC = sys.platform == "darwin"`); a lógica (sessão, relógio, pausa e pedaços, eventos, leitura) é uma só.
O relatório completo do porte, peça por peça, está em `PORTE-MAC-DO-GU.md`.

**Provado no Mac:** o gravador do PC (voz, som do PC, tela, prints do «aqui» na tela Retina, janela da frente, elemento sob o mouse,
link da aba da frente, `/kakashi` colado), cancelar, o painel do Premiere (.ccx + o servidor 7815: corte, trim com ripple, efeito,
ajuste de valor) e ligar com o Mac. **Ainda não:** histórico do Chrome/Safari (o macOS bloqueia o Python; o link vem da aba da frente),
replay, vários monitores (só a tela principal), e o PC check (o instalador e a atualização pelo git chegaram em 14/11, abaixo). A pausa
e os pedaços (PAUSAR / CONTINUAR, APAGAR N) chegaram depois do porte: são a mesma lógica, mas ainda não foram provados num Mac.

## Instalar no Mac (14/11/2026: agora tem INSTALADOR — pro Claude que estiver ajudando, com o «pode» da pessoa)
1. **Programas (Homebrew), uma vez:** `brew install python@3.14 python-tk@3.14 ffmpeg` e `xcode-select --install` (o `swiftc`, pro
   som do Mac).
2. **Pasta:** `git clone https://github.com/luancarvalho-fly/kakashi` onde a pessoa quiser (o Gu usa `~/Documents/FLY MEDIA/Kakashi`).
   Quem já tem o clone: `git pull` antes (guarde o `config.json` e o `premiere/config.json` se não estiverem com skip-worktree).
3. **Instalar:** dentro da pasta, `python3.14 instalar.py` (opções: `--atalho f1`, `--sem-premiere`, `--sem-ligar`,
   `--transcricao tandera --tandera <pasta>`, `--trocar-skill`, `--desinstalar`). Ele faz sozinho:
   - o Python só dele (`.venv`) com as bibliotecas do Mac e o som do Mac compilado (`som_mac/som_do_mac`);
   - o atalho no `config.json` (padrão no Mac: `f1` = fn+F1);
   - **o PAINEL DO PREMIERE**: monta o `.ccx` e instala pelo instalador de plugins da Adobe; sem ele, abre o `.ccx` no Creative Cloud
     (a pessoa clica INSTALAR). No Premiere: Janela > Plugins > KAKASHI. O servidor do painel (porta 7815) liga junto;
   - **o app KAKASHI** em `~/Applications` (Launchpad / Spotlight / Dock): abre a janelinha;
   - liga com o Mac por dois LaunchAgents (`com.flymedia.kakashi` e `com.flymedia.kakashi.premiere`). LaunchAgents feitos à mão antes
     que rodavam ESTA pasta são desligados e guardados com `.antes-instalador-<data>` (nada é apagado);
   - a skill `/kakashi` no Claude Code com os caminhos do Mac.
4. **Permissões** (só a pessoa libera; o instalador mostra qual Python): Ajustes do Sistema → Privacidade e Segurança →
   **Gravação de Tela e Áudio do Sistema**, **Acessibilidade**, **Microfone** e **Automação**. Se o Homebrew atualizar o Python, pede de novo.
5. **A extensão do Chrome** (recomendado; a pessoa clica): `chrome://extensions` → Modo do desenvolvedor → Carregar sem compactação →
   a pasta `chrome/` do clone.
6. **Atualizar:** o botão ATUALIZAÇÃO da janelinha (ou `python3 atualizar.py --instalar`) faz o `git pull` e roda
   `instalar.py --so-atualizar` (bibliotecas, painel, app, skill) e reinicia os dois serviços.
7. **Prova:** grave 10 s falando e mostrando uma página, conclua, e no Claude Code `/kakashi`: o `LEITURA.md` tem que trazer a fala, a
   janela, o print do «aqui», o link e (com a extensão) as linhas «Chrome (parou/clique)». No Premiere: abra o painel KAKASHI, grave
   10 s mexendo num corte e conclua.

**No Mac, por enquanto, sem:** o DESENHO por cima da tela (caneta/seta da barra — o desenho usa janelas do Windows) e o MODO CAPTURA
(Page Down). A barra mostra só o que funciona no Mac. O visual é o 8 BITS (o mesmo do painel do Premiere); `"visual": "grafite"` no
`config.json` troca pro liso.

## O mapa de antes do porte (02/11, referência de cada peça)

**Como ler:** **[CÓDIGO]** = conferido no código · **[SABIDO]** = documentação pública, NÃO testada num Mac · **[TESTAR]** = hipótese.

## O mapa, peça por peça
| peça | o que no código é só Windows (onde) | o caminho no Mac | dificuldade | 1ª versão? |
|---|---|---|---|---|
| todos os .pyw/.py do gravador | `kakashi.pyw` e `olho.py` carregam `ctypes.windll` / `ctypes.wintypes` no topo: **no Mac quebram no `import`** [CÓDIGO] | separar o que é Windows num módulo e escrever o do Mac ao lado (o resto da lógica — sessão, relógio, replay, eventos — é Python comum) | — | — |
| atalho global | `atalho.py` e `kakashi.pyw` (`thread_atalhos`): `user32.RegisterHotKey`, teclas virtuais do Windows [CÓDIGO] | `pynput` (GlobalHotKeys) ou Carbon `RegisterEventHotKey` / Quartz event tap pelo `pyobjc`; precisa de **Acessibilidade** ou **Monitoramento de Entrada** [SABIDO] | média | sim |
| o olho (Sharingan) e a janelinha | `tkinter` (roda no Mac) + `SetWindowPos(HWND_TOPMOST)` e DPI do Windows [CÓDIGO] | tkinter `-topmost` [TESTAR]; se sumir atrás de outra janela, nível da janela pelo `pyobjc` (NSWindow level) [SABIDO] | baixa | sim |
| janela da frente (app + título) | `user32.GetForegroundWindow` + `QueryFullProcessImageNameW` [CÓDIGO] | `NSWorkspace.frontmostApplication` + `CGWindowListCopyWindowInfo` (o título das janelas dos outros apps pede **Gravação de Tela**) [SABIDO] | média | sim |
| tela (5 q/s) | ffmpeg `-f gdigrab -i desktop` [CÓDIGO] | ffmpeg `-f avfoundation -i "<n>:"` («Capture screen 0»), com **Gravação de Tela** [SABIDO]; ou ScreenCaptureKit | média | sim |
| microfone | ffmpeg `-f dshow -i audio=<nome>` + lista do dshow [CÓDIGO] | ffmpeg `-f avfoundation -i ":<n>"` (lista: `ffmpeg -f avfoundation -list_devices true -i ""`), com **Microfone** [SABIDO] | baixa | sim |
| **som do PC** (trilha separada) | `gravar_pc.py`: WASAPI loopback pelo PyAudioWPatch, segue a saída padrão quando ela muda [CÓDIGO] | **o macOS não tem loopback pronto**: (a) **ScreenCaptureKit** (macOS 13+ captura o áudio do sistema; precisa de um pequeno programa Swift ou `pyobjc`) ou (b) um dispositivo virtual (**BlackHole** + «Dispositivo de Saída Múltipla» no *Configuração de Áudio e MIDI* — o Gu instala e clica) [SABIDO] | **alta** | decidir com o Luan (sem ela, a 1ª versão grava só a voz) |
| elemento debaixo do mouse | `olho.py` `UIA`: Windows UI Automation por COM, na mão [CÓDIGO] | Accessibility API (`AXUIElementCopyElementAtPosition`, pelo `pyobjc`), com **Acessibilidade** [SABIDO] | alta | pode ficar fora |
| cliques e caminho do mouse | consulta periódica: `user32.GetCursorPos` + `GetAsyncKeyState` (sem gancho) [CÓDIGO] | a mesma consulta no Mac: `NSEvent.mouseLocation()` + `CGEventSourceButtonState` pelo `pyobjc` [SABIDO]; ou `pynput` (mouse) | média | sim |
| print nativo + recorte | `PIL.ImageGrab.grab(all_screens=True)` + `MonitorFromPoint` [CÓDIGO] | o `ImageGrab` do Pillow funciona no Mac [SABIDO]; o monitor do cursor pelo `NSScreen` [TESTAR] | baixa | sim |
| cópias (+ «senha nunca») | área de transferência do Win32 (formatos, `CanIncludeInClipboardHistory` dos gerenciadores de senha) + a pasta «Capturas de Tela» do Win+Shift+S [CÓDIGO] | `NSPasteboard` (`pyobjc`), pulando os tipos `org.nspasteboard.ConcealedType`/`TransientType` que os gerenciadores de senha marcam [SABIDO]; as capturas ⌘⇧4 vão pra pasta de `defaults read com.apple.screencapture location` (padrão: Mesa) [SABIDO] | média | texto e link sim; imagem depois |
| links do Chrome | `olho.py` lê o `History` (sqlite) do perfil mais usado em `%LOCALAPPDATA%\Google\Chrome\User Data` [CÓDIGO] | o mesmo sqlite em `~/Library/Application Support/Google/Chrome/<perfil>/History` [SABIDO] (Safari pede Acesso Total ao Disco: fora) | baixa | sim |
| colar "/kakashi" ao concluir | `keybd_event` Ctrl+V + clipboard do Win32 [CÓDIGO] | `NSPasteboard` + Cmd+V por `CGEvent` (Acessibilidade) [SABIDO] | baixa | sim |
| replay dos 2 min | ffmpeg `segment` rotativo com dshow/gdigrab [CÓDIGO] | o mesmo com avfoundation [TESTAR] | média | pode ficar fora |
| som do alerta (mic morto) | `winsound.PlaySound` [CÓDIGO] | `afplay sons/sharingan.wav` (vem no macOS) [SABIDO] | baixa | sim |
| processos órfãos | `psutil` [CÓDIGO] | igual (o psutil roda no Mac) [SABIDO] | — | sim |
| ligar com o sistema | atalho `.lnk` na pasta Inicializar (PowerShell/WScript), `pythonw`, `CREATE_NO_WINDOW` [CÓDIGO] | um **LaunchAgent** (`~/Library/LaunchAgents/*.plist` + `launchctl`) — mostre o plist ao Gu e espere o "pode" [SABIDO] | média | depois (no começo, ligar à mão) |
| instalador | `instalar.py`: `%LOCALAPPDATA%`, `venv\Scripts`, `.lnk`, `UnifiedPluginInstallerAgent.exe`, PowerShell; para em quem não é Windows [CÓDIGO] | escrever o do Mac (ou instalar à mão, passo a passo, na pasta que o Gu escolher) | média | à mão |
| atualizar / PC check | `atualizar.py` (vigia o GitHub público da Fly; abre o instalador numa janela preta) · `pc_check.py` (`nvidia-smi`, Windows) [CÓDIGO] | — | — | fora |
| **painel do Premiere** | nada: o `main.js` só usa `require("premierepro")` e `fetch` pra 127.0.0.1:7815; manifest UXP v5, Premiere ≥ 25.6 [CÓDIGO]. **É UXP, não CEP.** | o mesmo painel: montar o `.ccx` (é um zip de `manifest.json`, `index.html`, `main.js`, `icones/` — `instalar.py` → `montar_ccx`) e instalar pelo Creative Cloud (dois cliques no `.ccx`) ou pelo UPIA do Mac, ou carregar pelo *UXP Developer Tool* [TESTAR] | baixa | **sim** |
| **servidor do painel** (porta 7815) | `premiere/servidor.py`: microfone (dshow), tela (gdigrab), som do PC (`gravar_pc.py`/WASAPI), Job Object do Windows (mata os ffmpeg se ele cair), `winsound` [CÓDIGO] | as mesmas trocas do gravador (tela, microfone, som do PC, alerta); o Job Object vira grupo de processo (`os.setsid` + `killpg`) ou `psutil` [SABIDO] | média-alta | **sim** (voz + tela; som do PC conforme a decisão de cima) |
| leitor do Premiere | `premiere/resumo.py`: só biblioteca padrão [CÓDIGO] | roda como está | — | sim |
| leitor do PC | `resumo_pc.py` importa o `olho.py` (que tem `windll` no topo) [CÓDIGO] | tirar do `olho.py` as funções puras que ele usa (`duracao`, `ler_wav`, `t_da_sessao`, `fim_da_sessao`, `links_da_sessao`) pra um módulo comum | baixa | sim |
| já lidas, importar transcrição | `kakashi_lidas.py`, `importar_transcricao.py`: Python comum [CÓDIGO] | rodam | — | sim |
| skill /kakashi | o texto fala de `%LOCALAPPDATA%\Programs\Kakashi-Fly\`, `\` e `.venv\Scripts\python.exe` [CÓDIGO] | trocar os caminhos pelos do Mac; as leis ficam iguais | baixa | sim |

## A ordem sugerida (o mais valioso e mais fácil primeiro)
1. **O Tandera no processador do Mac:** ambiente Python → `python -m tandera versao` → o exemplo sintético → `comparar.py` dá IGUAL/PERTO.
   Prova o motor no Mac sem placa nenhuma. Fácil.
2. **Ler gravações** (o leitor do Premiere, o leitor do PC sem o `windll`, as já lidas, a skill com os caminhos do Mac, a transcrição pelo
   Tandera): já serve pra ler gravações feitas no Windows. Fácil.
3. **O painel do Premiere no Mac + o servidor (porta 7815)** com voz e tela pelo avfoundation: é **o mais valioso pro editor** (a timeline).
4. **O gravador do PC básico:** atalho escolhido pelo Gu, voz, tela, janela da frente, cliques, o Sharingan no canto, colar "/kakashi".
5. **O som do PC** (BlackHole ou ScreenCaptureKit — decisão com o Luan) e o **«olho de Deus» completo** (elemento sob o mouse, cópias,
   prints, links, replay, alerta).
6. **O Tandera com a placa da Apple** (MPS) nas peças leves, uma por vez, comparando; o olho pelo Ollama.
7. Ligar com o sistema (LaunchAgent), instalador do Mac. As pesadas (separação sem stems, Ovis, busca, texto em volume): RunPod.

**Pode ficar de fora numa 1ª versão:** replay, elemento sob o mouse, imagem copiada/captura de tela, alerta de som, troca automática PC →
Premiere, atualização automática, PC check, o app pessoal (AppPessoal), e no Tandera: boca, corpo, efeitos, rostos, busca, Ovis, texto.
