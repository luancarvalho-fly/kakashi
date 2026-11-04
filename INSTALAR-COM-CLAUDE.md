# Pro Claude Code: como instalar o KAKASHI neste PC (Windows)

> **⚠ ANTES DE TUDO: RODE O PC CHECK.** Antes de instalar qualquer coisa, rode `py -3 pc_check.py` (desta pasta; só LÊ o PC, não
> instala nada) e mostre pra pessoa, em palavras simples, o nível do PC dela (N0 leve, N1 médio, N2 forte) e a tabela "onde roda o
> quê": o que roda no PC dela, o que vai pela ARDI e o que não roda. Só depois siga os passos abaixo. O gravador é leve em qualquer
> PC; o que muda com o nível é a transcrição (e, no Tandera, a análise).

1. **Sistema:** precisa ser **Windows 10/11**. No Mac, pare e leia o `MAC.md`: o gravador do Mac ainda está em porte.
2. **Python 3.10+** (`py -3 --version`) e **ffmpeg** (`ffmpeg -version`). Faltando: ofereça instalar com
   `winget install Python.Python.3.12` / `winget install Gyan.FFmpeg` (peça o OK da pessoa antes; depois feche e abra o terminal).
3. **PC check** (o aviso lá de cima): `py -3 pc_check.py` → explique o resultado.
4. **Pergunte duas coisas, uma de cada vez:**
   - **O atalho.** "Qual atalho você quer pra começar e concluir a gravação? O do Luan é Ctrl+Page Down; pode ser qualquer um, tipo
     Ctrl+Alt+K ou F9." O de cancelar vira o mesmo + Shift. Confira antes com
     `py -3 atalho.py --conferir "<o que ela escolheu>"` (diz se vale e se outro programa já usa).
   - **Como transcrever a fala** (é a parte pesada do Kakashi):
     - **ARDI** (padrão): "Você tem conta na ARDI (é da Fly)?" Sim → a fala é transcrita pela ARDI, centavos por gravação, qualquer PC.
     - **Tandera no PC** (sem ARDI): a peça «fala» do TANDERA roda no processador deste PC. Precisa só do CÓDIGO do Tandera (não a
       instalação pesada dele): clone `https://github.com/luancarvalho-fly/tandera` ao lado desta pasta (ou onde a pessoa quiser) e
       passe `--transcricao tandera --tandera "<pasta do clone>"`. No PC N0 fica lento (minutos por minuto de fala); N1/N2, ok.
     - O **RunPod** (máquina alugada, `RUNPOD.md` do Tandera) é pra ANÁLISE de vídeo pesada de quem não tem PC forte, não pra
       transcrever uma gravação de 1 minuto: pra isso a ARDI ou o processador bastam.
5. **Instale**, de dentro desta pasta (o clone ou o zip extraído):
   `py -3 instalar.py --atalho "<o atalho dela>"` (+ `--transcricao tandera --tandera "<pasta>"` se ela não usa a ARDI).
   - Se ela não usa o Premiere: `--sem-premiere`. Com o Premiere instalado, o instalador põe o painel KAKASHI nele (fechar e abrir o
     Premiere depois).
   - Se já existir uma skill `/kakashi` que não veio deste pacote, o instalador NÃO troca e avisa: pergunte antes de rodar com
     `--trocar-skill` (a antiga é guardada, não apagada).
6. **Mostre o resumo** que o instalador escreve e diga como usar: o atalho começa e conclui, o de cancelar cancela (vai pra
   `_descartadas`, nunca apaga), PAUSAR / CONTINUAR na janelinha, e depois de gravar é só digitar **/kakashi** aqui no Claude Code. O
   atalho dá pra trocar quando quiser: atalho **KAKASHI** na área de trabalho → **TROCAR O ATALHO**.
7. **A extensão do Chrome** (recomendado; 1 minuto, a pessoa clica): ela diz ao Kakashi QUAL elemento da página está debaixo do
   mouse, pelo código (HTML, seletor, link, o endereço da imagem e, em app local, o arquivo:linha). Sem ela, o Kakashi só sabe
   «um título chamado X». Passo a passo pra pessoa: no Chrome, abrir `chrome://extensions` → ligar **Modo do desenvolvedor** (canto
   de cima, à direita) → **Carregar sem compactação** → escolher a pasta `%LOCALAPPDATA%\Programs\Kakashi-Fly\chrome`. Pronto: o
   Sharingan aparece na lista. Ela só manda alguma coisa enquanto o Kakashi grava, e só pro próprio PC (127.0.0.1); o que a pessoa
   digita em campo nunca sai. Depois de uma atualização do Kakashi a extensão
   se recarrega sozinha (confere os próprios arquivos a cada minuto) e entra nas guias já abertas, sem F5. Se o Claude consegue
   operar o Chrome da pessoa (UI Automation do Windows), ele mesmo faz os cliques acima; senão, passa os 3 cliques pra ela.
8. Se o Windows avisar "O Windows protegeu o computador" num atalho: "Mais informações" → "Executar assim mesmo".

Atualizar: sozinho (a janelinha mostra ATUALIZAR quando sai versão nova), ou rodar o `instalar.py` da versão nova (as gravações, o
config e o atalho ficam).
Desinstalar: `py -3 "%LOCALAPPDATA%\Programs\Kakashi-Fly\instalar.py" --desinstalar` (as gravações ficam).
