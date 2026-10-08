# Eventos gerais

Eventos que não pertencem a um único PR (operações Git e retomadas que cobrem várias frentes).

### Commit+push — 21/09/2026 — Claude Sonnet / operação Git a pedido direto do usuário

- **Pedido:** usuário interrompeu a execução do prompt B12-02 (eu tinha lido
  `prompt.md`, nenhuma edição de código ou teste executado) e pediu
  diretamente "Faça commit com push de tudo que foi feito" — instrução
  explícita para esta operação, distinta de qualquer autorização anterior
  (os prompts de B07-A-06/B11-02/B12-02 vedavam commit/push).
- **Conferência antes de agir:** `git remote -v` (origin =
  github.com/GustavoECocchi/ConvIQ), `git branch -vv` (as três branches
  `spike/b07-a-viabilidade-whisper`, `fix/b11-negacao-sentimento` e
  `fix/b12-contexto-risco` apontavam para o mesmo `cc61925`; só a primeira
  publicada), `git status`/`git diff --cached --stat` completos, suíte do
  backend (143/143) e busca por arquivos sensíveis no diff (nenhum).
- **Ação:** `git add -A`; um commit único em `fix/b12-contexto-risco`,
  mensagem detalhando o estado separado de cada frente (B07-A-06 EM_REVISAO,
  B11 EM_REVISAO, B12 FINALIZADA com R02/R03/R04 pendentes) — nenhuma
  aprovada; `git push -u origin fix/b12-contexto-risco`. Publicação
  confirmada por consulta atual à API do GitHub, hash idêntico ao local.
  Detalhe completo na "Fotografia Git vigente" no topo deste documento.
- **Decisão registrada:** consolidar as três frentes num commit só, em vez
  de separar em branches/commits próprios por PR — decisão minha, motivada
  pelo pedido literal ("tudo que foi feito") e pelo precedente já existente
  no repositório (`cc61925`). Não reconstruí histórico entre as branches
  `spike/b07-a-viabilidade-whisper`/`fix/b11-negacao-sentimento` (permanecem
  em `cc61925`, sem commit próprio) para evitar operações arriscadas
  (rebase/cherry-pick) sem pedido explícito para isso.
- **Não feito:** PR remoto (`NAO_ABERTO`); merge; integração; correção dos
  achados B12-R02/R03/R04; continuação da revisão B12-02; nenhuma operação
  destrutiva (`reset`/`stash`/`checkout` descartando trabalho).
- **Git:** entrega das três frentes agora `COMMITADO`/`PUBLICADO` em
  `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`, branch `fix/b12-contexto-risco`.
  Esta atualização do registro é posterior ao commit/push, portanto
  `NAO_COMMITADA`/`NAO_PUBLICADA` — próxima operação Git deve incluí-la.
- **Próximo responsável:** usuário decide se retoma a revisão B12-02 pelo
  Opus, pede separação em branches próprias, abre PR, ou outro
  encaminhamento. Nenhum aceite técnico foi concedido por esta operação.

### Análise de estado e relatório ao Codex — 06/10/2026 — Claude Sonnet / análise

- **Pedido:** usuário pediu a análise do estado atual do ConvIQ e, em seguida,
  um relatório para o Codex com estado e próximos passos, com base na
  documentação. Papel: Sonnet, análise sem implementação.
- **Ação:** leitura de `AGENTS.md`, `CLAUDE.md`, índice/fichas B07-A/B11/B12,
  início de `prompt.md` e roteiro B11–B21; conferência de Git e execução da
  suíte do backend (143 passed em 0,39 s). Relatório gravado em
  `docs/revisoes/RELATORIO_SONNET_2026-10-06.md`. `prompt.md` **não** foi
  alterado (segue com o prompt B12-02, desatualizado em HEAD e hashes).
- **Achados para o Codex:** `prompt.md` cita `cc61925` e diff não commitado,
  mas o HEAD é `d5fb40a`; frentes B07-A-06/B11/B12 num commit só; B12-R02/R03/
  R04 sem correção; B11 e B07-A-06 sem aceite; referência geral de governança
  ausente; registro com ~4.900 linhas.
- **Não feito:** código, testes novos, commit, push, PR, consulta ao servidor,
  releitura integral da governança. Nenhuma aprovação presumida.
- **Git:** HEAD `d5fb40a` = `origin/fix/b12-contexto-risco` (referência local).
  Esta atualização e o relatório são `NAO_COMMITADOS`/`NAO_PUBLICADOS`;
  principal, PR e integração `NAO_VERIFICADO`.
- **Próximo responsável:** Codex (decidir estrutura Git, regerar `prompt.md`
  para B12-02, verificar B11/B07-A-06).

### Retomada B11-04/B07-A-07/B12-03 — 06/10/2026 — Codex / coordenação e verificação

- **Pedido:** retomar o desenvolvimento a partir do relatório do Sonnet de
  06/10. Lidos AGENTS, governança local, relatório, plano B11–B21, fichas e
  eventos pertinentes, prompt anterior, código e testes. Referência geral
  `/home/gustavoecocchi/Documents/GOVERNANCA/REGRAS.md` indisponível;
  aplicadas as instruções do projeto.
- **Reconciliação:** branch `fix/b12-contexto-risco`, HEAD `d5fb40a` =
  `origin/fix/b12-contexto-risco` **local**; `git diff cc61925..d5fb40a`
  confirma B07-A-06/B11/B12 no mesmo commit. Antes da atuação, o registro
  tinha atualização pós-commit modificada e o relatório Sonnet de 06/10 era
  não rastreado; índice vazio. Nenhuma alteração descartada. A descrição
  do prompt antigo (`cc61925`, diff não commitado) divergia do Git e foi
  substituída. O commit composto será mantido durante a revisão.
- **Verificação:** SHA-256 dos nove arquivos B12 e três artefatos B07-A-06
  conferidos; `.venv-whisper/` ignorado; sondas da composição reconfirmam
  B11-R01 corrigido e B12-R02/R03/R04 pendentes. Subconjunto de
  sentimento/sinais/composição: 99 passed. Suíte completa no sandbox
  travou no primeiro teste HTTP após 11 pontos (código 137 sob timeout),
  inclusive teste HTTP isolado; fora do sandbox, 143 passed em 0,38 s,
  dois avisos de depreciação. A causa exata do travamento no sandbox não
  foi isolada. `git diff --check` sem diagnóstico.
- **Decisões e arquivos:** B11 aceito tecnicamente em `d5fb40a`, sem
  integração; correções R03/R04 de B07-A verificadas, mas entrega parcial
  por P01 (fala real). B12 segue EM_REVISAO; `prompt.md` substituído pelo
  prompt completo para Opus sobre `d5fb40a`, com hashes atuais, achados
  e preservação das preexistências. Atualizados índice/fichas/evento em
  `REGISTRO_TRABALHO.md`. Nenhum arquivo de aplicação foi editado.
- **Git/publicação/integração:** B11, B07-A-06 e B12 COMMITADOS em
  `d5fb40a`, publicados em 21/09 conforme verificação daquele dia;
  consulta atual ao servidor `NAO_VERIFICADA`. Esta atualização de
  `REGISTRO_TRABALHO.md` e `prompt.md` está `NAO_COMMITADA`/
  `NAO_PUBLICADA`; o relatório Sonnet não rastreado também permanece
  `NAO_COMMITADO`/`NAO_PUBLICADO`. Índice vazio. Nenhum commit, push, PR,
  merge ou troca de branch nesta atuação. Destino/principal/PR remoto
  atuais `NAO_VERIFICADO`; integração nesta atuação `NAO_INTEGRADO`.
- **Pendências/próximo responsável:** usuário encaminha `prompt.md` ao
  Opus para revisar/corrigir B12; Opus registra sua atuação e devolve ao
  Codex. B07-A precisa de amostra de fala real P01 antes do fechamento;
  B13 não liberado. Após B12, Codex revalida B11 se houver mudança no
  módulo compartilhado e define a integração Git com base confirmada.

### EST01-01 — 07/10/2026 — Claude Opus / estrutura ágil de registro e Git

- **Escopo:** o usuário aprovou aplicar à estrutura as melhorias propostas para
  reduzir leitura, escrita e tokens (registro de 7.000 linhas, informação
  repetida em registro, relatório, prompt e chat, e cerimônia de Git).
- **Versão:** worktree `/home/gustavoecocchi/Documents/CONVIQ-estrutura`, branch
  `chore/estrutura-agil`, base `6d8bcfa` (head do PR #2 de B13, **empilhada**
  sobre ele porque o PR altera o `REGISTRO_TRABALHO.md`; o registro de partida
  é o do worktree B13 com os eventos B13-07 a B13-09 ainda não commitados).
- **Resultado:** `REGISTRO_TRABALHO.md` passou de 7.067 para ~80 linhas (índice
  e fotografia vigente); ficha e eventos de cada PR foram para
  `docs/registro/<ID>.md`, os eventos gerais para `GERAL.md` e as fotografias
  antigas para `FOTOGRAFIAS_HISTORICAS.md`. Divisão verificada por contagem de
  linhas: nenhuma linha perdida (a única diferença é o título "Índice atual",
  recriado), 78 de 78 eventos mapeados, só cabeçalhos e separadores novos.
  Criados `STATUS.md` (estado, próximo passo e armadilhas),
  `docs/registro/README.md` (formato do evento, até ~25 linhas) e
  `backend/scripts/sondar.py` (sondagem pela composição real, com teste).
  `SISTEMA_GOVERNANCIA_CONVIQ.md` ganhou a seção 11 (versão 1.2): registro em
  um lugar, commit e push na branch de trabalho, revisão por nível A/B,
  contraprovas obrigatórias e sondagem reproduzível; `AGENTS.md`, `CLAUDE.md`
  e o roteiro de refinamento foram alinhados.
- **Decisões que mudam regras (a confirmar pelo Codex):** (1) executor e
  revisor passam a poder commitar e dar push na branch de trabalho, com PR,
  merge e branch padrão sob ordem do usuário; (2) nível B dispensa o Opus,
  salvo achado impeditivo; (3) PRs de mesmo nível sobre os mesmos arquivos
  podem ser entregues juntos.
- **Validação:** `pytest` em `backend/` do worktree → 273 passed (271 de B13 +
  2 do `sondar.py`); `sondar.py` executado de outra pasta, mostrando o `app`
  do próprio checkout; `git diff --check`. Não reexecutado: o histórico não
  foi reaberto (movido sem alteração).
- **Pendências:** os prompts já escritos (`prompt.md`, `docs/planejamento/`)
  não foram alterados e ainda citam o formato antigo; `REGISTRO_TRABALHO.md`
  da pasta raiz e do worktree B13 continuam com o formato longo até esta
  branch ser integrada. Os links `](#...)` foram trocados por arquivos só na
  tabela do índice.
- **Git:** tudo `NAO_COMMITADO`/`NAO_PUBLICADO`; PR `NAO_ABERTO`;
  `NAO_INTEGRADO`. Nenhum commit, push, merge, reset ou stash.
- **Próximo:** Codex analisa; o usuário decide integrar depois do PR #2
  (esta branch parte do head dele, então vem em seguida) e atualizar os
  prompts pendentes.

### EST01-02 — 07/10/2026 — Codex / revisão inicial

- **Escopo/versão:** revisão do worktree `CONVIQ-estrutura`, branch
  `chore/estrutura-agil`, HEAD/base `6d8bcfa` e diff local; PR #2
  consultado no servidor: `OPEN`, head `6d8bcfa`, destino
  `feat/b01-fundacao-api`, `MERGEABLE`.
- **Conferido:** 7.067 linhas do registro longo B13 comparadas com índice e
  arquivos divididos: só 16 links da tabela mudaram; 44 links relativos
  auditados, um quebrado em `B01.md:85`. Sondagem de outra pasta importou
  o app do worktree; suíte completa fora do sandbox: 273 passed, dois avisos.
- **Achados:** seção 11 se dizia adotada antes do aceite e concedia
  commit/push sem autorização da sessão; regra só por hash não cobria diff
  local; B16 é nível A por associação contextual; agrupamentos B15+B16 e
  B14+B19 não podem ser automáticos. JSON do sondar omitia caminho do app.
- **Estado/Git:** divisão do registro, STATUS, contraprovas e sondagem
  aceitos como desenho; EST01 EM_REVISAO. Nada commitado, publicado,
  aberto como PR ou integrado nesta atuação. Próximo: corrigir e revalidar.

### EST01-03 — 07/10/2026 — Codex / correções e verificação final

- **Escopo/versão:** pedido do usuário para corrigir EST01. Worktree
  `CONVIQ-estrutura`, branch `chore/estrutura-agil`, HEAD/base
  `6d8bcfa`; entrega = diff local e arquivos não rastreados.
- **Correção:** seção 11 passa a valer após aceite e integração; commit/push
  exigem autorização do usuário para a entrega. Entrega local é identificada
  por HEAD, status, diff e arquivos não rastreados. B16 é nível A; agrupamento
  depende de decisão expressa e conferência de dependências. Alinhados
  `AGENTS.md`, `CLAUDE.md`, `STATUS.md`, roteiro e guia do registro.
- **Outros arquivos:** link da ficha B01 corrigido; `sondar.py --json`
  inclui o caminho do app, coberto pelo teste existente atualizado.
- **Validação conferida:** 44 links relativos, zero quebrados; JSON executado
  de `/tmp` aponta para o app deste worktree; suíte completa fora do
  sandbox: 273 passed, dois avisos de depreciação; `git diff --check` limpo.
  Não executados: frontend, áudio, merge ou teste de integração remota.
- **Estado/Git:** EST01 FINALIZADA e APROVADA tecnicamente; ainda
  NAO_COMMITADA, NAO_PUBLICADA, PR próprio NAO_ABERTO, NAO_INTEGRADA.
  PR #2 segue `OPEN`; destino previsto `feat/b01-fundacao-api`.
  Nenhum commit, push, merge, reset ou stash nesta atuação.
- **Próximo:** usuário decide publicação/PR de EST01; integrar depois do
  PR #2 e verificar o destino antes de declarar EST01 integrada.

### EST01-04 — 08/10/2026 — Codex / commit, publicação e PR

- **Pedido/versão:** usuário mandou dar sequência após a recomendação de
  publicar EST01. Branch `chore/estrutura-agil`, base `6d8bcfa`; o
  merge B13 `2811d84` tem árvore idêntica à base, então o diff do PR
  contém só EST01.
- **Validação própria:** 273 testes aprovados, dois avisos conhecidos;
  43 links relativos válidos, zero quebrados. `git diff --cached --check`
  limpo após remover linhas em branco finais de 17 arquivos migrados.
  O PR remoto lista os 28 arquivos esperados, sem código B13 extra.
- **Git:** entrega commitada em `53823a17adf5199f3a117abba9a8535b3aca193f`,
  enviada a `origin/chore/estrutura-agil`. PR
  [#3](https://github.com/GustavoECocchi/ConvIQ/pull/3) aberto para
  `feat/b01-fundacao-api` em `2811d84`; na conferência inicial,
  `OPEN`, não draft, `MERGEABLE/CLEAN`, sem checks ou revisão
  impeditiva. Este evento, índice, fotografia e STATUS formam o
  commit documental HEAD posterior, enviado à mesma branch.
- **Estado/próximo:** EST01 FINALIZADA, APROVADA tecnicamente,
  COMMITADA e PUBLICADA; PR ABERTO, NAO_INTEGRADA. Nenhum merge,
  reset ou stash. Usuário decide a integração do PR #3; Codex
  verifica o destino antes de declarar a seção 11 vigente. B14
  permanece liberado e não foi iniciado nesta atuação.

### EST01-05 — 08/10/2026 — Codex / merge e verificação no destino

- **Pedido/versão:** usuário autorizou mesclar o PR #3. Antes: `OPEN`,
  head `5c2c421`, destino `feat/b01-fundacao-api` em `2811d84`,
  `MERGEABLE/CLEAN`, sem checks ou revisão impeditiva; 28 arquivos
  esperados. Worktrees existentes preservados.
- **Git:** `gh pr merge 3 --merge --match-head-commit 5c2c421...`
  concluiu sem excluir a branch. Servidor confirmou `MERGED`, merge
  `4063830db9b5f8400b60b8c09e9413b35115b106`, pais `2811d84`
  e `5c2c421`; branch padrão aponta ao merge, origem preservada.
- **Verificação própria:** clone isolado da árvore integrada em `/tmp`,
  removido depois. Árvore Git igual à do head aprovado; `app.__file__`
  apontou ao clone. Suíte completa: 273 passed, dois avisos conhecidos;
  43 links relativos válidos. Frontend e áudio não executados.
- **Estado/próximo:** EST01 FINALIZADA, APROVADA, COMMITADA,
  PUBLICADA e INTEGRADA; seção 11 vigente. Este registro pós-merge
  fica local no worktree B14, NAO_COMMITADO/NAO_PUBLICADO; não houve
  commit direto na branch padrão. B14 liberado e preparado em B14-00.
