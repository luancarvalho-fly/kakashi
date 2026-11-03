# KAKASHI — o gravador de correção pro Claude Code

Feito pelo Luan Carvalho (Fly). Você aperta **o seu atalho**, fala e mexe à vontade (Chrome, Fly Studio, Premiere, qualquer janela),
aperta de novo e digita **/kakashi** no Claude Code. O Claude lê a sua fala junto com o que estava na tela: a janela, o link, o elemento
debaixo do mouse, o que você copiou, um print com zoom de cada "olha aqui" e, no Premiere, cada ação na timeline. Acabou o "mandar
áudio, print e gravação de tela" pro Claude.

O irmão dele é o **[TANDERA](https://github.com/luancarvalho-fly/tandera)** (o motor de análise de vídeo e som da Fly), que o Kakashi
pode usar pra transcrever a sua fala no seu próprio PC.

## Instalar (o jeito mais fácil: pedir pro seu Claude)
Abra o **Claude Code** e escreva:

> instala o Kakashi pra mim: https://github.com/luancarvalho-fly/kakashi

Ele lê o `CLAUDE.md` deste repositório e faz tudo com você: o **PC check** (o que o seu PC aguenta), pergunta o atalho que você quer e
como você quer transcrever a fala, e instala (gravador + painel do Premiere + a skill `/kakashi`). Nada de conta, senha ou cartão.

Na mão (Windows): baixe o zip (botão verde **Code → Download ZIP**), extraia e dê dois cliques no `Instalar.bat`.

## O que precisa
| | |
|---|---|
| **Sistema** | **Windows 10/11.** Mac: já roda no Mac do Gu (porte de 02/11); entra aqui quando for juntado — ver `MAC.md`. |
| **O gravador** | leve em qualquer PC (0,1–1% do processador). |
| **A transcrição da fala** | é a parte pesada. Dois caminhos, o instalador ajuda a escolher: **ARDI** (o conector da Fly no seu Claude; centavos por gravação; qualquer PC) · **Tandera no seu PC** (de graça; no processador: ok em PC médio/forte, lento em PC fraco). |
| **PC forte / RunPod** | o Kakashi em si não precisa. Quem vai usar a análise completa de vídeo (o **Tandera**) precisa de placa NVIDIA; sem ela, o Tandera roda numa máquina alugada por hora no **RunPod** (passo a passo no `RUNPOD.md` do Tandera). |
| **Premiere** | opcional: com o Premiere 25.6+ o instalador põe o painel KAKASHI (grava a timeline junto). |

## Usar
- **O atalho** começa e conclui. O mesmo + **Shift** cancela (vai pra `sessoes\_descartadas`, nunca apaga).
- Gravando no PC: **PAUSAR / CONTINUAR** na janelinha; cada continuação vira um pedaço, e **APAGAR N** tira um pedaço da correção.
- **A correção é do atalho ao atalho**: o que você fez antes de apertar ou depois de concluir não entra.
- Depois de gravar: **/kakashi** no Claude Code.
- Trocar o atalho e procurar atualização: atalho **KAKASHI** na área de trabalho.

## Atualização
O Kakashi confere este repositório sozinho a cada 12 h; achou versão nova, a janelinha mostra **ATUALIZAR** (gravações, config e atalho
ficam). Cada versão é uma etiqueta `vAAAA.MM.DD`. O que mudou: aba **Commits**.

## O que já foi testado
O gravador é o mesmo que o Luan usa todo dia. Deste repositório (03/11/2026, no PC dele): o instalador numa pasta de teste, a leitura
de uma gravação com a fala transcrita pelo Tandera clonado ao lado, e o atualizador olhando este repositório. Em outubro, a instalação
limpa, o atalho escolhível e a janelinha. **Ainda não:** o painel do Premiere desta versão instalado num Premiere de outra pessoa.

## Privacidade
Tudo fica no seu PC (`%LOCALAPPDATA%\Programs\Kakashi-Fly\sessoes`). Só o áudio da sua voz sai do PC, e só se você escolheu transcrever
pela ARDI ou pelo RunPod. Senhas copiadas de gerenciador de senha nunca são guardadas.

## Mais
`LEIA-ME.md` (o manual), `INSTALAR-COM-CLAUDE.md` (o passo a passo do instalador), `skill/SKILL.md` (como o Claude lê uma gravação),
`MAC.md` (o porte pro Mac).
