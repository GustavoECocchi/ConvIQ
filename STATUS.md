# Estado do ConvIQ — leia primeiro

Atualizado em 12/10/2026 (Codex, B19-05). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api` em `0a29627` (servidor,
  12/10). `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`), EST01 (PR #3, `4063830`), B14 (PR #4), F01 (PR #5), F02-A (PR #6), F02-B (PR #7) e B19 (PR #8, `0a29627`).
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
  pelo Codex em B14-04. COMMITADA/PUBLICADA em `13b1519`; PR [#4](https://github.com/GustavoECocchi/ConvIQ/pull/4)
  MERGEADO em `b688afb`, árvore idêntica, **330 testes na integração**.
  B14 INTEGRADA; registros B14-05–07 carregados localmente no worktree B19.
- **B19 (evidência exata):** origem revisada em `CONVIQ-b19` (`fix/b19-unificar-evidencias`, base `b688afb`) COMMITADA em `aa3b5ba` e PUBLICADA. Revisões B19-02/03 e aceite B19-04 confirmaram 344 testes; o mesmo diff técnico foi reaplicado e INTEGRADO pelo PR #8 em `0a29627`. Esta branch de origem não teve PR próprio.

## Próximo passo
1. F03-A está publicado em branch própria, mas aguarda revisão independente do Opus e reconciliação com a ponta integrada antes de PR/merge.
2. Frente planejada de backend: B15 → B16 → B17 → B18 → B20 → B21.

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
