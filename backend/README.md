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
│       ├── texto.py             # normalizar_preservando_posicoes(texto), usada por B02 e B03
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
`\b`, texto normalizado para minúsculas/sem acento preservando o
comprimento e as posições originais):

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

Ver `_escopos_de_negacao`/`_inicio_da_negacao_mais_proxima` em
`sentimento.py` e os casos em `test_sentimento.py`.

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
  `"péssimo"`) não casa sinais acentuados: a normalização preserva o
  índice de cada código e não pode fundir dois códigos em um sem quebrar as
  posições das evidências. Transcrições em NFC (o padrão de editores e
  APIs) não são afetadas. Falso negativo, sem correção sem remapear índices.
- Não distingue intensidade; não considera quem fala.
- `analisar_sentimento` é função interna: espera `str` já validado pelo
  contrato C01 e não faz coerção de tipo (`None`/número → `TypeError`).
  Quem chama pela API é B04, depois de `AnaliseTextoRequest` validar.

A normalização (`_normalizar_preservando_posicoes`) foi extraída para
`app/services/texto.py` em B03, para reúso — comportamento idêntico, sem
mudança de resultado (suíte de B02 continua passando sem alteração).

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
  para sentimento).
- `"cancelar"`/`"cancelamento"`/`"reavaliar"`/`"rescindir"` só são risco
  quando há um **objeto da relação comercial** (`"contrato"`, `"serviço"`,
  `"fornecedor"`) na **mesma oração** (delimitada só por `. ! ? ;`/quebra de
  linha, não por vírgula — a ameaça pode estar numa frase mais longa:
  `"Se o suporte continuar assim, vamos cancelar o contrato."` → sinal) e
  são **suprimidos quando a própria ação está negada**. A evidência é a
  ação (`"cancelar"`), como antes de B12 — o objeto não vira evidência.
- `"satisfeito"` (positivo) é o espelho de `"insatisfeito"`: só é risco
  **quando negado** — `"Não estamos satisfeitos com o suporte."` → sinal,
  evidência `"Não estamos satisfeitos"` (o trecho negado inteiro, como a
  evidência negada de B11); satisfação afirmada nunca é risco.

Como `"insatisfeito"`/`"satisfeito"` também alimentam o sentimento de B02,
o mesmo trecho pode virar duas evidências (uma de cada serviço) — B04 as
renumera ao compor (ver seção seguinte).

**Ausência de sinal vs. informação insuficiente (revisão B03-R01).** Sem
risco explícito, o serviço decide entre dois estados distintos do contrato:

- `sem_sinal_detectado` quando há **conteúdo comercial avaliável**:
  oportunidade, produto, concorrente **ou** vocabulário da relação
  comercial (`_PADROES_CONTEXTO_COMERCIAL`: contrato, renovação, suporte,
  atendimento, serviço, produto, implantação, licença, preço, custo,
  proposta, parceria, fornecedor, plataforma, pagamento, faturamento,
  mensalidade, satisfeito — `"sistema"` removido em B12, ver limites
  abaixo). Foi avaliado e nada indica risco — o que não é o mesmo que
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
  refere — correlacionar com `produtos` mencionados é melhoria futura.
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
  lista é melhoria futura, não corrigida nesta entrega.
- **"Mesma oração" do vínculo ação–objeto usa só pontuação de fim de
  frase** (`. ! ? ;`/quebra de linha), não vírgula/conjunção — mais
  permissivo que o escopo de negação. `"Vamos cancelar o contrato, que já
  estava vencido, e o serviço de suporte."` liga `"cancelar"` a qualquer
  objeto na mesma frase, mesmo depois de uma vírgula intermediária; não
  testado como caso de aceite, mas seria detectado.

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
   evidências distintas apontando para o mesmo trecho — verificado com
   servidor real (`uvicorn`) no exemplo do contrato C01.
3. **Deriva `recomendacoes`:** uma recomendação genérica para
   `churn.situacao == sinal_detectado` (evidenciada pelas evidências de
   churn) e uma por oportunidade (evidenciada pela evidência daquela
   oportunidade). Sem risco nem oportunidade, a lista fica vazia — nenhuma
   recomendação é inventada sem evidência.
4. Usa `metodo="regras"` e `versao_analise="0.2"` (B11 sobre a base `0.1`
   de B04 — negação simples no sentimento, contrato C01 inalterado), os
   mesmos valores dos exemplos do contrato.

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
