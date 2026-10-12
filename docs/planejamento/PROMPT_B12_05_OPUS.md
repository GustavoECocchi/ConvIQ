# B12 — Correção após verificação do Codex — Claude Opus

Revise e corrija os dois problemas impeditivos abaixo na entrega B12-04.
Faça revisão própria, preserve os comportamentos já corrigidos e devolva a
versão final ao Codex. Esta é a rodada B12-05; B12 ainda está EM_CORRECAO.

## Entrada e leitura

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` (seções
4.4–6 e 8), o índice, a ficha B12 e os eventos B12-04/B12-05 em
`REGISTRO_TRABALHO.md`, o cartão B12 em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md`, os critérios da seção
B11–B21 de `PLANO_DESENVOLVIMENTO.md`, `backend/README.md` e
`docs/contratos/analise-texto.md`. O prompt B12-03 foi executado pelo Opus;
seus achados R02/R03/R04 e os resultados constam da ficha B12-04.

- Raiz: `/home/gustavoecocchi/Documents/CONVIQ`.
- Branch: `fix/b12-contexto-risco`.
- HEAD: `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`, pai `cc61925`.
  As correções B12-04 estão em **diff local não commitado** sobre esse HEAD.
- Entrada de B12-05: os seis arquivos B12-04 abaixo, com SHA-256 conferidos
  pelo Opus em B12-04 e reconferidos pelo Codex em 07/10:

```text
169a6d8a0c55bad0c88c2fe99d3488857abb969ef547f60cf632643125a81dce  backend/app/services/sinais_comerciais.py
7a1053d9020925c7a7f2dfb4b498601af07357ab0e89d4b8ed49700093fd6af1  backend/tests/test_sinais_comerciais.py
0723b4a6a351546db9fdea5b20be13283616120bfae1aed6a090c370c73d50e3  backend/tests/test_analise.py
bbfaebc96f30e25fccc2b7111710dafdff67e6c993bbdb75dc823739265e598e  backend/tests/test_analises_rota.py
649d2d95f22bbf2539e784cf2745496ab3d6ac66cc6ff0ecd18191c1e349daa0  backend/README.md
7ea3213b199a66e6fa2ed029f36811527431dba7f025545cdf58d7c990c04306  docs/contratos/analise-texto.md
```

O registro e o prompt estão modificados; o relatório Sonnet de 06/10 está
não rastreado. Preserve essas preexistências e confira o Git antes de editar.
`negacao.py` e `sentimento.py` pertencem a B11/B12-01 e não mudaram em
B12-04. B11 tem aceite técnico em `d5fb40a`; revalide suas regressões se
alterar a lógica compartilhada. B07-A-06 está no mesmo commit e fora do
escopo. Destino/principal/PR remoto atuais: `NAO_VERIFICADO`; a referência
remota **local** `origin/fix/b12-contexto-risco` aponta para `d5fb40a`.

## Achados impeditivos verificados pelo Codex em 07/10

### B12-R04 — Insatisfação fora da relação comercial gera churn

O cartão B12 pede insatisfação atual **com a relação comercial**. Na
composição real, `Estamos insatisfeitos com o clima.` e `Não estamos
satisfeitos com o almoço.` ainda retornam `sinal_detectado` e uma
recomendação de retenção cada. O primeiro caminho veio de B03; o segundo
foi introduzido em B12. A evidência ampliada de B12-04 mostra o complemento,
mas a classificação incorreta permanece. O Codex considera R04 impeditivo
para o aceite de B12, conforme seção 6 da governança.

Corrija os casos inequivocamente alheios à relação, tanto para
`insatisfeito`/`frustrado` quanto para satisfação negada. Em texto isolado
sem outro contexto comercial, o churn deve ser `informacao_insuficiente`,
sem evidência de churn nem recomendação de retenção. Quando houver contexto
comercial independente, mas a insatisfação for sobre tema alheio, espere
`sem_sinal_detectado`, salvo outro sinal real de risco. Preserve risco para
`insatisfeitos com o suporte`, `frustrados com o atendimento`, `não estamos
satisfeitos com o serviço` e o comportamento existente de `frustrados com
o atraso`; preserve sentimento negativo e oportunidades pertinentes.

Escolha uma regra local explícita e pequena, com contraprovas além das duas
frases do achado. Documente o vocabulário, os falsos positivos/negativos
remanescentes e a relação com a regra antiga de B03. Não prometa interpretar
qualquer assunto em português nem altere C01.

### B12-R06 — Oração coordenada confunde sujeito com objeto cancelado

Após B12-04, `_fim_do_objeto_da_acao` em
`backend/app/services/sinais_comerciais.py` trata o substantivo após `e`
como segundo objeto, mesmo quando ele é sujeito de outra oração. Reproduzido
na composição real:

- `Vamos cancelar a reunião e o contrato continua vigente.` →
  `sinal_detectado`, evidência `cancelar a reunião e o contrato` e uma
  recomendação de retenção; esperado `sem_sinal_detectado`, sem evidência de
  churn nem recomendação de retenção.
- `Vamos cancelar a reunião e o fornecedor será avisado.` → mesmo erro;
  esperado `sem_sinal_detectado`.

Preserve a contraprova `Vamos cancelar a reunião e o contrato.` → risco,
porque o contrato também é objeto da ação. Preserve os casos R02 corrigidos,
inclusive `cancelar a reunião sobre o contrato`, `reavaliar a pauta com o
fornecedor`, `cancelar o contrato` e a ameaça condicional. A regra pode
continuar local e limitada; explique seus limites com exemplos. Verifique
o resultado no serviço, na composição e na rota, incluindo recortes literais,
IDs e recomendações.

## Critérios que permanecem

- R02/R03 devem continuar corrigidos: ligação ação–objeto pertinente,
  evidência literal com contexto, condição e índices corretos.
- Preserve prospect `nao_aplicavel`, vínculo desconhecido, concorrente
  isolado sem risco presumido, coexistência de risco e oportunidade,
  `metodo="regras"`, `versao_analise="0.3"` e o contrato C01.
- Não inicie B13, B14, B19, áudio ou persistência. Avalie a premissa de B19
  como nota à coordenação, sem implementar B19 nesta rodada.

Na verificação do Codex, os 131 testes de sentimento/sinais/composição
passaram no sandbox. A suíte completa travou no primeiro teste HTTP dentro
do sandbox (código 137 sob limite), mas passou fora dele: **177 passed em
0,43 s**, com dois avisos de depreciação. Os três exemplos dos achados foram
reproduzidos na composição. Rode os testes afetados e a suíte completa com
limite de tempo; se o `TestClient` travar no sandbox, registre a restrição e
execute fora dele quando autorizado. Não trate teste existente que fixa R04
como critério de aceite para manter o falso positivo.

## Git, registro e entrega

Escopo autorizado: revisão, correção, testes e documentação **locais** nesta
branch. Não fazer commit, push, PR remoto, merge, reset/stash nem reescrever
branches/commits. Preserve `prompt.md` como instrução da coordenação.

Atualize a linha do índice, a ficha B12 e acrescente o evento B12-06 em
`REGISTRO_TRABALHO.md`, preservando os eventos anteriores. Responda R04 e
R06 com classificação, evidência da correção e limites; relate qualquer
achado novo. Entregue o relatório da seção 8 da governança: arquivos,
critérios, comandos/resultados, versão/hashes, estado da revisão, Git da
entrega e do registro, publicação, PR remoto, integração e próximo
responsável. O Codex fará a verificação final; não marque B12 como APROVADO
ou INTEGRADO por conta própria.
