# Relatório consolidado do Sonnet para o Codex — B01, C01, B02 e B03

Preparado pelo Claude Sonnet em 18/09/2026, a pedido direto do usuário
("manda um prompt no prompt.md para o codex"), fora da regra geral de
DOC01-06 (normalmente é o Codex quem grava prompts aqui). Este texto é o
retorno do executor ao coordenador, no formato da seção 9.3 da governança,
cobrindo de uma vez as quatro entregas pendentes de verificação.

---

Você é o **Codex, coordenador do ConvIQ**. O Sonnet entregou B01, C01 e B02
— já revisados e corrigidos pelo Opus — e B03, ainda sem revisão. Analise
as quatro conforme `SISTEMA_GOVERNANCIA_CONVIQ.md` e os critérios do plano.

## Leitura recomendada, antes de analisar

- `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` — seções 4.3,
  4.5, 5, 6 e 8.
- `REGISTRO_TRABALHO.md`: índice; fichas B01, C01, B02 e B03 completas;
  eventos B01-01 a B01-06, C01-01 a C01-03, B02-01 a B02-03 e B03-01.
- `PLANO_DESENVOLVIMENTO.md`: linhas de B01, C01, B02 e B03 na tabela de PRs.
- `docs/contratos/analise-texto.md` (contrato consolidado em C01).
- Código: `backend/app/**`, `backend/tests/**`, `backend/README.md`.

Se `docs/governanca/REGRAS.md` ou a referência geral em
`/home/gustavoecocchi/Documents/GOVERNANCA/` continuarem indisponíveis,
registre a limitação e prossiga pelas instruções locais, como nas rodadas
anteriores.

## Referência da entrega (igual para as quatro)

- **Pasta:** `/home/gustavoecocchi/Documents/CONVIQ`.
- **Branch:** `feat/b01-fundacao-api`.
- **Base local / HEAD observado:** `master` /
  `3c52ea3ed0d3c3d38de5b9adf2a4a4ff320a1842`. O HEAD não contém nenhuma das
  quatro entregas — todas estão na pasta de trabalho, sem commit.
- **Destino de integração / principal remota:** `NAO_VERIFICADO` nesta
  sessão (ver DOC01-04 sobre a referência local `origin/main`, provavelmente
  desatualizada). Não presuma `origin/main` como prova da principal atual.
- **Git da entrega:** `NAO_COMMITADO` para as quatro; índice vazio; nenhum
  push, PR remoto ou integração. Confira `git status --short --branch
  --untracked-files=all`, `git diff`, `git diff --cached` e `git rev-parse
  HEAD master` antes de analisar — o estado pode ter mudado desde este texto.

## B01 — Fundação da API

- **Estado no índice:** `EM_REVISAO`; revisão do Opus concluída (evento
  B01-06), aguardando verificação final do Codex.
- **Pedido:** confirme se os critérios de aceite de B01 (fundação FastAPI,
  configuração por ambiente, saúde, schemas iniciais, inicialização
  reproduzível) estão realmente atendidos na versão revisada pelo Opus, com
  suas próprias verificações — não só a leitura do relatório. Se concordar,
  registre o aceite técnico da versão examinada (seção 4.5); se houver
  pendência impeditiva, prepare uma rodada de correção objetiva.

## C01 — Contrato de análise por texto

- **Estado no índice:** `EM_REVISAO`; revisão do Opus concluída (C01-R01 a
  C01-R03 corrigidos, evento C01-03), aguardando verificação final.
- **Pedido:** confira se `docs/contratos/analise-texto.md` e os schemas em
  `backend/app/schemas/` continuam coerentes entre si (campos, enums,
  limites, convenção de posição de evidência, códigos de erro HTTP) e se os
  três achados do Opus foram mesmo corrigidos, com evidência reproduzível.
  Mesma decisão esperada: aceite técnico ou nova rodada de correção.

## B02 — Sentimento e evidências

- **Estado no índice:** `EM_REVISAO`; revisão do Opus concluída (B02-R01
  corrigido, limitações de negação/NFD ampliadas no README, evento B02-03),
  aguardando verificação final.
- **Pedido:** confirme que `app/services/sentimento.py` cobre os três
  cenários do critério (insatisfeito, ausência de evidência, trechos
  repetidos), que a correção de `ruim|ruins` não regrediu nada e que as
  limitações documentadas (negação de frase, entrada NFD) são aceitáveis
  para o escopo de B02, sem virar bloqueio. Mesma decisão esperada.

## B03 — Sinais comerciais

- **Estado no índice:** `ENTREGUE`; **sem revisão do Opus ainda** — esta é a
  única das quatro que precisa da etapa de **análise inicial** (seção 4.3),
  não da verificação final.
- **Pedido:** examine `app/services/sinais_comerciais.py` e
  `tests/test_sinais_comerciais.py` (evento B03-01 tem o relato completo,
  incluindo a reprodução dos dois padrões evitados do experimento de
  referência — concorrente isolado implicando churn, e oportunidade
  suprimida quando há churn). Confirme ou não os achados que encontrar,
  registre o estado em `REGISTRO_TRABALHO.md` e **prepare o prompt de
  revisão para o Opus**, no mesmo formato usado em B01-03/C01-02/B02-02,
  incluindo os critérios originais, o relato do Sonnet e qualquer achado
  seu. Não implemente nem corrija B03 diretamente — essa etapa é do Opus.

## Antes de decidir

Reproduza o que for possível: `cd backend && source .venv/bin/activate &&
pytest -q` (74 testes esperados na versão entregue), e qualquer verificação
pontual que julgar necessária para os achados específicos de cada PR.
Distinga o que você verificou do que está apenas relatado, como pede a
seção 4.3. Não declare `APROVADO` ou `INTEGRADO` para nenhuma das quatro
sem essa verificação própria.

## Ao concluir

Atualize o índice, as quatro fichas e acrescente um evento por PR analisado
em `REGISTRO_TRABALHO.md`, preservando o histórico. Para B01/C01/B02: se
aceitar, registre o aceite técnico da versão examinada e o próximo passo
(B04, ou outra pendência). Para B03: registre o prompt preparado para o
Opus, sem antecipar o resultado da revisão dele. Nenhuma integração deve
ocorrer sem autorização explícita do usuário.
