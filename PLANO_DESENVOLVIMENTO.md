# ConvIQ — Stack e etapas de desenvolvimento

Atualizado em: 07/10/2026.

## Estado e objetivo

Python no backend e React no frontend foram confirmados pelo usuário. Em 18/09/2026, o usuário definiu transcrição somente gratuita, permitindo Whisper, e dispensou persistência na primeira apresentação, desejando-a depois. Acesso por link no navegador é o objetivo; execução/hospedagem ficam **A_RESOLVER**. Whisper aberto em máquina disponível é a primeira candidata técnica, sujeita ao ensaio B07-A; não há escolha de API paga ou garantia de hospedagem gratuita.

Objetivo: uma demonstração em que o usuário envia o áudio de uma reunião fictícia, acompanha o processamento e consulta a transcrição e um card de inteligência com evidências.

**Prioridade reafirmada pelo usuário em 17/09/2026:** concluir primeiro o
ConvIQ que analisa reuniões. Contas individuais, grupos, personalização por
equipe, atribuição de tarefas e lembretes ficam como evolução futura, descrita
adiante. Essa evolução não amplia os critérios dos PRs atuais.

Este documento será compartilhado com o colega de equipe responsável pelo frontend. Ele reúne a visão geral e um guia de execução para essa frente, incluindo o que pode avançar antes de a API estar disponível.

Existe neste repositório o experimento acadêmico `conviq_datascience.py`. Após a perda da primeira base local, B01–B04/C01 foram implementados e aprovados tecnicamente: saúde, contrato de texto, sentimento, sinais comerciais e `POST /api/analises/texto`. Estão no commit agregado `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`. B11/B12 foram aprovados e integrados pelo PR #1 na branch padrão `feat/b01-fundacao-api`, merge `e31e6ba81692c61e0b0615d349972e2b3a0c459d`, verificado em 07/10. Áudio e persistência ainda não existem; F01 e F02-A do frontend estão integrados, mas a jornada de texto F06 ainda não foi entregue. Os materiais Java e Oracle citados no contexto não estão nesta pasta.

Em 19/09/2026, B07-A tem entrega parcial do experimento isolado de Whisper
na branch `spike/b07-a-viabilidade-whisper`, sobre o mesmo commit, ainda sem
commit próprio. Falta validação com fala real; não há áudio integrado à API.
O usuário também solicitou refinamento das capacidades já existentes:
B11–B21 abaixo melhoram a análise por texto, aproveitável pelo áudio depois.
Em 07/10, B07-A continua parcial, com P01 (fala real) pendente; B11/B12
estão integrados, e B13 é o próximo refinamento preparado para execução.

## Stack proposta

| Parte | Tecnologia | Responsabilidade |
|---|---|---|
| Backend | Python + FastAPI | API HTTP, validação das entradas e coordenação do processamento |
| Contratos | Pydantic e OpenAPI do FastAPI | Definir os dados recebidos e devolvidos pela API |
| Servidor local | Uvicorn | Executar a API durante o desenvolvimento |
| Análise | Serviço Python separado das rotas | Extrair sentimento, sinais, produtos, concorrentes e evidências |
| Frontend | React + TypeScript + Vite | Construir a aplicação no navegador e verificar tipos no desenvolvimento |
| Estilos | CSS com variáveis e componentes reutilizáveis | Manter consistência visual e adaptação a telas menores |
| Comunicação | HTTP/JSON com `fetch`; multipart para áudio | Conectar interface e backend |
| Estado da demonstração, na etapa 4 | Memória e arquivos de áudio temporários | Consultar tentativas e resultados enquanto o backend estiver ativo |
| Persistência posterior, na etapa 5 | SQLite + SQLAlchemy; Alembic como proposta a confirmar | Guardar reuniões, transcrições, resultados e estados entre reinícios |
| Testes | pytest no backend; Vitest e React Testing Library no frontend | Verificar regras, contratos e interações relevantes |
| Validação integrada | Playwright, na etapa final | Exercitar a jornada pelo navegador |
| Transcrição | Adaptador para Whisper aberto, após viabilidade B07-A | Converter áudio em texto usando somente solução gratuita |

A escolha de FastAPI aproveita Python no processamento e oferece contratos e documentação da API. React com Vite atende à proposta de uma interface que consome essa API. TypeScript ajuda a explicitar os dados usados pelos componentes.

SQLite é uma proposta para a fase posterior de persistência, não um requisito da demonstração. Antes de escolher o banco publicado, verificar disco e concorrência; a infraestrutura pode exigir outra solução. Não introduzir Oracle sem exigência confirmada. Na demonstração sem banco, reiniciar o backend perde estados/resultados e exige novo envio do áudio.

O experimento acadêmico permanece como referência. Extrair e revisar funções úteis em um serviço próprio, evitando executar treinamento, downloads ou gráficos ao iniciar a API. A adoção do classificador supervisionado depende de avaliação separada; a primeira entrega pode usar regras identificadas como tal.

## Estrutura prevista

```text
CONVIQ/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/           # Rotas HTTP
│   │   ├── schemas/       # Entradas e saídas
│   │   ├── services/      # Análise e processamento
│   │   ├── integrations/ # Transcrição
│   │   └── db/            # Persistência posterior, etapa 5
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/      # Cliente HTTP
│   │   ├── types/
│   │   └── styles/
│   └── package.json
├── conviq_datascience.py
└── PLANO_DESENVOLVIMENTO.md
```

Criar as pastas conforme cada etapa precisar delas. Fixar versões compatíveis e registrar dependências na implementação inicial.

## Etapas de desenvolvimento

As etapas abaixo descrevem a sequência de entregas, incluindo as já concluídas tecnicamente no backend (B01–B04/C01). O colega de equipe é responsável pelo frontend; Claude executa os PRs de backend e Codex coordena/verifica. O responsável humano pelo backend e as datas ainda precisam ser registrados. As duas frentes devem alinhar o contrato antes da integração.

### 1. Fundação e contrato de dados

- **Python:** criar o projeto FastAPI, configuração por ambiente, endpoint de saúde e schemas iniciais de reunião e análise.
- **React:** criar o projeto com TypeScript e Vite, estrutura visual básica e cliente HTTP configurável.
- **Em conjunto:** definir campos, valores permitidos, erros e um exemplo fictício de resposta para desenvolver a interface.
- **Entrega verificável:** API e frontend iniciam localmente; o frontend consegue consultar a saúde da API; instruções de execução estão registradas.

### 2. Análise real de uma transcrição em texto

- **Python:** extrair a lógica útil do experimento para um serviço testável; implementar `POST /api/analises/texto`; retornar sinais associados a trechos da entrada.
- **React:** construir o formulário com nome da reunião, empresa, vínculo comercial e transcrição; implementar validação, carregamento e erro.
- **Regras essenciais:** distinguir cliente existente de prospect; corrigir a colisão entre “satisfeito” e “insatisfeito”; tratar menção a concorrente como menção, sem concluir automaticamente que existe intenção de troca.
- **Entrega verificável:** uma transcrição enviada pela interface gera análise derivada desse texto. Os testes cobrem prospect, insatisfação e entrada sem evidência suficiente.

### 3. Card de inteligência e evidências

- **Python:** consolidar formato de sentimento, churn, oportunidades, produtos, concorrentes e recomendações; informar método e versão da análise.
- **React:** exibir o card, permitir consultar cada evidência na transcrição e tratar ausência de sinais ou informação insuficiente.
- **Em conjunto:** verificar casos fictícios de risco de cancelamento, oportunidade comercial e conversa sem sinais suficientes. Risco e oportunidade podem coexistir quando houver evidências para ambos.
- **Entrega verificável:** o usuário consegue entender cada sinal e localizar o trecho que o sustenta; recomendações aparecem como sugestões.

Ao concluir a etapa 3, teremos a primeira versão utilizável: texto → análise → card.

### 4. Áudio, transcrição e estado do processamento

- **Pré-requisito específico:** verificar Whisper gratuito no ambiente disponível, medir recursos e definir limites de arquivo. Hospedagem permanece a resolver, sem bloquear o ensaio local.
- **Python:** implementar upload validado, adaptador de transcrição e estado em memória; encadear transcrição e o mesmo serviço de análise usado no texto. Guardar áudio temporariamente conforme retenção explícita.
- **Python:** oferecer consulta de estado e resultado; registrar falhas e permitir nova tentativa sem confundir tentativas distintas. Definir o executor de tarefas conforme o transcritor e o ambiente escolhidos.
- **React:** adicionar seleção de áudio, envio, acompanhamento das etapas e recuperação de falhas. Consultar periodicamente o estado usando o identificador devolvido pela API.
- **Entrega verificável:** um áudio fictício percorre transcrição real e análise até o card; arquivos inválidos, falhas e timeout produzem mensagens úteis. Após reinício, registros em memória deixam de existir e a interface encerra a consulta e orienta novo envio; recuperação durável fica para B09-C, após persistência.

Estados previstos: recebido → transcrevendo → analisando → concluído, com falha ou interrupção quando aplicável. Mostrar etapas reais; percentual somente quando houver medição disponível.

### 5. Consulta de resultados salvos

- **Python:** implementar persistência em B05-A/B, recuperação após reinício em B09-C e depois listagem em B10, com data, estado e resultado.
- **React:** criar lista de reuniões e navegação para os detalhes, permitindo reabrir uma análise.
- **Entrega verificável:** após recarregar a página e reiniciar o backend, os resultados concluídos continuam disponíveis.

Esta etapa fica depois da primeira apresentação conforme a decisão do usuário de 18/09/2026. Banco, recuperação durável e histórico não bloqueiam a demonstração de áudio.

### 6. Validação e preparação da demonstração

- **Python:** revisar limites de entrada, tratamento de falhas, configuração de credenciais e limpeza dos áudios temporários.
- **React:** revisar legibilidade, navegação por teclado, layout responsivo e estados de carregamento, vazio e erro.
- **Em conjunto:** testar a jornada completa com áudio fictício, documentar execução e preparar um exemplo pré-processado explicitamente identificado para apoio à apresentação.
- **Entrega verificável:** a jornada principal funciona no ambiente escolhido para a apresentação, com resultados derivados da entrada e instruções reproduzíveis.

Hospedagem por link depende da escolha de infraestrutura. Publicação e contratação de serviços serão tratadas quando houver uma entrega pronta para revisão e autorização correspondente.

## Divisão em PRs pequenos

Os identificadores abaixo são rótulos de planejamento, não números de PRs abertos no GitHub. Nenhum PR foi aberto nesta revisão. `B` identifica backend, `F` frontend, `C` contrato compartilhado e `I` validação integrada.

Cada PR deve entregar um comportamento ou artefato revisável, incluir sua validação e manter a aplicação utilizável no estágio atual. As dependências indicam o que precisa estar integrado antes de concluir o PR; rascunhos e trabalho com exemplos podem começar antes. Não há limite artificial de linhas: se uma entrega exigir revisão de assuntos independentes, dividir novamente.

Codex e Claude registram cada atuação e o estado de cada PR em [REGISTRO_TRABALHO.md](REGISTRO_TRABALHO.md), conforme [SISTEMA_GOVERNANCIA_CONVIQ.md](SISTEMA_GOVERNANCIA_CONVIQ.md). Entrega finalizada, aprovação, commit na branch de trabalho, push e integração na principal são informações separadas; consultar a ficha e o Git antes de retomar.

**Responsáveis:** os PRs `F` foram inicialmente atribuídos ao colega do frontend; Claude Sonnet executa os PRs `B`, Codex coordena/verifica e Opus revisa. O responsável humano pelo backend permanece a registrar. Nos PRs `C` e `I`, definir um autor e solicitar participação da outra frente quando houver integração.

Em 09/10/2026, o usuário confirmou que o colega ainda não iniciou o frontend e atribuiu o início de F01 ao Codex neste repositório. A execução dos próximos cartões `F` será definida conforme o andamento da frente; essa atribuição não altera o escopo de cada cartão.

### Primeira entrega: texto → análise → card

| PR | Escopo e arquivos principais | Depende de | Critério de aceite |
|---|---|---|---|
| B01 — Fundação da API | Criar o projeto FastAPI em `backend/`, configuração por ambiente, endpoint de saúde, schemas iniciais, instruções de execução e `.gitignore` | — | Inicialização reproduzível, resposta de saúde e teste de saúde passando; registrar limites dos schemas iniciais |
| F01 — Fundação React | `frontend/`: React, TypeScript, Vite, estilos básicos e instruções | — | Página inicial abre; build e verificação de tipos passam |
| C01 — Contrato de análise por texto | Revisar `backend/app/schemas/` e registrar contrato e exemplos em `docs/contratos/analise-texto.md` | B01 | Campos, enums, limites, erros HTTP e localização de evidências definidos; exemplos válidos, incluindo prospect e falta de informação |
| F02 — Tipos e cliente da API | `frontend/src/types/`, `services/api.ts` e exemplos fictícios | F01, C01 | Tipos seguem o contrato; URL configurável; cliente trata erro HTTP e de rede; exemplos identificados |
| B02 — Sentimento e evidências | `backend/app/services/` e testes de análise textual | C01 | Extrai trechos do texto original e avalia sentimento; cobre “insatisfeito”, ausência de evidência e localização de trechos repetidos |
| F03 — Formulário de transcrição | `MeetingForm`, campos e estados de envio usando exemplos | F02 | Valida entrada, impede envio duplicado e preserva formulário após erro |
| B03 — Sinais comerciais | Serviço de churn, oportunidades, produtos e concorrentes com testes | B02 | Prospect recebe churn não aplicável; concorrente isolado não implica troca; risco e oportunidade podem coexistir |
| F04 — Card de resultado | `IntelligenceCard` e listas de sinais usando exemplos | F02 | Exibe todos os campos e estados de informação insuficiente, sem calcular classificações no navegador |
| B04 — Endpoint de análise | Recomendações derivadas dos sinais, composição do resultado e `POST /api/analises/texto` | B03 | Responde conforme C01, com método/versão e erros padronizados; testes HTTP cobrem entrada válida e inválida |
| F05 — Consulta de evidências | `EvidenceViewer` e `TranscriptViewer` | F04 | Sinal leva ao trecho correto, inclusive quando há texto repetido; interação utilizável por teclado |
| F06 — Integração real por texto | Conectar formulário, card e evidências ao backend | F03, F05, B04 | Uma transcrição digitada percorre a API real e gera o card; indisponibilidade e erro de validação são tratados |

B01–B04/C01 já têm aceite técnico; seus critérios acima permanecem como referência. Confirmar integração e base Git antes de abrir os próximos PRs. C01 é o contrato vigente para o frontend.

F03 e F04 podem avançar em paralelo ao serviço Python após F02. **O marco de primeira versão utilizável é F06**, sem depender de transcrição de áudio ou histórico.

Em 09/10/2026, F02–F06 foram subdivididos em PRs A/B no roteiro [Navegação do usuário](docs/planejamento/PRS_FRONTEND_NAVEGACAO.md). Os critérios desta tabela continuam válidos; o roteiro define rotas, estados, dependências e aceite de cada corte pequeno. F07–F11 permanecem no escopo original.

### Refinamento da análise existente — B11 a B21

Solicitado pelo usuário em 19/09/2026, após o panorama ANA02. Esses PRs
evoluem as limitações aceitas de B02–B04, mantendo a primeira versão de texto
como base. Não dependem de Whisper, persistência ou hospedagem. O roteiro
[Refinamento da análise](docs/planejamento/PRS_REFINAMENTO_ANALISE.md) contém
problemas reproduzidos, cartões completos, exclusões, exemplos e validação.

| Ordem sugerida | PR | Refinamento | Depende de |
|---|---|---|---|
| 1 | B11 | Negação simples no sentimento, com evidência do sentido completo | B04, C01 |
| 2 | B12 | Risco de cancelamento: negação e contexto da relação comercial | B11 |
| 3 | B13 | Oportunidade baseada em intenção, evitando menção ou interesse negado | B11 |
| 4 | B14 | Unicode/NFD com mapeamento correto para os trechos originais | B11, B12, B13 |
| 5 | B19 | Evidência única por intervalo, com referências preservadas | B14 |
| 6 | B15 | Vocabulário de sentimento ampliado com contraexemplos | B11 |
| 7 | B16 | Catálogo com contexto para marcas/siglas ambíguas | B04, C01 |
| 8 | B17 | Uma oportunidade por intenção local, sem duplicar palavras do mesmo pedido | B13 |
| 9 | B18 | Descrição ligada ao produto ou necessidade explícita | B16, B17 |
| 10 | B20 | Recomendações específicas, sustentadas e sem repetição | B12, B18, B19 |
| 11 | B21 | Avaliação pequena e reproduzível de ganhos e erros remanescentes | B15, B20 |

Prioridade inicial: B11–B14, seguidos de B19. Manter regras locais gratuitas,
formato C01 compatível e versionar mudanças observáveis da análise. Não
prometer compreensão geral, probabilidades calibradas ou ironia resolvida.
Cada PR terá testes próprios e revisão; B21 complementa, não adia, a validação.
Todos estão planejados, sem implementação/branch nova nesta preparação.

### Segunda entrega: áudio → transcrição → análise → card

| PR | Escopo e arquivos principais | Depende de | Critério de aceite |
|---|---|---|---|
| C02-A — Contrato técnico | `docs/contratos/audio.md`, schemas: limites, executor, estados, respostas e nova tentativa | B07-A, C01 | Contrato explícito para estado temporário, falhas, expiração, reinício e exemplos |
| C02-B — Alinhamento entre frentes | Conferência de exemplos e consumo após integração de texto | C02-A, F06 | Compatibilidade confirmada pelo responsável do frontend antes de concluir integração de áudio |
| B06-A/B — Recepção de áudio | Validação; depois recebimento e armazenamento temporário | A: C02-A; B: B06-A e B08-A | Validação efetiva e recebimento não deixam órfãos; sem dependência de banco |
| B07-A/B — Transcrição gratuita | A: viabilidade isolada; B: adaptador na aplicação | A: B04/C01 como referência; B: B07-A e C02-A | Áudio fictício transcrito realmente; erros tratados; simulação identificada |
| F07 — Seleção e envio de áudio | `AudioUpload` e cliente com exemplos | C02-B, F06 | Limites e rejeições tratados; resultados temporários claramente comunicados |
| B08-A/B/C — Processamento e consulta | A: repositório em memória; B: executor; C: rotas | A: C02-A; B: B04, B06-B, B07-B, B08-A; C: B08-B | Upload devolve IDs; etapas reais; consulta retorna resultado temporário ou falha |
| F08 — Acompanhamento real | `ProcessingStatus`, consulta periódica e resultado | F07, B08-C | Áudio chega ao card real; consulta para em estado final, ID perdido ou saída da tela |
| B09-A/B — Nova tentativa e limpeza | A: retry; B: expiração e limpeza | A: B08-C; B: B09-A | Timeout tratado, nova identidade por tentativa, retenção respeitada |
| F09 — Recuperação de falhas | Interface de erro, nova tentativa e reenvio | F08, B09-A/B | Falha explica próxima ação; após reinício/expiração solicita reenvio quando necessário |

Os cartões completos, branches propostas, exclusões e validações estão em
[PRs pequenos de áudio](docs/planejamento/PRS_BACKEND_AUDIO.md). Os sufixos
subdividem os IDs antigos. C02-A permite backend independente; a antiga
dependência de C02 em F06 fica em C02-B, preservando o acordo entre frentes
antes da integração de áudio. B06 entrega serviço interno; HTTP entra em B08-C.

**O marco da demonstração com áudio é F09**, com o fluxo de falha e recuperação também integrado.

### Histórico opcional e preparação da apresentação

| PR | Escopo e arquivos principais | Depende de | Critério de aceite |
|---|---|---|---|
| B05-A/B — Persistência posterior | A: banco/migração; B: repositório persistente | A: C02-A, B08-A e escolha de banco; B: B05-A, B09-B | Resultados e tentativas persistem após reabrir/reiniciar; fora da primeira demonstração |
| B09-C — Recuperação durável | Reconciliação de estados após queda/reinício | B05-B | Ativos interrompidos não ficam eternos; concluídos preservados |
| B10 — Listagem de reuniões | `GET /api/reunioes`, ordenação e limite de resultados | B09-C | Lista registros persistidos de modo previsível; detalhe continua disponível |
| F10 — Histórico | `MeetingList` e navegação para detalhes | F09, B10 | Reabre análises salvas após recarregar a página |
| F11 — Revisão visual e acessibilidade | Ajustes pontuais de layout, foco, teclado e mensagens | F09; F10 se incluído | Jornada utilizável em computador e tela menor; sem falhas de interação identificadas na revisão |
| I01-A — Ensaio real do backend | Áudio fictício → Whisper → API/análise, falhas e reenvio | B09-B | Transcrição real e evidências reproduzíveis no ambiente de desenvolvimento |
| I01 — Ensaio da demonstração | Jornada no navegador, instruções e exemplo de apoio identificado | F11, I01-A e ambiente definido em H01 | Jornada real validada no ambiente de apresentação; distinguir simulação, ensaio local e acesso por link |

B05-A/B, B09-C, B10 e F10 ficam posteriores à apresentação. H01 é a decisão
de execução/hospedagem **A_RESOLVER**, sem PR de implantação liberado. Problemas
independentes encontrados no ensaio devem gerar PRs de correção próprios.

### Como abrir e revisar cada PR

- Uma branch por PR, com nomes como `feat/b02-sentimento-evidencias` ou `feat/f03-formulario-transcricao`.
- Título com o identificador e a entrega concreta. Abrir a partir da branch principal atualizada após integrar as dependências; se houver PR dependente ainda aberto, informar a base e a ordem de integração.
- Descrição curta: comportamento entregue, dependências, validação executada e limitações restantes. Para mudanças visuais, incluir captura da tela quando possível.
- Backend altera principalmente `backend/`; frontend, `frontend/`. Mudanças em contrato e arquivos compartilhados devem ter um autor coordenando a edição.
- Testes relevantes acompanham o comportamento que verificam. A revisão visual final e I01 complementam essa validação.
- Integrar após revisão, verificações pertinentes e ausência de dependências pendentes. Registrar se o resultado foi verificado com exemplos, API real ou transcrição real.

**Encaminhamento vigente (09/10/2026):** F01 (PR #5), F02-A (PR #6) e F02-B (PR #7, merge bf7a1a1) estão integrados. F03-A foi entregue como diff local no worktree CONVIQ-f03a e segue EM_REVISAO após correção R01/R02 pelo Codex. B19 aprovado em B19-04 foi reaplicado, com diff técnico idêntico, na branch integrate/b19-evidencias sobre bf7a1a1; está publicado no PR #8 e aguarda integração. O [roteiro de frontend](docs/planejamento/PRS_FRONTEND_NAVEGACAO.md) define a jornada seguinte.
B07-A continua parcial por falta da amostra P01 de fala real, e sua instrução de retomada
permanece em `docs/planejamento/PROMPT_B07_A_VIABILIDADE_WHISPER.md`.
Confirmar F06 com a frente frontend para C02-B; conferir registro/Git antes
de iniciar, uma entrega por vez, preservando os trabalhos existentes.

## Guia de trabalho do responsável pelo frontend

### Limite de responsabilidade

O frontend recebe entradas, envia requisições e apresenta os resultados. A análise, a transcrição, as regras de churn e as credenciais de serviços ficam no backend. O React deve exibir a classificação recebida, sem recalculá-la no navegador.

Trabalhar principalmente em `frontend/`. Se uma necessidade da interface exigir mudanças na API, combinar o contrato com o responsável pelo backend antes de depender do novo campo ou endpoint.

### Telas e componentes previstos

| Tela ou área | Componentes sugeridos | Etapa |
|---|---|---|
| Nova análise | `MeetingForm`, campo de transcrição e botão de analisar | 2 |
| Resultado | `IntelligenceCard`, `SignalList`, `EvidenceViewer`, `TranscriptViewer` | 3 |
| Envio de áudio | `AudioUpload`, validação do arquivo e ação de envio | 4 |
| Acompanhamento | `ProcessingStatus`, mensagem de falha e nova tentativa | 4 |
| Reuniões salvas | `MeetingList` e acesso ao detalhe | 5, extensão proposta |

Nova análise e resultado podem começar na mesma página. Adicionar navegação entre páginas quando a listagem de reuniões entrar no escopo. Nomes dos componentes são sugestões de organização.

### Ordem de execução do frontend

1. Criar React com TypeScript e Vite, scripts de desenvolvimento/build e estilos básicos. Registrar como iniciar o projeto.
2. Definir os tipos do contrato e centralizar chamadas HTTP em `src/services/api.ts`.
3. Criar exemplos fictícios em `src/services/mocks/` para sucesso, ausência de evidência e falha. Usá-los para desenvolver o formulário e o card enquanto a API está pendente.
4. Implementar os estados inicial, enviando, sucesso e erro. Preservar os dados do formulário quando a requisição falhar e impedir envios duplicados enquanto estiver em andamento.
5. Conectar a análise por texto à API real e verificar os mesmos casos usados nos exemplos.
6. Implementar áudio e acompanhamento quando o contrato de processamento da etapa 4 estiver disponível. Parar a consulta periódica ao concluir, falhar, interromper ou sair da tela.
7. Implementar o histórico se incluído na entrega e validar a jornada completa com o backend.

Identificar o uso de dados fictícios durante o desenvolvimento. Uma tela preenchida por esses exemplos comprova a interface; a integração estará concluída somente após consumir a API real.

### Configuração para conectar à API

Proposta de configuração local, a adotar na etapa 1:

```dotenv
# frontend/.env.example
VITE_API_BASE_URL=http://localhost:8000/api
```

O cliente HTTP combina essa base com caminhos como `/analises/texto`. A frente de backend deve configurar o acesso da origem local do frontend, prevista como `http://localhost:5173`. Confirmar as portas ao iniciar os projetos.

O frontend precisa apenas da URL pública da API. Chaves do serviço de transcrição devem ser configuradas exclusivamente no backend.

### Critérios de entrega do frontend

- Formulário com rótulos claros, campos obrigatórios e indicação de vínculo comercial.
- Card legível com distinção entre sinal detectado, informação insuficiente e churn não aplicável.
- Evidências consultáveis na transcrição, sem inventar trechos, participantes ou horários.
- Estados de carregamento, vazio, erro de validação e indisponibilidade da API.
- Layout utilizável em computador e tela menor, com navegação por teclado.
- Build e verificação de tipos passando; testes das interações relevantes de envio, erro e consulta de evidências.
- Instruções de execução e indicação clara das partes integradas e das que ainda usam exemplos.

## Contrato inicial entre Python e React

**Situação:** `GET /api/health` e `POST /api/analises/texto` existem. O contrato
vigente de texto é [C01](docs/contratos/analise-texto.md), com schemas e exemplos
verificáveis. Áudio continua planejado em C02-A/B. Comunicar alterações de
formato compartilhado à outra frente antes da integração.

Campos de referência (consultar C01 para os detalhes já implementados):

- **Entrada por texto:** título da reunião, empresa, vínculo (`cliente`, `prospect` ou `nao_informado`) e transcrição.
- **Resultado:** sentimento, situação do risco de churn, oportunidades, produtos e concorrentes, evidências, recomendações, método e versão da análise.
- **Evidência:** trecho literal da transcrição e posição no texto original. Timestamps de áudio somente quando fornecidos pelo transcritor.
- **Churn:** `nao_aplicavel` para prospect; `informacao_insuficiente` quando não for possível avaliar. Ausência de sinais detectados não garante baixo risco real.
- **Processamento de áudio:** identificador, estado, erro quando houver e referência ao resultado quando concluído.

Rotas existentes nas etapas 1/2; propostas para as etapas 4/5:

| Etapa | Rota | Finalidade |
|---|---|---|
| 1 | `GET /api/health` | Verificar disponibilidade da API |
| 2 | `POST /api/analises/texto` | Analisar uma transcrição |
| 4 | `POST /api/reunioes/audio` | Receber áudio e devolver identificador de processamento |
| 4 | `GET /api/processamentos/{id}` | Consultar andamento e referência ao resultado |
| 4 | `GET /api/reunioes/{id}` | Recuperar transcrição e análise disponíveis na instância atual |
| 4 | `POST /api/processamentos/{id}/tentativas` | Criar nova tentativa elegível enquanto houver áudio |
| 5 | `GET /api/reunioes` | Listar reuniões salvas |

### Exemplo histórico para iniciar o formulário e o card

O exemplo abaixo é um rascunho histórico, não o contrato atual: não contém
todos os campos de C01 (como posições das evidências). Para implementar,
usar os exemplos completos em [C01](docs/contratos/analise-texto.md).

Entrada fictícia proposta para `POST /api/analises/texto`:

```json
{
  "titulo": "Acompanhamento comercial",
  "empresa": "Empresa Exemplo",
  "vinculo": "cliente",
  "transcricao": "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."
}
```

Resposta fictícia correspondente, destinada ao desenvolvimento da interface:

```json
{
  "transcricao": "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.",
  "sentimento": "negativo",
  "churn": {
    "situacao": "sinal_detectado",
    "evidencias": ["e1"]
  },
  "oportunidades": [
    {
      "descricao": "Interesse em conhecer o Fluig",
      "evidencias": ["e2"]
    }
  ],
  "produtos": ["Fluig"],
  "concorrentes": [],
  "evidencias": [
    {"id": "e1", "trecho": "Estamos insatisfeitos com o suporte."},
    {"id": "e2", "trecho": "Queremos conhecer o Fluig."}
  ],
  "recomendacoes": [
    {"texto": "Investigar a insatisfação com o suporte.", "evidencias": ["e1"]},
    {"texto": "Oferecer uma apresentação do Fluig.", "evidencias": ["e2"]}
  ],
  "metodo": "regras",
  "versao_analise": "0.1"
}
```

Esse exemplo não representa saída validada do analisador. A classificação é
um sinal para investigação, sem probabilidade de cancelamento. As posições
das evidências já estão definidas em C01 para localizar trechos sem ambiguidade.

Valores propostos para os tipos do frontend:

- `sentimento`: `positivo`, `neutro`, `negativo` ou `informacao_insuficiente`.
- `churn.situacao`: `sinal_detectado`, `sem_sinal_detectado`, `nao_aplicavel` ou `informacao_insuficiente`.
- `vinculo`: `cliente`, `prospect` ou `nao_informado`.
- Coleções sem itens: lista vazia; não criar um item fictício para preencher o card.

Proposta de erro padronizado pela API, inclusive com adaptação dos erros de validação do framework no backend:

```json
{
  "erro": {
    "codigo": "TRANSCRICAO_VAZIA",
    "mensagem": "Informe a transcrição para continuar."
  }
}
```

Os códigos HTTP e de erro de texto constam de C01; o rascunho acima não os
substitui. C02-A acrescentará exemplos completos de upload, estados, resultado
e nova tentativa; os formatos de áudio ainda não são contratos implementados.

## Evolução futura — grupos, memória da equipe e compromissos

### Direção definida pelo usuário em 17/09/2026

Após a versão de análise de reuniões, permitir que cada usuário tenha seu
espaço e crie ou participe de grupos no ConvIQ. A evolução deve ajudar a
acompanhar reuniões, participantes, informações relevantes, responsáveis,
destinatários e compromissos com prazo, reduzindo esquecimentos e desorganização.
O usuário também indicou interesse em modelos de IA pré-treinados e adaptação
progressiva ao contexto de cada equipe. Não há fornecedor, modelo, orçamento
ou treinamento específico escolhido nesta decisão.

### Personalização proposta pelo Codex

1. **Modelo pré-treinado:** avaliar um modelo existente para interpretar a
   reunião, mantendo saída estruturada, evidências e validação das regras do
   produto. A adoção no analisador será decidida explicitamente na tarefa
   correspondente, sem substituir automaticamente a abordagem atual.
2. **Contexto do grupo:** manter vocabulário, projetos, integrantes, funções,
   preferências e acordos confirmados da equipe, com origem e data de atualização.
3. **Memória consultável:** recuperar apenas o contexto relevante e autorizado
   daquele grupo ao analisar uma nova reunião. Essa consulta pode usar RAG,
   que fornece informações ao modelo durante a análise; não é treinamento
   automático dos parâmetros do modelo.
4. **Feedback:** registrar correções confirmadas pelos usuários, atualizar
   informações desatualizadas e avaliar se elas melhoram análises futuras.
   Uma previsão do próprio modelo não se torna um fato confirmado na memória.
5. **Ajuste fino opcional:** considerar treinamento adicional somente se houver
   exemplos revisados suficientes e ganho mensurável sobre modelo com contexto,
   usando avaliação separada dos exemplos de treino. Não é necessário assumir
   um modelo treinado exclusivo por equipe para oferecer personalização.

O histórico precisa ser armazenado e consultado pela aplicação: usar o modelo
em várias reuniões, sozinho, não implementa memória persistente nem melhora
automática. Manter o contexto isolado por grupo e por permissão de acesso;
permitir corrigir/remover informações e refletir isso nas consultas futuras.
Mudanças de função, projeto ou acordo não devem ficar presas ao histórico antigo.

Exemplo de contexto útil: o grupo confirma que “Projeto Atlas” é uma implantação
específica e que determinada sigla se refere ao seu produto. Isso ajuda a
interpretar a reunião seguinte. Não permite atribuir uma tarefa a quem costuma
executá-la se a reunião atual não sustentar essa atribuição.

### Capacidades futuras de tarefas e acompanhamento

- Distinguir participantes informados/confirmados de vozes detectadas; uma
  pessoa pode participar sem falar. Separação de falantes no áudio (diarização)
  e associação de cada voz a uma pessoa/conta são etapas distintas.
- Separar autor da fala, pessoa mencionada, responsável pela ação e destinatário
  da entrega. Exemplo fictício: Ana diz “João, envie a proposta para Marina em
  três dias”: Ana fala, João recebe a atribuição e Marina recebe a proposta.
  A frase não comprova que João aceitou a tarefa.
- Extrair ação, prazo original, prazo interpretado e evidência. Datas relativas
  usam data/fuso da reunião, não do upload; se faltar referência ou houver
  dúvida sobre dias úteis/corridos, deixar a interpretação a confirmar.
- Identificar decisões, tarefas, bloqueios e informações relevantes com uma
  justificativa. Sugestão, hipótese ou nome citado não equivalem a compromisso.
- Encaminhar tarefas ao responsável por canal a definir, acompanhar aceite,
  andamento e conclusão e enviar lembretes. Corrigir prazo ou cancelar tarefa
  deve atualizar os avisos; reprocessamentos não devem duplicar tarefas/envios.
- Manter dúvidas sobre pessoa, intenção ou prazo visíveis. A recomendação
  inicial do Codex é permitir conferência antes de encaminhar; confirmação
  versus automação, canais e política de lembretes ficam para essa fase futura.

### Momento de implementar e avaliar

Primeiro, entregar a análise de reuniões conforme os PRs atuais. Depois,
detalhar contas/grupos e contratos de contexto, validar personalização com
histórico e feedback e decompor tarefas/notificações em PRs próprios. Nenhuma
dessas capacidades é dependência nova de B01 ou do MVP já planejado.

Antes da implementação futura, definir acesso aos grupos, convidados,
retenção/correção do histórico, método e custo da IA e canais de encaminhamento.
Avaliar extrações incorretas, correções de nomes/prazos, qualidade com e sem
contexto, uso de informação desatualizada e acesso entre grupos. “Integrado à
equipe” é um objetivo de personalização, não promessa de compreensão perfeita
ou redução de esquecimentos já comprovada.

Referências conceituais consultadas, sem escolha de fornecedor:
[diarização](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-stt-diarization),
[contexto recuperado com RAG](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview)
e [ajuste de modelos](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning).

## Decisões ainda abertas

- Viabilidade/configuração do Whisper aberto em B07-A; somente transcrição
  gratuita está autorizada. Recursos da hospedagem seguem a resolver em H01.
- Método de análise além das regras, com interesse do usuário em modelos
  pré-treinados; fornecedor, custo e avaliação ainda a definir. Grupos,
  memória da equipe, tarefas e encaminhamento ficam para a evolução futura
  acima; resumos continuam a detalhar.
- Formatos, duração e tamanho máximos dos áudios, conforme a solução escolhida.
- Prazo, responsável pelo backend e exigências acadêmicas aplicáveis; o frontend já tem responsável definido pelo usuário.
- Execução por link, hospedagem e política de acesso em H01; banco do ambiente
  publicado apenas na fase posterior de persistência.

Essas decisões não impedem B07-A nem o planejamento dos PRs. Os limites
concretos devem ser fechados em C02-A antes de implementar seus consumidores.
Login e grupos acompanham a evolução
futura definida acima. Dashboards agregados, gravação ao vivo e integrações
com plataformas de reuniões também permanecem fora dos PRs atuais.

## Referências técnicas

Consultadas em 17/09/2026:

- [FastAPI — documentação oficial](https://fastapi.tiangolo.com/): API Python, validação e documentação OpenAPI.
- [React — construir uma aplicação do zero](https://react.dev/learn/build-a-react-app-from-scratch): organização de aplicações com ferramentas de build e responsabilidades adicionais.
- [Vite — início do projeto](https://vite.dev/guide/): criação do frontend, incluindo o template React com TypeScript.

## Registro desta atualização

Planejamento preparado e revisado por Codex. Arquivos envolvidos no planejamento: este plano e a nota de atualização no documento de contexto. A revisão para PRs altera somente este plano. Critério da entrega: registrar stack confirmada e proposta, etapas de cada frente, PRs com dependências e critérios de aceite sem atribuir implementação ao que ainda é plano.

Validação: confronto com o contexto, leitura da análise existente no Python e inspeção da base local do backend; revisão documental. Nenhum código da aplicação foi criado, alterado ou executado nesta revisão de planejamento; nenhum PR foi aberto.

### Atualização em 17/09/2026 (Claude)

Nota histórica: descreve o estado em 17/09, sucedido pela implementação
B01–B04/C01 e pela atualização de 18/09 acima.

A base local em `backend/` citada acima foi apagada por descuido antes de qualquer commit; não há nada versionado ou recuperável. As referências a "revisar" ou "código existente" no backend foram corrigidas neste documento para refletir que a implementação recomeça do zero a partir de B01, sem mudar o restante do planejamento (stack, etapas, PRs e contrato seguem os mesmos).

Também foi corrigida a estrutura de pastas do repositório local: existia um `.git` aninhado dentro de uma subpasta `ConvIQ/`, sem nenhum commit, separado do repositório principal (que já tem remote no GitHub e um commit inicial com `conviq_datascience.py` e a documentação de contexto). Esse `.git` aninhado foi removido e este plano passou a viver na raiz do repositório principal, ao lado de `conviq_datascience.py`, conforme a árvore da seção "Estrutura prevista".

### Atualização em 18/09/2026 (Codex, PLN01)

Decisões do usuário incorporadas: transcrição gratuita com Whisper permitido,
persistência posterior e execução por link a resolver. Famílias C02/B05–B10
divididas em cartões pequenos no roteiro vinculado; C02-B conserva a conferência
com F06, sem bloquear o backend independente. `prompt.md` prepara somente
B07-A. Nenhuma implementação, instalação, execução de teste da aplicação,
abertura de PR, commit, push ou integração nesta atualização documental.

### Atualização em 19/09/2026 (Codex, PLN02)

Acrescentados B11–B21 para refinar as capacidades atuais, com base em dez
sondagens da composição real que reproduzem limitações de sentido, contexto,
vocabulário, catálogo, oportunidades e evidências. Roteiro detalhado e prompt
B11 preparados; prompt B07-A preservado para a tarefa parcial. Implementação,
testes de aceitação e revisão dos novos PRs continuam futuros. Sem alteração
de código ou operação Git de escrita nesta preparação.
