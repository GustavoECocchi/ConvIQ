# B12 — Revisão do risco de cancelamento com contexto local — Claude Opus

Revise e corrija a entrega **B12**, preparada e implementada pelo Sonnet em
B12-01. Use o cartão B12 e as regras comuns do roteiro como especificação.
Faça revisão própria do código e dos testes, confirme os apontamentos abaixo
e corrija falhas comprovadas no escopo. Devolva ao Codex para verificação final.

## Leitura, versão e preexistências

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` (4.4–4.5,
5, 6 e 8), índice/ficha B12 e eventos B12-01/B12-02 em
`REGISTRO_TRABALHO.md`, a ficha/evento B11-03 (dependência), a seção B11–B21
de `PLANO_DESENVOLVIMENTO.md`, as regras comuns, o cartão B12 e a validação
de `docs/planejamento/PRS_REFINAMENTO_ANALISE.md`, README e C01 em
`docs/contratos/analise-texto.md`. Não há prompt original separado de execução
B12: o Sonnet relata autorização do usuário para preparar e executar pelo cartão.

- Pasta: `/home/gustavoecocchi/Documents/CONVIQ`.
- Branch: `fix/b12-contexto-risco`.
- HEAD: `cc61925f48d0981517a11480691c6f3f5465dcc0`; pai `6169fec`.
- Versão entregue: **diff local NAO_COMMITADO**, incluindo
  `backend/app/services/negacao.py` **não rastreado**.
- B12 depende do B11 local revisado em B11-03, ainda sem verificação final do
  Codex. A revisão B12 não concede automaticamente o aceite de B11.
- As branches B11/B12/B07-A apontam ao mesmo HEAD. B11 e B12 ainda não existem
  nesses commits: comparar apenas branches não mostra a entrega nem isola B12.
  O diff contra `cc61925` contém trabalho acumulado; confira o relato de
  B12-01, os arquivos atuais e as fronteiras de cada tarefa.
- Principal, destino, PR remoto e integração atuais: `NAO_VERIFICADO`;
  servidor não consultado nesta preparação.

Na conferência havia 14 arquivos rastreados modificados, um não rastreado e
índice vazio. Os nove arquivos de B12 têm estes SHA-256 de entrada:

```text
2457adc0d55dcce79416e48fbf97bf257dfce74d62a8d7bb16f55cb1b2537e27  backend/app/services/negacao.py
f4d4fafbfdba1b8a08511e84ec7d8b7b3e26049015c095419141bc76d259dd21  backend/app/services/sentimento.py
b86fa464a123a48542beb0363bc619e2842a15b889ada0f8f348733abf923328  backend/app/services/sinais_comerciais.py
aa1de4d1135d752ede69ec17eb890bc127bc804760569abcfcfd0f9df301ffe4  backend/app/services/analise.py
8affdfb4fe257b0a072dc034c02142063b2b3cbe42d03042735deb409a6418d5  backend/tests/test_sinais_comerciais.py
de585b1e5af7dd0b8b47f5b82785ed0ba9c80b9db8861f9f3b5f9a8eed2ae749  backend/tests/test_analise.py
fc2d9da0aff65870813a130407aacea85b0fdf2a0f1ee3cc87a749cbb1b11aee  backend/tests/test_analises_rota.py
0e7cd2ecc80fc0a40ae728b2e4b83e85b1544082b202f1eb050add2b4e354629  backend/README.md
9a3d559479ed36f273f5ba2058884cd293119d5cdd3fd9c1296ae11507f13dde  docs/contratos/analise-texto.md
```

Preserve B11, inclusive suas regressões em `backend/tests/test_sentimento.py`.
`sentimento.py`, composição/testes, README e C01 acumulam B11/B12: não restaure
esses arquivos a uma versão anterior. As mudanças de `.gitignore`,
`backend/scripts/verificar_whisper.py` e
`docs/decisoes/transcricao-whisper.md` são de B07-A-06 e ficam fora da revisão.
`REGISTRO_TRABALHO.md` é compartilhado; `prompt.md` é coordenação.

Confira raiz, branch, HEAD, status, índice, arquivos não rastreados e hashes
antes de editar. Registre eventual divergência sem descartar mudanças. Escopo
autorizado: revisão, correção, validação e documentação locais nesta branch.
Não fazer commit, push, PR remoto, merge, reset/stash ou reorganização das
branches/commits. A coordenação tratará a separação das entregas depois.

## Critérios originais e resultado esperado

Regras locais devem distinguir cancelamento/reavaliação/rescisão da relação
comercial de ações sobre reunião/pauta; respeitar a negação e a insatisfação
atual com essa relação. Para `cliente`, confirme:

| Entrada | Churn esperado |
|---|---|
| Não vamos cancelar o contrato. | sem_sinal_detectado |
| Vamos cancelar a reunião. | informacao_insuficiente |
| Vamos cancelar o contrato. | sinal_detectado |
| Se o suporte continuar assim, vamos cancelar o contrato. | sinal_detectado |
| Vamos reavaliar a pauta. | informacao_insuficiente |
| O sistema solar é extenso. | informacao_insuficiente |
| Não estamos satisfeitos com o suporte. | sinal_detectado |

Cada sinal precisa de evidência literal com o contexto relevante e posições
corretas no texto devolvido. Negar cancelamento não comprova baixo risco.
Preserve prospect `nao_aplicavel`, concorrente isolado sem risco presumido,
vínculo desconhecido sem pressupor baixo risco e coexistência de risco com
oportunidade. IDs de churn/oportunidades/recomendações devem continuar válidos.

Reusar a negação de B11 sem regredir sentimento, “não só”, “nem”, acentos,
pontuação, repetições ou recortes. Preservar C01, `metodo="regras"` e versão
`0.3` da entrega B12, com documentação coerente.

Fora do escopo: oportunidades B13, Unicode/NFD B14, deduplicação B19,
ampliação geral de catálogo/vocabulário, probabilidades, classificador novo,
ironia/negação dupla geral, autoria de falas, história remota, áudio,
persistência e hospedagem. Mudanças necessárias ao contexto/evidência de churn
são B12; não substituir o motor por análise gramatical geral.

## Achados do Codex a confirmar

B12-01 já usa **B12-R01** para o problema original do cartão. Preserve essa
referência; os apontamentos desta preparação recebem os IDs seguintes.

### B12-R02 — Palavra comercial próxima é tratada como objeto da ação

Reproduzido na composição real: todos os exemplos abaixo geram
`sinal_detectado`, evidência apenas da ação e uma recomendação de retenção:

- “Vamos cancelar a reunião sobre o contrato.”
- “Vamos reavaliar a pauta com o fornecedor.”
- “O contrato continua vigente, vamos cancelar a reunião.”
- “Vamos cancelar a reunião, mas não o contrato.”

Esperado: nenhuma dessas frases deve gerar sinal de encerramento da relação
comercial; com contexto comercial avaliável, `sem_sinal_detectado`.
O objeto cancelado é a reunião; no segundo caso, reavalia-se a pauta.

Localização: `_ocorrencias_risco`/`_mesma_oracao` em
`backend/app/services/sinais_comerciais.py`: qualquer objeto comercial antes
ou depois da ação na mesma frase basta, inclusive em outra oração. A negação
sobre “o contrato” no quarto caso também é ignorada por essa associação.

Confirme e corrija a ligação local ação–objeto, com regressões e contraprovas.
Preserve “cancelar o contrato”, “reavaliar o fornecedor”, “rescindir o contrato”
e a ameaça condicional original. Não resolva só cortando em toda vírgula nem
exigindo que ação/objeto sejam sempre palavras adjacentes.

### B12-R03 — Evidência omite o contexto que sustenta a classificação

Reproduzido: “Vamos cancelar o contrato.” retorna evidência `cancelar`;
“Se o suporte continuar assim, vamos cancelar o contrato.” também retorna
somente `cancelar`. “Não estamos satisfeitos com o suporte.” retorna
`Não estamos satisfeitos`, sem a relação mencionada.

O cartão exige evidência do contexto relevante. Uma ação solta não explica
por que se trata de churn em vez de cancelamento de reunião. Os testes atuais
de serviço/composição chegam a fixar `trecho == "cancelar"`, e README/docstring
justificam isso pelo comportamento anterior — revise essa expectativa à luz
do critério B12, preservando o histórico da mudança.

A evidência deve incluir a expressão e o objeto/contexto usados para decidir
o risco; quando necessário, a negação ou condição. Mantenha recortes literais,
índices exatos, ocorrências repetidas e referências válidas, sem paráfrase nem
novos campos públicos. Atualize testes/documentação de forma justificada.

### B12-R04 — Insatisfação fora da relação comercial: ponto adicional

O Codex também reproduziu `sinal_detectado` e recomendação de retenção em
“Estamos insatisfeitos com o clima.” e “Não estamos satisfeitos com o almoço.”.
A primeira regra é herdada; a segunda usa o caminho novo de satisfação negada.

Avalie contra o objetivo de “insatisfação atual com essa relação” no cartão.
Não confunda sentimento negativo geral com risco comercial. Corrija casos
inequivocamente fora da relação quando abrangidos por B12, preservando
insatisfação com suporte/serviço, e justifique o que considerar limitação
remanescente. Distinguir herança de B03, comportamento novo e mudança de
escopo; não invalidar silenciosamente o aceite histórico de B03.

## Validação já feita e revisão independente

Conferência do Codex em `backend/`:

- `timeout --signal=INT --kill-after=5s 30s .venv/bin/python -m pytest -q tests/test_sentimento.py tests/test_sinais_comerciais.py tests/test_analise.py`
  → **99 passed in 0.06s**.
- Sondagem dos sete exemplos explícitos do cartão → **7/7**, com recortes
  literais conferidos; dez sondagens adicionais na composição reproduziram os
  resultados descritos acima e um controle com frases separadas por ponto.
- Diff vazio em schemas, API, `texto.py` e `pyproject.toml`;
  `git diff --check` sem diagnóstico. Hashes atuais correspondem aos prefixos
  registrados em B12-01; `negacao.py` foi lido diretamente.
- Suíte completa, `timeout --signal=INT --kill-after=5s 45s .venv/bin/python -m pytest -q`,
  ficou sem progresso após onze pontos e terminou com **137** sob o limite
  configurado. Causa do travamento não diagnosticada; nenhum resultado final
  de testes. Os **143 passed** e o servidor real de B12-01 continuam sendo
  relato do Sonnet, não reprodução do Codex.

Revise o conjunto B12, não apenas os achados. Confira a extração do módulo
compartilhado e execute as regressões B11. Teste classificação, evidência e
referências na composição/rota, com casos positivos, negados, não comerciais,
condicionais e repetidos. Confirme que oportunidades e catálogos não mudaram.

Depois das correções, rode testes afetados e suíte completa com limite de
tempo. Registre restrições e testes não executados; não altere código para
acomodar um travamento de ferramenta sem diagnosticar a causa. Não alegue
resultado de suíte/HTTP a partir de sondagem direta do serviço.

## Registro e entrega

Atualize índice/ficha B12 e acrescente evento próprio em
`REGISTRO_TRABALHO.md`, preservando B12-01/B12-02 e o histórico B11/B07-A.
Responda a R02/R03/R04 como confirmado e corrigido, não confirmado ou pendente,
com evidência e impacto no aceite. Inclua outros achados que comprovar.

Entregue o relatório da seção 8 da governança: arquivos, critérios,
comandos/resultados, limites, versão/hashes, entrega finalizada/parcial,
revisão, Git não commitado (inclusive `negacao.py` e registro), branch/base,
push, PR e integração. Não marque APROVADO/INTEGRADO nem inicie B13.
Próximo responsável: Codex verifica a devolução do Opus.
