---
description: Busca eventos locais (jogos, shows, estreias de filme, peças de teatro, datas comemorativas) perto de cada loja e atualiza os CSVs de curadoria.
---

Não existe uma API confiável e gratuita para "todos os eventos perto de um
shopping". A abordagem é uma busca na web, curada por humano antes de entrar
no pipeline de previsão de demanda.

## O que fazer

Para cada loja, use a ferramenta de busca na web (WebSearch) para procurar
eventos do mês atual e do próximo mês. Consultas sugeridas:

**Butantã Shopping** (perto do MorumBIS / Estádio do São Paulo, no Morumbi):
- "jogos São Paulo Futebol Clube Morumbi <mês> <ano>"
- "shows MorumBIS <mês> <ano>"
- "eventos Butantã <mês> <ano>"

**Shopping Metro Santa Cruz**:
- "estreias de filmes cinema <mês> <ano> Brasil"
- "peças de teatro em cartaz São Paulo <mês> <ano>"
- "eventos Shopping Metro Santa Cruz <mês> <ano>"

Ajuste ou acrescente buscas conforme o que fizer sentido (outras datas
comemorativas do bairro, outros locais de shows próximos, etc.).

## Onde salvar

Atualize (não sobrescreva) os CSVs de curadoria:

- `outputs/buscar_eventos/butanta_shopping/eventos.csv`
- `outputs/buscar_eventos/shopping_metro_santa_cruz/eventos.csv`

Colunas: `data_evento,evento,tipo,local,fonte_url,confirmado,observacoes`

- `tipo`: `jogo_futebol`, `show`, `estreia_filme`, `peca_teatro`,
  `data_comemorativa_bairro` ou `outro`.
- `data_evento`: data específica (`AAAA-MM-DD`) quando souber, ou um
  período (`AAAA-MM-DD a AAAA-MM-DD`) quando for uma temporada/janela.
- `confirmado` e `observacoes`: deixe em branco em linhas novas — são
  preenchidos manualmente pelo usuário depois.

## Regras de atualização (curadoria humana)

1. Leia o CSV existente antes de escrever.
2. Nunca apague ou sobrescreva uma linha que já tenha algo em `confirmado`
   ou `observacoes` — essa é a curadoria já feita pelo usuário.
3. Não duplique uma linha já existente (mesma `data_evento` + `evento` +
   `local`).
4. Acrescente apenas as linhas novas encontradas na busca, com
   `confirmado` e `observacoes` vazios.
5. No final, informe ao usuário quantas linhas novas foram adicionadas em
   cada CSV e lembre que elas precisam ser revisadas (`confirmado`
   preenchido) antes de entrarem no pipeline final de previsão de demanda.
