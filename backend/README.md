# ConvIQ — Backend (B01 + C01 + B02 + B03 + B04)

API em Python com FastAPI. B01 entregou o projeto executável, configuração
por ambiente e o endpoint de saúde. C01 consolidou o contrato de
`POST /api/analises/texto` — campos, limites, localização de evidências e
erros HTTP — documentado em
[`docs/contratos/analise-texto.md`](../docs/contratos/analise-texto.md). B02
implementou o serviço de sentimento (`app/services/sentimento.py`) e B03 o
de sinais comerciais (`app/services/sinais_comerciais.py`). **B04 liga os
dois**: `POST /api/analises/texto` já responde de verdade, com
recomendações derivadas dos sinais. Áudio, transcrição, persistência e
frontend continuam fora do backend atual.

## Requisitos

- Python 3.11 ou superior (testado com 3.14.7).

## Como rodar localmente

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env  # opcional; os padrões já funcionam localmente

uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Verificar a saúde:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","ambiente":"desenvolvimento"}
```

Analisar uma transcrição:

```bash
curl -X POST http://localhost:8000/api/analises/texto \
  -H "content-type: application/json" \
  -d '{"titulo":"Acompanhamento","empresa":"Empresa Exemplo","vinculo":"cliente","transcricao":"Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."}'
```

Documentação interativa gerada pelo FastAPI: `http://localhost:8000/docs`.

## Como rodar os testes

```bash
cd backend
source .venv/bin/activate  # se ainda não estiver ativo
pytest
```

Os testes não leem variáveis de ambiente nem `backend/.env`: cada teste
monta a aplicação com `criar_app(Settings(...))` e uma configuração
explícita, então o resultado é o mesmo com ou sem `.env` local ou
`AMBIENTE`/`PREFIXO_API` definidos no shell.

## Configuração por ambiente

Lida em `app/config.py` via `pydantic-settings`, a partir de variáveis de
ambiente ou de um arquivo `backend/.env` (não versionado; ver
`.env.example`). O `.env` é procurado no diretório atual, por isso os
comandos acima começam com `cd backend`. Chaves atuais:

| Variável | Padrão | Uso |
|---|---|---|
| `AMBIENTE` | `desenvolvimento` | Rótulo devolvido por `GET /api/health`. |
| `PREFIXO_API` | `/api` | Prefixo aplicado às rotas da API. |
| `ORIGENS_CORS` | `["http://localhost:5173"]` | Lista JSON de origens autorizadas pelo CORS; inclui a porta padrão do Vite. |

## Estrutura

```text
backend/
├── app/
│   ├── main.py          # criar_app(configuracao) monta FastAPI, CORS, erros e rotas; app = criar_app()
│   ├── config.py         # Configuração por ambiente
│   ├── erros.py           # C01: erros de validação -> envelope {"erro": {...}}
│   ├── api/
│   │   ├── health.py     # GET /api/health
│   │   └── analises.py    # B04: POST /api/analises/texto
│   ├── schemas/
│   │   ├── saude.py       # Resposta de GET /api/health
│   │   ├── comum.py       # Enums: Vinculo, Sentimento, ChurnSituacao
│   │   ├── reuniao.py      # Entrada de POST /api/analises/texto (contrato C01)
│   │   ├── analise.py      # Saída de POST /api/analises/texto (contrato C01)
│   │   └── erro.py         # Envelope padronizado de erro
│   └── services/
│       ├── texto.py             # normalizar_com_mapa(texto): texto de busca + mapa para a transcrição (B14)
│       ├── sentimento.py         # B02: analisar_sentimento(transcricao) -> ResultadoSentimento
│       ├── sinais_comerciais.py  # B03: analisar_sinais_comerciais(transcricao, vinculo) -> ResultadoSinaisComerciais
│       └── analise.py            # B04: compor_analise_texto(pedido) -> AnaliseTextoResponse
├── tests/
│   ├── conftest.py       # Fixtures: ambiente limpo e configuração padrão
│   ├── test_config.py    # Padrões, variáveis de ambiente e leitura de .env
│   ├── test_health.py    # Saúde na configuração padrão, alternativa e CORS
│   ├── test_erros.py      # Envelope de erro, via rota descartável só do teste
│   ├── test_schemas.py
│   ├── test_sentimento.py       # B02: insatisfeito, ausência de sinal, trechos repetidos; B11: negação e seus limites
│   ├── test_sinais_comerciais.py # B03: prospect, concorrente isolado, coexistência; B12: risco com objeto/negação
│   ├── test_analise.py           # B04: composição, renumeração de evidências, recomendações
│   └── test_analises_rota.py     # B04: POST /api/analises/texto, entrada válida e inválida
└── pyproject.toml
```

`app/integrations/` e `app/db/` ainda não existem — o plano pede para criar
cada pasta apenas quando a etapa correspondente precisar dela (B05 em diante).

## Serviço de sentimento (B02, negação simples em B11)

`app/services/sentimento.py` expõe `analisar_sentimento(transcricao: str) ->
ResultadoSentimento` (`sentimento: Sentimento`, `evidencias: list[Evidencia]`),
serviço interno, consumido pela rota de B04 via `compor_analise_texto`
(`app/services/analise.py`), não diretamente pela rota. Classifica por
contagem de padrões negativos/positivos (regex com fronteira de palavra
`\b`, texto normalizado para minúsculas/sem acento, com um mapa de volta às
posições da transcrição — ver "Normalização e índices (B14)" abaixo):

- Nenhum sinal encontrado (após a negação) → `informacao_insuficiente`, sem
  evidências.
- Mais sinais negativos → `negativo`. Mais positivos → `positivo`. Empate
  (e maior que zero) → `neutro`, com as evidências dos dois lados.
- Cada ocorrência vira uma evidência própria, então a mesma palavra repetida
  na transcrição gera uma evidência por posição, não uma só.

Corrige a colisão citada nas regras de produto: o experimento de referência
(`conviq_datascience.py`) conta o radical `"satisfeit"` por substring
(`texto.count(...)`), o que também soma a ocorrência de `"satisfeit"` dentro
de `"insatisfeito"`. Aqui, `\bsatisfeit[oa]s?\b` não casa dentro de
`"insatisfeito"` porque não há fronteira de palavra entre `"in"` e
`"satisfeito"` (letras coladas, sem separador).

**Negação simples (B11).** `"não"`, `"nem"`, `"sem"` e `"nenhum(a)"` abrem
um escopo de negação que vai do marcador até o primeiro **fim de escopo**
depois dele, ou o fim do texto. Fecham o escopo (revisão B11-R01):
pontuação `. ! ? ; ,` e quebra de linha; as conjunções adversativas
`"mas"`, `"porém"`, `"contudo"`, `"todavia"`, `"entretanto"`; e a conjunção
`"e"` isolada por espaços. Assim `"sem problemas, estamos satisfeitos"`
alcança `"problemas"` (antes da vírgula) e não `"satisfeitos"` (depois
dela) → positivo; `"não gostei do atendimento, mas adoramos o produto"` não
inverte `"adoramos"` → neutro; `"nenhum problema e estamos satisfeitos"` →
positivo. O `"é"` do verbo também vira `"e"` na normalização, então o
serviço confere o caractere original e `"é"`/`"É"` **não** fecha escopo
(`"não é ruim, é ótimo"` → positivo, com `"ruim"` suprimido). A negação
nunca é estendida até a próxima palavra do léxico — não se presume onde a
expressão termina. Dentro do escopo:

- Um sinal **positivo** vira **negativo** — `"não gostei"` é insatisfação,
  não elogio anulado. A evidência cobre o trecho negado inteiro, do
  marcador ao fim da palavra léxica (`"Não estamos satisfeitos"`, recorte
  literal da transcrição original).
- Um sinal **negativo** é só **suprimido**, nunca vira positivo — negar um
  problema (`"sem problemas"`, `"não foi ruim"`) não é prova de elogio,
  então essa ocorrência não gera evidência. Sem outro sinal na oração, o
  resultado é `informacao_insuficiente`, não `neutro`.
- **Exceção `"não só"`:** não abre negação — `"não só X, como/mas também
  Y"` afirma X e Y, não nega X (`"Não só estamos satisfeitos, como adoramos
  o atendimento."` → positivo, 2 evidências).
- **Conjunção não corta a negação pertinente:** `"Não gostei do suporte e
  do produto."` → negativo (`"gostei"` vem antes do `"e"`); `"Não estamos
  satisfeitos nem contentes."` → negativo com duas evidências,
  `"Não estamos satisfeitos"` e `"nem contentes"` — `"nem"` é marcador
  próprio, por isso funciona também com vírgula antes.

Ver `escopos_de_negacao`/`inicio_da_negacao_mais_proxima` em
`app/services/negacao.py` (extraídos de `sentimento.py` em B12, sem mudança
de comportamento) e os casos em `test_sentimento.py`.

**Limitações desta versão**, deliberadamente fora do escopo de B02/B11:

- **Léxico pequeno**, sem sinônimos exaustivos: por exemplo, `"frustrante"`,
  `"reclamou"` e `"satisfeitíssimo"` não são reconhecidos (falso negativo,
  nunca sinal trocado).
- **Só quatro marcadores de negação** (`"não"`, `"nem"`, `"sem"`,
  `"nenhum(a)"`); outras formas (`"jamais"`, `"nunca"`, `"não obstante"`)
  não abrem escopo.
- **Vírgula parentética dentro da mesma expressão** fecha o escopo cedo
  demais: `"Não estamos, hoje, satisfeitos."` → **positivo**. A regra de
  B11-R01 fecha em toda vírgula, sem análise sintática; pinado em
  `test_sentimento.py`.
- **Adjetivos coordenados por `"e"` sob uma só negação** deixam o segundo
  sem negação: `"Não estamos satisfeitos e contentes."` → **neutro**. Em
  português a forma natural é `"nem"`, que é marcador e funciona. Pinado
  em `test_sentimento.py`.
- **Só as conjunções listadas fecham escopo**; `"ou"`, `"como"`, `"porque"`
  e outras não — `"não gostei do azul ou do verde"` mantém a negação, o
  que costuma ser o sentido pretendido, mas não é análise gramatical.
- **Ironia não é detectada** — `"Ótimo, mais um problema."` conta `"ótimo"`
  como sinal positivo genuíno (empate → neutro), pinado em
  `test_sentimento.py`.
- **`"O problema foi resolvido"` não é reconhecido como neutralização do
  problema** — comportamento inalterado desde B02:
  `"O problema foi resolvido, ficamos satisfeitos."` → **neutro** (1 × 1).
- **Negação dupla geral não é corrigida** — cada marcador nega o sinal mais
  próximo dentro do escopo, sem compor duas negações numa afirmação:
  `"Não é verdade que não gostamos do produto."` → **negativo** (a negação
  linguisticamente correta seria afirmativa).
- **Entrada em forma NFD** (acento como código combinante separado, ex.:
  `"pe\u0301ssimo"`) é tratada desde B14 como a forma NFC (ver abaixo).
- Não distingue intensidade; não considera quem fala.
- `analisar_sentimento` é função interna: espera `str` já validado pelo
  contrato C01 e não faz coerção de tipo (`None`/número → `TypeError`).
  Quem chama pela API é B04, depois de `AnaliseTextoRequest` validar.

A normalização foi extraída para `app/services/texto.py` em B03, para reúso,
e passou a devolver também um mapa de posições em B14.

### Normalização e índices (B14)

`normalizar_com_mapa(texto)` (`app/services/texto.py`) devolve um
`TextoNormalizado`: o texto de busca (`texto`, minúsculas e sem acento) e, para
cada caractere dele, o intervalo da transcrição de onde veio. Antes, a saída
tinha um caractere por caractere de entrada, o que impedia casar palavras com
acento decomposto (NFD): `"O suporte é pe\u0301ssimo."` dava sentimento
`informacao_insuficiente`, e `"Na\u0303o estamos satisfeitos"` perdia a
negação (sentimento positivo, churn sem sinal).

- **Combinantes** (acento decomposto) são absorvidos pelo caractere anterior:
  `"pe\u0301ssimo"` vira `"pessimo"` (7 caracteres) e o mapa sabe que o `"e"`
  ocupa 2 posições da transcrição. Por isso os índices do texto normalizado
  **não** coincidem com os da transcrição; só ficam dentro dos serviços.
- **`intervalo_original(inicio, fim)`** converte `[inicio, fim)` normalizado em
  `[inicio, fim)` da transcrição: o início é o do primeiro caractere e o fim
  (exclusivo) é o do último **mais os combinantes que o seguem**. Por isso o
  recorte de uma evidência NFD contém o código combinante, e
  `transcricao[inicio:fim] == trecho` vale para toda `Evidencia`, nas duas
  formas. Os offsets continuam sendo caracteres Python do eco devolvido (que já
  vem sem espaços nas pontas, C01), não bytes nem UTF-16.
- **Expansão:** um caractere que vira vários na normalização (`"ﬁ"` → `"fi"`)
  gera vários caracteres normalizados com o mesmo intervalo; um casamento que
  cubra só parte deles devolve o caractere inteiro.
- **`é` do verbo × `e` conjunção:** viram o mesmo `"e"` no texto normalizado;
  `caractere_original` devolve o trecho original composto (NFC), válido para
  `e\u0301`, e é o que `negacao.py` e `sinais_comerciais.py` consultam.
- **Combinante órfão** (início do texto ou depois de outro órfão) não gera
  caractere e fica fora de qualquer recorte; pontuação, emoji e quebras de linha
  continuam no texto, um caractere cada.
- Nenhuma posição é recuperada com `str.find`. Sentimento, escopos de negação,
  risco, oportunidades e catálogo trabalham em coordenadas normalizadas e só
  convertem ao criar a `Evidencia`.

Limites: recortes NFD têm mais caracteres que os NFC equivalentes (o frontend
deve destacar por índice, não pelo tamanho da palavra); a normalização de
compatibilidade (NFKD) também funde, por exemplo, `"ª"` em `"a"`, como antes;
combinantes de classe 0 (alguns sinais de línguas fora do português) não são
absorvidos.

## Serviço de sinais comerciais (B03, risco com contexto em B12)

`app/services/sinais_comerciais.py` expõe `analisar_sinais_comerciais(
transcricao: str, vinculo: Vinculo) -> ResultadoSinaisComerciais` (`churn`,
`oportunidades`, `produtos`, `concorrentes`, `evidencias`), também serviço
interno, consumido pela composição de B04 (`compor_analise_texto`), que é
quem a rota chama. Implementa as três regras de produto
específicas de B03, cada uma corrigindo um padrão do experimento de
referência (`conviq_datascience.py`, `analisar_reuniao`):

- **Prospect recebe `churn.situacao = nao_aplicavel`, sempre.** `vinculo`
  decide isso antes de qualquer análise de texto — o experimento não faz
  essa distinção (calcula risco igual para qualquer vínculo).
- **Concorrente isolado não implica troca.** `concorrentes` é detectado à
  parte (lista de nomes únicos, sem evidência — o contrato de C01 não prevê
  evidência para esse campo) e não influencia `churn`. O experimento faz
  `churn = bool(concorrente) or (...)` — citar um concorrente, sozinho, já
  classificava risco `ALTO`; reproduzido e confirmado na revisão de B03.
- **Risco e oportunidade podem coexistir.** `churn` e `oportunidades` vêm de
  padrões independentes (risco em `_ocorrencias_risco` e oportunidade em
  `_REGEX_OPORTUNIDADE`), sem um suprimir o outro. O experimento faz
  `upsell = (not churn) and (...)` — uma oportunidade só era registrada
  quando não havia churn; reproduzido com um texto de risco real que também
  teria oportunidade (o experimento zera o `upsell` nesse caso; B03 mantém
  as duas).

**Risco de cancelamento com contexto local (B12).** Antes, `"cancelar"` /
`"reavaliar"` / `"rescindir"` geravam risco sozinhos, com qualquer objeto —
`"cancelar a reunião"` valia tanto quanto `"cancelar o contrato"` — e sem
checar negação — `"não vamos cancelar o contrato"` gerava o mesmo risco que
`"vamos cancelar"`. `_ocorrencias_risco` (`app/services/sinais_comerciais.py`)
combina três fontes, reaproveitando o escopo de negação de B11
(`app/services/negacao.py`, extraído de `sentimento.py` para os dois
serviços usarem):

- `"insatisfeito"`/`"frustrado"` continuam risco por si só, mas agora
  **suprimidos quando negados** — `"Não estamos insatisfeitos."` deixa de
  ser risco (negar um problema não prova baixo risco; a mesma regra de B11
  para sentimento) — e **quando a insatisfação é com tema alheio à relação
  comercial** (revisão B12-R04, ver abaixo).
- `"cancelar"`/`"cancelamento"`/`"reavaliar"`/`"rescindir"` só são risco
  quando um **objeto da relação comercial** (`"contrato"`, `"serviço"`,
  `"fornecedor"`) é o **núcleo do complemento da ação** e são **suprimidos
  quando a própria ação está negada**. Ligação ação–objeto (revisão
  B12-R02, `_fim_do_objeto_da_acao`): depois da ação, pulam-se só palavras
  funcionais (artigos, preposições como `"do"`/`"com"`, possessivos,
  demonstrativos, `"todos"`, alguns advérbios curtos como `"já"` e
  `"imediatamente"`); a primeira outra palavra é o núcleo. `"cancelar o
  contrato"`, `"rescindir o nosso contrato"`, `"cancelamento do contrato"`,
  `"cancelar com o fornecedor"` → sinal. `"Vamos cancelar a reunião sobre
  o contrato."` e `"Vamos reavaliar a pauta com o fornecedor."` → sem sinal:
  o núcleo é a reunião/pauta, e o contrato só a modifica. `"e"`/`"ou"`
  coordenam um segundo membro do complemento (`"cancelar a reunião e o
  contrato"` → sinal; `"a reunião e não o contrato"` → sem sinal). O
  complemento termina em vírgula, pontuação de frase ou adversativa
  (`"mas"`, `"porém"`...); objeto antes da ação ou em outra oração (`"O
  contrato continua vigente, vamos cancelar a reunião."`) não se liga. A
  condição antes da vírgula não atrapalha: `"Se o suporte continuar assim,
  vamos cancelar o contrato."` → sinal.
- **Sujeito de outra oração não é objeto coordenado (revisão B12-R06,
  `_membros_coordenados`).** Depois de `"e"`/`"ou"`, o membro só entra no
  complemento se terminar como sintagma nominal: núcleo seguido apenas de
  palavras funcionais ou de complemento preposicionado (`de`, `do`, `com`,
  `no`, `em`, `até`...). `"cancelar a reunião e o contrato de suporte"`,
  `"... e o contrato atual"` e `"... e o contrato no fim do mês"` → sinal;
  `"Vamos cancelar a reunião e o contrato continua vigente."` e `"... e o
  fornecedor será avisado."` → sem sinal, porque `"continua"`/`"será"` não
  modifica o substantivo e mostra outra oração. O objeto **direto** não
  passa por essa verificação: `"Vamos cancelar o contrato e o suporte
  continua."` → sinal, com evidência `"cancelar o contrato"`.
- `"satisfeito"` (positivo) é o espelho de `"insatisfeito"`: só é risco
  **quando negado** — `"Não estamos satisfeitos com o suporte."` → sinal;
  satisfação afirmada nunca é risco. A exceção de tema alheio vale igual.

**Insatisfação com tema alheio à relação comercial (revisão B12-R04,
`_e_tema_alheio`).** A regra de B03 tratava qualquer `"insatisfeito"` como
risco de churn, e B12 espelhou isso em `"não ... satisfeito"`; `"Estamos
insatisfeitos com o clima."` e `"Não estamos satisfeitos com o almoço."`
geravam churn e recomendação de retenção. O cartão B12 pede insatisfação
com a relação comercial, e a regra agora exclui os casos inequívocos:

- o **núcleo** de cada membro do complemento `"com ..."` está na lista
  fechada `_PADROES_TEMA_ALHEIO` — clima (`clima`, `chuva`, `calor`,
  `frio`), refeições (`almoço`, `jantar`, `café`, `lanche`, `comida`,
  `restaurante`), deslocamento (`trânsito`, `estacionamento`) e lazer
  (`futebol`), com plurais; **e**
- o complemento não cita termo da relação (vocabulário de contexto
  comercial ou produto do catálogo).

Satisfeitas as duas condições, a insatisfação não é risco e o
`"satisfeito"` dessa expressão não conta como contexto comercial. Isolada,
a frase dá `informacao_insuficiente` (`"Estamos satisfeitos com o
almoço."` também, antes `sem_sinal_detectado`); com contexto comercial
independente (`"Estamos insatisfeitos com o clima, mas o contrato segue
normal."`), `sem_sinal_detectado`; com outro risco real (`"... com o clima
e vamos cancelar o contrato."`), o sinal vem só do cancelamento. O
sentimento negativo e as oportunidades não mudam. Continuam risco, como em
B03: `"insatisfeitos com o suporte"`, `"frustrados com o atendimento"`,
`"não estamos satisfeitos com o serviço"`, complementos fora da lista
(`"frustrados com o atraso"`, `"com a demora"`) e tema da lista com termo
da relação (`"com o clima da parceria"`, `"com o almoço e com o suporte"`).
A lista evita de propósito termos ambíguos numa reunião comercial
(`tempo`, `time`, `viagem`, `equipe`). A alternativa de exigir um termo da
relação no complemento foi descartada, porque tornaria falso negativo
queixas do domínio fora do vocabulário (`"com o atraso"`, `"com o prazo"`,
`"com vocês"`).

**Evidência com o contexto que sustenta o risco (revisão B12-R03).** Até a
revisão, a evidência de ação era só `"cancelar"` — não mostrava por que era
risco comercial e não cancelamento de reunião — e a satisfação negada
omitia com o que era a insatisfação. Agora, sempre recorte literal e
contínuo da transcrição:

- ação → da ação ao objeto ligado: `"cancelar o contrato"`, `"cancelar a
  reunião e o contrato"`;
- condição que abre a frase → a evidência começa no `"Se"`: `"Se o suporte
  continuar assim, vamos cancelar o contrato"` (a ameaça condicional não
  parece decisão tomada); `"se"` em outra posição (`"Decidiu-se"`) não
  estende;
- insatisfação (`"insatisfeito"`, `"frustrado"`, `"não ... satisfeito"`) →
  inclui o complemento `"com ..."` até vírgula ou adversativa, com os
  membros coordenados que são sintagma nominal (B12-R06): `"insatisfeitos
  com o suporte"`, `"Não estamos satisfeitos com o suporte"`,
  `"insatisfeitos com o suporte e o atendimento"`; `"insatisfeitos com o
  suporte e vamos cancelar o contrato"` → `"insatisfeitos com o suporte"`
  (o resto é outra oração). Sem `"com"` logo depois, só a expressão
  (`"insatisfeitos"`).

Como `"insatisfeito"`/`"satisfeito"` também alimentam o sentimento de B02,
o mesmo trecho aparece em duas evidências: a do sentimento é a expressão
(`"insatisfeitos"`) e a do churn inclui o complemento (`"insatisfeitos com
o suporte"`), começando na mesma posição. Sem complemento, os intervalos
são idênticos. B04 renumera as duas ao compor (ver seção seguinte).

**Oportunidade por intenção comercial (B13, `_ocorrencias_oportunidade`).**
Antes, cada palavra como `"interesse"`, `"conhecer"` ou `"módulo"` gerava
uma oportunidade, mesmo negada, sem objeto comercial ou como simples menção
(`"Não temos interesse em conhecer o Fluig."` → duas oportunidades;
`"O módulo atual está instalado."` → uma). Agora um **gatilho** só gera
oportunidade quando:

- **não está no escopo de uma negação** de B11 (`app/services/negacao.py`, a
  mesma regra de sentimento e risco): `"Não temos interesse em conhecer o
  Fluig."`, `"Sem interesse no Protheus."` → nada. A vírgula e o `"mas"`
  fecham o escopo: `"Não queremos o Fluig, mas temos interesse no
  Protheus."` → só `"interesse no Protheus"`, e `produtos` lista Fluig e
  Protheus. Uma frase seguinte não é alcançada: `"Não temos interesse.
  Queremos conhecer o Fluig."` → uma oportunidade; e
- **tem um objeto comercial como núcleo do seu complemento**, na mesma
  oração, pela ligação ação–objeto de B12 adaptada para a oportunidade
  (`_fim_do_objeto_da_oportunidade`,
  com artigos, preposições como `em`/`no`/`para`, `outra`, `novo`, `mais` e
  os gatilhos encadeados pulados). Objeto comercial é um produto do catálogo
  ou um destes substantivos: módulo, solução, sistema, plataforma, software,
  ferramenta, produto, serviço, licença, integração, automação,
  faturamento, proposta, filial, unidade, usuário. `"Queremos conhecer o
  Fluig."` e `"Precisamos automatizar o faturamento."` → oportunidade;
  `"Quero conhecer a cidade."` e `"Quero conhecer o novo diretor."` → nada.

Gatilhos: `interesse`, `interessado(a)(s)`, `conhecer`, `avaliar`,
`contratar`, `adquirir`, `implantar`, `expandir`, `ampliar`, `integrar`,
`automatizar`. As formas de querer ou precisar (`quero`, `queremos`,
`queria`, `precisamos`, `necessitamos`, `gostaríamos`, `pretendemos`,
`buscamos`...) logo antes do gatilho entram no recorte e também são
avaliadas como intenção própria, com o seu complemento (`"Precisamos de um
módulo"`, `"Queremos o Fluig"`). **Revisão B13-R01:** na entrega inicial,
qualquer gatilho posterior na oração descartava essa intenção, mesmo sem
objeto comercial ou negado — `"Queremos o Fluig e conhecer a cidade."` e
`"Queremos o Fluig e não conhecer o Protheus."` perdiam a oportunidade sobre
Fluig, e `"Precisamos de um módulo e conhecer o Fluig."` ficava só com
`"conhecer o Fluig"`. Agora as três mantêm `"Queremos o Fluig"`/`"Precisamos
de um módulo"`, o gatilho alheio ou negado não gera outra, e a última tem as
duas intenções (sem agrupar, B17). Quando o querer só introduz o gatilho
(`"Queremos conhecer o Fluig"`), os dois recortes coincidem e contam uma
vez. `"módulo"` deixou de ser gatilho: é só objeto.
`"avaliar"`, `"contratar"`, `"adquirir"`, `"implantar"` e `"ampliar"` são
novos gatilhos de B13 (avaliação e contratação do cartão).

**`"sistema"` com modificador alheio (revisão B13-R02, `_e_sistema_alheio`).**
`"sistema"` é o objeto mais genérico da lista (B12 já o tirou do contexto de
churn por `"o sistema solar"`). Quando a palavra logo depois dele é um
modificador astronômico ou biológico (`solar`, `planetário`, `nervoso`,
`imunológico`, `digestivo`, `respiratório`, `circulatório`, `cardiovascular`,
`reprodutor`, `linfático`, `endócrino`), ele não é objeto comercial:
`"Queremos integrar o sistema solar."` → nenhuma oportunidade, churn
`informacao_insuficiente` (antes, `"Queremos integrar o sistema"` com
recomendação). `"o sistema ERP"`, `"o sistema de faturamento"` e `"o
sistema"` sem modificador continuam oportunidade, e um membro coordenado
comercial depois do rejeitado ainda liga (`"... o sistema solar e o Fluig"`).
Lista fechada, não classificador de temas.

**A evidência é a intenção inteira**, recorte literal e contínuo do início
da intenção ao fim do objeto: `"Queremos conhecer o Fluig"`, `"Precisamos
automatizar o faturamento"`, `"interesse no Protheus"` — antes, só a palavra
(`"conhecer"`). A `descricao` continua `'Interesse comercial sinalizado por
"<trecho>".'`, agora com o trecho completo. Evidência de risco e de
oportunidade seguem independentes (`"Estamos insatisfeitos com o suporte.
Queremos conhecer o Fluig."` → as duas, cada uma com a sua recomendação).

**Efeitos em outras regras.** Uma ocorrência rejeitada como oportunidade não
é, por si só, conteúdo comercial: `"O módulo atual está instalado."` e
`"Quero conhecer a cidade."` → churn `informacao_insuficiente` (antes
`sem_sinal_detectado`). Produto, concorrente ou outro termo de contexto
independente continuam tornando o churn avaliável (`"Não temos interesse em
conhecer o Fluig."` → `sem_sinal_detectado`, `produtos == ["Fluig"]`). Um
concorrente isolado (`"Queremos conhecer a SAP."`) não é oportunidade nem
risco. Prospect continua `nao_aplicavel` e recebe oportunidades pela mesma
regra.

**Limites da regra local (B13)**, pinados em `test_sinais_comerciais.py`:

- **Não agrupa gatilhos da mesma intenção (B17):** `"Temos interesse em
  conhecer o Fluig."` ainda gera duas oportunidades, `"interesse em
  conhecer o Fluig"` e `"conhecer o Fluig"` (agora com recortes distintos).
- **Objeto coordenado é aceito:** `"Queremos conhecer a cidade e o Fluig."`
  declara intenção de conhecer o Fluig e gera `"Queremos conhecer a cidade e
  o Fluig"`; a revisão B13 não o trata como falso positivo.
- **Falsos positivos:** quem quer não é identificado (`"O analista vai
  conhecer o Fluig."`), nem pergunta do fornecedor (`"Vocês querem conhecer
  o Fluig?"`); `"avaliar o serviço"` é lida como oportunidade, mesmo podendo
  ser avaliação de um serviço atual; `filial`, `unidade` e `usuário` são
  alvos de expansão (`"integrar as filiais"`, `"precisamos de mais
  usuários"`), mas com `"conhecer"` podem ser visita ou encontro (`"Queremos
  conhecer a filial de São Paulo."` → oportunidade); outros sentidos
  genéricos de objetos da lista (`"plataforma de petróleo"`) e de `"sistema"`
  fora dos modificadores listados.
- **Falsos negativos:** vírgula entre gatilho e objeto (`"Queremos muito
  conhecer, no mês que vem, o Fluig."`); objeto fora da lista (`"Queremos
  conhecer o suporte técnico."`, `"Precisamos automatizar o processo."`);
  ironia e discurso indireto.
- **A negação de B11 fecha no `"e"`:** `"Não queremos o Fluig e conhecer o
  Protheus."` gera `"conhecer o Protheus"`; é o sentido provável nesse
  exemplo, mas a regra não sabe se o `"e"` abre uma nova intenção ou
  continua a negada.
- A descrição segue genérica (B18) e `produtos` continua listando menções,
  não intenções.

**Ausência de sinal vs. informação insuficiente (revisão B03-R01).** Sem
risco explícito, o serviço decide entre dois estados distintos do contrato:

- `sem_sinal_detectado` quando há **conteúdo comercial avaliável**:
  oportunidade, produto, concorrente **ou** vocabulário da relação
  comercial (`_PADROES_CONTEXTO_COMERCIAL`: contrato, renovação, suporte,
  atendimento, serviço, produto, implantação, licença, preço, custo,
  proposta, parceria, fornecedor, plataforma, pagamento, faturamento,
  mensalidade, satisfeito — `"sistema"` removido em B12, ver limites
  abaixo; `"satisfeito"` com tema alheio não conta, B12-R04). Foi avaliado
  e nada indica risco — o que não é o mesmo que
  confirmar baixo risco. Uma ação de risco sem objeto (`"cancelar a
  reunião"`) **não** conta como contexto por si só —
  `"informacao_insuficiente"` quando isolada.
- `informacao_insuficiente` quando não há nada disso: saudação, pauta,
  encerramento, texto vazio. Ex.: `"Bom dia a todos. Vamos seguir a pauta
  de hoje."` (exemplo 3 do contrato) → insuficiente; `"O suporte foi
  excelente e o contrato segue normal."` → sem sinal.

Antes de B03-R01, `informacao_insuficiente` só saía para texto vazio, que
o contrato rejeita antes de chamar o serviço — o estado era inalcançável
para qualquer entrada válida. **Limites da heurística:** vocabulário fixo;
uma conversa sobre a relação comercial que não use nenhum desses termos cai
em insuficiente, e um termo genérico (`"produto"`) usado fora do sentido
comercial ainda conta como contexto — `"sistema"` foi corrigido em B12
(`"O sistema solar é extenso."` → insuficiente), `"produto"` permanece,
limite conhecido e não resolvido nesta entrega. `vinculo == nao_informado`
segue a mesma regra que `cliente` (não é presumido prospect nem baixo risco).

`produtos` (Protheus, Datasul, Fluig, Analytics, RM) e `concorrentes`
(Senior, SAP, Oracle, Sankhya) reaproveitam os catálogos do experimento —
dados factuais de nome de produto/mercado, não a lógica de contagem com bug.

**Limitações desta versão**, deliberadamente fora do escopo de B03:

- **Léxicos de risco/oportunidade pequenos**, no mesmo espírito de B02 —
  cobrem os cenários pedidos pelo plano, não são exaustivos.
- **Descrição da oportunidade é genérica** (`'Interesse comercial
  sinalizado por "<trecho>".'`), sem nomear a qual produto ou contexto se
  refere — correlacionar com `produtos` mencionados é melhoria futura. Desde
  B13 o trecho citado é a intenção inteira, não só a palavra.
- **Sobreposição proposital com o léxico de B02** (`"insatisfeit"`,
  `"frustrad"`, `"satisfeit"` aparecem nos dois): sentimento geral e risco
  de cancelamento respondem perguntas diferentes; os dois serviços podem
  gerar evidência própria para o mesmo trecho, com IDs de namespace
  separado — B04 renumera ao juntar num `AnaliseTextoResponse` só (ver
  seção seguinte).
- `analisar_sinais_comerciais` é função interna: espera `str` e `Vinculo`
  já validados pelo contrato C01.

**Limites da negação de B12**, herdados de B11 (mesmo módulo
`app/services/negacao.py`, ver "Serviço de sentimento" acima para exemplos):
só quatro marcadores (`"não"`, `"nem"`, `"sem"`, `"nenhum(a)"`); vírgula
parentética fecha escopo cedo demais; adjetivos coordenados por `"e"` sob
uma só negação deixam o segundo sem negação; negação dupla geral e ironia
não são tratadas.

- **Objeto de risco é vocabulário fixo e pequeno** (`"contrato"`,
  `"serviço"`, `"fornecedor"`): `"cancelar a assinatura"` ou `"cancelar o
  plano"` não viram risco, mesmo quando o sentido é o mesmo. Ampliar essa
  lista é melhoria futura, não corrigida nesta entrega. Com a ligação ao
  núcleo (B12-R02), isso vale também para um núcleo intermediário:
  `"cancelar a renovação do contrato"` não é risco (era em `d5fb40a`, só
  por haver `"contrato"` na frase) — a mesma estrutura de `"cancelar a
  reunião sobre o contrato"`; separar as duas exige decidir quais núcleos
  são da relação comercial.
- **Ligação ação–objeto é local e simples, não análise gramatical**:
  palavra fora da lista funcional entre ação e objeto (`"cancelar de vez o
  contrato"`), vírgula intercalada (`"cancelar, infelizmente, o
  contrato"`) ou objeto antes da ação (`"O contrato, vamos cancelar."`)
  impedem a ligação — falso negativo, pinado em `test_sinais_comerciais.py`.
  Formas como `"cancelado"`/`"cancelaremos"` não são ações de risco (léxico
  de B03).
- **Membro coordenado reconhecido sem identificar verbos (B12-R06)**:
  qualquer palavra fora das listas funcionais depois do núcleo coordenado
  encerra o sintagma, inclusive advérbio ou adjetivo. `"Vamos cancelar a
  reunião e o contrato hoje."` (pinado) e `"... e o contrato vigente."` →
  sem sinal, falso negativo; `"... e o contrato atual."` e `"... e o
  contrato também."` são sinal, porque `"atual"`/`"também"` estão na lista
  funcional.
- **Condição só no início da frase**: `"Vamos cancelar o contrato se nada
  mudar."` é risco, mas a evidência é `"cancelar o contrato"`, sem a
  condição posposta.
- **Tema alheio é lista fechada, só no complemento `"com ..."` (B12-R04)**:
  tema alheio fora da lista continua risco (`"Estamos insatisfeitos com o
  hotel."` → sinal, falso positivo, pinado), assim como o tema antes da
  palavra (`"O almoço nos deixou insatisfeitos."`) ou sem complemento
  (`"Estamos insatisfeitos."`, regra de B03). Um termo da relação em
  qualquer lugar do complemento mantém o risco, mesmo que só de passagem.
  Não é um classificador de assuntos.
- **Complemento da insatisfação só com `"com"`**: `"insatisfeitos em
  relação ao suporte"` continua risco, com evidência `"insatisfeitos"`;
  `"Não estamos satisfeitos nem contentes com o suporte."` → evidência
  `"Não estamos satisfeitos"`.
- **Evidências podem se sobrepor**: com a condição, `"Se continuarmos
  insatisfeitos com o suporte, vamos cancelar o contrato."` gera duas
  evidências de churn, uma contida na outra. Unir intervalos sobrepostos
  não é feito aqui (B19 trata só intervalos idênticos).

## Rota de análise (B04)

`app/api/analises.py` expõe `POST /api/analises/texto`, a única rota que
chama `app/services/analise.py`
(`compor_analise_texto(pedido: AnaliseTextoRequest) -> AnaliseTextoResponse`).
A rota em si só delega: validação é do schema (C01), erros já eram
traduzidos pelo manipulador de B01/C01 sem precisar de ajuste (o corpo é o
mesmo `AnaliseTextoRequest`), e a análise não lê nem escreve nada —
persistência é B05.

`compor_analise_texto`:

1. Roda `analisar_sentimento` (B02) e `analisar_sinais_comerciais` (B03)
   sobre a mesma transcrição.
2. **Renumera as evidências.** B02 e B03 numeram cada um a partir de `e1`;
   juntos sem ajuste, colidiriam. A composição reúne as duas listas, ordena
   por `inicio` (posição no texto, não por origem) e renumera em sequência
   única, atualizando as referências em `churn.evidencias` e em cada
   `oportunidades[].evidencias`. Consequência esperada, não um bug: quando
   B02 e B03 detectam o mesmo radical (ex.: `"insatisfeito"`, sinal de
   sentimento negativo **e** de risco de churn), a resposta tem duas
   evidências distintas para o mesmo trecho — verificado com servidor real
   (`uvicorn`) no exemplo do contrato C01. Desde a revisão B12-R03, a de
   churn inclui o complemento (`"insatisfeitos"` e `"insatisfeitos com o
   suporte"`, mesma posição inicial); sem complemento, os intervalos são
   idênticos. Empate de posição mantém a ordem sentimento → comercial.
3. **Deriva `recomendacoes`:** uma recomendação genérica para
   `churn.situacao == sinal_detectado` (evidenciada pelas evidências de
   churn) e uma por oportunidade (evidenciada pela evidência daquela
   oportunidade). Sem risco nem oportunidade, a lista fica vazia — nenhuma
   recomendação é inventada sem evidência.
4. Usa `metodo="regras"` e `versao_analise="0.5"` (`0.1` em B04, `0.2`
   com a negação de B11, `0.3` com o risco em contexto de B12, `0.4` com a
   oportunidade por intenção de B13, `0.5` com o Unicode NFD de B14; contrato
   C01 inalterado), os mesmos valores dos exemplos do contrato.

**Limitações desta versão:** as recomendações são genéricas (não citam o
produto/trecho específico, mesmo estilo já documentado para a descrição de
oportunidades em B03); evidências duplicadas do mesmo trecho (item 2 acima)
não são mescladas — a resposta **não** tem campo que diga de qual serviço
cada evidência veio; o que fica preservado são os IDs únicos e as
referências (qual evidência sustenta `churn`, cada oportunidade e cada
recomendação). Uma interface que listar `evidencias` pode mostrar o mesmo
trecho destacado duas vezes; decidir se isso precisa de tratamento é
decisão de produto/frontend (F05), não deste PR.

## Contrato de análise por texto (C01)

Campos, enums, limites, localização de evidências e códigos de erro HTTP
estão documentados em
[`docs/contratos/analise-texto.md`](../docs/contratos/analise-texto.md),
com exemplos (cliente com risco e oportunidade, prospect e informação
insuficiente) validados diretamente contra os schemas Pydantic. Este README
lista só o que ainda fica pendente para outras etapas.

## Limites conhecidos (pendentes para outras etapas)

- **`POST /api/analises/texto` é a única rota que usa
  `AnaliseTextoRequest`/`AnaliseTextoResponse`** (B04). O envelope de erro de
  C01 é exercitado de duas formas: `tests/test_erros.py` por uma rota
  descartável só do teste (criada em C01, antes de existir rota real) e
  `tests/test_analises_rota.py` pela rota real, inclusive o schema 422
  anunciado no OpenAPI (revisão B04-R01).
- **Posição da evidência (`Evidencia.inicio`/`fim`)** é só validada
  internamente pelo schema (`fim > inicio`); o schema em si não confirma que
  o trecho aparece na transcrição naquela posição — quem garante isso é
  quem gera a evidência. `analisar_sentimento` (B02) e
  `analisar_sinais_comerciais` (B03) garantem essa correspondência por
  construção (usam `match.start()`/`match.end()` do próprio texto); testado
  em `test_sentimento.py` e `test_sinais_comerciais.py`.
- **A regra "prospect recebe `churn.situacao = nao_aplicavel`"** não é
  imposta pelo schema: `AnaliseTextoRequest` (com `vinculo`) e
  `AnaliseTextoResponse` (com `churn`) são validados separadamente — isso
  continua verdadeiro como limite do *schema*. A regra **é** aplicada no
  serviço (`analisar_sinais_comerciais`, B03), e a composição de B04 passa o
  `vinculo` do pedido a esse serviço — testado em `test_analise.py` e pela
  rota em `test_analises_rota.py` (prospect → `nao_aplicavel`). Só não é
  uma validação cruzada do schema.
- **CORS** libera só `http://localhost:5173` por padrão (origem prevista
  para o frontend); outras origens exigem configurar `ORIGENS_CORS`.
- **Aviso de depreciação `httpx` → `httpx2`** em `starlette.testclient`
  (ver B01-06); não bloqueia os testes, mantido sem alteração.

Resolvido em C01 (não é mais limitação): `titulo`/`empresa`/`transcricao`
só com espaços em branco agora são tratados como vazios (`BeforeValidator`
que só aplica `strip()` a `str`, em `app/schemas/reuniao.py` — outro tipo
JSON no campo vira erro de validação 422, não 500; revisão C01-R01); IDs de
evidência duplicados em `evidencias` agora são rejeitados
(`app/schemas/analise.py`); erros de validação do FastAPI agora respondem
no envelope `{"erro": {"codigo", "mensagem"}}`, com HTTP 422
(`app/erros.py`).
