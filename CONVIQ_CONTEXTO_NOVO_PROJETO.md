# ConvIQ — Contexto para iniciar um novo projeto

Atualizado em: 15/09/2026.

## 1. Finalidade deste documento

Este documento reúne a visão do ConvIQ, a base acadêmica existente e as decisões da conversa sobre uma futura demonstração funcional. Pode ser anexado ou copiado para um novo projeto ou conversa, sem depender do histórico anterior.

**Pedido atual do usuário: apenas documentação e contextualização.** A implementação será tratada depois. A divisão de tarefas e o tempo disponível ainda não foram definidos.

## 2. O que é o ConvIQ

O **ConvIQ é uma solução de inteligência conversacional para equipes de Vendas e Customer Success**, desenvolvida no contexto do Challenge FIAP × TOTVS 2026.

Sua proposta é transformar o conteúdo de reuniões com clientes e potenciais clientes em informações úteis para a operação comercial:

- Sentimento manifestado na conversa.
- Sinais de risco de cancelamento de clientes existentes, chamado de **churn**.
- Oportunidades de expansão da contratação, chamadas de **upsell**.
- Produtos TOTVS e concorrentes mencionados.
- Recomendações de próximos passos com base nos sinais encontrados.

O resultado central é um **card de inteligência da reunião**, que permite entender os principais sinais e consultar as evidências na transcrição.

### Problema que busca resolver

Reuniões contêm reclamações, intenções de compra, objeções e sinais de insatisfação que precisam ser lidos e interpretados. O ConvIQ busca reduzir esse trabalho manual e apoiar a priorização de ações comerciais e de relacionamento.

### Público principal

- Vendas: identificar necessidades, objeções e oportunidades comerciais.
- Customer Success (CS): acompanhar clientes e investigar sinais de insatisfação ou cancelamento.
- Gestão: consultar os resultados das análises e apoiar a priorização do atendimento.

## 3. Contexto acadêmico e materiais existentes

O projeto reúne entregas de Data Science, Java/Domain Driven Design e Database Design. Os documentos históricos também relacionam a solução a Agile e AR/VR, incluindo uma representação visual em Unreal Engine. Essa referência acadêmica não define a tecnologia da futura interface web.

### Estado identificado nos arquivos locais

| Área | O que existe | Limite do que está comprovado |
|---|---|---|
| Java | Aplicação de terminal com exemplos de reuniões, entrada manual de transcrição e análise por palavras-chave | Não foi encontrada uma API HTTP, interface web ou camada de persistência no código Java inspecionado |
| Data Science | Script para uso como notebook, dataset de 14 reuniões fictícias, limpeza de texto, TF-IDF, regras e comparação de Naive Bayes com Logistic Regression | Experimento acadêmico; não comprova um serviço de análise integrado à aplicação |
| Banco de dados | Scripts Oracle com estrutura, carga de exemplos e operações de atualização | A presença dos scripts não confirma banco provisionado ou conexão ativa na futura aplicação |
| Documentação | Plano de melhorias, especificação Java, achados de Data Science e roteiro de banca | Parte dos planos é anterior às evoluções dos arquivos atuais |
| Áudio e aplicação web | Fluxo discutido na conversa | Não foi localizada implementação de upload, transcrição de áudio ou aplicação web nos materiais inspecionados |

Essa verificação foi documental e por leitura de código. Os programas e o banco não foram executados durante a preparação deste documento.

### Domínio já representado

O Java contém `Reuniao`, `Participante`, `Transcricao`, `ProdutoTotvs`, `Sinal`, `SinalChurn` e `SinalOportunidade`, além do serviço `AnalisadorTexto` e do menu `Main`.

O script Oracle representa `CLIENTE`, `REUNIAO`, `PARTICIPANTE`, `TRANSCRICAO`, `SINAL`, `PRODUTO_TOTVS` e `FEEDBACK_CS`. O feedback registra confirmações ou correções humanas dos sinais.

Esses materiais são referências para o novo projeto. O reaproveitamento técnico e as exigências acadêmicas aplicáveis à próxima entrega precisam ser avaliados antes da implementação.

## 4. Demonstração desejada e decisões da conversa

O usuário pretende **abrir o ConvIQ no computador da faculdade e mostrar seu funcionamento**.

| Tema | Situação |
|---|---|
| Entrada de áudio | O usuário aceitou a recomendação da Q1; na retomada da conversa, ela foi registrada como envio de um arquivo de áudio de reunião fictícia |
| Fluxo pretendido | Enviar áudio → transcrever → analisar → mostrar resultado |
| Local da apresentação | Computador da faculdade |
| APIs externas | O usuário considera possível utilizá-las, mas ainda vai decidir com sua dupla |
| Provedor e orçamento | Pendentes; nenhum serviço ou gasto aprovado |
| Acesso pelo navegador e hospedagem por link | Recomendação apresentada, ainda sem decisão de infraestrutura |
| React | Mencionado como possibilidade para a interface; escolha ainda não confirmada |
| Responsáveis por interface e backend | Não definidos |
| Prazo da demonstração e disponibilidade da dupla | Não informados |

O trecho original da Q1 foi recuperado incompleto. O fluxo de upload acima é a interpretação registrada na conversa retomada; detalhes como formato, duração e tamanho do arquivo permanecem abertos.

## 5. Escopo proposto para a primeira versão demonstrável

Esta seção organiza uma proposta para o trabalho futuro. Os itens abaixo ainda não representam funcionalidades implementadas nem um escopo integralmente aprovado.

### Jornada principal

1. Abrir a aplicação no navegador.
2. Informar os dados básicos da reunião e selecionar um áudio fictício preparado para a demonstração.
3. Enviar o arquivo para processamento.
4. Acompanhar as etapas de envio, transcrição e análise.
5. Consultar a transcrição e o card de inteligência.
6. Conferir os trechos que sustentam os sinais e as recomendações.

### Conteúdo proposto para o resultado

| Informação | Papel no produto |
|---|---|
| Transcrição | Permitir a consulta ao conteúdo processado |
| Sentimento | Sintetizar os sinais positivos, neutros ou negativos da conversa |
| Risco de churn | Apoiar a investigação de possível cancelamento de clientes existentes |
| Oportunidades comerciais | Destacar interesse em módulos, expansão ou novas soluções |
| Produtos e concorrentes | Organizar as menções encontradas no conteúdo |
| Evidências e recomendações | Relacionar o sinal ao trecho de origem e sugerir próximos passos |
| Resumo, decisões e tarefas | Complementos sugeridos na conversa; ainda precisam entrar na definição final de escopo |

### Critério sugerido de demonstração funcional

Um áudio fictício enviado pela interface deve percorrer o processamento real e produzir uma transcrição consultável e uma análise derivada do conteúdo. Se houver exemplos pré-processados como apoio à apresentação, eles devem estar identificados como exemplos.

O resultado deve indicar quando não houver informação suficiente. Responsáveis, prazos e decisões só devem ser apresentados como fatos quando estiverem no conteúdo da reunião.

### Possíveis evoluções

Histórico de reuniões, perguntas sobre a transcrição, edição e feedback dos sinais, autenticação, painéis agregados, gravação ao vivo e integração com plataformas de reunião podem ser avaliados depois. Nenhum desses recursos foi confirmado como requisito imediato.

## 6. Direção técnica sugerida, ainda sem stack fechada

Separar as responsabilidades em três partes:

1. **Interface:** selecionar o áudio, acompanhar o processamento e apresentar os resultados.
2. **Backend:** receber a entrada, validar o arquivo, coordenar os serviços e devolver o resultado.
3. **Processamento:** converter áudio em texto e analisar a transcrição.

A transcrição e a análise são etapas distintas: podem usar serviços diferentes. O modelo acadêmico de churn também é diferente de um serviço que gera resumos e tarefas; a existência de um não resolve automaticamente o outro.

Se forem utilizadas APIs externas, as credenciais devem ficar no backend. Provedor, custos, limites de upload e forma de hospedagem dependem da decisão da dupla.

A base atual usa Java, Python e Oracle em entregas separadas. Ainda será necessário definir como reaproveitá-los e integrá-los. Não há decisão registrada de framework de backend, banco para a aplicação web ou obrigação de manter todos esses componentes na demonstração.

## 7. Aprendizados e limites a preservar

### Análise acadêmica não equivale a validação com clientes reais

O dataset contém **14 reuniões sintéticas**. Os rótulos de risco foram produzidos por regras, sem histórico real de cancelamento ou validação humana abrangente.

O documento de achados registra que a Logistic Regression apresentou recall de aproximadamente **83,3% para a classe ALTO** no cenário original de validação deixando uma reunião de fora por vez. Essa é uma métrica do experimento documentado, não uma garantia de desempenho do produto.

### Prospect não deve receber risco de cancelamento de contrato inexistente

Um potencial cliente sem contrato não pode cancelar esse contrato. A modelagem futura deve distinguir cliente existente de prospect e tratar churn como não aplicável quando adequado. A simples menção a um concorrente também não comprova intenção de troca.

### Limitação conhecida das regras atuais

As listas de sentimento no Java e no Python incluem `satisfeit` e `insatisfeit`. A contagem por substring pode contabilizar ambos em “insatisfeito” e distorcer o resultado. Essa limitação precisa ser considerada se o analisador for reaproveitado.

### Planos antigos precisam ser lidos com contexto

O arquivo `CONVIQ_GAPS_E_PLANO.md` descreve uma fase sem modelo supervisionado e sem tabela de feedback. Os arquivos atuais já contêm comparação de classificadores e a definição de `FEEDBACK_CS`. Esses itens não devem voltar a ser tratados como totalmente ausentes com base apenas no plano antigo.

## 8. Materiais de referência para levar ao novo projeto

Este documento é autossuficiente para contextualização. Para implementar ou revisar o código existente, levar também os arquivos abaixo. Os caminhos são relativos à pasta de origem e só funcionarão se os materiais forem copiados junto.

- `ConvIQ_Projeto_Java/ConvIQ/`: fontes Java e instruções de execução.
- `Data_Science/conviq_datascience.py`: código do experimento de Data Science.
- `Data_Science/ACHADOS_TECNICOS_SPRINT3.md`: resultados e limitações documentadas.
- `Database_Design/conviq_oracle.sql`: estrutura e exemplos do banco Oracle.
- `CONVIQ_GAPS_E_PLANO.md`: plano histórico de evolução.
- `ESPECIFICACAO_JAVA_SPRINT3.md`: especificação histórica das pendências Java.
- `ROTEIRO_BANCA_SPRINT3.pdf`: roteiro existente da apresentação acadêmica.
- `SPRINT_3_E_4_CHALLENGE_2026_TOTVS.pdf`: documento disponível para conferir as exigências acadêmicas da próxima etapa.

As datas e rubricas históricas não definem automaticamente o prazo ou o escopo da nova aplicação.

## 9. Texto pronto para abrir a nova conversa

> Estou iniciando a continuidade do ConvIQ, uma solução de inteligência conversacional do Challenge FIAP × TOTVS 2026. Leia o documento de contexto anexado como referência inicial.
>
> O ConvIQ analisa reuniões de Vendas e Customer Success para apresentar sentimento, sinais de risco de cancelamento de clientes existentes, oportunidades comerciais, produtos e concorrentes mencionados e recomendações apoiadas na transcrição.
>
> Já temos materiais acadêmicos separados: aplicação Java de terminal com regras de palavras-chave, experimento Python de Data Science com 14 reuniões sintéticas e scripts Oracle. Isso ainda não representa uma aplicação web integrada com transcrição de áudio.
>
> Queremos evoluir para uma demonstração no computador da faculdade, seguindo o fluxo de enviar um áudio fictício, transcrever, analisar e mostrar o resultado. O acesso pelo navegador e a hospedagem por link foram sugeridos. APIs externas são uma possibilidade, mas vou decidir seu uso e orçamento com minha dupla. React foi mencionado, sem decisão final. Ainda não sei a divisão de tarefas nem o prazo da apresentação.
>
> Preserve essas decisões em aberto e diferencie o que existe do que está apenas proposto. Use este contexto para dar continuidade ao trabalho que eu solicitar a seguir.
