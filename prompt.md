# B13 — Integrar o PR #2 e verificar o destino

Você é o agente responsável pela integração de B13 no ConvIQ. O usuário
encaminha este prompt para executar o próximo passo acordado: integrar o
PR #2 após conferir a versão aprovada, e verificar o resultado na branch
de destino. O envio deste prompt pelo usuário autoriza o merge desse PR
se todas as condições abaixo forem confirmadas. Execute a integração
sem pedir uma confirmação repetida; se a versão ou as condições mudaram,
registre a divergência e devolva ao Codex antes de mesclar.

## Leia e confira o estado

Leia `AGENTS.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` (seções 4.5, 5, 6,
8 e 10), o índice, a ficha e os eventos B13 em
`REGISTRO_TRABALHO.md`, o cartão B13 em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md` e o contrato C01.
`docs/governanca/REGRAS.md` e a referência geral alternativa não
estavam disponíveis na última conferência; se continuarem ausentes,
registre a limitação e siga a governança específica.

- Repositório: `/home/gustavoecocchi/Documents/CONVIQ`.
- Worktree de B13: `/home/gustavoecocchi/Documents/CONVIQ-b13`.
- PR: `https://github.com/GustavoECocchi/ConvIQ/pull/2`.
- Branch de origem: `fix/b13-intencao-oportunidade`, head publicado
  `6d8bcfacbc4ab9583c74cbf3b426f263884148cf`.
- Commit com os sete arquivos técnicos aprovados:
  `ebed307d0861b54de6f1f7664d02b4f64a0fb407`. O commit seguinte,
  `6d8bcfa`, altera só `REGISTRO_TRABALHO.md`.
- Branch padrão e destino: `feat/b01-fundacao-api`, base observada
  `9921f579481fdfac098576de425b7ed19df8ef8d`.
- Estado observado pelo Codex em 07/10/2026: PR `OPEN`, não draft,
  `MERGEABLE`, sem checks listados ou decisão de revisão; B13 aprovada
  tecnicamente em B13-04, ainda `NAO_INTEGRADA`. **Reconsulte o servidor
  antes de agir**; esta fotografia pode mudar.
- A pasta raiz está em `fix/b12-contexto-risco` com alterações locais;
  o worktree B13 tem `REGISTRO_TRABALHO.md` e `prompt.md` locais.
  Preserve todas essas alterações. Não troque a branch de um worktree
  sujo, não faça reset, stash nem descarte arquivos.

## Conferência antes do merge

1. Use `gh pr view 2` e `git ls-remote origin` para confirmar PR `OPEN`,
   origem, destino, hashes, mergeabilidade, checks e regras aplicáveis.
   Confirme que o head ainda é `6d8bcfa` e a base ainda é `9921f57`.
   Se o PR já estiver mergeado, não repita o merge: passe à verificação
   do resultado. Se head ou base mudaram, checks obrigatórios falham,
   houver conflito ou revisão impeditiva, pare antes do merge e relate.
   Não force nem contorne proteção da branch.
2. Confira que o diff remoto contém os sete arquivos técnicos de B13,
   `REGISTRO_TRABALHO.md` e o relatório Sonnet, sem `prompt.md`.
   Os sete SHA-256 aprovados em B13-04 são:

   ```text
   70ae18b36ea7f05c8d7defc1626543bae91a18ae614bcddd98612629d6b26a85  backend/app/services/sinais_comerciais.py
   061454cdf42d31cc386c97986524ef9c2bdb35fe03de9d62cb6699515c87b5c  backend/app/services/analise.py
   0e90bb5e3fc725c3941920656a83c874c11ec36732a83176e33917a8a13cc89e  backend/tests/test_sinais_comerciais.py
   1be454915d280131feee5589c3970379f8a48a51690cf6e5280d62fa45f094bc  backend/tests/test_analise.py
   73b1781caafc8e9e69e8b2618eb6124dd359c1f7270bd0c5e682be55c34c0630  backend/tests/test_analises_rota.py
   14dd5a86571e7ab0897b36131ad338f60f6136d9ae7684a614cc9f565ace965d  backend/README.md
   b927f77042908021ca691f234ab424417989808f6c7c6fed632c7a65afe3e17a  docs/contratos/analise-texto.md
   ```

## Integração autorizada e verificação

3. Se a versão e as condições acima estiverem iguais, mescle o PR #2
   pelo método **merge commit** (`gh pr merge 2 --merge`), preservando a
   branch de origem. Não use squash, rebase, auto merge nem exclusão da
   branch. Não crie outros commits ou pushes de código.
4. Confirme no servidor `MERGED`, o hash do merge, a branch de destino
   apontando para ele e que `6d8bcfa` está na ancestralidade do commit
   integrado. Não trate o hash local `origin/...` como prova remota.
5. Verifique os sete SHA-256 acima **na árvore integrada**. Use um
   checkout/worktree temporário e isolado no commit integrado para
   preservar as duas árvores sujas existentes. Confirme `app.__file__`
   apontando para esse checkout. O venv da pasta raiz tem instalação
   editável apontando ao backend da pasta raiz: rode a suíte dentro de
   `backend/` do checkout integrado com
   `PYTHONPATH=<checkout-integrado>/backend` e timeout de 60 s.
   Registre comando, resultado e avisos. Se o TestClient travar no
   sandbox, reexecute fora dele quando possível. Confira ao menos um
   caso de R01, R02 e coexistência na composição, com recortes e
   referências. Remova só o checkout temporário que você criou, após
   concluir a verificação e sem perder arquivos.
6. Atualize índice, fotografia Git, ficha B13 e seu evento próprio em
   `REGISTRO_TRABALHO.md`, preservando B13-01 a B13-07 e o evento do
   Opus. Distinga entrega FINALIZADA, revisão APROVADA, commits, push,
   PR remoto e integração. Marque `INTEGRADO` apenas depois de conferir
   o destino real. Se o merge acontecer mas a verificação falhar,
   registre `INTEGRADO` com a falha/pendência; não o descreva como
   não integrado. Sincronize a cópia local do registro na pasta raiz
   sem sobrescrever alterações preexistentes. Não faça um novo commit
   direto na branch padrão apenas para registrar o próprio hash.

Não implemente B14, B17 ou outro PR nesta tarefa; B14 só pode ser
liberado pelo Codex após a integração verificada. Não execute o prompt
B13 antigo: a revisão foi concluída em B13-03. Ao devolver, informe
hashes observados, método de merge, testes próprios, diferenças entre
versão aprovada e integrada, Git/local pendente e próximo responsável.
