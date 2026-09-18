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
│   ├── test_sentimento.py       # B02: insatisfeito, ausência de sinal, trechos repetidos
│   ├── test_sinais_comerciais.py # B03: prospect, concorrente isolado, coexistência
│   ├── test_analise.py           # B04: composição, renumeração de evidências, recomendações
│   └── test_analises_rota.py     # B04: POST /api/analises/texto, entrada válida e inválida
└── pyproject.toml
```

`app/integrations/` e `app/db/` ainda não existem — o plano pede para criar
cada pasta apenas quando a etapa correspondente precisar dela (B05 em diante).

## Serviço de sentimento (B02)

`app/services/sentimento.py` expõe `analisar_sentimento(transcricao: str) ->
ResultadoSentimento` (`sentimento: Sentimento`, `evidencias: list[Evidencia]`),
serviço interno, consumido pela rota de B04 via `compor_analise_texto`
(`app/services/analise.py`), não diretamente pela rota. Classifica por
contagem de padrões negativos/positivos (regex com fronteira de palavra
`\b`, texto normalizado para minúsculas/sem acento preservando o
comprimento e as posições originais):

- Nenhum sinal encontrado → `informacao_insuficiente`, sem evidências.
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

**Limitações desta versão**, deliberadamente fora do escopo de B02:

- **Léxico pequeno**, sem sinônimos exaustivos: por exemplo, `"frustrante"`,
  `"reclamou"` e `"satisfeitíssimo"` não são reconhecidos (falso negativo,
  nunca sinal trocado).
- **Negação e contexto de frase não são tratados** — o serviço conta a
  palavra, não a frase. Casos verificados na revisão B02-03, pinados em
  `test_sentimento.py` como comportamento atual: `"Não estamos satisfeitos."`
  → **positivo**; `"Sem problemas, tudo certo."` e `"Nenhum problema até
  agora."` → **negativo**; `"Não foi ruim."` → **negativo**; `"Não gostei."`
  → **positivo**; `"O problema foi resolvido, ficamos satisfeitos."` →
  **neutro** (1 × 1). `"Sem problemas"` é frase comum em português, então
  este é o limite mais visível para quem ler o card. Tratar negação é
  melhoria futura, a decidir na coordenação, não uma correção de B02.
- **Entrada em forma NFD** (acento como código combinante separado, ex.:
  `"péssimo"`) não casa sinais acentuados: a normalização preserva o
  índice de cada código e não pode fundir dois códigos em um sem quebrar as
  posições das evidências. Transcrições em NFC (o padrão de editores e
  APIs) não são afetadas. Falso negativo, sem correção sem remapear índices.
- Não distingue intensidade nem ironia; não considera quem fala.
- `analisar_sentimento` é função interna: espera `str` já validado pelo
  contrato C01 e não faz coerção de tipo (`None`/número → `TypeError`).
  Quem chama pela API é B04, depois de `AnaliseTextoRequest` validar.

A normalização (`_normalizar_preservando_posicoes`) foi extraída para
`app/services/texto.py` em B03, para reúso — comportamento idêntico, sem
mudança de resultado (suíte de B02 continua passando sem alteração).

## Serviço de sinais comerciais (B03)

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
  padrões independentes (`_REGEX_RISCO` e `_REGEX_OPORTUNIDADE`), sem um
  suprimir o outro. O experimento faz `upsell = (not churn) and (...)` —
  uma oportunidade só era registrada quando não havia churn; reproduzido com
  um texto de risco real que também teria oportunidade (o experimento zera
  o `upsell` nesse caso; B03 mantém as duas).

**Ausência de sinal vs. informação insuficiente (revisão B03-R01).** Sem
risco explícito, o serviço decide entre dois estados distintos do contrato:

- `sem_sinal_detectado` quando há **conteúdo comercial avaliável**:
  oportunidade, produto, concorrente **ou** vocabulário da relação
  comercial (`_PADROES_CONTEXTO_COMERCIAL`: contrato, renovação, suporte,
  atendimento, serviço, sistema, produto, implantação, licença, preço,
  custo, proposta, parceria, fornecedor, plataforma, pagamento,
  faturamento, mensalidade, satisfeito). Foi avaliado e nada indica risco —
  o que não é o mesmo que confirmar baixo risco.
- `informacao_insuficiente` quando não há nada disso: saudação, pauta,
  encerramento, texto vazio. Ex.: `"Bom dia a todos. Vamos seguir a pauta
  de hoje."` (exemplo 3 do contrato) → insuficiente; `"O suporte foi
  excelente e o contrato segue normal."` → sem sinal.

Antes de B03-R01, `informacao_insuficiente` só saía para texto vazio, que
o contrato rejeita antes de chamar o serviço — o estado era inalcançável
para qualquer entrada válida. **Limites da heurística:** vocabulário fixo;
uma conversa sobre a relação comercial que não use nenhum desses termos cai
em insuficiente, e um termo genérico (`"sistema"`, `"produto"`) usado fora
do sentido comercial conta como contexto. `vinculo == nao_informado` segue
a mesma regra que `cliente` (não é presumido prospect nem baixo risco).

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
  `"frustrad"` aparecem nos dois): sentimento geral e risco de cancelamento
  respondem perguntas diferentes; os dois serviços podem gerar evidência
  própria para o mesmo trecho, com IDs de namespace separado — B04 renumera
  ao juntar num `AnaliseTextoResponse` só (ver seção seguinte).
- Não trata negação/contexto de frase, pelo mesmo motivo documentado em B02.
- `analisar_sinais_comerciais` é função interna: espera `str` e `Vinculo`
  já validados pelo contrato C01.

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
4. Usa `metodo="regras"` e `versao_analise="0.1"`, os mesmos valores do
   exemplo do contrato.

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
