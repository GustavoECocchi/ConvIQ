# Contrato de análise por texto (C01)

Consolidado em 17/09/2026, sobre os schemas entregues em B01 e revisados na
correção de B01 (evento B01-06 em `REGISTRO_TRABALHO.md`). Fonte de verdade
em código: `backend/app/schemas/{reuniao,analise,comum,erro}.py` e
`backend/app/erros.py`. Este documento descreve o que já está implementado;
não é uma proposta.

**O que já existe (atualizado em 18/09/2026, B04):** a rota
`POST /api/analises/texto` responde de verdade — validação pelos schemas
abaixo, erros traduzidos para o envelope padronizado
(`backend/app/erros.py`), sentimento e evidências (B02), churn, oportunidades,
produtos e concorrentes (B03), e a composição de tudo isso, incluindo
`recomendacoes` derivadas e a renumeração de IDs de evidência
(`backend/app/services/analise.py`, `backend/app/api/analises.py`). Ver
`backend/README.md`, seção "Rota de análise (B04)", para o comportamento e
os limites da composição. Verificado com servidor real (`uvicorn`) e testes
HTTP (`backend/tests/test_analises_rota.py`), não só `TestClient`. **O que
ainda não existe:** persistência (B05) e o restante do fluxo de áudio.
Os exemplos deste documento continuam ilustrando o contrato — foram gerados
com as classes Pydantic (`model_dump_json()`), não por uma chamada real à
API; um exemplo real da rota está em `backend/README.md`.

## Rota

`POST /api/analises/texto` — implementada em B04 (`backend/app/api/analises.py`),
sobre a composição dos serviços de B02 e B03 (`backend/app/services/analise.py`).
Corpo: `AnaliseTextoRequest`; resposta 200: `AnaliseTextoResponse`; resposta
422: `ErroResposta` — os três anunciados assim no OpenAPI (`/openapi.json`,
`/docs`), não só devolvidos.

## Entrada — `AnaliseTextoRequest`

| Campo | Tipo | Obrigatório | Limites |
|---|---|---|---|
| `titulo` | string | sim | 1–200 caracteres; espaços nas pontas são removidos antes de contar o tamanho |
| `empresa` | string | sim | 1–200 caracteres; mesma remoção de espaços nas pontas |
| `vinculo` | enum | sim | `cliente`, `prospect` ou `nao_informado` |
| `transcricao` | string | sim | mínimo 1 caractere após remover espaços nas pontas; sem limite máximo definido nesta etapa |

Uma string só com espaços (`"   "`) é tratada como vazia nos três campos de
texto — antes, apenas `min_length=1` deixava esse caso passar (limitação
registrada no README de B01 e corrigida nesta revisão).

## Saída — `AnaliseTextoResponse`

| Campo | Tipo | Observação |
|---|---|---|
| `transcricao` | string | eco da transcrição recebida |
| `sentimento` | enum | `positivo`, `neutro`, `negativo` ou `informacao_insuficiente` |
| `churn` | objeto | `situacao` (enum abaixo) + `evidencias` (lista de IDs) |
| `oportunidades` | lista | cada item: `descricao` + `evidencias` |
| `produtos` | lista de strings | vazia quando nenhum foi identificado |
| `concorrentes` | lista de strings | menção isolada não implica intenção de troca (regra aplicada em B03, não no schema) |
| `evidencias` | lista de objetos | ver seção seguinte |
| `recomendacoes` | lista | cada item: `texto` + `evidencias` |
| `metodo` | string | ex.: `"regras"` |
| `versao_analise` | string | versão do método usado |

`churn.situacao`: `sinal_detectado`, `sem_sinal_detectado`, `nao_aplicavel`
ou `informacao_insuficiente`. `sem_sinal_detectado` não deve ser lido como
baixo risco confirmado — é a ausência de sinal, não a confirmação de que não
há risco.

## Localização de evidências

Cada `Evidencia` tem `id`, `trecho`, `inicio` e `fim`. `inicio`/`fim` são
posições em **caracteres** (índices Python de `str`, não bytes) no campo
`transcricao` **da resposta**, com `fim` exclusivo:
`resposta.transcricao[inicio:fim] == trecho`. A base é o texto ecoado, não
o texto bruto enviado: a entrada remove espaços nas pontas antes de validar,
então um envio com espaço inicial tem os índices deslocados em relação ao
que o cliente digitou — por isso a interface deve localizar evidências no
`transcricao` devolvido. Essa convenção permite localizar um trecho mesmo
quando o mesmo texto aparece mais de uma vez na transcrição, porque cada
evidência aponta para uma posição específica, não só para um texto que pode
se repetir. Timestamps de áudio não fazem parte deste schema porque só
existem quando fornecidos pelo transcritor, a partir da etapa 4;
`inicio`/`fim` continuam sendo posições no texto, não no tempo do áudio.

O schema **não** confere `transcricao[inicio:fim] == trecho` — só que
`fim > inicio` (ver seção seguinte). Quem gera as evidências (B02) é
responsável por produzir índices corretos; os exemplos deste documento
foram conferidos manualmente com esse recorte (ver evento C01-03 no
registro).

## Consistência aplicada pelo schema

Validado por `AnaliseTextoResponse` e `Evidencia`, sem depender de uma rota:

- `fim` maior que `inicio` em cada evidência.
- IDs de evidência únicos dentro de `evidencias`.
- Todo ID citado em `churn.evidencias`, `oportunidades[].evidencias` ou
  `recomendacoes[].evidencias` precisa existir em `evidencias`.

## Regras de negócio que o schema não impõe

Ficam para os serviços de análise, não para a validação de dados:

- **Prospect recebe `churn.situacao = nao_aplicavel`.** O schema não pode
  impor isso porque `vinculo` está em `AnaliseTextoRequest` e `churn` está
  em `AnaliseTextoResponse` — são validados em separado. Cabe a B03 aplicar
  essa regra antes de montar a resposta.
- Risco e oportunidade podem coexistir (ver exemplo 1 abaixo) — o schema
  permite os dois simultaneamente, sem forçar nenhuma combinação.
- Distinguir "satisfeito" de "insatisfeito" sem colisão, e "ausência de
  sinal" de "informação insuficiente" — são decisões da análise (B02/B03),
  não do formato de dados.

## Erros HTTP

Envelope padrão de `POST /api/analises/texto` (e de qualquer rota futura que
aceite `AnaliseTextoRequest`): `{"erro": {"codigo": "...", "mensagem":
"..."}}`, sempre HTTP 422 para erro de validação do corpo. Implementado em
`backend/app/erros.py` (`registrar_manipuladores_erro`, chamado por
`criar_app`) e declarado no OpenAPI da rota como `ErroResposta` (revisão
B04-R01 — antes o OpenAPI anunciava o `HTTPValidationError` padrão do
FastAPI, que não é o formato devolvido).

| Código | Quando |
|---|---|
| `TITULO_OBRIGATORIO` | `titulo` ausente, vazio ou só espaços |
| `TITULO_INVALIDO` | `titulo` com mais de 200 caracteres |
| `EMPRESA_OBRIGATORIA` | `empresa` ausente, vazia ou só espaços |
| `EMPRESA_INVALIDA` | `empresa` com mais de 200 caracteres |
| `TRANSCRICAO_VAZIA` | `transcricao` ausente, vazia ou só espaços |
| `VINCULO_INVALIDO` | `vinculo` ausente ou fora de `cliente`/`prospect`/`nao_informado` |
| `DADOS_INVALIDOS` | qualquer outro erro de validação não mapeado acima: tipo de campo incorreto (ex.: `"titulo": 1`, `null`, lista) → mensagem `"Campo inválido: <campo>."`; JSON malformado ou corpo que não é objeto → mensagem genérica `"Confira os dados enviados e tente novamente."` |

Números, `null`, listas e objetos enviados num campo de texto **não** são
convertidos para string: caem em `DADOS_INVALIDOS`, nunca em 500.

A API devolve um único erro por resposta — o primeiro encontrado pela
validação do FastAPI, na ordem dos campos do schema — mesmo quando há mais
de um campo inválido no mesmo envio.

## Exemplos

### 1. Cliente com risco e oportunidade coexistindo

Requisição:

```json
{
  "titulo": "Acompanhamento comercial",
  "empresa": "Empresa Exemplo",
  "vinculo": "cliente",
  "transcricao": "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."
}
```

Resposta:

```json
{
  "transcricao": "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.",
  "sentimento": "negativo",
  "churn": {
    "situacao": "sinal_detectado",
    "evidencias": ["e1"]
  },
  "oportunidades": [
    {"descricao": "Interesse em conhecer o Fluig", "evidencias": ["e2"]}
  ],
  "produtos": ["Fluig"],
  "concorrentes": [],
  "evidencias": [
    {"id": "e1", "trecho": "Estamos insatisfeitos com o suporte.", "inicio": 0, "fim": 36},
    {"id": "e2", "trecho": "Queremos conhecer o Fluig.", "inicio": 37, "fim": 63}
  ],
  "recomendacoes": [
    {"texto": "Investigar a insatisfação com o suporte.", "evidencias": ["e1"]},
    {"texto": "Oferecer uma apresentação do Fluig.", "evidencias": ["e2"]}
  ],
  "metodo": "regras",
  "versao_analise": "0.1"
}
```

### 2. Prospect — churn não aplicável, com oportunidade

Requisição:

```json
{
  "titulo": "Primeira reunião comercial",
  "empresa": "Prospect Exemplo LTDA",
  "vinculo": "prospect",
  "transcricao": "Vocês trabalham com integração via API? Hoje usamos uma planilha manual."
}
```

Resposta:

```json
{
  "transcricao": "Vocês trabalham com integração via API? Hoje usamos uma planilha manual.",
  "sentimento": "neutro",
  "churn": {
    "situacao": "nao_aplicavel",
    "evidencias": []
  },
  "oportunidades": [
    {"descricao": "Interesse em integração via API", "evidencias": ["e1"]}
  ],
  "produtos": [],
  "concorrentes": [],
  "evidencias": [
    {"id": "e1", "trecho": "Vocês trabalham com integração via API?", "inicio": 0, "fim": 39}
  ],
  "recomendacoes": [
    {"texto": "Apresentar a documentação de integração via API.", "evidencias": ["e1"]}
  ],
  "metodo": "regras",
  "versao_analise": "0.1"
}
```

Mesmo sendo prospect (sem contrato para cancelar), a oportunidade comercial
continua sendo reportada — `nao_aplicavel` é sobre `churn`, não sobre o
restante da análise.

### 3. Informação insuficiente

Requisição:

```json
{
  "titulo": "Reunião de alinhamento",
  "empresa": "Empresa Exemplo",
  "vinculo": "cliente",
  "transcricao": "Bom dia a todos. Vamos seguir a pauta de hoje."
}
```

Resposta:

```json
{
  "transcricao": "Bom dia a todos. Vamos seguir a pauta de hoje.",
  "sentimento": "informacao_insuficiente",
  "churn": {
    "situacao": "informacao_insuficiente",
    "evidencias": []
  },
  "oportunidades": [],
  "produtos": [],
  "concorrentes": [],
  "evidencias": [],
  "recomendacoes": [],
  "metodo": "regras",
  "versao_analise": "0.1"
}
```

Sem sinal na transcrição, as listas ficam vazias — o contrato não cria um
item fictício para preencher o card, conforme o plano.

### 4. Erro de validação

Requisição com `transcricao` vazia; resposta HTTP 422:

```json
{
  "erro": {
    "codigo": "TRANSCRICAO_VAZIA",
    "mensagem": "Informe a transcrição para continuar."
  }
}
```

## Em aberto para outras etapas

- Persistência de reuniões, transcrições e resultados (B05) e o restante do
  fluxo de áudio (etapa 4) — não são tratados aqui.
- Limite máximo de tamanho de `transcricao` — nenhum foi definido nesta
  etapa; se necessário, é decisão de B04 ou de infraestrutura.
- Contrato de áudio e processamento (C02, etapa 4) — não é tratado aqui.
