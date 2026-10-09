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
| [B14 — Normalização Unicode e evidências](docs/registro/B14.md) | FINALIZADA (B14-01, Sonnet) | INTEGRADO em B14-07; aceite B14-04; PR [#4](https://github.com/GustavoECocchi/ConvIQ/pull/4) MERGEADO | COMMITADO em `13b1519`; registros B14-05–07 publicados junto do F01 no PR #5, ainda fora do destino | `fix/b14-unicode-evidencias`, base `4063830`, HEAD `13b1519` | PUBLICADA em `origin/fix/b14-unicode-evidencias` (`13b1519`) | INTEGRADA em `feat/b01-fundacao-api`, merge `b688afb` |
| [F01 — Fundação React](docs/registro/F01.md) | FINALIZADA (F01-01, Codex) | APROVADO tecnicamente em F01-05 após revisão Opus F01-04 | Entrega COMMITADA em `d8e06b2`; registro F01-06 no HEAD documental posterior | `feat/f01-fundacao-react`, base `b688afb`, HEAD `89e0801` | PUBLICADA em `origin/feat/f01-fundacao-react`; PR [#5](https://github.com/GustavoECocchi/ConvIQ/pull/5) ABERTO | NAO_INTEGRADA |
| [F02-A — Tipos C01 e exemplos](docs/registro/F02-A.md) | FINALIZADA (F02-A-01, Sonnet) | APROVADA tecnicamente em F02-A-02 (nível B) | Entrega COMMITADA em `68ebde7`; registro F02-A-03 no HEAD documental posterior | `feat/f02a-tipos-c01`, base `89e0801` | PUBLICADA em `origin/feat/f02a-tipos-c01`; PR [#6](https://github.com/GustavoECocchi/ConvIQ/pull/6) ABERTO | NAO_INTEGRADA; empilhada sobre F01 (PR #5 aberto) |

Os demais PRs B, F, C e I continuam planejados. Os novos cartões constam de
[PRs pequenos de áudio](docs/planejamento/PRS_BACKEND_AUDIO.md), com estados
iniciais, branches propostas, dependências e critérios. O PR #1 foi
integrado em INT01-06; B13 foi integrado e verificado em B13-10.
B14 foi integrada pelo PR #4; F01 iniciou a frente frontend no worktree isolado.
F02–F06 foram subdivididos no [roteiro de navegação](docs/planejamento/PRS_FRONTEND_NAVEGACAO.md). F02-A foi aprovada tecnicamente e publicada no PR #6; os demais continuam PLANEJADOS. O prompt vigente ainda descreve F02-A.
Criar/atualizar a ficha de cada tarefa
quando encaminhada, sem declarar conclusão por antecipação.

### Fotografia Git vigente — 09/10/2026, F02-A-03 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-f02a`, branch
  `feat/f02a-tipos-c01`, base `89e0801` (head do PR #5 F01); branch padrão
  `feat/b01-fundacao-api` em `b688afb`.
- Entrega F02-A COMMITADA em `68ebde7` e PUBLICADA em
  `origin/feat/f02a-tipos-c01`. [PR #6](https://github.com/GustavoECocchi/ConvIQ/pull/6)
  OPEN, base F01, MERGEABLE; F01 [PR #5](https://github.com/GustavoECocchi/ConvIQ/pull/5) OPEN.
- Esta atualização do registro F02-A-03 entra em commit documental posterior,
  publicado na mesma branch; hash verificado no Git, sem autorreferência.
  F02-A NAO_INTEGRADA; pasta raiz e outros worktrees intocados.
