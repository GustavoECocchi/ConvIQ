# Fotografias Git históricas e introduções do índice

Fotografias que já não são a vigente, preservadas sem alteração. A vigente fica em `REGISTRO_TRABALHO.md`.

## Introdução do índice antes da reorganização (07/10/2026, B13-08)


Fotografia atualizada em 07/10/2026 pelo Codex (B13-08). B13 foi finalizada
pelo Sonnet em B13-01, corrigida pelo Opus em B13-03 e aprovada tecnicamente
pelo Codex em B13-04. A versão aprovada foi commitada em `ebed307`, e o
registro da publicação em `6d8bcfa`. Ambos foram publicados no PR #2 para
`feat/b01-fundacao-api`.
Consulta atual ao servidor confirma PR #2 `OPEN` e B13 NAO_INTEGRADA.
O prompt de integração/verificação substituiu o prompt de revisão B13
já consumido em `prompt.md`, ainda local e não executado.
B11/B12 estão integrados pelo PR #1;
B07-A segue parcial.
Fotografias anteriores são históricas.


### Fotografia Git histórica — 07/10/2026, B13-07 (Codex)

- Consulta atual a `gh pr view 2`: [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2)
  `OPEN`, não draft, head `6d8bcfa`, base
  `feat/b01-fundacao-api` em `9921f57`, `MERGEABLE`,
  sem checks listados nem decisão de revisão. `git ls-remote`
  confirmou os mesmos hashes das branches. B13 permanece APROVADO
  tecnicamente e NAO_INTEGRADA; nenhum merge nesta atuação.
- Worktree B13 em `fix/b13-intencao-oportunidade`, HEAD `6d8bcfa`;
  `REGISTRO_TRABALHO.md` e `prompt.md` modificados localmente, índice
  vazio. O evento posterior do Opus, "Retomada sem execução", foi
  preservado; este registro B13-07 é local e foi sincronizado com a
  cópia da pasta raiz. Código, testes e PR não foram alterados.

### Fotografia Git histórica — 07/10/2026, B13-06 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`, branch
  `fix/b13-intencao-oportunidade`, HEAD `6d8bcfacbc4ab9583c74cbf3b426f263884148cf`,
  base `9921f579481fdfac098576de425b7ed19df8ef8d`. Entrega aprovada
  COMMITADA em `ebed307`; registro da publicação/PR COMMITADO em
  `6d8bcfa`. `prompt.md` é rascunho local preexistente, fora do PR;
  atualização B13-06 deste registro ainda não commitada.
- Servidor: `origin/fix/b13-intencao-oportunidade` em `6d8bcfa`, destino
  `feat/b01-fundacao-api` em `9921f57`. PR
  [#2](https://github.com/GustavoECocchi/ConvIQ/pull/2) `OPEN`, não draft,
  head `6d8bcfa`, `MERGEABLE`, sem checks listados ou decisão de revisão
  nesta consulta. B13 NAO_INTEGRADA; nenhum merge.
- A alteração de `6d8bcfa` é só `REGISTRO_TRABALHO.md`; os sete arquivos
  de código/testes/documentação aprovados permanecem como em `ebed307`,
  com 271 testes e 21 sondas verificados em B13-04. A cópia do registro
  na pasta raiz foi sincronizada; seu trabalho preexistente em outra
  branch foi preservado.

### Fotografia Git histórica — 07/10/2026, B13-05 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`, branch
  `fix/b13-intencao-oportunidade`, base `9921f57`. A versão aprovada de
  B13 (sete arquivos), o registro até B13-04 e o relatório Sonnet estão
  COMMITADOS em `ebed307d0861b54de6f1f7664d02b4f64a0fb407`.
  Conferi os sete hashes dos arquivos aprovados após o commit. A atualização
  B13-05 deste registro ainda é local; `prompt.md` é rascunho local
  preexistente, fora do commit/PR. Índice vazio após o primeiro commit.
- `origin/fix/b13-intencao-oportunidade` publicado em `ebed307`;
  PR [#2](https://github.com/GustavoECocchi/ConvIQ/pull/2) ABERTO,
  `head=ebed307`, `base=feat/b01-fundacao-api` em `9921f57`.
  Servidor informou `mergeable=MERGEABLE` e nenhuma verificação automática
  listada nesta consulta. B13 NAO_INTEGRADA. Nenhum merge executado.
- O registro da pasta raiz será sincronizado após o fechamento documental
  desta atuação. As alterações preexistentes de sua branch foram preservadas.

### Fotografia Git histórica — 07/10/2026, B13-04 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`, branch
  `fix/b13-intencao-oportunidade`, HEAD/base `9921f57`, índice vazio.
  Entrega aprovada = diff local dos mesmos sete arquivos de B13-03,
  com correção documental de uma referência no `backend/README.md` pelo
  Codex em B13-04. Seis hashes de B13-03 permanecem iguais; README final
  `14dd5a86571e7ab0897b36131ad338f60f6136d9ae7684a614cc9f565ace965d`.
  `REGISTRO_TRABALHO.md` e `prompt.md` modificados localmente; relatório
  Sonnet não rastreado. Nenhum commit/push/PR/merge nesta verificação.
- Consulta atual: branch padrão/destino `feat/b01-fundacao-api` em
  `9921f579481fdfac098576de425b7ed19df8ef8d` no servidor; branch B13
  remota ausente e lista de PRs B13 vazia. B13 NAO_PUBLICADA/
  NAO_INTEGRADA, PR remoto NAO_ABERTO.
- Verificação própria: suíte completa 271 passed, dois avisos; 21 sondas
  de composição com `app.__file__` do worktree, recortes e referências
  conferidos; funções centrais de risco B12 iguais à base integrada por
  AST; `git diff --check` limpo. Os 13 casos em servidor real são relato
  do Opus, não reexecução do Codex.
- A cópia do registro na pasta raiz `/home/gustavoecocchi/Documents/CONVIQ`
  foi sincronizada com esta fotografia; a pasta raiz continua em outra
  branch com suas alterações preexistentes. O código B13 está só no worktree.

### Fotografia Git histórica — 07/10/2026, B13-03 (Opus)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`, branch
  `fix/b13-intencao-oportunidade`, HEAD e base `9921f57`, índice vazio.
  Consulta atual ao servidor nesta atuação: `feat/b01-fundacao-api` =
  `9921f57` (`git ls-remote`); branch remota B13 inexistente; único PR do
  repositório é o #1 (B11/B12, MERGED) — PR B13 `NAO_ABERTO`.
- **Antes:** sete SHA-256 de B13-01 do prompt conferidos 7/7; registro e
  `prompt.md` modificados pelo Codex; relatório Sonnet não rastreado.
- **Ao encerrar:** os mesmos sete arquivos com as correções B13-03 (hashes
  no evento B13-03) e este registro, `NAO_COMMITADOS`/`NAO_PUBLICADOS`.
  `prompt.md` e o relatório Sonnet preservados sem edição. A pasta raiz
  `/home/gustavoecocchi/Documents/CONVIQ` não foi tocada. Nenhum commit,
  push, PR, merge, reset ou stash.

### Fotografia Git histórica — 07/10/2026, B13-02 (Codex)

- Worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`, branch
  `fix/b13-intencao-oportunidade`, HEAD/base `9921f57`. Sete arquivos de
  implementação/testes/documentação com diff local NAO_COMMITADO e
  SHA-256 conferidos com B13-01; `REGISTRO_TRABALHO.md` e `prompt.md`
  modificados localmente; relatório Sonnet não rastreado. Índice vazio.
- GitHub: branch padrão `feat/b01-fundacao-api` em `9921f57`, branch
  remota B13 ausente (404), listagem de PRs B13 vazia. B13
  NAO_PUBLICADA/NAO_INTEGRADA; nenhum commit/push/PR/merge nesta revisão.
- Suíte completa no worktree: 255/255 fora do sandbox, dois avisos;
  execução no sandbox parou no primeiro teste HTTP e terminou 137 pelo
  timeout. Sondas próprias com `app.__file__` apontando ao worktree
  confirmaram B13-R01/R02 e os critérios principais. Servidor real e
  comparação de 48 falhas na base permanecem evidências relatadas pelo
  Sonnet, não executadas pelo Codex.
- A pasta raiz `/home/gustavoecocchi/Documents/CONVIQ` segue na branch
  `fix/b12-contexto-risco` com alterações preexistentes preservadas;
  seu evento local INT01-07/B13-01 foi reconciliado abaixo sem apagar
  B13-01 do Sonnet. Prompt de revisão Opus substitui o prompt de
  execução B13 neste worktree e na pasta raiz.

### Fotografia Git histórica — 07/10/2026, B13-01 (Sonnet)

- **Worktree/branch/base:** `/home/gustavoecocchi/Documents/CONVIQ-b13`,
  branch `fix/b13-intencao-oportunidade`, criada com `git worktree add -b`
  de `9921f579481fdfac098576de425b7ed19df8ef8d`. A branch padrão
  `feat/b01-fundacao-api` foi confirmada **no servidor** nesta atuação
  (`gh repo view` e `git ls-remote origin`): mesmo hash `9921f57`, que
  contém o merge `e31e6ba` de B11/B12. HEAD do worktree = base; índice vazio.
- **Alterações:** sete arquivos modificados no worktree, `NAO_COMMITADOS`
  (lista e SHA-256 no evento B13-01). Nenhum arquivo não rastreado.
- **Pasta raiz preservada:** `/home/gustavoecocchi/Documents/CONVIQ` continua
  em `fix/b12-contexto-risco` (HEAD `b14f0a5`, à frente do remoto), com
  `PLANO_DESENVOLVIMENTO.md`, `REGISTRO_TRABALHO.md`, o cartão de refinamento
  e `prompt.md` modificados e `PROMPT_B12_05_OPUS.md` e o relatório Sonnet
  não rastreados — nada disso foi tocado. Este registro é o do worktree
  (base `9921f57`); a cópia da pasta raiz tem modificações próprias do Codex
  que não foram incorporadas aqui.
- Publicação `NAO_PUBLICADA`; PR remoto `NAO_ABERTO`; `NAO_INTEGRADO`.
  Nenhum commit, push, PR, merge, reset ou stash.

### Fotografia Git histórica — 07/10/2026, INT01-06/B13-00 (Codex)

- GitHub confirmou o PR #1 `MERGED` em 07/10/2026 19:50:03 UTC, merge
  `e31e6ba81692c61e0b0615d349972e2b3a0c459d`, na branch padrão
  `feat/b01-fundacao-api`. Pais `6169fec` e `ae71f84`; a árvore do merge
  não difere do head do PR. A suíte completa pós-merge passou 212/212,
  com dois avisos de depreciação. Os seis hashes aprovados de B12 conferem
  no commit integrado. B01–B04/C01 já estavam no destino desde `6169fec`;
  B11/B12 INTEGRADOS; B07-A experimental segue fora.
- Worktree `/tmp/conviq-default-merged`, branch local de coordenação
  `coord/posmerge-b13`, HEAD `e31e6ba`; mudanças documentais locais em
  `REGISTRO_TRABALHO.md`, `PLANO_DESENVOLVIMENTO.md`, roteiro de refinamento
  e `prompt.md` B13. O prompt B12-05 consumido, antes só local, foi
  preservado em `docs/planejamento/PROMPT_B12_05_OPUS.md` com SHA-256
  `d39c637cfb7239ae410083fb05ee3295c3b5ef7f1823fe24d3482387e362b5f9`.
  O registro/ficha/prompt estão NAO_COMMITADOS nesta fotografia, sem
  publicação posterior ao merge. O relatório Sonnet não rastreado no
  worktree original segue preservado.

### Fotografia Git histórica — 07/10/2026, INT01-05 (Codex)

- O registro do PR foi commitado em `ae71f84` e publicado em
  `origin/integrate/b11-b12-analise`. O GitHub confirmou o PR #1 `OPEN`,
  head `ae71f844dcedde710627a03cda7830329ab27d4e`, base
  `feat/b01-fundacao-api` ainda em `6169fec`, `MERGEABLE` e sem checks
  listados. B11/B12 NAO_INTEGRADAS; não houve merge. Esta nota é local,
  posterior ao commit/push, e fica fora do commit publicado para evitar
  um ciclo de commits contendo o próprio hash.

### Fotografia Git histórica — 07/10/2026, INT01-04 (Codex)

- PR [#1](https://github.com/GustavoECocchi/ConvIQ/pull/1) confirmado
  `OPEN`, não rascunho, head `integrate/b11-b12-analise` em `45e1e76`,
  base `feat/b01-fundacao-api`, `MERGEABLE`, sem checks de CI listados na
  consulta. Nenhum merge feito; B11/B12 continuam APROVADAS tecnicamente,
  PUBLICADAS na branch de integração e NAO_INTEGRADAS na branch padrão.
  Esta atualização do registro é local, posterior à abertura do PR.

### Fotografia Git histórica — 07/10/2026, INT01-03 (Codex)

- GitHub confirmou `integrate/b11-b12-analise` em
  `45e1e7665b8a6c2e8cdd8ad2fdc1e729d7fa84af`. A comparação remota com
  `feat/b01-fundacao-api` mostrou `ahead_by=1`, um único commit e 18
  arquivos esperados, sem script, requisitos, WAV ou decisão experimental
  de B07-A. PR ainda não aberto e nenhum merge realizado. Esta atualização
  de registro é local, posterior ao push.

### Fotografia Git histórica — 07/10/2026, INT01-02 (Codex)

- Commit local `45e1e76` em `integrate/b11-b12-analise`, base `6169fec`,
  contém 18 arquivos de B11/B12 e documentação de coordenação. O diff
  preparado passou `git diff --cached --check`; a suíte completa da
  composição passou 212/212 antes do commit. Nenhum artefato executável de
  B07-A entrou. Esta atualização de registro é local e posterior ao commit.
- Sem push, PR ou merge nesta fotografia. A branch padrão confirmada na
  última consulta é `feat/b01-fundacao-api` em `6169fec`. O worktree de
  origem continua com `prompt.md` modificado e relatório Sonnet não
  rastreado, ambos preservados.

### Fotografia Git histórica — 07/10/2026, INT01-01 (Codex)

- Worktree `/tmp/conviq-b11-b12-analise`, branch
  `integrate/b11-b12-analise`, HEAD/base `6169fec`. Arquivos da aplicação
  B11/B12 copiados de `b14f0a5` sem diferença de conteúdo; módulo novo
  `negacao.py` também confere por SHA-256. Os scripts, o WAV e as decisões
  experimentais de B07-A não foram trazidos. Entram documentos de
  planejamento, governança, registro e revisão pertinentes ao ciclo;
  B07-A continua parcial no registro.
- Suíte completa nessa composição: 212 passed, dois avisos de depreciação;
  `git diff --check` limpo. Branch ainda local, arquivos NAO_COMMITADOS,
  sem push, PR ou merge nesta fotografia. O worktree de origem permanece em
  `fix/b12-contexto-risco` (`b14f0a5`) com `prompt.md` modificado e relatório
  Sonnet não rastreado, preservados fora desta entrega.

### Fotografia Git histórica — 07/10/2026, B12-09 (Codex)

- Commit local `b14f0a5` na branch `fix/b12-contexto-risco`: seis arquivos
  B12-04/B12-06, relatório Opus e versão anterior deste registro. Os seis
  hashes aprovados em B12-07 conferem com os arquivos de `b14f0a5`;
  `git diff --cached --check` estava limpo. O servidor só foi conferido
  antes do commit, quando a branch remota apontava para `d5fb40a`;
  `b14f0a5` ainda não foi publicado nesta etapa. Esta atualização do
  registro é local e posterior ao commit.
- `prompt.md` modificado e o relatório Sonnet não rastreado permanecem
  fora do commit. B11/B12 ainda não integrados à branch padrão.

### Fotografia Git histórica — 07/10/2026, B12-08 (Codex)

- Consulta atual ao GitHub: branch padrão `feat/b01-fundacao-api` no hash
  `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`; branch
  `fix/b12-contexto-risco` no hash
  `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`; `main` retorna 404;
  listagem de PRs (todos os estados, limite 20) vazia. Branches remotas
  listadas: `feat/b01-fundacao-api`, `fix/b12-contexto-risco` e
  `spike/b07-a-viabilidade-whisper`. A referência remota **local**
  `origin/main` em `8d48e75` está obsoleta para decidir o destino.
- O conteúdo aprovado de B01–B04/C01 no commit `6169fec` está presente na
  branch padrão confirmada. B12 continua somente na branch de trabalho,
  com seis arquivos locais aprovados fora de commit. Um PR direto de
  `fix/b12-contexto-risco` para a branch padrão incluiria B07-A parcial,
  pois `cc61925` e `d5fb40a` misturam as frentes.
- Recomendação de coordenação: preservar a versão B12-07 em commit na
  branch atual; depois preparar uma branch de integração limpa a partir
  da branch padrão confirmada, contendo apenas B11/B12 e a documentação
  pertinente, revisar o diff e validar antes de abrir PR. Nenhuma operação
  Git de escrita foi autorizada nem executada nesta consulta.

### Fotografia Git histórica — 07/10/2026, B12-07 (Codex)

- Raiz `/home/gustavoecocchi/Documents/CONVIQ`, branch
  `fix/b12-contexto-risco`, HEAD `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`
  (pai `cc61925`), igual à referência remota **local**
  `origin/fix/b12-contexto-risco`. Servidor não consultado; principal,
  destino e PR remoto atuais `NAO_VERIFICADO`.
- Os seis arquivos B12-04/B12-06 aprovados tecnicamente permanecem em diff
  local `NAO_COMMITADO`/`NAO_PUBLICADO`, com SHA-256 na ficha B12-07.
  `REGISTRO_TRABALHO.md` contém este aceite; `prompt.md` (B12-05 já
  executado) segue modificado, e os relatórios Opus/Sonnet em
  `docs/revisoes/` seguem não rastreados. Índice vazio. Nenhum código da
  aplicação foi alterado pelo Codex nesta atuação.
- Nenhum commit, push, PR ou merge nesta atuação. B12 `APROVADO`
  tecnicamente/`PARCIALMENTE_COMMITADO`/`NAO_INTEGRADO`; publicação atual
  das correções `NAO_PUBLICADA`. O hash do HEAD não contém as correções
  aprovadas; antes da integração, conferir que eventual commit corresponda
  aos seis hashes aprovados e ao conteúdo do registro.

### Fotografia Git histórica — 07/10/2026, B12-06 (Opus)

- Raiz, branch e HEAD iguais à fotografia B12-05 abaixo
  (`fix/b12-contexto-risco`, `d5fb40a`, pai `cc61925`). Referências remotas
  só locais; servidor não consultado; principal, destino e PR remoto atuais
  `NAO_VERIFICADO`.
- **Antes da atuação:** os seis arquivos B12-04 com os SHA-256 do prompt
  B12-05 (6/6 conferidos), registro e `prompt.md` modificados, relatório
  Sonnet não rastreado, índice vazio.
- **Ao encerrar:** os mesmos seis arquivos com as correções B12-06 (hashes
  no evento B12-06) e este registro, todos `NAO_COMMITADOS`/
  `NAO_PUBLICADOS`. `prompt.md` (instrução B12-05) e o relatório Sonnet
  preservados sem edição. Índice vazio. Nenhuma operação Git de escrita.

### Fotografia Git histórica — 07/10/2026, B12-05 (Codex)

- Raiz `/home/gustavoecocchi/Documents/CONVIQ`, branch
  `fix/b12-contexto-risco`, HEAD `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`
  (pai `cc61925`), igual à referência remota **local**
  `origin/fix/b12-contexto-risco`. Servidor não consultado nesta atuação;
  principal, destino e PR remoto atuais `NAO_VERIFICADO`.
- Seis arquivos de código/testes/documentação corrigidos pelo Opus em
  B12-04 continuam modificados e `NAO_COMMITADOS`/`NAO_PUBLICADOS`.
  `REGISTRO_TRABALHO.md` contém também esta verificação do Codex;
  `prompt.md` foi substituído pelo prompt B12-05 e o relatório Sonnet de
  06/10 continua não rastreado. Índice vazio. O código da aplicação
  commitado em `d5fb40a` não foi alterado pelo Codex nesta verificação.
- Nenhum commit, push, PR ou merge nesta atuação. B12 `PARCIALMENTE_COMMITADO`,
  `EM_CORRECAO`, `NAO_INTEGRADO`; B11 permanece tecnicamente aprovado em
  `d5fb40a`, sujeito a revalidação se a correção alterar a negação comum.

### Fotografia Git histórica — 06/10/2026, B12-04 (Opus)

- **Raiz/branch/HEAD:** `/home/gustavoecocchi/Documents/CONVIQ`,
  `fix/b12-contexto-risco`, `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`
  (pai `cc61925`), iguais à retomada do Codex abaixo. Referências remotas
  só locais (`origin/fix/b12-contexto-risco` = HEAD; `origin/main` =
  `8d48e75`); servidor não consultado. Principal, destino e PR remoto
  atuais `NAO_VERIFICADO`; nenhuma integração.
- **Árvore antes da atuação:** igual à descrita pelo Codex — registro e
  `prompt.md` modificados, relatório Sonnet não rastreado, índice vazio; os
  nove SHA-256 de entrada de B12 conferidos 9/9.
- **Árvore ao encerrar:** correções B12-04 em seis arquivos rastreados
  (`sinais_comerciais.py`, três testes, README, C01) e este registro,
  todos `NAO_COMMITADOS`/`NAO_PUBLICADOS`. `prompt.md` e o relatório Sonnet
  preservados sem edição. Índice vazio. Nenhuma operação Git de escrita.

### Fotografia Git histórica — 06/10/2026, retomada (Codex)

- **Raiz/branch/HEAD:** `/home/gustavoecocchi/Documents/CONVIQ`,
  `fix/b12-contexto-risco`, `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`;
  pai `cc61925f48d0981517a11480691c6f3f5465dcc0`. A referência remota
  **local** `origin/fix/b12-contexto-risco` coincide com o HEAD. Não houve
  consulta atual ao servidor; o push desse hash foi verificado em 21/09 pelo
  Sonnet. `fix/b11-negacao-sentimento` e `spike/b07-a-viabilidade-whisper`
  locais permanecem em `cc61925`. `master` local está em `3c52ea3` e a
  referência remota **local** `origin/main` em `8d48e75`; principal e destino
  de integração atuais `NAO_VERIFICADO`. Nenhuma integração realizada nesta
  atuação; PR remoto atual `NAO_VERIFICADO` (último relato: não aberto).
- **Divergência reconciliada:** o registro do Sonnet de 06/10 e seu relatório
  são posteriores ao commit; o prompt B12-02 antigo descrevia HEAD
  `cc61925` e diff local. O código e os nove hashes de B12 já estão no
  commit `d5fb40a`. `prompt.md` foi atualizado para essa versão, sem alterar
  o código. Manter o commit composto para esta revisão evita reescrever a
  versão publicada; separação em PRs Git, se necessária, será coordenada
  após a correção, com versões verificadas.
- **Árvore antes da atuação:** `REGISTRO_TRABALHO.md` modificado pelo Sonnet
  (registro de 21/09 e relatório de 06/10),
  `docs/revisoes/RELATORIO_SONNET_2026-10-06.md` não rastreado, índice vazio.
  **Árvore ao encerrar:** os dois arquivos preexistentes preservados;
  `prompt.md` e este registro modificados pelo Codex; índice vazio. Os
  arquivos da aplicação em `d5fb40a` permanecem sem alterações locais.
  Atualização de registro/prompt e relatório: `NAO_COMMITADOS`/
  `NAO_PUBLICADOS`, distintos da entrega do código `COMMITADA` e publicada
  em 21/09. Nenhuma operação Git de escrita nesta retomada.

### Fotografia Git histórica — 21/09/2026, commit+push (Sonnet)

- **Pedido:** usuário interrompeu a revisão B12-02 (eu tinha acabado de ler
  `prompt.md`, nenhuma edição de código feita) e pediu diretamente "commit
  com push de tudo que foi feito".
- **Ação:** `git add -A` sobre a árvore de trabalho (14 rastreados
  modificados + `negacao.py` novo, incluindo o conteúdo que o Codex já
  tinha escrito em `prompt.md`/`REGISTRO_TRABALHO.md` para B12-02, presente
  em disco antes desta atuação — não reescrito por mim). Um commit único,
  `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`, na branch
  `fix/b12-contexto-risco` (HEAD anterior `cc61925`, pai `6169fec`), com
  mensagem detalhando o estado de cada frente (B07-A-06, B11, B12) — nenhuma
  declarada aprovada. `git push -u origin fix/b12-contexto-risco` publicou a
  branch (nova no remoto). Publicação confirmada por consulta atual à API do
  GitHub (`gh api repos/GustavoECocchi/ConvIQ/git/ref/heads/fix/b12-contexto-
  risco`), não só referência local: hash idêntico ao local.
- **Decisão de estrutura, registrada explicitamente:** optei por um único
  commit consolidando as três frentes, em vez de separá-las em commits/
  branches próprios (o que exigiria reconstruir histórico entre branches
  que hoje compartilham o mesmo HEAD). Isso segue o pedido literal do
  usuário ("tudo que foi feito") e o precedente já existente no próprio
  repositório (`cc61925` também reuniu múltiplas frentes num commit só,
  registrado em B07-A-04). `spike/b07-a-viabilidade-whisper` e
  `fix/b11-negacao-sentimento` continuam, como ponteiros locais, apontando
  para `cc61925` — não receberam commit próprio; o conteúdo de B07-A-06 e
  B11 está fisicamente publicado via `fix/b12-contexto-risco`. Separar em
  PRs/commits próprios por frente, se desejado, fica para a coordenação.
- **Não feito:** abertura de PR remoto (só commit+push, conforme pedido);
  merge; integração na principal; correção dos achados B12-R02/R03/R04;
  continuação da revisão B12-02. Suíte do backend conferida antes do commit:
  143/143. Nenhum arquivo sensível (`.env`, credenciais) no commit —
  conferido antes de commitar.
- **Próximo responsável:** usuário decide se retoma a revisão B12-02 (Opus),
  pede a separação em branches próprias, ou outro encaminhamento. PR remoto
  `NAO_ABERTO`; principal/destino/integração `NAO_VERIFICADO`.

### Fotografia Git histórica — 21/09/2026, B12-02

- Branch `fix/b12-contexto-risco`, HEAD
  `cc61925f48d0981517a11480691c6f3f5465dcc0`, pai `6169fec`; estado consistente
  com B12-01. Índice vazio, 14 rastreados modificados e `negacao.py` não
  rastreado. As branches B11/B12/B07-A apontam ao mesmo commit: a dependência
  B11 e a entrega B12 estão na árvore local, não em commits empilhados.
- Nesta atuação, somente `prompt.md` e `REGISTRO_TRABALHO.md` foram editados;
  os nove arquivos B12 e demais preexistências foram preservados. B12 e a
  preparação continuam NAO_COMMITADOS/NAO_PUBLICADOS.
- Principal/destino/PR remoto/integração atuais NAO_VERIFICADOS, sem consulta
  ao servidor. Nenhuma operação Git de escrita nesta atuação. Revisão B11-03
  relatada não equivale a aceite final do Codex nem a integração da dependência.

### Fotografia Git histórica — 21/09/2026, B12-01

- Branch trocada nesta atuação: `git checkout -b fix/b12-contexto-risco` a
  partir da posição atual (sem especificar outro commit) — HEAD continua
  `cc61925f48d0981517a11480691c6f3f5465dcc0`, pai `6169fec`, só o nome da
  branch mudou; nenhum arquivo tocado pela troca. `spike/b07-a-viabilidade-
  whisper` e `fix/b11-negacao-sentimento` continuam existindo, apontando ao
  mesmo commit; nada foi removido delas. B12 depende de B11 (ordem 2 do
  roteiro), então empilhar sobre a árvore que já tinha B11 é a base correta,
  não uma divergência — diferente da mudança B07-A→B11, que era independente.
- Antes de editar, `git status --short` mostrava os 5 arquivos de B07-A-06 e
  os 7 de B11 (12 no total), como a fotografia B11-03 descrevia. Ao encerrar,
  1 arquivo novo (`backend/app/services/negacao.py`) e mais 8 modificados
  por B12: `backend/app/services/sentimento.py` (extração, sem mudança de
  comportamento), `backend/app/services/sinais_comerciais.py`,
  `backend/app/services/analise.py`, `backend/tests/test_sinais_comerciais.py`,
  `backend/tests/test_analise.py`, `backend/tests/test_analises_rota.py`,
  `backend/README.md`, `docs/contratos/analise-texto.md` — estes três
  últimos também tinham alterações de B11-03, preservadas e ampliadas.
  Índice vazio; nenhum commit, push, PR ou merge.
- Origem remota não consultada nesta atuação; publicação de `cc61925`
  continua conforme a última consulta ao GitHub (B07-A-05, Codex).
  Principal/destino/PR remoto: `NAO_VERIFICADO`.

### Fotografia Git histórica — 21/09/2026, B11-03

- Branch `fix/b11-negacao-sentimento`, HEAD `cc61925f48d0981517a11480691c6f3f5465dcc0`,
  pai `6169fec`, iguais ao início e ao fim da revisão; índice vazio; 12
  modificados, nenhum não rastreado — exatamente o que o prompt B11-02
  descrevia. Os sete hashes B11 do prompt conferiram 7/7 antes de editar.
- Alterados por esta revisão (6 dos 7 de B11 + registro): `sentimento.py`,
  `test_sentimento.py`, `test_analise.py`, `test_analises_rota.py`,
  `backend/README.md`, `docs/contratos/analise-texto.md`,
  `REGISTRO_TRABALHO.md`. `analise.py` continua com o hash do prompt.
  Os três arquivos de B07-A-06 e `prompt.md` não foram tocados (hashes
  iguais aos de B07-A-06/B11-02). Tudo NAO_COMMITADO/NAO_PUBLICADO; o HEAD
  não contém B11. Sem commit, push, PR, merge, checkout de arquivo, reset
  ou stash; a separação dos commits B07-A/B11 continua com a coordenação.
- Principal, destino, PR remoto e integração: NAO_VERIFICADO; servidor não
  consultado.

### Fotografia Git histórica — 21/09/2026, B11-02

- Branch `fix/b11-negacao-sentimento`, HEAD/base do diff
  `cc61925f48d0981517a11480691c6f3f5465dcc0`, pai `6169fec`. A mudança de
  branch desde B07-A-06 confere com B11-01; nenhuma nova divergência de Git.
- Índice vazio, 12 arquivos modificados, nenhum não rastreado. Os sete arquivos
  de B11 e os três de B07-A-06 foram preservados; nesta preparação apenas
  `prompt.md` e `REGISTRO_TRABALHO.md` são editados. B11, prompt e atualização
  do registro continuam NAO_COMMITADOS/NAO_PUBLICADOS; o HEAD não contém B11.
- Branch principal, destino, PR remoto e integração atuais NAO_VERIFICADOS;
  servidor não consultado. Nenhum commit, push, merge ou troca de branch nesta
  atuação. O prompt identifica a mistura de entregas sem reorganizar o Git.

### Fotografia Git histórica — 21/09/2026, B11-01

- Branch trocada nesta atuação: `git checkout -b fix/b11-negacao-sentimento`
  a partir da posição atual (sem especificar outro commit) — HEAD continua
  `cc61925f48d0981517a11480691c6f3f5465dcc0`, só o nome da branch mudou;
  nenhum arquivo tocado pela troca, nenhum reset/checkout de outra base.
  `spike/b07-a-viabilidade-whisper` continua existindo, apontando ao mesmo
  commit; nada foi removido dela.
- Antes de editar, `git status --short` mostrava só os 5 arquivos de
  B07-A-06 (já esperado, ver fotografia anterior). Ao encerrar, 12 arquivos
  modificados: os 5 de B07-A-06 (`.gitignore`, `REGISTRO_TRABALHO.md`,
  `backend/scripts/verificar_whisper.py`,
  `docs/decisoes/transcricao-whisper.md`, `prompt.md` — este último não
  tocado por mim) mais 7 de B11 (`backend/README.md`,
  `backend/app/services/analise.py`, `backend/app/services/sentimento.py`,
  `backend/tests/test_analise.py`, `backend/tests/test_analises_rota.py`,
  `backend/tests/test_sentimento.py`, `docs/contratos/analise-texto.md`).
  Índice vazio; nenhum commit, push, PR ou merge.
- Origem remota não consultada nesta atuação; publicação de `cc61925`
  continua conforme a última consulta ao GitHub (B07-A-05, Codex).
  Principal/destino/PR remoto: `NAO_VERIFICADO`.

### Fotografia Git histórica — 21/09/2026, B07-A-06

- HEAD conferido ao iniciar e ao encerrar: `cc61925f48d0981517a11480691c6f3f5465dcc0`,
  branch `spike/b07-a-viabilidade-whisper`, pai/base
  `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`; índice vazio; referência local
  `origin/spike/b07-a-viabilidade-whisper` no mesmo hash (servidor não
  consultado nesta atuação — publicação de `cc61925` continua conforme a
  consulta do Codex em B07-A-05). Ao iniciar, só `REGISTRO_TRABALHO.md`
  (B07-A-04/05) e `prompt.md` (B07-A-05) estavam modificados, como o prompt
  descrevia; nenhuma divergência.
- Alterações locais desta revisão, todas NAO_COMMITADAS/NAO_PUBLICADAS:
  `.gitignore` (R03), `backend/scripts/verificar_whisper.py` (R04, docstring),
  `docs/decisoes/transcricao-whisper.md` (R03/R04 e seção 10) e este registro.
  `requirements-whisper.txt` e o WAV permanecem iguais a `cc61925`.
  Git de B07-A passa a PARCIALMENTE_COMMITADO. Nenhum commit, push, PR,
  merge, troca de branch, reset ou stash nesta atuação.
- Principal/destino de integração e PR remoto: NAO_VERIFICADO nesta atuação
  (última consulta: B07-A-05, PR NAO_ABERTO).

### Fotografia Git histórica — 21/09/2026, B07-A-05

- HEAD conferido: `cc61925f48d0981517a11480691c6f3f5465dcc0`, branch
  `spike/b07-a-viabilidade-whisper`, pai/base
  `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`. Antes desta preparação, havia
  somente a atualização local B07-A-04 em `REGISTRO_TRABALHO.md`; ela foi
  preservada. Esta atuação substitui `prompt.md` e acrescenta este registro,
  ambos ainda NAO_COMMITADOS/NAO_PUBLICADOS.
- `gh api repos/GustavoECocchi/ConvIQ/git/ref/heads/spike/b07-a-viabilidade-whisper`
  retornou o mesmo hash em 21/09. `gh pr list --head
  spike/b07-a-viabilidade-whisper --state all` retornou lista vazia: PR remoto
  NAO_ABERTO nesta consulta. A consulta da branch principal falhou por conexão;
  destino/principal e integração seguem NAO_VERIFICADOS.
- Esta é apenas preparação de prompt, sem nova verificação técnica das correções
  relatadas em B07-A-03. O prompt vigente manda o Opus revisar de modo
  independente a versão commitada; B07-A continua PARCIAL/EM_REVISAO por P01.
  Nenhum commit, push, merge, troca de branch, instalação ou teste de aplicação
  foi executado nesta atuação.

### Fotografia Git histórica — 19/09/2026, B07-A-04

- HEAD atual: `cc61925f48d0981517a11480691c6f3f5465dcc0`, branch
  `spike/b07-a-viabilidade-whisper`, pai/base `6169fec`. A pasta estava
  limpa ao iniciar esta conferência, com índice vazio.
- O commit novo contém 13 arquivos: B07-A corrigido pelo Opus e documentação
  de PLN01/PLN02/ANA02, roteiros, plano, governança, prompts e manifesto.
  Assim, a documentação anterior do Codex foi incluída junto do trabalho
  do Claude. Não se atribui ao Codex a autoria dessa operação Git.
- Publicação confirmada no servidor: `gh api repos/GustavoECocchi/ConvIQ/git/ref/heads/spike/b07-a-viabilidade-whisper --jq .object.sha`
  retornou `cc61925f48d0981517a11480691c6f3f5465dcc0`. Não foi apenas leitura
  de referência remota local. Principal, PR e integração ainda NAO_VERIFICADO.
- Opus registrou revisão concluída em B07-A-03, entrega ainda PARCIAL;
  verificação final do Codex/áudio falado real permanecem pendentes. Esta
  conferência Git não substitui a revisão técnica da devolução do Opus.
- **Somente esta atualização do registro, feita após o commit/push, continua
  NAO_COMMITADA/NAO_PUBLICADA.** Os outros documentos recebidos permanecem
  como no commit confirmado. Nenhuma operação Git de escrita nesta atuação.

### Fotografia Git histórica — 19/09/2026, B07-A-02

Branch atual `spike/b07-a-viabilidade-whisper`, HEAD/base de código
`6169feca8c3a6cc6c5500eeab264eba817c8fbbc`. A criação da branch pelo Sonnet
já está relatada em B07-A-01. A fotografia de PLN01 abaixo é histórica.
B01–B04/C01 permanecem commitados e correspondem ao manifesto de aceite
(33/33 conferidos nesta consulta). B07-A é PARCIAL, não commitado, ainda sem
aceite; métricas de Whisper são relato do Sonnet, não reproduzidas pelo Codex
nesta consulta funcional. Plano/governança/prompt/registro modificados e
9 arquivos não rastreados (scripts, relatório/amostra, roteiros, cópias de
retomada B07-A/B11 e manifesto da revisão B07-A). Aplicação e experimento
preservados. B07-A está EM_REVISAO após análise inicial do Codex; revisão
do Opus ainda pendente. O prompt vigente encaminha essa revisão.
Índice vazio; principal, destino, publicação e PR remoto atuais NAO_VERIFICADO,
sem consulta ao servidor. Nenhuma operação Git de escrita pelo Codex.

### Fotografia Git histórica — 18/09/2026, PLN01-02/03

- Branch observada: `feat/b01-fundacao-api`; HEAD e commit agregado das entregas
  de texto: `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`; pai/base local anterior
  `master`: `3c52ea3ed0d3c3d38de5b9adf2a4a4ff320a1842`.
- A aplicação/C01/.gitignore no commit correspondem aos arquivos locais e às
  33 entradas do manifesto de aceite B04. Não há mudanças locais de código.
  Os aceites técnicos existentes permanecem; não se atribui novo teste a PLN01.
- A referência local `origin/feat/b01-fundacao-api` aponta ao mesmo commit;
  `origin/main` local permanece em `8d48e7546ad5987f12f3bb3ab1c7ded514c0e322`.
  Servidor não consultado: publicação, PR, principal e destino atuais
  NAO_VERIFICADO. O commit não está na `master` local observada; isso não
  comprova a situação da principal remota.
- DOC01/ANA01/PROD01 também entraram no commit agregado. Suas fichas abaixo
  conservam a fotografia histórica das entregas; este bloco atualiza o Git,
  sem atribuir a operação de commit/push ao Codex nesta rodada.
- PLN01 modifica plano, governança, registro e `prompt.md`, além do arquivo
  novo `docs/planejamento/PRS_BACKEND_AUDIO.md`. Tudo NAO_COMMITADO;
  índice vazio. Documentação local não integra automaticamente o HEAD.
- Não houve criação/troca de branch, commit, push, abertura de PR ou merge
  pelo Codex nesta atuação. Organização futura: uma branch por PR pequeno.
