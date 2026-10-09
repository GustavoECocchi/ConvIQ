# Estado do ConvIQ — leia primeiro

Atualizado em 09/10/2026 (Codex, F02-A-03). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api` em `b688afb` (servidor,
  09/10). `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`), EST01 (PR #3, `4063830`) e B14 (PR #4, `b688afb`).
- **B13 (oportunidade por intenção):** aprovado em B13-04 e integrado no
  [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2); B13-10 verificou
  sete hashes, 271 testes e casos críticos na árvore integrada.
- **Frontend:** usuário atribuiu F01 ao Codex nesta rodada. F01 está
  implementado localmente no worktree `CONVIQ-f01`, branch
  `feat/f01-fundacao-react`, base `b688afb`: dashboard horizontal
  React/TypeScript/Vite, com prévias desktop/celular. Typecheck, lint, build e
  preview passaram; revisão do Opus F01-04 e aceite técnico do Codex F01-05
  concluídos. Código F01 commitado e publicado em d8e06b2; PR #5 ABERTO
  para feat/b01-fundacao-api, ainda não integrado. F02–F06 foram subdivididos
  em PRs pequenos. F02-A entregue por F02-A-01 como diff local no worktree
  CONVIQ-f02a (branch feat/f02a-tipos-c01, base 89e0801): tipos de C01, 4
  exemplos ilustrativos e 22 testes; aprovada tecnicamente em F02-A-02 após
  testes e quatro respostas HTTP idênticas às fixtures. Entrega COMMITADA
  em `68ebde7`, PUBLICADA em `origin/feat/f02a-tipos-c01`;
  [PR #6](https://github.com/GustavoECocchi/ConvIQ/pull/6) ABERTO sobre F01,
  NAO_INTEGRADA.
- **Áudio:** B07-A parcial (falta fala real, P01). Nada além disso.
- **EST01:** integrada no [PR #3](https://github.com/GustavoECocchi/ConvIQ/pull/3);
  validação EST01-05 confirmou árvore e 273 testes. Seção 11 vigente.
- **B14 (Unicode NFD):** INTEGRADA pelo PR #4 em `b688afb` e verificada
  em B14-07 (330 testes na árvore integrada). Registros B14-05–07 foram
  publicados na branch F01 pelo PR #5, ainda não integrados no destino.
- **B19:** aprovado tecnicamente em B19-04 no worktree `CONVIQ-b19`, mas
  continua como diff local naquele worktree; código B19 não integra esta branch.

## Próximo passo
1. O PR #5 de F01 segue OPEN e precisa integrar antes do PR #6 de F02-A;
   ambos os merges dependem de autorização do usuário. F02-B pode partir do
   commit publicado de F02-A; F03-A resolverá as observações de menu do Opus.
2. B19 segue aprovado localmente em worktree separado, aguardando decisão
   de publicação/integração; F01 não depende dessa publicação.

## Decisões abertas
- B12-R04 usa lista fechada de temas alheios; decidir se cresce (PR próprio ou B21).
- `conhecer` + filial/unidade/usuário pode ser visita, não expansão (B13).
- Pergunta do fornecedor ("Vocês querem conhecer o Fluig?") vira oportunidade.
- Modelo pré-treinado além das regras, formatos/limites de áudio, hospedagem (H01), banco.

## Armadilhas (já custaram tempo)
- O venv da pasta raiz tem instalação **editável** apontando para a pasta raiz:
  scripts avulsos importam o código errado. Use `python backend/scripts/sondar.py`
  (resolve o `app` do próprio checkout) ou `PYTHONPATH=<checkout>/backend`, e
  rode `pytest` dentro de `backend/` do checkout.
- `TestClient` pode travar no sandbox (exit 137); reexecute fora dele, não
  declare suíte interrompida como aprovada.
- A pasta raiz está em `fix/b12-contexto-risco` com alterações antigas;
  trabalhe em worktree isolado e preserve-a.
- `docs/governanca/REGRAS.md` e a pasta `GOVERNANCA` não existem: siga a
  governança do projeto.

## Regras em uma linha (detalhes: `SISTEMA_GOVERNANCIA_CONVIQ.md` seção 11)
Leia STATUS → linha do PR → `docs/registro/<ID>.md`. Escreva **um** evento curto
por atuação (é o relatório). A seção 11 está vigente desde EST01-05.
Commit e push na branch de trabalho exigem autorização do usuário e testes
aprovados; PR, merge e escrita na branch padrão exigem ordem do usuário.
