# PRs pequenos — áudio do ConvIQ

Planejamento do Codex em 18/09/2026. Estes IDs são entregas planejadas,
não números de PRs abertos. Claude Sonnet implementa uma entrega por vez;
Codex coordena e verifica; Claude Opus revisa conforme a governança.

## Decisões e limites da primeira demonstração

- **Execução por link:** objetivo do usuário, com hospedagem e forma de
  disponibilização **A_RESOLVER**. Os PRs abaixo preparam e validam o backend
  em ambiente de desenvolvimento; não comprovam acesso público pelo navegador.
- **Transcrição gratuita:** usar como primeira candidata a implementação
  aberta do Whisper, executada em máquina disponível. Não usar API paga,
  créditos promocionais, cartão ou migração automática para serviço pago.
  Software gratuito não garante infraestrutura de hospedagem gratuita.
- **Persistência posterior:** a demonstração pode usar memória para metadados,
  estados e resultados e disco temporário para áudio. Reiniciar o backend
  perde essas informações; a interface orienta novo envio. Não prometer
  retomada automática nem histórico entre reinícios nessa fase.
- **Escopo preservado:** mesmo analisador de texto de B04; sem contas,
  grupos, diarização, gravação ao vivo ou treinamento de modelo.
- **Ainda sem resposta:** prazo da apresentação, duração/tamanho desejados
  e hardware final. B07-A mede viabilidade; C02-A fixa limites conservadores
  configuráveis com essa evidência. Não assumir suporte a reuniões longas.

O usuário dispensou a persistência na apresentação. Por isso B05 e a
recuperação durável de B09 ficam posteriores; B06 deixa de depender de B05.
Os IDs originais são preservados como famílias. C02 foi separado: C02-A
define o contrato técnico para o backend; C02-B mantém a validação entre
as frentes após F06, antes da integração de áudio. F06 não bloqueia a
investigação nem o backend independente, mas continua sendo o marco da
primeira jornada utilizável e pré-requisito do frontend de áudio.

## Base observada e disciplina de entrega

B01–B04/C01 têm aceite técnico registrado e estão no commit agregado
`6169feca8c3a6cc6c5500eeab264eba817c8fbbc`, em `feat/b01-fundacao-api`.
O manifesto `docs/revisoes/2026-09-18-aceite-b04.sha256` identifica a base
de aplicação aceita. Frontend/F06 não foram comprovados nesta cópia.
Branch principal, integração, PR e publicação atuais no servidor:
`NAO_VERIFICADO`. O planejamento desta rodada ainda está fora do commit.

Para cada entrega:

1. Conferir Git, instruções e ficha em [REGISTRO_TRABALHO.md](../../REGISTRO_TRABALHO.md).
   Preservar alterações locais e usar uma branch por PR, sem reescrever o
   commit agregado existente. Os nomes abaixo são propostos, ainda não criados.
2. Confirmar a base real com as dependências disponíveis. B07-A pode partir
   do commit acima; os demais partem das dependências revisadas. PR empilhado
   deve declarar a branch base e a ordem de integração. Não presumir `main`.
3. Entregar apenas o escopo do cartão, com evidências proporcionais,
   exclusões e limitações. Não começar o próximo PR automaticamente.
4. Atualizar ficha e evento: execução, revisão, arquivos, comandos/resultados,
   branch, hashes, commit, push, PR e integração separados. Dependência
   entregue localmente não equivale a dependência integrada.

Atualização de 19/09/2026: B07-A tem entrega **PARCIAL**, relatada pelo Sonnet
na branch `spike/b07-a-viabilidade-whisper`, com arquivos locais não commitados,
sem aceite ou integração; falta validar fala real. Os demais cartões continuam
**PLANEJADOS / NAO_INICIADOS / SEM_ALTERACOES próprias**, sem branch criada
ou commit da tarefa. Para retomar B07-A, consultar sua ficha e o
[prompt preservado](PROMPT_B07_A_VIABILIDADE_WHISPER.md).
Após o pedido de revisão em B07-A-02 (19/09/2026), o `prompt.md` vigente
encaminha B07-A ao Opus para revisão/correção da entrega parcial, ainda sem
revisão Opus concluída. B11 da frente de
[refinamento da análise](PRS_REFINAMENTO_ANALISE.md) continua planejado,
com [prompt de execução preservado](PROMPT_B11_NEGACAO_SENTIMENTO.md).
Os nomes de arquivos novos abaixo são sugestões; manter as fronteiras de
responsabilidade é o critério, sem impor uma arquitetura maior que a tarefa.

## Ordem e dependências

| Ordem sugerida | ID | Entrega | Dependências |
|---|---|---|---|
| 1 | B07-A | Viabilidade real do Whisper gratuito | B04/C01 disponíveis como referência |
| 2 | C02-A | Contrato técnico e limites de áudio | B07-A, C01 |
| 3 | B08-A | Estados e repositório em memória | C02-A |
| 4 | B06-A | Validação do conteúdo de áudio | C02-A |
| 5 | B06-B | Recebimento e arquivos temporários | B06-A, B08-A |
| 6 | B07-B | Adaptador Whisper para a aplicação | B07-A, C02-A |
| 7 | B08-B | Executor e composição transcrição → análise | B06-B, B07-B, B08-A, B04 |
| 8 | B08-C | Rotas de upload, estado e resultado | B08-B |
| 9 | B09-A | Nova tentativa e falhas de execução | B08-C |
| 10 | B09-B | Expiração e limpeza de temporários | B09-A |
| Independente após texto | C02-B | Conferência do contrato com o frontend | C02-A, F06 |
| 11 | I01-A | Ensaio real do backend com áudio | B09-B |

C02-B pode ocorrer assim que F06 estiver disponível. É necessário antes
de concluir F07/F08, não antes do ensaio de backend I01-A. A integração
final I01 também depende de F09/F11 e do ambiente de apresentação definido.

## Cartões para o Claude

### B07-A — Verificar Whisper no ambiente disponível

- **Branch proposta:** `spike/b07-a-viabilidade-whisper`.
- **Objetivo:** demonstrar transcrição real em português e recomendar uma
  configuração gratuita reproduzível antes de alterar a API.
- **Arquivos:** `docs/decisoes/transcricao-whisper.md`, roteiro/script em
  `backend/scripts/`, dependências experimentais isoladas e registro da tarefa.
- **Escopo:** inventariar CPU, RAM, GPU se houver, Python e FFmpeg; experimentar
  inicialmente um modelo multilíngue pequeno (por exemplo `base`), medir tempo,
  memória e qualidade de trechos comerciais em áudio fictício. Registrar versão
  e origem dos pacotes/pesos, comandos, amostra e hardware. Testar silêncio e
  arquivo inválido. Recomendar modelo, runtime, executor e limites iniciais.
- **Aceite/validação:** áudio falado real → texto reconhecível, inclusive termos
  relevantes ao card; registrar texto esperado versus obtido, duração, tempo
  de processamento e limitações. Se não houver hardware/amostra/instalação
  viável, entregar diagnóstico parcial e o bloqueio concreto; simulação não
  aprova viabilidade. Não exigir benchmark extenso ou uma taxa sem amostra.
- **Fora:** dependências novas no ambiente da API, rotas, banco, frontend,
  instalação global ou hospedagem. Preparar pesos explicitamente; nada de
  baixar modelos ao importar a API. Não alterar a versão Python da aplicação
  só para fazer o experimento funcionar.

### C02-A — Fixar contrato técnico de áudio

- **Branch proposta:** `docs/c02-a-contrato-audio`.
- **Objetivo/arquivos:** `docs/contratos/audio.md` e schemas correspondentes
  em `backend/app/schemas/`, com exemplos verificáveis.
- **Escopo:** definir multipart com título, empresa, vínculo e arquivo;
  IDs distintos de reunião e tentativa; estados `recebido`, `transcrevendo`,
  `analisando`, `concluido`, `falhou` e, se necessário, `interrompido`.
  Definir transições terminais, respostas, erros, nova tentativa e expiração.
  Firmar limites de bytes/duração/formatos, timeout, capacidade, TTL de áudio
  e resultados a partir de B07-A. Preferir um processo de API e uma transcrição
  ativa, com recusa clara quando a capacidade estiver ocupada, sem fila externa.
- **Rotas propostas:** `POST /api/reunioes/audio` (202),
  `GET /api/processamentos/{id}`, `GET /api/reunioes/{id}` e
  `POST /api/processamentos/{id}/tentativas`. Resultado reutiliza o schema C01.
  Consolidar códigos HTTP para inválido, excesso, capacidade, não encontrado,
  conflito e expirado. Erros seguem o envelope C01.
- **Aceite/validação:** exemplos de sucesso, falha, execução ativa, tentativa
  nova, ID desconhecido após reinício e áudio expirado; schemas validam os
  exemplos e rejeitam combinações impossíveis. Sem percentual inventado.
  Enquanto houver registro, expiração pode ser distinguida; após reinício,
  sem memória, responder desconhecido, sem inventar histórico de interrupção.
- **Fora:** execução, armazenamento, rotas ativas ou mudança de C01. O contrato
  técnico orienta o backend; aceite de compatibilidade do frontend é C02-B.

### B08-A — Guardar estados e resultados em memória

- **Branch proposta:** `feat/b08-a-estados-memoria`.
- **Objetivo/arquivos:** modelo de tentativa e pequeno repositório em
  `backend/app/services/`, testáveis sem HTTP e substituíveis por B05 depois.
- **Escopo:** criar/consultar reuniões e tentativas, aplicar transições válidas,
  guardar resultado/erro e tempos; separar identidade da reunião da execução.
  Controlar acesso concorrente e capacidade definida em C02-A. Registrar a
  referência interna ao áudio sem expor caminho local na resposta.
- **Aceite/validação:** transições inválidas recusadas, IDs independentes,
  leitura durante atualização consistente, tentativa antiga preservada e
  nova instância vazia. Não deixar entradas crescerem sem limite de capacidade.
- **Fora:** banco, arquivo JSON usado como banco, threads de execução e rotas.

### B06-A — Validar áudio antes de processar

- **Branch proposta:** `feat/b06-a-validacao-audio`.
- **Objetivo/arquivos:** validador em `backend/app/services/` e testes com
  pequenas amostras sintéticas ou fictícias.
- **Escopo:** limites de bytes e duração, formato realmente decodificável,
  arquivo vazio/corrompido e metadados. Extensão/MIME sozinhos não comprovam
  conteúdo. Inspeção deve ter timeout e não depender de carregar todo o arquivo
  arbitrariamente em RAM. Chamadas ao FFmpeg/FFprobe sem shell interpolado.
- **Aceite/validação:** formato permitido, limite exato e excedido, nome/MIME
  enganoso, vazio, corrompido e inspeção travada geram resultado previsível.
- **Fora:** transcrição, criação de tentativa, política de retenção e HTTP.

### B06-B — Receber arquivo e criar tentativa

- **Branch proposta:** `feat/b06-b-recebimento-temporario`.
- **Objetivo/arquivos:** serviço de recebimento e utilitário de temporários
  em `backend/app/services/`, configuração específica em `app/config.py`.
- **Escopo:** copiar entrada em blocos com limite, gerar nome interno seguro,
  validar via B06-A e criar reunião/tentativa `recebido` via B08-A. Reservar
  capacidade de forma consistente; desfazer arquivo/reserva em qualquer erro.
  Diretório temporário configurável e separado de uploads publicados.
- **Aceite/validação:** upload válido cria um registro; dois nomes iguais não
  colidem; nome com caminho não escapa do diretório; excesso de bytes,
  indisponibilidade de disco, falha de validação ou cadastro não deixam órfãos.
- **Fora:** endpoint HTTP, limpeza por idade e disparo do transcritor.

### B07-B — Adaptar Whisper ao serviço de transcrição

- **Branch proposta:** `feat/b07-b-adaptador-whisper`.
- **Objetivo/arquivos:** adaptador em `backend/app/integrations/`, configuração,
  dependências opcionais ou ambiente separado conforme B07-A, README e testes.
- **Escopo:** interface que recebe referência de áudio e retorna texto e
  metadados do método/modelo; erros tipados para indisponibilidade e falha.
  Carregamento controlado do modelo, pesos preparados antes da execução e
  saúde da API de texto independente da disponibilidade do transcritor.
- **Aceite/validação:** contrato do adaptador testado com simulação identificada
  e ao menos um ensaio Whisper real registrado; silêncio/saída vazia vira falha
  útil. Não inventar texto, falantes ou timestamps. Eventuais repetições e
  alucinações do modelo são limites a registrar, sem prometer eliminá-las.
- **Fora:** provedor pago, fallback externo, análise de sentimentos e rotas.

### B08-B — Executar transcrição e análise fora da requisição

- **Branch proposta:** `feat/b08-b-executor-audio`.
- **Objetivo/arquivos:** executor e orquestrador em `backend/app/services/`;
  ciclo de vida da aplicação em `app/main.py` somente onde necessário.
- **Escopo:** consumir tentativa recebida, transcrever e chamar
  `compor_analise_texto` de B04, guardando transcrição e análise consistentes.
  Mudança de estado acompanha trabalho real. Limitar concorrência e tempo;
  timeout deve encerrar/isolar o trabalho e impedir resultado tardio de
  sobrescrever estado terminal. Não basta cancelar um await e deixar trabalho
  sem controle. Escolher executor conforme viabilidade, sem Celery/Redis agora.
- **Aceite/validação:** sequência completa, exceção em cada etapa, timeout,
  capacidade esgotada e encerramento controlado. Saúde e análise por texto
  continuam respondendo durante áudio. Evidências recortam exatamente a
  transcrição retornada; prospect e concorrentes mantêm regras de B04.
- **Fora:** rotas, retomada após queda abrupta e alteração do analisador.

### B08-C — Expor upload, estado e detalhe

- **Branch proposta:** `feat/b08-c-api-audio`.
- **Objetivo/arquivos:** rotas em `backend/app/api/`, registro em `main.py`,
  declarações OpenAPI, testes HTTP e exemplos de uso.
- **Escopo:** conectar os três endpoints principais de C02-A aos serviços;
  upload retorna 202 com IDs após aceitação, sem aguardar transcrição. Consulta
  informa estado/erro ou resultado concluído. Capacidades e rejeições do
  multipart obedecem ao contrato; não publicar caminho temporário ou traceback.
- **Aceite/validação:** upload → consultas → resultado via HTTP; 422/413 e
  demais erros de C02-A têm envelope e schemas OpenAPI corretos; ID desconhecido,
  processamento ativo e resultado ausente são distinguíveis conforme contrato.
  Simulação é permitida nos testes automatizados, claramente identificada.
- **Fora:** endpoint de nova tentativa, frontend e publicação do serviço.

### B09-A — Permitir nova tentativa sem confundir execuções

- **Branch proposta:** `feat/b09-a-nova-tentativa`.
- **Objetivo/arquivos:** serviço de tentativas, endpoint reservado em C02-A,
  testes de concorrência e falhas usando executor controlável.
- **Escopo:** repetir tentativa terminal elegível enquanto áudio estiver
  disponível, com novo ID e vínculo à origem. Evitar repetição simultânea e
  respeitar capacidade/timeout. Após perda/expiração, orientar novo upload;
  falha antiga continua consultável enquanto seu registro existir.
- **Aceite/validação:** falha → tentativa nova → sucesso; tentativa ativa
  recusada, duas requisições concorrentes não duplicam trabalho, arquivo
  ausente gera mensagem útil e resultado atrasado não altera execução nova.
- **Fora:** retomar trabalho após reinício, reenvio automático e histórico salvo.

### B09-B — Expirar resultados e limpar temporários

- **Branch proposta:** `feat/b09-b-limpeza-temporarios`.
- **Objetivo/arquivos:** política de retenção em serviço próprio, integração
  no ciclo de vida, documentação dos TTLs e testes com relógio controlado.
- **Escopo:** cumprir retenção de C02-A, limpar arquivos elegíveis e registros
  expirados, liberar capacidade; arquivos usados por tentativa ativa não podem
  ser removidos. Na inicialização, limpar resíduos identificáveis do diretório
  exclusivo, sem interpretar resíduos como estado durável de processamento.
- **Aceite/validação:** término com sucesso/falha, expiração, retry ativo,
  arquivo já removido e falha de limpeza; repetir limpeza é seguro, sem apagar
  fora da área gerenciada. Perda de estado após restart não vira ativo eterno.
- **Fora:** recuperar resultados ou tentativas antigas a partir dos arquivos.

### C02-B — Conferir contrato com a integração de texto

- **Branch proposta:** `docs/c02-b-alinhamento-frontend`.
- **Objetivo/arquivos:** exemplos e decisões em `docs/contratos/audio.md`,
  com evidência da conferência do responsável pelo frontend após F06.
- **Escopo:** confirmar compatibilidade do card C01 e consumo de IDs, etapas,
  erros, nova tentativa e perda de resultado. Registrar versão/branch de F06
  realmente examinada; ausência de frontend local não significa aprovação.
- **Aceite/validação:** acordo registrado entre frentes, exemplos consumíveis
  e divergências resolvidas antes de concluir F07/F08. Mudança de comportamento
  exige correção explícita dos consumidores, em PR separado quando necessário.
- **Fora:** implementar React, assumir que F06 existe ou aprovar em nome do colega.

### I01-A — Ensaiar o fluxo real de backend

- **Branch proposta:** `test/i01-a-ensaio-audio`.
- **Objetivo/arquivos:** roteiro e relatório em `docs/validacao/audio-backend.md`,
  pequenas amostras fictícias com origem/licença registrada ou instrução de
  gravação e hash, scripts auxiliares quando necessários.
- **Escopo:** executar Whisper real → análise → consultas, comparar transcrição
  e evidências, medir tempo no ambiente disponível. Ensaiar prospect, risco e
  oportunidade, silêncio/falha, retry e reinício com novo envio. Distinguir
  problema da transcrição de limitações já aceitas do analisador por regras.
- **Aceite/validação:** evidências HTTP e resultado real reproduzíveis; API de
  texto continua funcional, limites documentados e ausência de dependência
  paga. Simulação sozinha não aprova esta entrega; não precisa de benchmark
  extenso nem acrescentar teste que apenas espelhe implementação.
- **Fora:** declarar jornada de navegador ou acesso por link aprovado. I01
  final aguarda frontend integrado, F11 e ambiente de apresentação definido.

## Depois da demonstração — persistência e histórico

Estes PRs não bloqueiam a primeira apresentação. Permanecem planejados,
sem execução liberada; definir banco conforme infraestrutura antes de B05-A.

| ID / branch proposta | Dependências | Escopo e arquivos | Aceite e validação | Fora |
|---|---|---|---|---|
| B05-A / `feat/b05-a-schema-persistencia` | C02-A, B08-A; decisão de banco | `app/db/`, dependências e migração inicial de reuniões, tentativas, transcrição e resultado. SQLite é candidato local; implantação pode exigir outro banco | Migração sobe em banco novo; vínculos/IDs preservados; versão registrada | Troca do repositório ativo, histórico HTTP |
| B05-B / `feat/b05-b-repositorio-persistente` | B05-A, B09-B | Implementar a mesma interface do repositório e conectar aos serviços, com operações consistentes | Resultado concluído e tentativas sobrevivem à reabertura/reinício; falha parcial não deixa estado incoerente; mesmos testes de contrato do repositório | Reexecutar tentativas interrompidas, listagem |
| B09-C / `fix/b09-c-recuperacao-reinicio` | B05-B | Reconciliação no início: marcar trabalho não concluído como interrompido; conservar concluídos; retry segue disponibilidade do áudio | Queda abrupta/reinício não deixam estados ativos eternos; nova execução tem novo ID; inexistência de áudio pede reenvio | Retomada distribuída automática, fila externa |
| B10 / `feat/b10-listagem-reunioes` | B09-C | `GET /api/reunioes`, ordenação e paginação limitada, contrato/testes | Lista consistente de resultados salvos; detalhes acessíveis após restart; paginação previsível | Interface F10, busca avançada, grupos |

F10 segue B10 e F09. B05-B deve documentar a janela até B09-C em que a
recuperação de ativos ainda falta; só B09-C comprova a retomada segura do uso
após queda. Sem requisito confirmado de Oracle, não introduzir Oracle agora.

## Execução por link — A_RESOLVER

**H01 — decisão de execução/hospedagem (sem PR de implantação liberado).**
Responsável: usuário e Codex, com evidências de B07-A e I01-A. Escolher onde
rodam frontend, API e Whisper, recursos reais, acesso pelo navegador e duração
da disponibilidade. Conferir rede/URL da API, HTTPS/CORS, limites de envio e
tempo, ciclo de vida do processo e disponibilidade dos pesos. Conta, exposição
pública ou serviço com cobrança não estão autorizados por este planejamento.

Não escolher plataforma nem prometer capacidade gratuita antes dessa avaliação.
Depois da decisão, estruturar um PR de configuração de execução e outro de
validação pelo link, se forem entregas independentes. Os ensaios locais podem
avançar enquanto isso, mas não substituem o aceite do acesso por link.

## Fontes técnicas consultadas em 18/09/2026

- [Whisper — repositório oficial](https://github.com/openai/whisper): código
  e pesos com licença MIT, necessidade de FFmpeg e modelos multilíngues.
  A compatibilidade do runtime atual do projeto deve ser medida em B07-A;
  não inferir suporte ao Python 3.14 só porque a API já o utiliza.
- [Whisper — model card](https://github.com/openai/whisper/blob/main/model-card.md):
  desempenho varia com os dados; podem ocorrer texto alucinado e repetições.
  Isso justifica amostras reais em português e comparação com o áudio.

Referências locais: [plano geral](../../PLANO_DESENVOLVIMENTO.md),
[governança](../../SISTEMA_GOVERNANCIA_CONVIQ.md) e
[contrato de texto vigente](../contratos/analise-texto.md).
