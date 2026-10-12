# Estado do ConvIQ — leia primeiro

Atualizado em 12/10/2026 (Codex, F03-A-04). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em `docs/registro/`).

## Onde estamos
- **Branch padrão e destino:** `feat/b01-fundacao-api` em `0a29627` (servidor,
  12/10). `origin/main` é um resíduo (`8d48e75`), não use como destino.
- **Integrado:** B01–B04, C01 (`6169fec`), B11/B12 (PR #1, `e31e6ba`),
  B13 (PR #2, `2811d84`), EST01 (PR #3, `4063830`), B14 (PR #4,
  `b688afb`), F01 (PR #5, `5a2fede`), F02-A (PR #6, `9706315`), F02-B (PR #7, `bf7a1a1`) e B19 (PR #8, `0a29627`).
- **B13 (oportunidade por intenção):** aprovado em B13-04 e integrado no
  [PR #2](https://github.com/GustavoECocchi/ConvIQ/pull/2); B13-10 verificou
  sete hashes, 271 testes e casos críticos na árvore integrada.
- **Frontend:** F01 (PR #5), F02-A (PR #6) e F02-B (PR #7) integrados. F03-A partiu de 9706315, foi COMMITADA em caface2 e PUBLICADA na própria branch; R01/R02 corrigidos e verificados pelo Codex em F03-A-03. Ciclo EM_REVISAO até parecer independente do Opus; F02-B/B19 ainda não estão neste checkout.
- **Áudio:** B07-A parcial (falta fala real, P01). Nada além disso.
- **EST01:** integrada no [PR #3](https://github.com/GustavoECocchi/ConvIQ/pull/3);
  validação EST01-05 confirmou árvore e 273 testes. Seção 11 vigente.
- **B14 (Unicode NFD):** INTEGRADA pelo PR #4 em `b688afb` e verificada
  em B14-07 (330 testes na árvore integrada). Registros B14-05–07 foram
  integrados junto do F01 pelo PR #5.
- **B19:** INTEGRADO no destino pelo PR #8 (0a29627); a origem local também foi preservada e publicada em branch própria. Código B19 ainda não integra esta branch F03-A.

## Próximo passo
1. Opus revisa independentemente a correção F03-A-R01/R02 no head publicado da branch feat/f03a-rotas-navegacao; Codex verifica o parecer. F03-A ainda não está aprovado nem integrado.
2. A proposta de tela e critérios F03-B está publicada em docs/planejamento/F03-B_FORMULARIO.md; implementação espera F03-A. Depois da revisão, reconciliar F03-A com a ponta 0a29627 antes de abrir PR/mesclar.

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
