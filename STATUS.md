# Estado do ConvIQ — leia primeiro

Atualizado em 12/10/2026 (Codex, GIT01-02). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em docs/registro/).

## Onde estamos
- **Branch padrão e destino:** feat/b01-fundacao-api em 0a29627 (servidor, 09/10). origin/main é um resíduo (8d48e75), não use como destino.
- **Integrado:** B01–B04/C01, B11/B12 (PR #1), B13 (PR #2), EST01 (PR #3), B14 (PR #4), F01 (PR #5), F02-A (PR #6), F02-B (PR #7) e B19 (PR #8, 0a29627).
- **Frontend:** cliente HTTP F02-B integrado; F03-A está COMMITADA em caface2 e PUBLICADA em feat/f03a-rotas-navegacao (head documental 6f05046), base 9706315, EM_REVISAO após correção R01/R02 pelo Codex e sem parecer independente do Opus. F03-B tem proposta publicada naquela branch, sem código.
- **B19:** APROVADO tecnicamente em B19-04, reaplicado sem mudança técnica sobre bf7a1a1, COMMITADO em 7306b0e, PUBLICADO e INTEGRADO pelo PR #8 em 0a29627; árvore e testes verificados em B19-08. Registros pós-merge publicados nesta branch documental; origem CONVIQ-b19 preservada e publicada em f3b5701.
- **Áudio:** B07-A parcial (falta fala real, P01).

## Próximo passo
1. Opus revisa F03-A no worktree CONVIQ-f03a, candidato técnico caface2 já publicado, seguindo o prompt vigente ali; Codex verifica e reconcilia com a ponta integrada antes de abrir PR.
2. F03-B implementa após F03-A; B15 é o próximo refinamento de backend independente.

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
