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
| [EST01 — Estrutura ágil](docs/registro/GERAL.md) | FINALIZADA (EST01-01, Opus), corrigida em EST01-03 | APROVADA e INTEGRADA; PR [#3](https://github.com/GustavoECocchi/ConvIQ/pull/3) MERGEADO | Entrega COMMITADA em `53823a1`; registro COMMITADO em `5c2c421` | `chore/estrutura-agil`, base `6d8bcfa` | PUBLICADA; branch remota preservada em `5c2c421` | INTEGRADA em `feat/b01-fundacao-api`, merge `4063830` |
| [B14 — Normalização Unicode e evidências](docs/registro/B14.md) | FINALIZADA (B14-01, Sonnet) | INTEGRADO em B14-07; aceite B14-04; PR [#4](https://github.com/GustavoECocchi/ConvIQ/pull/4) MERGEADO | COMMITADO em `13b1519`; registros B14-05–07 integrados junto do F01 pelo PR #5 | `fix/b14-unicode-evidencias`, base `4063830`, HEAD `13b1519` | PUBLICADA em `origin/fix/b14-unicode-evidencias` (`13b1519`) | INTEGRADA em `feat/b01-fundacao-api`, merge `b688afb` |
| [F01 — Fundação React](docs/registro/F01.md) | FINALIZADA (F01-01, Codex) | INTEGRADA em F01-07 após aceite F01-05 e revisão Opus F01-04 | Entrega COMMITADA em `d8e06b2`; head documental `89e0801` | `feat/f01-fundacao-react`, base `b688afb` | PUBLICADA; PR [#5](https://github.com/GustavoECocchi/ConvIQ/pull/5) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `5a2fede` |
| [F02-A — Tipos C01 e exemplos](docs/registro/F02-A.md) | FINALIZADA (F02-A-01, Sonnet) | INTEGRADA em F02-A-04 após aceite F02-A-02 | Entrega COMMITADA em `68ebde7`; head documental `975857d` | `feat/f02a-tipos-c01`, base `89e0801` | PUBLICADA; PR [#6](https://github.com/GustavoECocchi/ConvIQ/pull/6) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `9706315` |
| [F02-B — Cliente HTTP C01](docs/registro/F02-B.md) | FINALIZADA (F02-B-01, Sonnet), corrigida em F02-B-03 | INTEGRADO em F02-B-07 após aceite F02-B-04 | Entrega COMMITADA em 1232ac9; head documental 73c4771 | feat/f02b-cliente-c01, base 9706315 | PUBLICADA; PR [#7](https://github.com/GustavoECocchi/ConvIQ/pull/7) MERGEADO | INTEGRADA em feat/b01-fundacao-api, merge bf7a1a1 |
| [F03-A — Rotas e navegação](docs/registro/F03-A.md) | FINALIZADA (F03-A-01, Sonnet), R01/R02 em F03-A-03, O01/O02 em F03-A-06 | INTEGRADA em F03-A-13 após revisão/aceite e PR #9 | COMMITADA: `708f5e5` (correções), `b6cfabe` (reconciliação), head `2741e53`; registro pós-merge `f235444` | `feat/f03a-rotas-navegacao`, base `9706315`, destino `feat/b01-fundacao-api` | PUBLICADA até `2741e53`; PR [#9](https://github.com/GustavoECocchi/ConvIQ/pull/9) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `b50ce86` |
| [F03-B — Formulário de nova análise](docs/registro/F03-B.md) | FINALIZADA (F03-B-03/04) | APROVADA_TECNICAMENTE e INTEGRADA em F03-B-06 | Entrega COMMITADA em `999b1d4`; registro pós-merge neste commit documental | `feat/f03b-formulario-analise`, base `0a0e8a8`, destino `feat/b01-fundacao-api` | PUBLICADA; PR [#10](https://github.com/GustavoECocchi/ConvIQ/pull/10) MERGED | INTEGRADA em `feat/b01-fundacao-api`, merge `f859e69` |
| [F04-A — Resumo do resultado](docs/registro/F04-A.md) | FINALIZADA (F04-A-03) | APROVADA_TECNICAMENTE pelo Codex, nível B; INTEGRADA e conferida em F04-A-04 | COMMITADA em `850bb06` | `feat/f04a-resumo-resultado`, base `6f1b53c`, destino `feat/b01-fundacao-api` | PUBLICADA; PR [#11](https://github.com/GustavoECocchi/ConvIQ/pull/11) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `cd6745c` |
| [F04-B — Detalhe do resultado](docs/registro/F04-B.md) | FINALIZADA (F04-B-01, Opus); O1 em F04-B-03 | APROVADA_TECNICAMENTE em F04-B-02 (revisão independente, sem impeditivos), nível B; INTEGRADA em F04-B-04 | COMMITADA em `8b8167d`; head documental `cdcf697` | `feat/f04b-detalhes-resultado`, base `cd6745c`, destino `feat/b01-fundacao-api` | PUBLICADA; PR [#12](https://github.com/GustavoECocchi/ConvIQ/pull/12) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `c66eba9` |
| [F05-A — Transcrição com evidências](docs/registro/F05-A.md) | FINALIZADA (F05-A-01, Sonnet) | APROVADA_TECNICAMENTE em F05-A-02 (revisão independente Claude Opus, sem impeditivos), nível A; INTEGRADA em F05-A-04 | COMMITADA em `574f970`; head documental `ff26e14` | `feat/f05a-transcricao`, base `c66eba9`, destino `feat/b01-fundacao-api` | PUBLICADA; PR [#13](https://github.com/GustavoECocchi/ConvIQ/pull/13) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `3a5de83` |
| [F05-B — Ver evidência](docs/registro/F05-B.md) | FINALIZADA (F05-B-01, Sonnet); correções F05-B-03/04/05 (Opus) | APROVADA_TECNICAMENTE em F05-B-06; INTEGRADA em F05-B-10 | Entrega `f90ddc5`, registros `5a8fc8a`/`cadfa5d`; F05-B-10 local em F06-A | `feat/f05b-ver-evidencia`, base `3a5de83` | PUBLICADA; PR [#14](https://github.com/GustavoECocchi/ConvIQ/pull/14) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `7821eee` |
| [F06-A — Integração real por texto](docs/registro/F06-A.md) | FINALIZADA (F06-A-02, Sonnet) | APROVADA_TECNICAMENTE em F06-A-05; INTEGRADA em F06-A-07 | Entrega `1bc9675`, registro `e4fc053`; F06-A-07 local em F06-B | `feat/f06a-integracao-texto`, base `7821eee` | PUBLICADA; PR [#15](https://github.com/GustavoECocchi/ConvIQ/pull/15) MERGEADO | INTEGRADA em `feat/b01-fundacao-api`, merge `4950292` |
| [F06-B — Jornada de texto completa](docs/registro/F06-B.md) | FINALIZADA (F06-B-02, Sonnet) | APROVADA_TECNICAMENTE em F06-B-03, nível B; PR #16 ABERTO | Entrega `4725ee9`, registro de push `e78f7b6`; F06-B-07 em commit documental posterior | `feat/f06b-jornada-texto`, base `4950292` | PUBLICADA; [PR #16](https://github.com/GustavoECocchi/ConvIQ/pull/16) ABERTO contra `feat/b01-fundacao-api` | NAO_INTEGRADA em `feat/b01-fundacao-api` |

Os demais PRs B, F, C e I continuam planejados. Os novos cartões constam de
[PRs pequenos de áudio](docs/planejamento/PRS_BACKEND_AUDIO.md), com estados
iniciais, branches propostas, dependências e critérios. O PR #1 foi
integrado em INT01-06; B13 foi integrado e verificado em B13-10.
B14 foi integrada pelo PR #4; F01 iniciou a frente frontend no worktree isolado.
F02–F06 foram subdivididos no [roteiro de navegação](docs/planejamento/PRS_FRONTEND_NAVEGACAO.md). F01–F06-A estão integrados; F06-A chegou à branch padrão pelo PR #15 (`4950292`), conferido em F06-A-07. F06-B foi executado em F06-B-02 (Claude Sonnet), aprovado tecnicamente em F06-B-03, publicado em F06-B-06 e aberto como PR #16 em F06-B-07; integração pendente.
Criar/atualizar a ficha de cada tarefa
quando encaminhada, sem declarar conclusão por antecipação.

### Fotografia Git vigente — 15/10/2026, F06-B-07 (Codex, PR #16)

- Branch padrão e destino remoto `feat/b01-fundacao-api` em `4950292679fb735a8c8daaa7324adccff300e615`, confirmado no GitHub após PR #15 MERGED. Merge com pais `7821eee` e `e4fc053`; árvore `aa22b986` igual à versão aprovada.
- Worktree F06-A `/home/gustavoecocchi/Documents/CONVIQ-f06a` em `e4fc053`. Worktree F06-B `/home/gustavoecocchi/Documents/CONVIQ-f06b`, branch `feat/f06b-jornada-texto` sobre `4950292`, entrega técnica `4725ee9fa88bf31396df2d6da19bf008bf9f5e94` e registro de publicação `e78f7b6ba1b53f02041cb78ee05752ca34346ee8`, ambos publicados. [PR #16](https://github.com/GustavoECocchi/ConvIQ/pull/16) ABERTO; no momento da abertura, head `e78f7b6`, base `4950292`, 19 arquivos, 2 commits, `mergeable=true`, sem checks remotos listados. Este snapshot, ficha F06-B-07 e STATUS entram em commit documental posterior; seu hash deve ser consultado por `git rev-parse HEAD`. Após a publicação desse registro, índice e worktree ficam limpos; integração não feita.
- Raiz `CONVIQ` em `fix/b12-contexto-risco`/`a13e889`, com `REGISTRO_TRABALHO.md` e `prompt.md` locais preservados; worktree F05-B em `cadfa5d`, também preservado. Documentação DOC02 em worktree isolado `docs/documentacao-conviq`, ainda local e não integrada; não faz parte da entrega F06-B.
