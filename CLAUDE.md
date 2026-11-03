# Pro Claude que abriu este repositório

Este é o **KAKASHI** da Fly (o gravador de correção do Luan Carvalho). Quem te mandou aqui quase sempre quer uma de duas coisas:

1. **"Instala o Kakashi"** → siga o `INSTALAR-COM-CLAUDE.md`, um passo de cada vez, falando em português simples (a maioria do time
   edita vídeo, não programa). O primeiro passo é SEMPRE o PC check.
2. **"Lê a minha correção" / `/kakashi`** → isso é a skill `/kakashi` que o instalador põe no Claude Code (`skill/SKILL.md`). Se ela
   ainda não está instalada, instale primeiro.

## Regras
- **Pergunte antes de instalar** qualquer programa (Python, ffmpeg, o painel do Premiere) e antes de trocar uma skill `/kakashi` que já
  existe. Permissão do Windows é a pessoa que clica.
- **Nada de conta, senha, chave ou cartão**: o Kakashi não precisa. A transcrição pela ARDI usa o conector da ARDI que a pessoa já
  tem no Claude (o `upload_file` + `view_file`); sem esse conector, é o caminho do Tandera.
- **Nunca toque som** no PC da pessoa pra testar; nunca abra gravação de outra pessoa.
- Deu erro na instalação: mostre a mensagem inteira e o que você acha que é; não saia apagando pasta. O Kakashi instala em
  `%LOCALAPPDATA%\Programs\Kakashi-Fly` e as gravações ficam em `sessoes\` (nunca apague essa pasta).
- **Mac**: o porte (do Gu, 02/11) ainda não está neste repositório (ver `MAC.md`). Não rode o `instalar.py` do Windows lá.

## Como este repositório é mantido
O código é o mesmo que o Luan usa todo dia, com os caminhos do PC dele trocados. Cada versão nova é publicada aqui como uma etiqueta
`vAAAA.MM.DD` e chega sozinha em quem já instalou. Melhoria sua: mande pro Luan (grave um Kakashi explicando, ou abra uma *issue*);
o motor é um só e a mudança entra no dele primeiro.
