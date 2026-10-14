# Estado do ConvIQ — leia primeiro

Atualizado em 14/10/2026 (Codex, F05-B-07). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api`, em `3a5de83` (PR #13,
  reconfirmado por `git ls-remote` em 14/10).
  `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`), EST01 (PR #3, `4063830`), B14 (PR #4,
  `b688afb`), F01 (PR #5, `5a2fede`), F02-A (PR #6, `9706315`), F02-B (PR #7, `bf7a1a1`), B19 (PR #8, `0a29627`), F03-A (PR #9, `b50ce86`), F03-B (PR #10, `f859e69`) F04-A (PR #11, `cd6745c`) e F04-B (PR #12, `c66eba9`) e F05-A (PR #13, `3a5de83`).
- **B13 (oportunidade por intenção):** aprovado em B13-04 e integrado no
  [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2); B13-10 verificou
  sete hashes, 271 testes e casos críticos na árvore integrada.
- **Frontend:** F01 a F05-A integrados. F05-B FINALIZADA e APROVADA_TECNICAMENTE em F05-B-06; entrega COMMITADA em `f90ddc5` sobre `3a5de83`, com 311 testes aprovados. Evento F05-B-07 ainda local; push, PR e integração pendentes. A interface ainda não envia à API.
- **Papéis desde 13/10:** Codex indisponível (sem tokens). Por decisão do usuário, Claude Opus executa e registra, outra sessão Claude revisa de forma independente pelo `prompt.md` da raiz (espelhado no worktree), e o usuário decide commit, push, PR e merge. Ninguém aprova a própria entrega. Em 14/10 o Codex voltou a verificar o F05-B (RET02, registrado no `REGISTRO_TRABALHO.md` da raiz).
- **Áudio:** B07-A parcial (falta fala real, P01). Nada além disso.
- **EST01:** integrada no [PR #3](https://github.com/GustavoECocchi/ConvIQ/pull/3);
  validação EST01-05 confirmou árvore e 273 testes. Seção 11 vigente.
- **B14 (Unicode NFD):** INTEGRADA pelo PR #4 em `b688afb` e verificada
  em B14-07 (330 testes na árvore integrada). Registros B14-05–07 foram
  integrados junto do F01 pelo PR #5.
- **B19:** INTEGRADO no destino pelo PR #8 (`0a29627`); preservado na árvore de F03-A.

## Próximo passo
1. Registrar o commit F05-B-07, publicar `feat/f05b-ver-evidencia`, abrir PR para `feat/b01-fundacao-api`, integrar e conferir a árvore, conforme autorização de 13/10 registrada em F05-A-03.
2. F06-A (envio real à API, nível A; tratar O2 de F05-B: zerar a seleção ao trocar de resposta) e F06-B (jornada completa; inclui O2 de F04-B, foco ao voltar em página rolada) a partir da versão integrada.

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
