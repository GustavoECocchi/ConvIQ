# Instruções do ConvIQ para agentes

Leia, nesta ordem: `STATUS.md` (estado e próximo passo), a linha do PR na
tabela de `REGISTRO_TRABALHO.md`, `docs/registro/<ID>.md` do PR em que vai
atuar e a seção pertinente de `PLANO_DESENVOLVIMENTO.md`. Consulte
`SISTEMA_GOVERNANCIA_CONVIQ.md` só no que precisar. A seção 11 complementa
as anteriores após o aceite e a integração de EST01; antes disso é proposta.
Confira o Git e a ficha da tarefa; registros
de outra branch ou versão não comprovam o estado atual.

## Registro obrigatório — Codex e Claude

- Cada agente registra sua própria atuação antes de passar o trabalho ou
  encerrar a resposta, com **um evento curto** (até ~25 linhas, formato em
  `docs/registro/README.md`) no fim de `docs/registro/<ID>.md`. O evento é o
  relatório: não crie arquivo de relatório separado e não o repita no chat
  (até 10 linhas, apontando para o evento).
- Atualize só o que mudou: os campos de estado da linha do índice, a ficha
  (se o estado do ciclo mudou), a **única** fotografia Git vigente
  (substitua, não acumule) e o `STATUS.md`. Preserve eventos anteriores.
- Para cada PR, informe separadamente: entrega finalizada ou pendente, estado
  da revisão, commit, push, PR remoto e integração. Commit em uma branch de
  trabalho não significa integração.
- Se a entrega estiver commitada, identifique-a pelo hash e por
  `git diff base..commit`. Se estiver local, informe HEAD, `git status`,
  diff local e arquivos não rastreados; use hashes de arquivos quando
  necessários para fixar uma versão. Diferencie conferido de apenas relatado
  e use `NAO_VERIFICADO` quando não houver evidência.
- Confirme os nomes reais da branch de trabalho, da base e do destino. Não
  presuma `main` ou `master`: o destino atual é `feat/b01-fundacao-api`.
- Ao retomar, compare ficha, branch, commits e alterações locais. Se houver
  divergência, registre-a antes de continuar. Não troque de branch de um
  checkout sujo; use worktree isolado e preserve o que já existe.
- Se o registro não puder ser editado, informe a limitação e entregue o
  texto do evento para incorporação; não diga que ele foi salvo.
- `prompt.md` é o arquivo de rascunho oficial para prompts. Sempre que o
  usuário pedir para gerar ou preparar um prompt, escreva o prompt completo
  nesse arquivo, substituindo o anterior, e registre a substituição em um
  evento. Prompts citam caminhos, commit e eventos; não colam listas de
  hashes nem eventos anteriores.

## Git

- Com autorização do usuário para a entrega, executor e revisor podem commitar
  e dar push na branch de trabalho depois dos testes passarem, com o registro
  no mesmo commit. Dependem de ordem do usuário: abrir ou fechar PR, merge,
  escrever na branch padrão, reescrever histórico, reset, stash e apagar
  branches.
- Scripts avulsos e testes podem importar o código errado: o venv tem
  instalação editável apontando para outra pasta. Use
  `python backend/scripts/sondar.py "frase"` ou `PYTHONPATH=<checkout>/backend`
  e rode `pytest` dentro de `backend/` do checkout.

Codex coordena e verifica; Claude implementa e revisa conforme o papel atribuído.
Uma atribuição diferente do usuário prevalece. Registrar trabalho não concede
autorização para commit, push, PR, merge ou escrita na branch padrão; valem as
autorizações da sessão e a seção Git acima.

## Referência geral

Se existir `docs/governanca/REGRAS.md`, leia essa versão adotada e os registros
pertinentes. Caso contrário, consulte
`/home/gustavoecocchi/Documents/GOVERNANCA/REGRAS.md`. Se estiver indisponível,
informe brevemente e siga as instruções e documentos disponíveis. Não atualize
automaticamente uma versão adotada. Instruções superiores, pedidos do usuário
e convenções específicas do projeto prevalecem sobre a referência geral.
