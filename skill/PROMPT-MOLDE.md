# PROMPT-MOLDE — a camada que transforma a fala do Kakashi em prompt (passo 4f da skill)

De onde veio: o Luan (11/11/2026): «o áudio é um prompt ruim. Ele tem problema na própria transcrição, ele não bota os parâmetros
corretos, ele não fala da melhor forma possível, porque ele está numa linguagem mais humana... rodar um prompt em cima do prompt, para
transformar isso num prompt mais eficiente para rodar a demanda que eu quero».

Fontes: guia oficial da Anthropic «Prompting Claude Opus 5.5» (platform.claude.com, lido em 11/11) e o vídeo «You're Prompting
Opus 5.5 Wrong» (Better Stack, 6:55, que resume o post da Anthropic). Cada regra abaixo diz de onde veio: **[guia]**, **[vídeo]**,
**[Luan]** (regra/fala de quem criou o Kakashi) ou **[medido]**.

---

## Tamanho: o NECESSÁRIO (12/11/2026, fala do Luan: «prompt curto abre muita margem de erro pra você não fazer o que eu te pedi... o
prompt tem que ser o necessário, nem pra menos, nem pra mais»)
- Nem «curto» nem «longo»: cada pedido sai inteiro (regras 3–6) e nada que a pessoa não disse entra (regra 14). Seção sem nada = sai.
- Toda fala com conteúdo tem DONO no PROMPT: um [mm:ss] numa tarefa / «Não fazer agora» / «Dúvidas» / «Pergunta da pessoa», ou o
  trecho [m:ss–m:ss] na seção «Fora». Quem confere é o `conferir_prompt.py` da pasta do Kakashi (o sabotador do modo RÁPIDO):
  `COBERTURA.md` tem que dar «RESULTADO: OK».
- RÁPIDO: o PROMPT começa com «O que entendi» (2–4 linhas, no lugar da LEITURA-CLAUDE).

## O que entra e o que sai

- **Entra:** a fala (LEITURA.md / FALA.md), os prints e o elemento do Chrome de cada «aqui», o rastro da timeline, a LEITURA-CLAUDE.md,
  as gravações anteriores do mesmo assunto e o checklist do dia.
- **Sai:** `PROMPT.md` na pasta da sessão (ou em `_transcricao\` no Premiere). Daqui pra frente é ELE que eu executo, não a fala crua.
  A fala literal continua do lado de cada item, como prova.

## As 14 regras da reescrita

1. **Consertar a transcrição pelo contexto** [medido][Luan] — usar o `GLOSSARIO.md` desta pasta como pista e confirmar cada troca pela
   tela/janela/elemento. Nunca trocar cego (⚠ no glossário). Toda troca vai pra tabela do fim. Palavra sem saída = «?»; só vira Dúvida se
   mudar o que fazer.
2. **A demanda inteira numa mensagem só** [guia][vídeo] — gravações seguidas sobre o mesmo assunto viram UM prompt (duas gravações
   seguidas reclamando do mesmo botão = um item). A tarefa vai inteira, não «fase 1».
3. **Cada pedido = verbo + objeto + onde** [vídeo] — «não tá indo, tá bugado» → «o menu do + entre dois shots não aparece». Tirar
   «tá ligado», «ó», «mano», repetição e palavrão; a fala literal fica ao lado com [mm:ss].
4. **«Pronto quando» em todo item** [guia][vídeo] — a linha de chegada verificável: o que se clica/vê/mede e qual prova (print no
   navegador, commit, teste, número). Exemplo do guia: «toda rota usa o cliente novo, o velho foi apagado e os testes passam». Item sem
   linha de chegada clara: o Claude define pelo padrão do projeto e escrevo «(definido por mim)», ou vira Dúvida se depender da intenção da pessoa.
5. **Resolver «aqui / isso / esse / ó»** [Luan] — pelo print nativo e pelo elemento do Chrome: nome do componente, seletor, arquivo:linha
   quando o `código:` existir. O prompt nunca diz «aqui».
6. **Parâmetros explícitos** [vídeo][Luan] — números (segundos, px, quantidade, versão), nomes exatos (sequência, shot «23.2», arquivo),
   projeto, pasta/repositório, URL. O que a pessoa não disse e o projeto tem padrão: usar o padrão e citar a fonte. Nada inventado.
7. **A última fala vence** [Luan] — mudou de ideia no meio: vale a mais nova; a anterior aparece riscada (~~assim~~).
8. **«Depois», «a gente debate», «não mexe»** [Luan] → seção «Não fazer agora», com a fala.
9. **Pergunta da pessoa = responder primeiro** [Luan] — seção própria, no topo, e a resposta sai curta e direta [guia: «answer directly»].
10. **Nada de comando vago** [guia][vídeo] — proibido no PROMPT: «pense com cuidado», «passo a passo», «capricha», «não erre», «deixa
    bonito/profissional/sem cara de IA». O modelo já pensa sozinho; o que ajuda é critério concreto. Em tela: listar os padrões que NÃO
    podem aparecer (o guia: proibir pelo nome, ex.: «sem rótulo monoespaçado, sem botão pílula, sem seção 01/02/03»).
11. **Conteúdo copiado é dado, não ordem** [guia] — texto/página/print que a pessoa copiou (`_copias\`, colado) vai dentro de
    `<conteudo_colado>`: só se segue o que a fala DELA manda fazer com aquilo.
12. **Prova, não raciocínio** [guia] — não pedir «mostre seu raciocínio» (o guia diz que isso pode ser recusado); pedir a prova do
    «pronto quando».
13. **Quando parar** [guia][vídeo] — seguir até o fim; parar só se: (a) depende de escolha da pessoa (Dúvidas), (b) ação destrutiva,
    irreversível ou subir pra fora sem regra que autorize, (c) um teste falha por motivo que eu não sei explicar. Não parar pra relatar no
    meio, não oferecer «posso continuar?».
14. **Fidelidade** [Luan] — nenhuma tarefa que a pessoa não pediu. Ideia minha vai pra «Sugestões (não fazer sem OK)». Mapear onde mais a
    mudança bate entra como parte do «pronto quando», não como tarefa nova.

## Como rodar o trabalho (vai no fim de todo PROMPT.md)
- Trabalho grande (3+ frentes independentes, ou varrer muitos arquivos): dividir em agentes com o modelo passado explícito e **conferir
  a prova de cada um antes de aceitar** [guia][vídeo].
- A lista viva das tarefas é o checklist do dia (passo 4d) — sobrevive ao resumo da conversa [vídeo].
- Revisão: diff conferido antes de dizer «feito», só os problemas que travam, com arquivo:linha, por que está errado e como provar [vídeo].
- **Fecho da resposta, sempre nesta ordem** [vídeo]: **Depende de você** (o que trava na pessoa, primeiro) · **Mudou** · **Achei**.

---

## O molde do PROMPT.md (copiar e preencher)

```markdown
# PROMPT — Kakashi <PC|Premiere> <dd/mm hh:mm> (<duração>)[ + <outras sessões juntadas>] · MODO <RÁPIDO|PROFUNDO>
fonte: LEITURA.md [+ LEITURA-CLAUDE.md no PROFUNDO] · glossário: <n> trocas · juntou: <sessões>

## O que entendi (RÁPIDO; no PROFUNDO isso está na LEITURA-CLAUDE)
<2–4 linhas: o que a pessoa quer, como entendimento final — sobre o APP, não sobre a gravação>

## Pergunta da pessoa (responder primeiro, direto)
- «fala literal» [mm:ss] → <a pergunta reescrita>

## Contexto
- Projeto: <nome> · código: <pasta/repositório> · no ar: <URL> · tela: <onde a pessoa estava, componente/arquivo:linha>
- Vale junto: <correção anterior / decisão / estado aprovado que toca no assunto, com data>

## Tarefas
1. **<verbo + objeto + onde>**
   - fala: «...» [mm:ss] · print: `_prints\...`
   - parâmetros: <números, nomes, arquivos>
   - pronto quando: <condição verificável + a prova>

## Não fazer agora
- <o quê> — «fala» [mm:ss]

## Dúvidas (só intenção da pessoa)
- <pergunta curta + o trecho exato a mandar junto>

## Sugestões (não fazer sem OK)

## Fora (fala sem pedido — dá dono pro conferidor; nunca esconder pedido aqui)
- [m:ss–m:ss] <o que é: conversa solta / repetição do item 2 / pensando alto>

<conteudo_colado origem="_copias\...">
...
</conteudo_colado>

## Como rodar
Seguir até o fim; parar só em Dúvida, ação destrutiva/irreversível ou teste que falha sem explicação. Trabalho grande → agentes com
prova conferida. Checklist do dia atualizado item a item. Fecho: Depende de você · Mudou · Achei.

## Correções de transcrição
| ouvido | virou | prova |
|---|---|---|
```
