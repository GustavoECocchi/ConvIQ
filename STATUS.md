# Estado do ConvIQ — leia primeiro

Atualizado em 15/10/2026 (Codex, F06-B-03). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api`, em `4950292` (PR #15,
  confirmado no GitHub em 15/10).
  `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`), EST01 (PR #3, `4063830`), B14 (PR #4,
  `b688afb`), F01 (PR #5, `5a2fede`), F02-A (PR #6, `9706315`), F02-B (PR #7, `bf7a1a1`), B19 (PR #8, `0a29627`), F03-A (PR #9, `b50ce86`), F03-B (PR #10, `f859e69`), F04-A (PR #11, `cd6745c`), F04-B (PR #12, `c66eba9`), F05-A (PR #13, `3a5de83`), F05-B (PR #14, `7821eee`) e F06-A (PR #15, `4950292`).
- **B13 (oportunidade por intenção):** aprovado em B13-04 e integrado no
  [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2); B13-10 verificou
  sete hashes, 271 testes e casos críticos na árvore integrada.
- **Frontend:** F01 a F06-A integrados. F06-A FINALIZADA/APROVADA_TECNICAMENTE, entrega `1bc9675` e registro `e4fc053` publicados; [PR #15](https://github.com/GustavoECocchi/ConvIQ/pull/15) MERGEADO em `4950292` e conferido em F06-A-07. F06-B está FINALIZADA/APROVADA_TECNICAMENTE em F06-B-03, ainda local e sem commit: Nova análise coerente, aviso de ausência sem quadro intermediário, campos somente leitura, foco ao voltar e E2E com API real. Codex reexecutou 350 testes duas vezes, typecheck, lint, build e 20/20 E2E a 320/1440 px. Observação não impeditiva O1 em F06-B-03; testes de leitor de tela/Firefox/Safari/aparelho real/CI não executados.
- **Papéis:** Claude Sonnet executou F06-B; Codex concedeu aceite técnico no nível B. Publicação e integração ainda dependem das autorizações aplicáveis.
- **Áudio:** B07-A parcial (falta fala real, P01). Nada além disso.
- **EST01:** integrada no [PR #3](https://github.com/GustavoECocchi/ConvIQ/pull/3);
  validação EST01-05 confirmou árvore e 273 testes. Seção 11 vigente.
- **B14 (Unicode NFD):** INTEGRADA pelo PR #4 em `b688afb` e verificada
  em B14-07 (330 testes na árvore integrada). Registros B14-05–07 foram
  integrados junto do F01 pelo PR #5.
- **B19:** INTEGRADO no destino pelo PR #8 (`0a29627`); preservado na árvore de F03-A.

## Próximo passo
1. Com autorização para a entrega, commitar e publicar F06-B na branch `feat/f06b-jornada-texto` com o registro, conferindo que o commit corresponde à versão aprovada. Abrir PR depende de ordem do usuário.
2. Após PR e integração autorizados, conferir a árvore no destino antes de iniciar outro cartão. Não iniciar F07 automaticamente.

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
