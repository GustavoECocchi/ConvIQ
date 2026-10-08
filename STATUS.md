# Estado do ConvIQ — leia primeiro

Atualizado em 08/10/2026 (Codex, B14-04). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api` em `4063830` (servidor,
  08/10). `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`) e EST01 (PR #3, `4063830`).
- **B13 (oportunidade por intenção):** aprovado em B13-04 e integrado no
  [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2); B13-10 verificou
  sete hashes, 271 testes e casos críticos na árvore integrada.
- **Frontend (F01–F06):** responsável é outra pessoa; não há código na cópia.
- **Áudio:** B07-A parcial (falta fala real, P01). Nada além disso.
- **EST01:** integrada no [PR #3](https://github.com/GustavoECocchi/ConvIQ/pull/3);
  validação EST01-05 confirmou árvore e 273 testes. Seção 11 vigente.
- **B14 (Unicode NFD):** entregue por B14-01 como diff local no worktree
  `CONVIQ-b14` (`fix/b14-unicode-evidencias`, base `4063830`): 330 testes,
  `versao_analise` `0.5`. Codex confirmou 330 testes e sondas em B14-02;
  revisão do Opus concluída sem achados em B14-03; **APROVADA tecnicamente**
  pelo Codex em B14-04. NAO_COMMITADA, NAO_PUBLICADA, sem PR, NAO_INTEGRADA.

## Próximo passo
1. Após autorização do usuário, commitar/publicar a versão aprovada de B14
   na branch de trabalho e abrir PR para `feat/b01-fundacao-api`; conferir o
   commit contra os hashes aprovados e validar a integração quando autorizada.
2. Depois da integração: revisar a premissa de B19 sobre evidências aninhadas
   por B12, então liberar B19 → B15 → B16 → B17 → B18 → B20 → B21.

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
