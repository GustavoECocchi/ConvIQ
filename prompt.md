# Revisão e correção de B04 — endpoint de análise — Claude Opus

Você revisará e corrigirá B04 do ConvIQ. Examine a entrega completa do
Sonnet, confirme os achados do Codex antes de corrigir e devolva para a
verificação final. Não inicie outra entrega nem declare aprovação final.

## Leitura e versão a revisar

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` (4.4, 5, 6,
8), índice/fichas B03 e B04 em `REGISTRO_TRABALHO.md`, critérios do plano,
`docs/contratos/analise-texto.md` e `backend/README.md`.

Relato do Sonnet: ficha B04, evento B04-01 e cópia preservada em
`docs/revisoes/RELATORIO_SONNET_B03_B04_2026-09-18.md`. Essa cópia descreve
a situação antes desta verificação. Resultados atuais: DOC01-10 (retomada),
B03-04 (aceite técnico de B03) e B04-02 (análise inicial e este prompt).

- Pasta: `/home/gustavoecocchi/Documents/CONVIQ`.
- Branch: `feat/b01-fundacao-api`; base local: `master`.
- HEAD/base: `3c52ea3ed0d3c3d38de5b9adf2a4a4ff320a1842`. Esse commit
  não contém B01–B04: tudo continua na pasta de trabalho, sem commit;
  índice vazio. Há 31 arquivos backend não rastreados.
- Versão examinada: 33 arquivos (backend, contrato, `.gitignore`) em
  `docs/revisoes/2026-09-18-verificacao-b03-b04.sha256`.
  Confira na raiz com `sha256sum -c` nesse arquivo. Preserve-o como
  referência de entrada; registre hashes da versão corrigida separadamente.
  O manifesto antigo de B01–B03 é histórico, não identifica B04.
- Destino de integração/principal/PR remoto atuais: `NAO_VERIFICADO`;
  servidor não consultado. Não use `origin/main` local como comprovação.
- B01/C01/B02 já tinham aceite técnico local; B03 foi verificado e aprovado
  tecnicamente em B03-04. Nenhuma dessas entregas foi commitada/integrada.
  B04 está `EM_REVISAO`, execução do Sonnet finalizada, correções pendentes.

Confira raiz, branch, HEAD/base, status com arquivos não rastreados, diff
e índice. Registre divergências antes de editar; preserve mudanças
preexistentes. A organização de branches/commits e a integração das
dependências continuam pendentes para a coordenação.

## Objetivo, critérios e escopo

Plano B04: “Recomendações derivadas dos sinais, composição do resultado e
`POST /api/analises/texto`”. Depende de B03. Critério: “Responde conforme
C01, com método/versão e erros padronizados; testes HTTP cobrem entrada
válida e inválida.”

Arquivos principais:

- `backend/app/services/analise.py` e `backend/tests/test_analise.py`.
- `backend/app/api/analises.py`, `backend/tests/test_analises_rota.py` e
  registro da rota em `backend/app/main.py`.
- Schemas, `backend/app/erros.py`, serviços B02/B03 relacionados, README e
  contrato C01. Leia-os para verificar integração, sem ampliar a entrega.

Preserve prospect → `nao_aplicavel`, concorrente isolado sem inferir troca,
coexistência de risco/oportunidade, distinção entre informação insuficiente
e ausência de sinal. Recomendações precisam ser sugestões sustentadas pelas
evidências. Os recortes são relativos à transcrição ecoada após strip, em
caracteres Python, com fim exclusivo; não invente horários ou falantes.

Fora desta rodada: frontend, persistência, áudio, LLM/treinamento, ampliação
geral dos léxicos/negação, deduplicação obrigatória de trechos, mudança de
contrato/enums ou dependências sem necessidade demonstrada. Se uma mudança
afetar escopo/contrato de outras entregas, devolva à coordenação.

## Relato e verificações do Codex

O Sonnet entregou a composição B02+B03, ordenação/renumeração única das
evidências, remapeamento das referências e recomendações (uma para risco,
uma por oportunidade). A rota chama esse serviço e reaproveita o handler
C01. Método/versão são `regras`/`0.1`; análise sem persistência.

O Codex verificou nesta versão:

- **99 testes passaram**, 2 avisos conhecidos de `httpx`/`anyio`, 0,29 s.
  Executados fora do sandbox devido ao bloqueio de TestClient já observado
  na sessão anterior; não houve falha da aplicação nessa execução.
- **B03-R01 resolvido:** código e testes iguais aos hashes finais do Opus.
  Churn dos três exemplos do contrato confere com B03. Saudação →
  insuficiente para cliente/vínculo desconhecido; conteúdo comercial sem
  risco → sem sinal; prospect mantém não aplicável; risco explícito e
  oportunidade continuam independentes.
- Sete blocos JSON de C01 válidos, round-trip sem diferenças e recortes
  corretos; 18 cenários de composição (6 textos × 3 vínculos) verificaram
  IDs únicos/ordenados, recortes, referências corretas por origem e
  recomendações ligadas ao sinal correto, inclusive repetição/emoji/strip.
- Uvicorn real + curl: os três pedidos do contrato responderam 200 e
  validaram no schema. Exemplo 1: negativo, risco, 3 evidências e 2
  recomendações; exemplo 2: sentimento insuficiente, churn não aplicável,
  sem oportunidade/recomendação; exemplo 3: insuficiente e listas vazias.
  O exemplo 2 ilustra oportunidade com “integração via API”, mas o léxico
  atual não a detecta; limitação já relatada/aceita em B03, não igualdade
  entre todos os campos do exemplo ilustrativo e a saída calculada.
- Servidor real: saúde 200; 11 entradas inválidas (incluindo os sete códigos
  C01, tipos incorretos, corpo lista e JSON malformado) → 422 no envelope
  correto. Processo iniciado para a revisão foi encerrado. Prefixo `/v1`
  registrado para saúde e análise em instância configurada separadamente.
- O handler existente atende os erros exercitados. Não há motivo demonstrado
  para reescrevê-lo; há divergência na declaração OpenAPI da rota (R01).

**Evidências repetidas do mesmo trecho não são impeditivo.** Exemplo 1:
`e1` e `e2` apontam para “insatisfeitos” em `[8:21]`; churn referencia `e2`;
`e3` aponta para “conhecer” em `[46:54]`; oportunidade referencia `e3`;
as recomendações referenciam `e2` e `e3`, respectivamente. IDs únicos,
recortes corretos e relações preservadas satisfazem C01. Mesclar trechos é
melhoria opcional de apresentação, não exigência desta revisão. A resposta
não possui campo explícito de origem da evidência; evite prometer isso.

## B04-R01 — OpenAPI anuncia o schema errado para HTTP 422

**Impeditivo, prioridade média.** Local: `backend/app/api/analises.py:12`.
O decorador declara somente `response_model=AnaliseTextoResponse`.

Reprodução (em `backend/`):

```python
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import criar_app

app = criar_app(Settings(_env_file=None))
with TestClient(app) as c:
    spec = c.get('/openapi.json').json()
    schema = spec['paths']['/api/analises/texto']['post']['responses']['422']['content']['application/json']['schema']
    print(schema)
    r = c.post('/api/analises/texto', json={
        'titulo': 'x', 'empresa': 'x', 'vinculo': 'cliente', 'transcricao': ''
    })
    print(r.status_code, r.json())
```

Observado: OpenAPI → `#/components/schemas/HTTPValidationError`, formato
padrão com `detail`; resposta real → 422
`{"erro":{"codigo":"TRANSCRICAO_VAZIA","mensagem":"Informe a transcrição para continuar."}}`.
A divergência também foi reproduzida via servidor real em `/openapi.json`.

Esperado: documentar o 422 com o schema `ErroResposta` de C01. Esse ajuste
por rota já havia sido reservado para B04 em C01-03/C01-04. Consumidores
baseados em `/docs` ou geração de tipos recebem o formato errado atualmente.
O teste existente só confere os caminhos do OpenAPI, não o contrato do erro.

Confirme e declare o modelo de erro no `responses` da rota (ou mecanismo
mínimo equivalente), preservando o handler e a resposta real. Acrescente
verificação do schema 422 anunciado e do envelope real; mantenha também o
200 com `AnaliseTextoResponse`. Rejeitar entrada inválida deve continuar
422, não exceção 500. Não redefina o contrato para acomodar a documentação.

## B04-R02 — documentação ainda afirma ausência da rota

**Baixa prioridade, não impeditivo funcional.** Locais atuais:
`backend/README.md:116`, `:167`, `:279` e `:295`;
`docs/contratos/analise-texto.md:24` e `:108`.

Apesar da introdução e da seção B04 corretas, as seções B02/B03 dizem que
nenhuma rota chama os serviços; “Limites conhecidos” diz que nenhuma rota
usa os schemas e trata a aplicação da regra de prospect por B04 como
pendente. O contrato ainda usa “Rota prevista” e “quando existir”.

Atualize essas referências para a rota/composição já existentes, mantendo
as limitações reais e distinguindo o serviço interno da rota que o consome.
Não reescreva o histórico do registro nem prometa integração/publicação.
Revise também a frase de que a resposta “preserva sua origem/propósito”:
ela preserva IDs/referências, mas não expõe um campo explícito de origem.
Não é necessário acrescentar campo ao contrato para ajustar essa explicação.

## Validação e devolução

Faça revisão própria do conjunto: vínculos, erros do handler, método/versão,
renumeração e referências semânticas de churn/oportunidades/recomendações,
recortes e repetições. Corrija problemas comprovados dentro do escopo;
justifique discordâncias com evidência. Não crie alterações artificiais.

Execute os testes pertinentes e a suíte completa em `backend/`:
`.venv/bin/python -m pytest -q`. Verifique o 422 anunciado no OpenAPI e o
real após R01. Se tocar no contrato, revalide os exemplos/recortes. Registre
quais verificações usaram TestClient, servidor real ou somente função/schema.
No sandbox, sockets podem ser bloqueados; informe a limitação e use o
fluxo de permissão disponível, sem declarar sucesso de teste não executado.

Autorizado: revisão, correções, testes e documentação locais na branch
atual. Sem autorização de commit, push, abertura de PR, troca de branch ou
merge nesta passagem. Preserve os manifestos e relatórios de entrada.

Antes de devolver, atualize índice/ficha B04 e acrescente seu evento em
`REGISTRO_TRABALHO.md`, preservando eventos anteriores. Responda R01/R02;
liste arquivos, validações, limitações, novos achados e hashes da versão
final. Separe execução, revisão, Git da entrega e do registro, publicação,
PR remoto e integração. Use o relatório da seção 8 da governança.

Aguarde a verificação final do Codex. Não declare B04 aprovado/integrado.
B05 não é o próximo PR elegível: depende de C02, ainda inexistente; C02
depende de F06 e das decisões de transcrição/orçamento. A próxima etapa
após esta revisão é a verificação final e a coordenação da integração por
texto com a frente frontend, respeitando as dependências do plano.
