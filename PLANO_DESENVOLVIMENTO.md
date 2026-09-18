# ConvIQ — Stack e etapas de desenvolvimento

Atualizado em: 17/09/2026.

## Estado e objetivo

Python no backend e React no frontend foram confirmados pelo usuário. Os demais componentes abaixo são recomendações técnicas para organizar a implementação. Provedor de transcrição, orçamento e hospedagem continuam em aberto.

Objetivo: uma demonstração em que o usuário envia o áudio de uma reunião fictícia, acompanha o processamento e consulta a transcrição e um card de inteligência com evidências.

**Prioridade reafirmada pelo usuário em 17/09/2026:** concluir primeiro o
ConvIQ que analisa reuniões. Contas individuais, grupos, personalização por
equipe, atribuição de tarefas e lembretes ficam como evolução futura, descrita
adiante. Essa evolução não amplia os critérios dos PRs atuais.

Este documento será compartilhado com o colega de equipe responsável pelo frontend. Ele reúne a visão geral e um guia de execução para essa frente, incluindo o que pode avançar antes de a API estar disponível.

Existe neste repositório o experimento acadêmico `conviq_datascience.py`. Uma base local em `backend/` (FastAPI, configuração, endpoint de saúde, schemas e teste de saúde) chegou a ser criada, mas foi apagada por descuido antes de qualquer commit; nada disso está recuperável. A implementação do backend recomeça do zero a partir da etapa 1. A análise pela API, a interface web e a transcrição continuam pendentes. Os materiais Java e Oracle citados no contexto não estão nesta pasta.

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
| Persistência local, na etapa 4 | SQLite + SQLAlchemy; Alembic para migrações | Guardar reuniões, transcrições, resultados e estados do processamento |
| Testes | pytest no backend; Vitest e React Testing Library no frontend | Verificar regras, contratos e interações relevantes |
| Validação integrada | Playwright, na etapa final | Exercitar a jornada pelo navegador |
| Transcrição | Adaptador Python para o provedor escolhido | Converter áudio em texto sem vincular a interface a um fornecedor |

A escolha de FastAPI aproveita Python no processamento e oferece contratos e documentação da API. React com Vite atende à proposta de uma interface que consome essa API. TypeScript ajuda a explicitar os dados usados pelos componentes.

SQLite é a proposta para desenvolvimento e demonstração local. Antes da hospedagem, verificar persistência de disco e concorrência; PostgreSQL pode ser necessário conforme a infraestrutura. Conferir eventuais exigências acadêmicas de Oracle antes de fechar a entrega de banco.

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
│   │   └── db/            # Persistência, a partir da etapa 4
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

As etapas abaixo descrevem a sequência de entregas. A fundação do backend precisa ser recriada em B01; a base anterior foi perdida antes de commit. O colega de equipe é responsável pelo frontend. A pessoa responsável pelo backend e as datas ainda precisam ser registradas. Os dois responsáveis devem alinhar o contrato antes de integrar as entregas.

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

- **Pré-requisito específico:** escolher serviço ou modelo local de transcrição, recursos necessários, limites de arquivo e orçamento quando houver custos.
- **Python:** implementar upload validado, adaptador de transcrição e persistência de reunião e processamento; encadear transcrição e o mesmo serviço de análise usado no texto.
- **Python:** oferecer consulta de estado e resultado; registrar falhas e permitir nova tentativa sem confundir tentativas distintas. Definir o executor de tarefas conforme o transcritor e o ambiente escolhidos.
- **React:** adicionar seleção de áudio, envio, acompanhamento das etapas e recuperação de falhas. Consultar periodicamente o estado usando o identificador devolvido pela API.
- **Entrega verificável:** um áudio fictício percorre transcrição real e análise até o card; arquivos inválidos e falhas de transcrição produzem mensagens úteis. Reiniciar o backend não pode deixar processamentos indefinidamente como ativos: recuperar ou marcar como interrompidos.

Estados previstos: recebido → transcrevendo → analisando → concluído, com falha ou interrupção quando aplicável. Mostrar etapas reais; percentual somente quando houver medição disponível.

### 5. Consulta de resultados salvos

- **Python:** implementar listagem e consulta das reuniões persistidas na etapa 4, com data, estado e resultado.
- **React:** criar lista de reuniões e navegação para os detalhes, permitindo reabrir uma análise.
- **Entrega verificável:** após recarregar a página e reiniciar o backend, os resultados concluídos continuam disponíveis.

Esta etapa é uma extensão proposta para facilitar a demonstração. Pode ficar para depois da primeira apresentação se o prazo exigir; a persistência mínima de processamento continua na etapa 4.

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

**Responsáveis:** PRs `F` ficam com o colega do frontend; PRs `B`, com o responsável pelo backend ainda a registrar. Nos PRs `C` e `I`, escolher um autor e solicitar revisão da outra frente, evitando edições simultâneas dos mesmos arquivos.

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

B01 recria a fundação do zero, já que a base anterior foi perdida antes de qualquer commit. C01 complementa os schemas iniciais antes de o frontend depender deles.

F03 e F04 podem avançar em paralelo ao serviço Python após F02. **O marco de primeira versão utilizável é F06**, sem depender de transcrição de áudio ou histórico.

### Segunda entrega: áudio → transcrição → análise → card

| PR | Escopo e arquivos principais | Depende de | Critério de aceite |
|---|---|---|---|
| C02 — Contrato e decisão de áudio | `docs/contratos/audio.md`: provedor, limites, executor, estados, respostas e nova tentativa | F06 e decisão de transcrição/orçamento | Contrato inclui identificadores, falhas, interrupção, política de arquivos temporários e exemplos; recursos necessários definidos |
| B05 — Persistência mínima | `backend/app/db/`, migrações e testes | C02 | Salva e recupera reunião, tentativa, transcrição e resultado; dados persistem após reabrir a conexão |
| B06 — Recepção de áudio | Validador, armazenamento temporário e serviço de recebimento | B05 | Arquivo válido gera registro recebido; inválido é rejeitado; falhas não deixam arquivos órfãos. Rota pública entra com B08 |
| B07 — Adaptador de transcrição | `backend/app/integrations/` e testes do adaptador | C02 | Retorna texto real de áudio fictício no ambiente escolhido; trata falha do transcritor; distingue testes simulados da verificação real |
| F07 — Seleção e envio de áudio | `AudioUpload` e cliente de upload com exemplos | C02, F06 | Aplica limites definidos, mostra arquivo selecionado e trata rejeição; uso de exemplos permanece identificado |
| B08 — Processamento e consulta | Ligar recebimento, transcrição e análise; expor rotas de upload, estado e detalhe | B04, B06, B07 | Upload inicia execução e devolve identificador; consulta reflete etapas reais e retorna resultado persistido ou falha |
| F08 — Acompanhamento real | `ProcessingStatus`, consulta periódica e resultado | F07, B08 | Áudio enviado pela interface chega ao card real; consulta termina em estado final ou saída da tela |
| B09 — Interrupção e nova tentativa | Recuperação após reinício, nova tentativa e limpeza de arquivos | B08 | Processo interrompido não fica ativo indefinidamente; nova tentativa tem identidade própria; limpeza segue C02 |
| F09 — Recuperação de falhas | Interface de interrupção e nova tentativa | F08, B09 | Usuário entende a falha e pode tentar novamente; resultado antigo não é confundido com nova execução |

B06 entrega um serviço interno testável. A interface pública de upload só entra em B08, quando houver execução conectada. A decisão de transcrição pode ser pesquisada antes de F06; C02 consolida o acordo antes da implementação do fluxo de áudio.

**O marco da demonstração com áudio é F09**, com o fluxo de falha e recuperação também integrado.

### Histórico opcional e preparação da apresentação

| PR | Escopo e arquivos principais | Depende de | Critério de aceite |
|---|---|---|---|
| B10 — Listagem de reuniões | `GET /api/reunioes`, ordenação e limite de resultados | B09 | Lista registros persistidos de modo previsível; detalhe continua disponível |
| F10 — Histórico | `MeetingList` e navegação para detalhes | F09, B10 | Reabre análises salvas após recarregar a página |
| F11 — Revisão visual e acessibilidade | Ajustes pontuais de layout, foco, teclado e mensagens | F09; F10 se incluído | Jornada utilizável em computador e tela menor; sem falhas de interação identificadas na revisão |
| I01 — Ensaio da demonstração | Teste integrado, instruções e exemplo de apoio identificado | F11, B09 | Jornada real validada no ambiente de apresentação; comandos e resultados registrados; distinguir teste com transcritor simulado do ensaio real |

B10 e F10 podem ser adiados juntos sem bloquear a apresentação. Problemas encontrados no ensaio que exijam mudanças independentes devem gerar PRs de correção próprios, em vez de ampliar I01.

### Como abrir e revisar cada PR

- Uma branch por PR, com nomes como `feat/b02-sentimento-evidencias` ou `feat/f03-formulario-transcricao`.
- Título com o identificador e a entrega concreta. Abrir a partir da branch principal atualizada após integrar as dependências; se houver PR dependente ainda aberto, informar a base e a ordem de integração.
- Descrição curta: comportamento entregue, dependências, validação executada e limitações restantes. Para mudanças visuais, incluir captura da tela quando possível.
- Backend altera principalmente `backend/`; frontend, `frontend/`. Mudanças em contrato e arquivos compartilhados devem ter um autor coordenando a edição.
- Testes relevantes acompanham o comportamento que verificam. A revisão visual final e I01 complementam essa validação.
- Integrar após revisão, verificações pertinentes e ausência de dependências pendentes. Registrar se o resultado foi verificado com exemplos, API real ou transcrição real.

**Próximo passo:** implementar B01 do zero e encaminhar F01 ao responsável pelo frontend. Depois da revisão e integração de B01, consolidar C01 para liberar o desenvolvimento independente das duas frentes. Consultar o registro de trabalho para saber o que já foi preparado, iniciado ou entregue.

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

**Situação:** proposta de contrato para alinhar as duas frentes. Nenhuma rota está implementada; `GET /api/health` e os demais endpoints abaixo continuam planejados, a começar pela etapa 1. Em C01, consolidar os schemas e exemplos de texto; em C02, os de áudio. Comunicar mudanças ao outro responsável antes de alterar o formato compartilhado.

Na etapa 1, detalhar estes campos em schemas e exemplos compartilhados:

- **Entrada por texto:** título da reunião, empresa, vínculo (`cliente`, `prospect` ou `nao_informado`) e transcrição.
- **Resultado:** sentimento, situação do risco de churn, oportunidades, produtos e concorrentes, evidências, recomendações, método e versão da análise.
- **Evidência:** trecho literal da transcrição e posição no texto original. Timestamps de áudio somente quando fornecidos pelo transcritor.
- **Churn:** `nao_aplicavel` para prospect; `informacao_insuficiente` quando não for possível avaliar. Ausência de sinais detectados não garante baixo risco real.
- **Processamento de áudio:** identificador, estado, erro quando houver e referência ao resultado quando concluído.

Rotas propostas, a implementar nas respectivas etapas:

| Etapa | Rota | Finalidade |
|---|---|---|
| 1 | `GET /api/health` | Verificar disponibilidade da API |
| 2 | `POST /api/analises/texto` | Analisar uma transcrição |
| 4 | `POST /api/reunioes/audio` | Receber áudio e devolver identificador de processamento |
| 4 | `GET /api/processamentos/{id}` | Consultar andamento e referência ao resultado |
| 4 | `GET /api/reunioes/{id}` | Recuperar transcrição e análise persistidas |
| 5 | `GET /api/reunioes` | Listar reuniões salvas |

### Exemplo para iniciar o formulário e o card

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

Esse exemplo não representa saída já validada do analisador. A classificação é um sinal para investigação, sem probabilidade de cancelamento. As posições das evidências serão detalhadas na etapa 1 para permitir localizar trechos repetidos sem ambiguidade.

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

Na etapa 1, combinar os códigos HTTP e de erro. Na etapa 4, acrescentar exemplos completos de upload, estados, resultado e nova tentativa. Esses formatos de áudio ainda não devem ser tratados como contratos fechados.

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

- Provedor de transcrição, processamento local ou externo e orçamento.
- Método de análise além das regras, com interesse do usuário em modelos
  pré-treinados; fornecedor, custo e avaliação ainda a definir. Grupos,
  memória da equipe, tarefas e encaminhamento ficam para a evolução futura
  acima; resumos continuam a detalhar.
- Formatos, duração e tamanho máximos dos áudios, conforme a solução escolhida.
- Prazo, responsável pelo backend e exigências acadêmicas aplicáveis; o frontend já tem responsável definido pelo usuário.
- Hospedagem, banco no ambiente publicado e política de acesso caso a aplicação seja disponibilizada publicamente.

Essas decisões não impedem a etapa 1. Login e grupos acompanham a evolução
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

A base local em `backend/` citada acima foi apagada por descuido antes de qualquer commit; não há nada versionado ou recuperável. As referências a "revisar" ou "código existente" no backend foram corrigidas neste documento para refletir que a implementação recomeça do zero a partir de B01, sem mudar o restante do planejamento (stack, etapas, PRs e contrato seguem os mesmos).

Também foi corrigida a estrutura de pastas do repositório local: existia um `.git` aninhado dentro de uma subpasta `ConvIQ/`, sem nenhum commit, separado do repositório principal (que já tem remote no GitHub e um commit inicial com `conviq_datascience.py` e a documentação de contexto). Esse `.git` aninhado foi removido e este plano passou a viver na raiz do repositório principal, ao lado de `conviq_datascience.py`, conforme a árvore da seção "Estrutura prevista".
