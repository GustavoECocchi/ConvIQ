# Estado do ConvIQ — leia primeiro

Atualizado em 09/10/2026 (Codex, B19-05). Quem muda o estado de um PR atualiza este
arquivo; ele não guarda histórico (isso fica em docs/registro/).

## Onde estamos
- **Branch padrão e destino:** feat/b01-fundacao-api em bf7a1a1 (servidor, 09/10). origin/main é um resíduo (8d48e75), não use como destino.
- **Integrado:** B01–B04/C01, B11/B12 (PR #1), B13 (PR #2), EST01 (PR #3), B14 (PR #4), F01 (PR #5), F02-A (PR #6) e F02-B (PR #7, bf7a1a1).
- **Frontend:** cliente HTTP F02-B integrado; F03-A é diff local em CONVIQ-f03a, base 9706315, EM_REVISAO após correção R01/R02 pelo Codex e ainda sem parecer independente do Opus. F03-B tem proposta de tela naquele worktree, sem código.
- **B19:** APROVADO tecnicamente em B19-04; mesmo diff técnico reaplicado sobre bf7a1a1 em integrate/b19-evidencias, mais exemplos ilustrativos atualizados para 0.6. Entrega local ainda sem commit, push, PR ou merge. Origem CONVIQ-b19 preservada.
- **Áudio:** B07-A parcial (falta fala real, P01).

## Próximo passo
1. Concluir conferência documental e publicar o PR B19 a partir de integrate/b19-evidencias; merge depende de ordem específica do usuário.
2. Quando Claude voltar, Opus revisa F03-A no worktree CONVIQ-f03a seguindo o prompt vigente ali; Codex verifica e reconcilia com a ponta integrada antes de publicar.
3. F03-B implementa após F03-A; B15 é o próximo refinamento de backend independente.

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
