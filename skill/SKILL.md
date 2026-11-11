---
name: kakashi
description: Lê a última gravação do KAKASHI (o gravador de correção que pega a voz, o som do PC, a tela, o mouse, a janela da frente, os links do Chrome, os prints do "aqui" e, no Premiere, cada ação da timeline) e transforma em pedidos, erros e decisões com o minuto. Use SEMPRE que a pessoa digitar /kakashi, ou disser "vê a gravação", "olha o que eu gravei no Kakashi", "gravei a correção", "passei o feedback pelo Kakashi".
---

# /kakashi — ler a gravação

A pessoa grava falando (o atalho dela começa e conclui; o padrão é Ctrl+Page Down, e cada um escolhe o seu) e digita /kakashi.
**O pedido dela está FALADO dentro da gravação: ela não vai repetir no chat.** Ler tudo antes de responder.
Pasta do Kakashi: `%LOCALAPPDATA%\Programs\Kakashi-Fly\` (abaixo, "a pasta"). Python dele: `.venv\Scripts\python.exe` da pasta.

## 0. JÁ LIDAS — antes de tudo, em TODO chat
0. **Versão nova?** `python atualizar.py --checar` (na pasta). Se disser `NOVA`, avise a pessoa numa linha no fim da resposta: "tem
   versão nova do Kakashi: botão ATUALIZAR na janelinha (atalho KAKASHI na área de trabalho)". Não atualize no meio da leitura.
1. `python kakashi_lidas.py novas` (na pasta) → só existe pra ler o que ele listar, da mais nova pra mais velha. Sessão com `LIDA.json`
   na pasta, ou `LEITURA-CLAUDE.md`, = OUTRO chat já leu: NÃO ler de novo, NÃO refazer o pedido dela.
2. Ao começar a trabalhar numa sessão: `python kakashi_lidas.py marcar "<pasta da sessão>" --chat <id deste chat> --nota lendo`.
   Marcar LOGO, antes de fazer os pedidos: outro chat aberto pode estar olhando. No fim, marcar de novo com `--nota "<o que virou>"`:
   **essa marca final só passa com `LEITURA-CLAUDE.md` e `SABOTADOR.md` na pasta da sessão** (passo 5). `python kakashi_lidas.py
   faltando` lista as gravações do dia que ficaram sem essa análise.

## 1. Achar a gravação (a MAIS NOVA que a lista deu)
- **PC** (qualquer janela: Chrome, ARDI, Fly Studio...): `sessoes\<AAAA-MM-DD_HHMMSS>_pc\`.
- **Premiere** (o painel do KAKASHI aberto): `premiere\sessoes\<AAAA-MM-DD_HHMM_SEQUÊNCIA>\` — `resumo.md` (cada ação da timeline),
  `audio.wav` (só a voz), `pc.wav` (só o som do PC), `tela.mp4`; e a pasta `_olho\` = o que a pessoa fez FORA da timeline enquanto o
  painel gravava (janela, mouse, elemento debaixo do mouse, print do "aqui", cópias, links), no MESMO relógio da sessão.
- **CONTINUA NO PREMIERE**: se a sessão de PC diz `"continua_em": "premiere"` (o `LEITURA.md` dela escreve "CONTINUA NO PREMIERE em
  m:ss" e o nome da sessão), a pessoa começou no PC e entrou no Premiere: é UMA correção só. Ler AS DUAS, na ordem PC → Premiere.
- Pular `_descartadas` e `sessao.json` com `"descartada": true` (a pessoa cancelou).
- Antes de reiniciar o Kakashi: `GET http://127.0.0.1:7816/status` (PC) e `GET http://127.0.0.1:7815/status` (Premiere) → `estado`
  tem que ser `parado`. Nunca reiniciar nem reinstalar no meio de uma gravação.

## 2. Transcrever (o motor está no `config.json` da pasta → `"transcricao"`)
- `"ardi"` (padrão de quem é da Fly): pelas ferramentas da ARDI. `upload_file` com o `fala.wav` da sessão de PC (no Premiere, o
  `_olho\fala.wav`) → rode o comando que ela devolve (curl) → `view_file` com o `assetId` (sem pergunta: é só transcrever). Salve o
  texto num .txt e rode `python importar_transcricao.py "<pasta da sessão ou _olho>" "<arquivo.txt>"`. Fica guardado.
  Sem as ferramentas da ARDI nesta sessão do Claude: diga isso e ofereça trocar pra `"tandera"`.
- `"tandera"` (`"local"` é o nome antigo, vale o mesmo): o próprio resumo transcreve pelo **TANDERA** — o motor de análise da Fly, UM
  só (lei do Luan, 01/11: «o Tandera é o nosso motor, pra análise de qualquer skill... Ele tem que estar 100% atualizado»). É a peça
  «fala»: Whisper large-v3-turbo, só os trechos com som (sem VAD), filtro de laço e de frase inventada, no PROCESSADOR (a placa fica
  livre pro Premiere). A pasta do Tandera vem do `config.json` → `"tandera"` (ou é a `tandera\` ao lado do Kakashi). A transcrição
  guardada (`fala_transcricao.json`) só é relida se foi feita com a versão ATUAL da peça; se a peça mudou, transcreve de novo sozinho.
  Se o Tandera falhar, o resumo PARA e diz por quê: não existe reserva com outro motor (nunca um Whisper à parte). O `perfil.json` do
  PC check diz se o PC aguenta.
- `"8178"`: um whisper-server que já esteja no ar nessa porta (o do Luan é o do ditado dele; no pacote é só opção).

## 3. Ler
- PC: `python resumo_pc.py "<pasta da sessão>" --quadros` → ler o `LEITURA.md` INTEIRO.
- Premiere: `python resumo_pc.py "<sessão>\_olho" --quadros` → ler o `_olho\LEITURA.md` INTEIRO junto com o `resumo.md` da sessão,
  pelo minuto (o print nativo do "aqui" vence o quadro do `tela.mp4`).
- Por trecho de 15 s: a fala literal, a janela da frente, o link exato do Chrome, o elemento debaixo do mouse, o que foi copiado
  (`_copias\`) e o print do "aqui / isso / esse / ó / olha" (`_prints\mmss_*_perto.jpg` = recorte em volta do cursor marcado de
  vermelho; abrir o recorte primeiro). Sem print perto: `_quadros\mmss.jpg`. **A CORREÇÃO É DO ATALHO AO ATALHO**: o que
  aconteceu antes de apertar o atalho ou depois de concluir NÃO é correção. O replay vem DESLIGADO; se a pessoa religou e o topo
  disser REPLAY (ou «REPLAY IGNORADO»), a parte de antes do atalho não se lê, nem quadro nem áudio dela. Trechos de "voz muda"
  (`sessao.json` → `voz_muda`) entram como "não ouvido", nunca somem. **Pausa**: se a sessão tem `pedacos` no `sessao.json`, ela foi
  gravada em pedaços (PAUSAR / CONTINUAR); o relógio já está sem as pausas e os pedaços apagados pela pessoa não existem.
- **Elemento do Chrome pelo código** (extensão `chrome\`, instalada uma vez no Chrome): as linhas «Chrome (parou/clique)» dizem o
  elemento da página de verdade: tag de abertura do HTML, texto, seletor, link, imagem (o endereço do PNG que a pessoa pede) e, em
  app local em modo de desenvolvimento (React, Vue, Svelte), `código:` = componente + arquivo:linha → abrir esse arquivo direto.
  Na página, essa linha vence o «mouse parou» do Windows/Mac (que só dá o papel e o nome). Valor digitado em campo nunca vem.

## 4. Entender — a gravação é pra NIVELAR o Claude, não só pra cumprir pedido
**A EXPLICAÇÃO VEM PRIMEIRO.** O que a pessoa FALA, do começo ao fim, junto do que ela fazia em cada minuto, é o centro. Comparar o
projeto/timeline de antes com o de depois serve pra conferir os números e achar o que ela fez calada; NUNCA substitui a fala.
(Erro de verdade que gerou esta regra: o Claude só comparou o projeto antigo com o novo e ignorou a explicação. Fala do Luan, 27/10:
«toda correção que eu fizer, ela vale pra nivelar o seu conhecimento, então não adianta nada você só comparar um projeto com outro,
que aí você tira toda a proposta do Kakashi... você tem que levar tudo em consideração, o projeto anterior com projeto novo, e ver a
minha explicação sobre isso».)
- **O MAIS NOVO VENCE.** Antes de guardar um ensinamento, conferir nas gravações MAIS NOVAS e na última versão que a PESSOA salvou se
  ela fez ou disse diferente depois. O caso velho fica marcado «MUDOU em <data>», não some. O que foi do momento (um lugar, um estado do
  projeto, frase de passagem) não vira «sempre»: «Não dá pra tu ficar levando tudo ao pé da letra».
- **Cruzar com o que já existe:** procurar nas instruções e skills da pessoa (CLAUDE.md, skills dela) o que briga com o ensinamento novo
  e PROPOR o ajuste. Ajuste dela = caso; vira regra só quando ela disser que é sempre.
- **Catar o que ela mostra:** arquivo, link ou referência que ela abre na gravação = guardar já na leitura (o caminho exato, o link do
  `links.json`). Nunca dizer "não achei" sem olhar o `links.json`, as `_copias\` e os prints daquele minuto.
- Dúvida sobre o que ela mostrou = caçar antes de perguntar (cliques no `eventos.jsonl`, quadros, links). Pergunta que sobrar = no chat,
  com o minuto, curta, com opções.

## 5. Responder e fazer — NADA DE FORA
- Escrever o `LEITURA-CLAUDE.md` na pasta da sessão: Pedidos diretos · Erros do Claude (fala dela) · Respostas a perguntas · Critérios
  dela (casos) · Ordens de "não fazer". Sempre a fala LITERAL curta entre aspas + `[mm:ss]`.
- Cada pedido falado vira uma linha de checklist (fala + minuto + onde foi feito). Pedido que vale pra mais de um lugar ("a roxa tem que
  ser verde") vale em TODOS os lugares. Gravação longa ou várias gravações do mesmo projeto: checklist de TODAS, não só da última.
  O checklist mora no projeto (`CHECKLIST-KAKASHI-<data>.md`, um por dia), uma linha por pedido: minuto · fala literal curta · FEITO /
  PARCIAL / NÃO FEITO / AMBÍGUO / DESCARTADO · prova (commit, arquivo:linha ou print). Antes de ler a gravação nova, abrir o checklist:
  o que está PARCIAL ou NÃO FEITO entra na resposta como «continua aberto». (Fala do Luan, 11/11: «aquele checklist de conferência das
  coisas que eu te peço que você tava fazendo, você não tá fazendo».)
- **Dose da análise**: gravação curta e clara (até ~1 min, um pedido) = `LEITURA.md` + prints + sabotador curto; longa ou confusa = tudo.
  Os passos não somem, só encolhem. (Fala do Luan, 11/11: «óbvio que não precisa de análise bizarramente completa toda hora, mas você
  tem que ser inteligente o suficiente pra fazer essa distinção».)
- **NUNCA DA TRANSCRIÇÃO DIRETO PRO CÓDIGO.** Ordem fixa, em TODA gravação (até as curtas, até em sequência, até com a pessoa com pressa):
  `LEITURA.md` inteira + prints → cruzar com a gravação antiga que ela citar → `LEITURA-CLAUDE.md` → sabotador → `SABOTADOR.md` (os
  achados e o que mudou na leitura) → só então mexer. (Erro de verdade: 11 gravações seguidas num dia lidas sem leitura escrita nem
  sabotador; a pessoa achou os furos depois. Fala do Luan, 06/11: «você tá lendo as correções do Kakashi sem analisar elas antes,
  cara? Será que é por isso que tá passando coisa batida... Você não pode fazer isso».)
- **Pergunta sobre a gravação vai com o trecho exato**: o arquivo do momento (recorte do áudio e do vídeo, ou o print) junto da
  pergunta, nunca só o minuto. (Fala do Luan, 06/11: «O certo é você me mandar o momento exato da gravação... Tu acha que eu tenho
  memória do homem de ferro?»)
- **SABOTADOR antes de responder** (SEMPRE): com o `LEITURA-CLAUDE.md` escrito, um agente SEPARADO lê a fala
  inteira, o `LEITURA.md`, a sua leitura e as gravações anteriores dos mesmos trechos, e devolve FALTOU · ERRADO · DESCARTADO-PELA-PESSOA ·
  DÚVIDA, cada um com a fala literal e o [mm:ss]; zero achado vale. Confira cada achado na fala original e corrija a leitura ANTES de
  responder. Não é pra "derrubar" pedido: é pra achar o que passou batido. (Fala do Luan, 27/10: «você já colocou o sabotador aqui,
  nessas etapas, pra poder pegar a coisa que você provavelmente ia passar batido? Não.»)
- Responder em português simples, lista numerada: o que entendeu, o que vai fazer, o que ficou ambíguo. Pedido claro = fazer. Decisão
  nova = propor e esperar o OK. Antes de dizer "feito": reler a fala inteira e riscar item por item.

## Trocar o atalho
A pessoa pode trocar quando quiser: janelinha do KAKASHI (atalho KAKASHI na área de trabalho) → **TROCAR O ATALHO** → apertar o novo
(Esc cancela); vale na hora. Se ela pedir pra você: conferir com `python atalho.py --conferir "ctrl+alt+k"` (diz se vale e se está
livre), gravar em `config.json` → `"atalho"` e pedir pra ela usar o botão TROCAR O ATALHO, ou reiniciar o Kakashi com ele `parado`.

## Cuidados
- Só lê: o Kakashi nunca toca som e não usa a placa de vídeo.
- Senha nunca é lida (o gravador pula campo de senha e gerenciador de senha).
- A gravação é da pessoa: não mande pra lugar nenhum além da transcrição (ARDI dela).
- A tela pode ser 4K: recortar só a região que importa antes de olhar.
