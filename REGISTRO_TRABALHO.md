# Registro de trabalho do ConvIQ

Este é o registro compartilhado de Codex e Claude. Leia a ficha da tarefa e
confira o Git antes de continuar. Cada agente atualiza a ficha, o índice e o
histórico antes de devolver o trabalho, seguindo as seções 5, 8 e 10 de
[SISTEMA_GOVERNANCIA_CONVIQ.md](SISTEMA_GOVERNANCIA_CONVIQ.md).

“Entrega finalizada” significa execução concluída; revisão, commit, push e
integração são registrados separadamente. Um commit em uma branch de trabalho
não comprova que o conteúdo chegou à principal. O registro também pode ter
alterações locais ainda não commitadas, mesmo quando o código já está commitado.

## Como navegar (estrutura de 07/10/2026)

Este arquivo é só o **índice**: a tabela de estado por PR e a fotografia Git
vigente. Para o estado atual e o próximo passo, leia primeiro
[STATUS.md](STATUS.md). O resto fica em `docs/registro/`:

| Onde | O que contém |
|---|---|
| [docs/registro/README.md](docs/registro/README.md) | Como registrar (formato curto), o que escrever onde e regras de tamanho |
| `docs/registro/<ID>.md` | A ficha do PR e **todos os seus eventos** (`B13.md`, `B12.md`...) |
| [docs/registro/GERAL.md](docs/registro/GERAL.md) | Eventos que cobrem várias frentes |
| [docs/registro/FOTOGRAFIAS_HISTORICAS.md](docs/registro/FOTOGRAFIAS_HISTORICAS.md) | Fotografias Git que já não são a vigente |

Agentes leem `STATUS.md`, a linha do PR na tabela e o arquivo do PR em que vão
atuar; não é preciso abrir o resto. O conteúdo anterior a esta reorganização
foi movido sem alteração (verificado linha a linha); o histórico completo
continua no Git.

## Índice atual

| PR/tarefa | Entrega do executor | Estado do ciclo | Git da entrega | Branch de trabalho | Publicação da entrega | Integração na principal |
|---|---|---|---|---|---|---|
| [DOC01 — Registro compartilhado](docs/registro/DOC01.md) | FINALIZADA | ENTREGUE | Original COMMITADO em `6169fec`; atualizações PLN01 locais | `feat/b01-fundacao-api` | NAO_VERIFICADO | NAO_VERIFICADO |
| [B01 — Fundação da API](docs/registro/B01.md) | FINALIZADA; verificada pelo Codex | APROVADO; B01-07 | COMMITADO; `6169fec` | `feat/b01-fundacao-api` | PRESENTE na branch padrão remota, confirmado em 07/10 | PRESENTE no destino `feat/b01-fundacao-api` desde `6169fec` |
| [C01 — Contrato de análise por texto](docs/registro/C01.md) | FINALIZADA; verificada pelo Codex | APROVADO; C01-04 | COMMITADO; `6169fec` | `feat/b01-fundacao-api` | PRESENTE na branch padrão remota, confirmado em 07/10 | PRESENTE no destino `feat/b01-fundacao-api` desde `6169fec` |
| [B02 — Sentimento e evidências](docs/registro/B02.md) | FINALIZADA; verificada pelo Codex | APROVADO; B02-04 | COMMITADO; `6169fec` | `feat/b01-fundacao-api` | PRESENTE na branch padrão remota, confirmado em 07/10 | PRESENTE no destino `feat/b01-fundacao-api` desde `6169fec` |
| [B03 — Sinais comerciais](docs/registro/B03.md) | FINALIZADA; verificada pelo Codex | APROVADO; B03-04 | COMMITADO; `6169fec` | `feat/b01-fundacao-api` | PRESENTE na branch padrão remota, confirmado em 07/10 | PRESENTE no destino `feat/b01-fundacao-api` desde `6169fec` |
| [B04 — Endpoint de análise](docs/registro/B04.md) | FINALIZADA; verificada pelo Codex | APROVADO; B04-04 | COMMITADO; `6169fec` | `feat/b01-fundacao-api` | PRESENTE na branch padrão remota, confirmado em 07/10 | PRESENTE no destino `feat/b01-fundacao-api` desde `6169fec` |
| [ANA01 — Avaliação de escalabilidade](docs/registro/ANA01.md) | FINALIZADA | ENTREGUE | COMMITADO; registro em `6169fec` | `feat/b01-fundacao-api` | NAO_VERIFICADO | NAO_SE_APLICA; análise |
| [PROD01 — Evolução futura por equipe](docs/registro/PROD01.md) | FINALIZADA | ENTREGUE | COMMITADO; plano/registro em `6169fec` | `feat/b01-fundacao-api` | NAO_VERIFICADO | NAO_SE_APLICA; planejamento |
| [PLN01 — Detalhamento dos PRs restantes](docs/registro/PLN01.md) | FINALIZADA; planejamento | ENTREGUE; implementação não iniciada | COMMITADO; `cc61925` | `spike/b07-a-viabilidade-whisper` | PUBLICADO; branch remota conferida | NAO_SE_APLICA; planejamento |
| [B07-A — Viabilidade do Whisper](docs/registro/B07-A.md) | PARCIAL; P01 (fala real) pendente | EM_REVISAO; Codex verificou R03/R04 em B07-A-07, sem encerrar a avaliação de viabilidade | COMMITADO; correções R03/R04 em `d5fb40a` (junto de B11/B12, não em commit próprio) | `fix/b12-contexto-risco` (commit `d5fb40a`); origem `spike/b07-a-viabilidade-whisper` continua em `cc61925` | PUBLICADO em 21/09; consulta atual ao servidor NAO_VERIFICADA | NAO_INTEGRADO |
| [ANA02 — Panorama funcional](docs/registro/ANA02.md) | FINALIZADA; análise | ENTREGUE | COMMITADO; `cc61925` | `spike/b07-a-viabilidade-whisper` | PUBLICADO; branch remota conferida | NAO_SE_APLICA |
| [PLN02 — Refinamento das capacidades](docs/registro/PLN02.md) | FINALIZADA; planejamento | ENTREGUE | COMMITADO; `cc61925` | `spike/b07-a-viabilidade-whisper` | PUBLICADO; branch remota conferida | NAO_SE_APLICA |
| [B11 — Negação no sentimento](docs/registro/B11.md) | FINALIZADA (B11-01) e corrigida pelo Opus (B11-03) | INTEGRADO após aceite B11-04; PR #1 MERGEADO | Origem `d5fb40a`; reaplicação aprovada em `45e1e76` | `integrate/b11-b12-analise` (base `6169fec`); origem `fix/b12-contexto-risco` | `45e1e76` PUBLICADO | INTEGRADO em `feat/b01-fundacao-api`, merge `e31e6ba` |
| [B12 — Risco com contexto local](docs/registro/B12.md) | FINALIZADA (B12-01), corrigida em B12-04 e B12-06 | INTEGRADO após aceite B12-07; PR #1 MERGEADO | Origem `d5fb40a` + `b14f0a5`; reaplicação aprovada em `45e1e76` | `integrate/b11-b12-analise` (base `6169fec`); origem `fix/b12-contexto-risco` | Conteúdo PUBLICADO no PR #1; `b14f0a5` permanece local na origem | INTEGRADO em `feat/b01-fundacao-api`, merge `e31e6ba` |
| [INT01 — Entrega isolada B11/B12](docs/registro/INT01.md) | FINALIZADA, validação concluída | PR [#1](https://github.com/GustavoECocchi/ConvIQ/pull/1) MERGEADO | `45e1e76` (entrega) + `ae71f84` (registro) sobre `6169fec` | `integrate/b11-b12-analise` | PUBLICADA em `origin/integrate/b11-b12-analise` | INTEGRADA em `feat/b01-fundacao-api`, merge `e31e6ba` |
| [B13 — Intenção comercial para oportunidade](docs/registro/B13.md) | FINALIZADA (B13-01, Sonnet), corrigida pelo Opus em B13-03 | APROVADA tecnicamente em B13-04; INTEGRADA e verificada em B13-10 | Entrega COMMITADA em `ebed307`; registro remoto COMMITADO em `6d8bcfa`; eventos posteriores locais | `fix/b13-intencao-oportunidade`, head `6d8bcfa`, base `9921f57` | PUBLICADA; origem remota preservada em `6d8bcfa` | INTEGRADA em `feat/b01-fundacao-api` pelo PR #2, merge `2811d84` |
| [EST01 — Estrutura ágil](docs/registro/GERAL.md) | FINALIZADA (EST01-01, Opus), corrigida em EST01-03 | APROVADA tecnicamente pelo Codex em EST01-03 | NAO_COMMITADA; diff local sobre `6d8bcfa` no worktree `CONVIQ-estrutura` | `chore/estrutura-agil`, base `6d8bcfa` (head do PR #2) | NAO_PUBLICADA | NAO_INTEGRADA; B13 já integrado em `2811d84` |

Os demais PRs B, F, C e I continuam planejados. Os novos cartões constam de
[PRs pequenos de áudio](docs/planejamento/PRS_BACKEND_AUDIO.md), com estados
iniciais, branches propostas, dependências e critérios. O PR #1 foi
integrado em INT01-06; B13 foi integrado e verificado em B13-10.
B14 está liberado.
Criar/atualizar a ficha de cada tarefa
quando encaminhada, sem declarar conclusão por antecipação.

### Fotografia Git vigente — 08/10/2026, B13-10 (Codex)

- PR #2 `MERGED` por merge commit `2811d84`, com pais `9921f57`
  e `6d8bcfa`. A branch padrão remota aponta ao merge; a origem B13
  permanece em `6d8bcfa`. B13 INTEGRADA e verificada.
- Este worktree EST01 permanece em `chore/estrutura-agil`, HEAD/base
  `6d8bcfa`, com diff local e arquivos não rastreados; EST01
  APROVADA tecnicamente, NAO_COMMITADA, NAO_PUBLICADA, PR NAO_ABERTO,
  NAO_INTEGRADA. Destino previsto `feat/b01-fundacao-api` em `2811d84`.
- Pasta raiz e worktree B13 preservados com alterações preexistentes;
  `prompt.md` de integração B13 consumido permanece local.

### Fotografia Git histórica — 07/10/2026, EST01-03 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-estrutura`, branch
  `chore/estrutura-agil`, HEAD/base `6d8bcfa` (head do PR #2). EST01
  está em diff local e arquivos não rastreados: STATUS, script/teste de
  sondagem e `docs/registro/`; índice e governança também modificados.
- EST01 FINALIZADA e APROVADA tecnicamente em EST01-03; NAO_COMMITADA,
  NAO_PUBLICADA, PR próprio NAO_ABERTO, NAO_INTEGRADA. Destino previsto:
  `feat/b01-fundacao-api`, após integrar o PR #2.
- Consulta atual ao servidor: PR #2 `OPEN`, head `6d8bcfa`, base
  `feat/b01-fundacao-api`, `MERGEABLE`; B13 aprovada tecnicamente e
  NAO_INTEGRADA. A tentativa de merge do Opus foi bloqueada conforme
  B13-09; nenhuma nova tentativa nesta atuação.
- Pasta raiz e worktree B13 mantêm suas alterações locais preexistentes.
  `prompt.md` continua com o prompt de integração do PR #2, não executado.
