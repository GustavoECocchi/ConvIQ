# Sistema de governança do ConvIQ

Versão: 1.1 — 17/09/2026. Registro compartilhado obrigatório solicitado pelo usuário.

**Versão 1.2 — 07/10/2026 (modo ágil):** a seção 11 reduz leitura, escrita e cerimônia de Git. Onde ela divergir das seções 1, 5.1, 5.2, 8, 9 e 10, a seção 11 prevalece; o ciclo de papéis, os estados e os critérios de aceite não mudam.

## 1. Objetivo e funcionamento

Organizar o desenvolvimento do ConvIQ em PRs pequenos, com escopo definido, execução pelo Claude, revisão com evidências e coordenação pelo Codex junto ao usuário.

O ciclo de trabalho é: **usuário + Codex planejam → Sonnet implementa → usuário retorna ao Codex → Codex analisa e prepara o prompt → Opus revisa e corrige → Codex verifica a entrega final → integração conforme autorização do usuário**.

Este documento define o acordo de trabalho. O acompanhamento atual e o histórico ficam em [REGISTRO_TRABALHO.md](REGISTRO_TRABALHO.md), que Codex e Claude devem ler e atualizar em cada atuação. As instruções de entrada estão em [AGENTS.md](AGENTS.md) e [CLAUDE.md](CLAUDE.md). O usuário leva os prompts e relatórios entre as conversas; os arquivos, por si só, não executam agentes nem transmitem mensagens. Em outra cópia do repositório, conferir também se os registros foram recebidos por commit/push ou pelo usuário.

### Regra do prompt de rascunho

`prompt.md` é o arquivo oficial de rascunho. Sempre que o usuário pedir para
gerar ou preparar um prompt, Codex grava ali o prompt completo e vigente para
o Claude ler. O prompt anterior é substituído por padrão; somente fica
acumulado se o usuário pedir. A substituição é registrada em
`REGISTRO_TRABALHO.md`, que é o histórico confiável. Cópias nomeadas podem ser
mantidas para rastreabilidade, mas o Claude usa `prompt.md` como a instrução
atual indicada pelo usuário.

## 2. Papéis e responsabilidades

| Participante | Responsabilidade | Resultado esperado |
|---|---|---|
| Usuário | Define prioridades e decisões de produto com o Codex, encaminha as entregas entre agentes e decide sobre integração e publicação | Direção do projeto e encaminhamento da próxima ação |
| Codex — coordenador | Organiza os PRs, define escopo e critérios, inspeciona o trabalho entregue, verifica evidências, prepara prompts e mantém o acompanhamento | Tarefa executável, parecer fundamentado e próximo passo claro |
| Claude Sonnet — executor | Implementa o PR liberado, escreve os testes pertinentes, valida, documenta e relata a entrega | Implementação pronta para revisão, com limitações declaradas |
| Claude Opus — revisor e corretor | Revisa o diff do Sonnet e os apontamentos do Codex, confirma os problemas, corrige o necessário e valida as correções | Entrega revisada e relatório do que foi corrigido, mantido ou ficou pendente |
| Responsável pelo frontend | Desenvolve os PRs `F`, participa dos contratos e da validação integrada | Interface compatível com os contratos e integrada nos marcos previstos |

Por padrão, Codex coordena e verifica; a implementação e as correções do código da aplicação ficam com Claude. Codex pode executar verificações e atualizar documentação de coordenação. Uma atribuição diferente feita pelo usuário prevalece para a tarefa correspondente.

**Cada agente registra o próprio trabalho em arquivo**, incluindo planejamento, implementação, revisão, correção, testes e operações Git. Sonnet e Opus atualizam a ficha e acrescentam seus eventos antes de entregar; Codex registra suas análises e as transições que verificou. Uma afirmação recebida de outro agente fica identificada como relatada até ser conferida. O relatório no chat complementa o registro persistido.

Sonnet e Opus não aprovam a própria entrega como conclusão do ciclo. Opus pode concluir a revisão sem alterações quando não encontrar problemas; não é necessário produzir mudanças artificiais. A revisão não parte da premissa de que o executor errou.

Os papéis dos agentes não substituem os responsáveis humanos pela entrega acadêmica. O responsável humano pelo backend e as datas continuam a registrar. PRs compartilhados `C` e `I` devem ter um autor definido e participação das duas frentes.

## 3. Referências e estado inicial

Consultar estes materiais conforme a tarefa:

| Referência | Uso |
|---|---|
| [PLANO_DESENVOLVIMENTO.md](PLANO_DESENVOLVIMENTO.md) | Escopo do produto, sequência, dependências e critérios dos PRs |
| Este documento | Papéis, passagem de trabalho, revisão e regras de registro |
| [REGISTRO_TRABALHO.md](REGISTRO_TRABALHO.md) | Índice atual, fichas por PR/tarefa e histórico de atuação de todos os agentes |
| [AGENTS.md](AGENTS.md) e [CLAUDE.md](CLAUDE.md) | Instruções de leitura e atualização para Codex e Claude |
| [prompt.md](prompt.md) | Rascunho do prompt vigente solicitado pelo usuário; substituído a cada novo prompt |
| [CONVIQ_CONTEXTO_NOVO_PROJETO.md](CONVIQ_CONTEXTO_NOVO_PROJETO.md) | Visão do produto e histórico acadêmico |
| [conviq_datascience.py](conviq_datascience.py) | Experimento de referência; funções e limitações a avaliar antes de reaproveitar |
| Contratos de texto e áudio, quando criados em C01 e C02 | Formatos acordados entre frontend e backend |

Instruções superiores e pedidos atuais do usuário prevalecem. Para decisões do projeto, considerar o acordo mais recente registrado. Cada documento tem a responsabilidade indicada acima; divergências devem ser apontadas e resolvidas explicitamente, sem alterar o escopo por suposição. Para afirmar o que está implementado, usar código, diff e validações da versão examinada.

Na criação desta governança, em 17/09/2026:

- Os arquivos disponíveis na pasta do projeto são o plano, o contexto e o experimento Python. Não há implementação local de `backend/` ou `frontend/` nessa pasta.
- O plano registra a perda da base inicial do backend antes de commit. B01 deve recriar a fundação. Trechos antigos que ainda falam em revisar uma base existente não comprovam implementação.
- Python e React estão confirmados. Os demais componentes seguem como propostas do plano, a concretizar nas tarefas correspondentes.
- Java e Oracle são referências históricas; seus materiais não estão nesta pasta.
- Nenhum PR funcional é considerado entregue ou aprovado por este documento. Os códigos B01, C01 etc. são identificadores de planejamento, não números de PR no GitHub. O estado remoto não foi verificado nesta criação.
- Não foi encontrada uma versão adotada em `docs/governanca/REGRAS.md`. A referência geral e seus modelos em `/home/gustavoecocchi/Documents/GOVERNANCA/` não estavam acessíveis. Este documento foi elaborado com as instruções do usuário e os materiais disponíveis; não constitui cópia adotada daquela referência.

## 4. Ciclo de cada PR

### 4.1. Preparação pelo usuário e Codex

Codex confere o estado real do projeto e prepara um prompt contendo: identificador, objetivo, pasta de trabalho, branch/base, dependências, escopo, exclusões, critérios verificáveis e forma de entrega. O usuário encaminha esse prompt ao executor.

O prompt também informa quais ações Git estão autorizadas: trabalho local, commit, push, abertura de PR ou integração. Usar a autorização já concedida pelo usuário, sem pedir novamente a mesma autorização. Na ausência de orientação sobre publicação, preparar a entrega local e informar essa condição.

### 4.2. Execução pelo Sonnet

Sonnet lê as instruções, confirma os caminhos e inspeciona o estado Git antes de editar. Implementa o PR atribuído e valida os comportamentos exigidos. Decisões rotineiras dentro do escopo podem ser resolvidas e justificadas pelo executor.

Se faltar uma decisão indispensável de produto, contrato ou infraestrutura, registra o ponto e conclui o que puder avançar independentemente. Uma melhoria fora do escopo vira proposta para outra tarefa.

Ao terminar, atualiza a ficha e o histórico em `REGISTRO_TRABALHO.md`, entrega o relatório da seção 8 e informa: **“Implementação do [ID] finalizada e entregue para revisão; Git: [situação] na branch [nome]; integração: [situação]. Aguardando coordenação.”** Só usa “finalizada” quando cumpriu o escopo; se houver trabalho pendente, registra entrega parcial ou bloqueio. Não inicia automaticamente o próximo PR.

### 4.3. Análise inicial pelo Codex

O usuário traz o relatório e a referência da entrega. Codex examina o diff, os arquivos relevantes e as evidências, verificando critérios, dependências e impacto sobre o restante do projeto. Quando possível, reproduz as verificações pertinentes.

Codex distingue o que verificou do que foi apenas relatado. Se não tiver acesso ao código ou ao resultado necessário, solicita o material específico e mantém o aceite pendente. A declaração “terminei” não substitui a análise da entrega.

Registra os achados, evidências e o encaminhamento no registro compartilhado antes de responder, inclusive quando a análise não produzir alterações no código.

### 4.4. Revisão e correção pelo Opus

Codex prepara um prompt com a versão exata a revisar, os achados e os critérios originais. O usuário o encaminha ao Opus.

Opus faz uma revisão própria do diff e confirma cada achado antes de modificar o código. Corrige os problemas comprovados dentro do escopo, acrescenta testes pertinentes e apresenta evidências. Se discordar de um apontamento, explica com referência ao código e ao comportamento observado.

Correções continuam na mesma branch do PR. Problemas novos dentro do escopo também podem ser corrigidos e relatados. Mudanças de escopo, contrato ou arquitetura que afetem outras entregas retornam à coordenação antes da implementação correspondente.

Opus registra a revisão, as correções e sua situação Git na ficha e no histórico, inclusive quando concluir a revisão sem mudar código.

### 4.5. Verificação final e integração

O usuário retorna com o relatório do Opus. Codex verifica o diff final, as correções, os critérios de aceite e a validação. Se houver pendências impeditivas, prepara uma rodada de correção objetiva; caso contrário, registra o aceite técnico da versão examinada.

Integração ocorre conforme a autorização do usuário. O registro deve diferenciar aprovação técnica de merge efetivamente realizado. Depois da integração, conferir o estado da branch de destino e executar uma verificação pertinente ao que foi integrado; repetir a validação afetada se a resolução de conflitos alterou código.

Codex atualiza `REGISTRO_TRABALHO.md` e prepara o próximo PR elegível. Trabalho em paralelo só avança quando for atribuído e houver independência de arquivos e dependências; cada frente mantém seu próprio ciclo de revisão e registro. Quem realizar commit, push ou integração registra a operação e o resultado verificado.

## 5. Estados e evidências

| Estado | Significado e condição para avançar |
|---|---|
| `PLANEJADO` | Está no plano, mas ainda não recebeu tarefa de execução |
| `LIBERADO` | Escopo, executor e critérios estão definidos; dependências necessárias foram verificadas |
| `EM_EXECUCAO` | Executor está implementando a tarefa atribuída |
| `ENTREGUE` | Executor disponibilizou alterações e relatório; aceite ainda pendente |
| `EM_REVISAO` | Codex ou Opus examina uma versão identificada da entrega |
| `EM_CORRECAO` | Existem problemas confirmados em tratamento; depois retorna à revisão |
| `APROVADO` | Codex verificou a entrega final, com critérios atendidos e sem pendências impeditivas |
| `INTEGRADO` | A versão aprovada foi incorporada à branch de destino e a integração foi conferida |
| `BLOQUEADO` | Falta uma condição indispensável; registrar causa, responsável por resolvê-la e condição de retomada |

Uma nova mudança após a aprovação exige rever o que foi afetado antes da integração. Registrar o commit revisado; para trabalho ainda sem commit, registrar o diff e os arquivos entregues, deixando explícita essa condição. Após criar o commit, conferir se corresponde ao conteúdo revisado.

Os estados são por PR. B04 aprovado não significa que a interface está integrada, e um teste com transcritor simulado não significa que a demonstração de áudio está concluída.

### 5.1. Finalização e situação Git são informações separadas

Toda ficha e todo encerramento informam os campos abaixo. Não usar apenas “feito”, “finalizado” ou “commitado” sem indicar a etapa, a branch e a versão.

| Campo | Valores e evidência necessária |
|---|---|
| Entrega do executor | `NAO_INICIADA`, `EM_ANDAMENTO`, `FINALIZADA` ou `PARCIAL`; indicar pendências e data da conclusão. `FINALIZADA` registra a conclusão da execução, ainda sujeita à revisão |
| Estado do ciclo | Um dos estados da seção 5; `APROVADO` exige a verificação do Codex e `INTEGRADO` exige incorporação conferida no destino informado |
| Git da entrega | `SEM_ALTERACOES`, `NAO_COMMITADO`, `PARCIALMENTE_COMMITADO`, `COMMITADO` ou `NAO_VERIFICADO`; listar hashes da tarefa e arquivos ainda fora dos commits, inclusive não rastreados |
| Branch e base | Branch de trabalho, base com hash, destino previsto e branch principal confirmada ou `NAO_VERIFICADO`; registrar `HEAD` separado dos commits da tarefa |
| Publicação | `NAO_PUBLICADO`, `PARCIALMENTE_PUBLICADO`, `PUBLICADO`, `NAO_VERIFICADO` ou `NAO_SE_APLICA`, sempre para a versão identificada; quando publicado, informar remoto/branch e hash confirmado |
| PR remoto | Número/link e estado observado (`ABERTO`, `FECHADO_SEM_MERGE`, `MERGEADO`, `NAO_ABERTO` ou `NAO_VERIFICADO`); ID lógico como B01 não comprova PR no GitHub |
| Integração | `NAO_INTEGRADO`, `INTEGRADO`, `NAO_VERIFICADO` ou `NAO_SE_APLICA`, com branch de destino e hash resultante quando integrado; informar separadamente se chegou à principal |

Exemplo fictício: **B01 — entrega FINALIZADA; ciclo APROVADO; COMMITADO em `feat/b01-fundacao-api` no hash registrado; PUBLICADO em `origin/feat/b01-fundacao-api`; NAO_INTEGRADO em `main`.** Nesse cenário o trabalho foi concluído e revisado, mas ainda não chegou à principal. Também é possível entregar ou aprovar um diff local `NAO_COMMITADO`; o registro identifica seus arquivos e a evidência examinada.

Um commit existente seguido de novas alterações da tarefa é `PARCIALMENTE_COMMITADO`. Um push de uma versão anterior não publica automaticamente a atual. Alterações de outra tarefa são listadas separadamente e não mudam a situação Git da entrega examinada.

Se houver integração numa branch intermediária, registrar esse destino e manter explícita a situação perante a principal. Fechar um PR remoto sem merge não significa integração. Após squash, rebase ou cherry-pick, registrar o mapeamento entre versão aprovada e commit resultante e verificar o conteúdo; o hash pode mudar.

### 5.2. Conferência antes de registrar

Inspecionar a raiz, a branch, o `HEAD`, o status, o diff não preparado e o diff preparado para commit. `git diff` sozinho não mostra arquivos não rastreados; consultar também `git status --short` e ler esses arquivos. Distinguir o hash da base do hash que contém a entrega.

Para confirmar publicação ou integração remota, usar evidência atual da operação ou consulta ao servidor. Referências locais como `origin/main` e `origin/HEAD` podem estar desatualizadas. Sem essa consulta, informar a referência local observada e marcar o estado remoto `NAO_VERIFICADO`, sem bloquear trabalho local independente.

Atualizar o registro antes de passar o trabalho e após cada operação Git. Incluir o registro pertinente no commit da tarefa quando houver commit autorizado. O hash desse commit só existe depois da gravação: registrar o hash verificado na atualização seguinte e indicar se essa atualização ainda não está commitada. Não criar ciclos de commits apenas para fazer um arquivo conter o próprio hash. Separar sempre **Git da entrega** de **Git da atualização do registro**.

## 6. Critérios de revisão e aceite

Um PR pode ser aprovado quando:

1. Entrega o comportamento ou artefato acordado, com as dependências necessárias disponíveis.
2. Mantém o escopo e os contratos combinados, sem incluir alterações alheias à tarefa.
3. Apresenta validação proporcional à mudança e aos critérios do plano, incluindo falhas e casos de borda relevantes.
4. Resolve os problemas impeditivos e registra as limitações restantes com clareza.
5. Identifica o método de análise, exemplos fictícios e integrações simuladas quando aplicável.
6. Traz instruções suficientes para reproduzir a execução e a verificação da entrega.

Para cada achado, usar um identificador estável, como `B02-R01`, e registrar: arquivo/linha ou cenário, comportamento observado, comportamento esperado, impacto e forma de verificar a correção.

**Impeditivo:** viola um critério acordado, quebra um contrato ou comportamento existente, produz resultado incorreto relevante, ou deixa sem evidência uma validação obrigatória. Precisa ser resolvido antes do aceite.

**Melhoria futura:** aprimoramento que não é necessário para os critérios atuais. Registrar separadamente; não ampliar o PR por preferência de estilo ou refatoração sem benefício demonstrado para a tarefa.

Relatórios distinguem testes aprovados, testes falhos e verificações não executadas, com o motivo. Se uma verificação obrigatória não puder ser executada por um agente, outro participante pode fornecer a evidência; até lá, aquele critério permanece pendente. Não inventar comandos executados, métricas, saídas ou aprovação de CI.

### Regras de produto a preservar

- Prospect recebe churn `nao_aplicavel`. Vínculo desconhecido ou falta de evidência não autorizam presumir baixo risco.
- Menção isolada a concorrente não comprova intenção de troca.
- Risco e oportunidade podem coexistir quando houver evidências para ambos.
- A análise deve evitar a colisão entre “satisfeito” e “insatisfeito”.
- Evidências apontam para trechos reais da entrada, preservando sua localização mesmo com texto repetido; horários só aparecem quando fornecidos pela transcrição.
- Ausência de sinal e informação insuficiente são situações distintas. Recomendações são sugestões sustentadas pelo conteúdo.
- O experimento com 14 reuniões sintéticas não comprova desempenho em produção. Seu reaproveitamento exige revisão das regras; a API não deve executar treinamento, downloads ou gráficos do notebook ao iniciar.
- Frontend apresenta a classificação recebida; regras de análise e credenciais ficam no backend.
- O áudio usa o mesmo serviço de análise do texto. Estados devem refletir o processamento real, inclusive falha e interrupção; nova tentativa tem identidade própria.

Aplicar cada regra nos PRs que a implementam ou consomem. B01 não precisa entregar funcionalidades previstas para B03 ou B09.

### Cuidados com o repositório

Confirmar a raiz Git e a pasta da aplicação antes de criar arquivos ou branches; não presumir que o diretório atual é a raiz. Preservar alterações preexistentes e incluir nos commits somente os arquivos da tarefa. Não mover pastas, reinicializar Git ou descartar alterações para “limpar” o ambiente sem uma solicitação específica.

Usar uma branch por PR, como `feat/b01-fundacao-api`, e registrar a base real. Correções feitas pelo Opus permanecem rastreáveis na mesma entrega. Segredos, arquivos de ambiente com credenciais e áudios privados não entram no versionamento.

## 7. Sequência de desenvolvimento e quadro inicial

O plano de desenvolvimento continua sendo a fonte dos critérios detalhados.
A tabela abaixo é a fotografia histórica inicial de 17/09/2026, anterior às
entregas B01–B04/C01 e à revisão de escopo abaixo. Todos começaram como
`PLANEJADO`; consultar o registro para o estado atual. Esta governança não
libera automaticamente a execução.

| ID | Entrega | Depende de | Estado inicial |
|---|---|---|---|
| B01 | Fundação da API e teste de saúde | — | `PLANEJADO` |
| C01 | Contrato de análise por texto | B01 | `PLANEJADO` |
| B02 | Sentimento e evidências | C01 | `PLANEJADO` |
| B03 | Sinais comerciais | B02 | `PLANEJADO` |
| B04 | Endpoint de análise e recomendações | B03 | `PLANEJADO` |
| C02 | Contrato de áudio, provedor, limites e executor | F06 e decisão de transcrição/orçamento | `PLANEJADO` |
| B05 | Persistência mínima | C02 | `PLANEJADO` |
| B06 | Recepção e validação interna de áudio | B05 | `PLANEJADO` |
| B07 | Adaptador de transcrição | C02 | `PLANEJADO` |
| B08 | Processamento e rotas de upload, estado e detalhe | B04, B06, B07 | `PLANEJADO` |
| B09 | Interrupção, nova tentativa e limpeza | B08 | `PLANEJADO` |
| B10 | Listagem de reuniões, opcional para a apresentação | B09 | `PLANEJADO` |
| I01 | Ensaio integrado da demonstração | F11 e B09 | `PLANEJADO` |

Os PRs de frontend seguem a sequência do plano e ficam com o responsável dessa frente. C01 e o contrato de áudio precisam estar alinhados antes da integração entre as frentes; a divisão C02-A/B abaixo permite preparação independente do backend.

| Marco do ConvIQ | O que comprova sua conclusão |
|---|---|
| Backend de análise textual disponível | B04 integrado e validado conforme C01 |
| Primeira versão utilizável por texto | F06 integrado: formulário → API real → card e evidências |
| Demonstração com áudio e nova tentativa | F09 integrado, incluindo B09-A/B e transcrição real; após reinício sem banco, orientar reenvio |
| Histórico navegável posterior | B05-A/B, B09-C, B10 e F10 integrados, com resultados acessíveis após reinício |
| Preparação da apresentação | I01 concluído no ambiente da apresentação, após revisão F11 |

### Ajuste de escopo — decisão do usuário em 18/09/2026

A exigência inicial de persistência mínima antes do áudio foi substituída:
o usuário não precisa apresentar persistência no dia, mas a deseja depois.
B05-A/B, recuperação durável B09-C e histórico B10/F10 ficam posteriores.
A demonstração pode guardar estados/resultados em memória e áudio temporário;
reinício perde estado e exige novo envio, sem prometer recuperação automática.
Continuam obrigatórios tratamento de falhas/timeout, identidade por tentativa,
limpeza e explicação desse comportamento ao usuário.

Transcrição deve ser somente gratuita; Whisper aberto é candidato permitido,
validado primeiro em B07-A. Execução por link no navegador é o objetivo e
permanece **A_RESOLVER** (H01), sem escolha de hospedagem ou implantação.
C02-A define contrato técnico e limites após B07-A, permitindo backend
independente; C02-B conserva o alinhamento com frontend após F06 antes de
concluir F07/F08. Assim, F06 deixa de bloquear pesquisa e backend de áudio,
mas continua requisito da integração pelo navegador.

O detalhamento vigente e as dependências que substituem o quadro inicial
estão em [PRs pequenos de áudio](docs/planejamento/PRS_BACKEND_AUDIO.md)
e no [plano](PLANO_DESENVOLVIMENTO.md). Este ajuste registra o pedido do
usuário; não atualiza nenhuma versão externa de governança adotada.

## 8. Relatório padrão de entrega

Codex, Sonnet e Opus usam este formato nas fichas de `REGISTRO_TRABALHO.md` e o resumem na resposta ao usuário. Em planejamento ou revisão sem implementação, adaptar os campos e indicar o que não se aplica. Não incluir saídas extensas quando um resumo verificável for suficiente.

```text
PR lógico ou tarefa e título:
Data e agente/papel: Codex/coordenador, Sonnet/executor ou Opus/revisor-corretor
Entrega do executor: NAO_INICIADA / EM_ANDAMENTO / FINALIZADA / PARCIAL
Estado do ciclo: conforme seção 5
Pasta do projeto e branch de trabalho:
Base de comparação e HEAD observado:
Destino previsto / branch principal: nomes confirmados ou NAO_VERIFICADO

Entrega: o que o ConvIQ passou a fazer neste escopo.
Arquivos alterados: principais arquivos e finalidade.
Critérios de aceite: cada critério → atendido ou pendente → evidência.
Validação: comando, diretório, resultado e uso de simulação, quando houver.
Não executado: verificação, motivo e impacto no aceite.
Limitações ou bloqueios:

Para revisão/correção:
Achado [ID] → confirmado e corrigido / não confirmado / pendente.
Justificativa, alteração e evidência de validação de cada achado.
Novos problemas encontrados e eventuais propostas fora do escopo.

Git da entrega: situação, hashes da tarefa e arquivos ainda sem commit.
Versão entregue / versão aprovada: hashes ou diff local identificado.
Publicação: situação da versão, remoto/branch, hash e evidência.
PR remoto: link/número e estado observado ou NAO_ABERTO / NAO_VERIFICADO.
Integração no destino: situação, branch, hash resultante e evidência.
Integração na principal: situação e branch explicitamente identificadas.
Git da atualização do registro: commitada / não commitada / não verificada.
Outras alterações preexistentes: separadas da entrega.
Próxima ação e responsável:
Evento acrescentado: identificador no histórico de REGISTRO_TRABALHO.md.
```

## 9. Modelos de prompts

Codex preenche os campos antes de entregar o prompt ao usuário. Não enviar campos indefinidos que impeçam a execução; registrar explicitamente o que não se aplica.

### 9.1. Execução pelo Sonnet

```text
Você é o executor do PR [ID — título] do ConvIQ.

Leia AGENTS.md, CLAUDE.md, SISTEMA_GOVERNANCIA_CONVIQ.md,
REGISTRO_TRABALHO.md e a seção pertinente de PLANO_DESENVOLVIMENTO.md.

Pasta de trabalho: [caminho confirmado].
Branch/base: [branch da tarefa e referência de origem].
Dependências verificadas: [IDs e evidências de integração].
Objetivo: [comportamento concreto que esta entrega habilita].
Escopo: [arquivos/áreas e mudanças necessárias].
Fora do escopo: [funcionalidades reservadas para outros PRs].
Contrato e decisões aplicáveis: [referências].
Critérios de aceite: [lista verificável].
Validações necessárias: [cenários e comandos conhecidos; registrar os usados].
Ações Git autorizadas: [trabalho local/commit/push/abrir PR, conforme atribuição].

Inspecione o estado atual, preserve mudanças preexistentes e implemente esta
tarefa. Resolva escolhas rotineiras dentro do escopo e explique as relevantes.
Se surgir uma dependência ou decisão indispensável não resolvida, registre-a
e avance no trabalho independente que ainda for possível.

Antes de devolver o trabalho, atualize sua ficha, o índice e o histórico em
REGISTRO_TRABALHO.md. Registre o que fez, validação, pendências, finalização,
branch, commits, push e integração separadamente, conforme a seção 8.
Inclua a situação Git da própria atualização do registro. Apresente o
relatório e aguarde a coordenação antes de iniciar outro PR.
```

### 9.2. Revisão e correção pelo Opus

```text
Você revisará e corrigirá a entrega do PR [ID — título] do ConvIQ.

Leia AGENTS.md, CLAUDE.md, SISTEMA_GOVERNANCIA_CONVIQ.md,
REGISTRO_TRABALHO.md, o escopo original e os contratos aplicáveis.
Pasta/branch: [caminho e branch].
Base e versão entregue: [referências ou diff local identificado].
Objetivo e critérios originais: [conteúdo].
Relatório do Sonnet: [conteúdo ou referência acessível].
Achados do Codex: [ID, localização, comportamento, impacto e validação esperada].
Ações Git autorizadas: [ações já autorizadas para esta rodada].

Confira se a versão disponível corresponde à indicada. Examine o diff completo
do PR e o código relacionado; não se limite ao relatório ou aos achados prévios.
Confirme os problemas antes de corrigir e justifique tecnicamente discordâncias.
Corrija falhas comprovadas dentro do escopo na mesma branch, com testes
pertinentes. Preserve os contratos e as alterações preexistentes.

Se não houver problema, relate a revisão sem criar mudanças artificiais.
Proponha separadamente melhorias fora do escopo; mudanças que afetem outras
entregas precisam retornar à coordenação.

Atualize sua ficha, o índice e o histórico em REGISTRO_TRABALHO.md, mesmo
se não houver correções. Entregue o relatório da seção 8, respondendo aos
achados e identificando validações, limitações, versão final e situação de
commit, push e integração, inclusive do registro. Aguarde a verificação
do Codex; não declare aprovação final nem inicie o próximo PR.
```

### 9.3. Retorno do usuário ao Codex

```text
O [Sonnet/Opus] entregou o [ID]. Analise a entrega conforme
SISTEMA_GOVERNANCIA_CONVIQ.md e os critérios do plano.

Referência da entrega: [branch/commit/link do PR ou diff local].
Relatório: [colar o relatório].

Confira o código, o Git e as evidências. Atualize a ficha, o índice e seu
evento em REGISTRO_TRABALHO.md, separando finalização, revisão, commit,
push e integração e distinguindo o que conferiu do que foi só relatado.
Se for a entrega inicial, prepare o prompt de revisão para o Opus.
Se for uma correção, verifique os achados e prepare nova rodada somente se
necessária; caso contrário, registre o aceite técnico e o próximo passo.
```

## 10. Continuidade e registro das decisões

O índice, as fichas atuais e o histórico de atuação têm uma única fonte: [REGISTRO_TRABALHO.md](REGISTRO_TRABALHO.md). Cada PR preparado ou iniciado recebe uma ficha com os campos da seção 8; tarefas de documentação ou coordenação usam um ID próprio, sem simular um PR remoto. A tabela da seção 7 e o registro inicial abaixo permanecem como contexto histórico.

Cada agente atualiza a ficha e o índice e acrescenta um evento antes de passar o trabalho ou encerrar sua atuação. O evento contém data (e fuso se usar horário), agente/papel, PR/tarefa, ação realizada, arquivos/versão, validação e resultado, pendências e próximo responsável. Eventos anteriores não são apagados; uma correção referencia o evento corrigido. Não registrar credenciais, áudios privados ou conteúdo sensível.

Uma revisão só relatada fica identificada como tal; o agente não assina pelo outro nem inventa ações antigas. Codex registra a aprovação após sua conferência. Caso o agente não possa editar o registro, deve declarar a limitação e fornecer o evento pronto para incorporação, sem afirmar que já o salvou.

Ao retomar, ler o índice, a ficha e os últimos eventos. Conferir a raiz Git, a branch, os commits e as alterações locais, inclusive não rastreadas, e comparar com a versão registrada. Registrar divergências antes de continuar. Uma ficha ausente na branch atual não prova que o trabalho não existe em outra; consultar a branch/commit indicada antes de duplicá-lo. Mudanças em branches diferentes precisam ter seus registros reconciliados na integração, preservando todos os eventos e o estado verificado.

### Registro inicial

| Data | Decisão ou observação | Consequência |
|---|---|---|
| 17/09/2026 | Usuário definiu Codex como coordenador e Claude como executor/revisor/corretor | Adotado ciclo Sonnet → Codex → Opus → Codex |
| 17/09/2026 | Criado este documento de governança | Fluxo documentado; nenhum PR funcional iniciado nesta tarefa |
| 17/09/2026 | Backend ausente na inspeção local, consistente com o registro de perda no plano | Próxima tarefa de backend a preparar: B01, desde a fundação |

Permanecem abertas as decisões do plano sobre transcrição, custos, limites de áudio, hospedagem, eventual uso de modelo de linguagem, exigências acadêmicas e prazos. Devem ser resolvidas quando necessárias à entrega correspondente; não impedem preparar B01.

### Atualização em 17/09/2026 — versão 1.1

A pedido do usuário, Codex e Claude passam a registrar a própria atuação no arquivo compartilhado, com conclusão, revisão, commit, branch, push e integração separados. Foram criados os pontos de entrada `AGENTS.md` e `CLAUDE.md`. O estado atual, inclusive o preparo de B01 e a situação Git desta atualização documental, está em `REGISTRO_TRABALHO.md`.

## 11. Modo ágil (versão 1.2, vigente desde 08/10/2026)

Adotada após o aceite técnico EST01-03 e a integração do PR #3 no merge `4063830`. As instruções do usuário e as autorizações da sessão prevalecem. O registro de 7.000 linhas era lido e reescrito em toda atuação; o mesmo fato aparecia no registro, num relatório separado, no prompt e na resposta do chat.

### 11.1. Onde está cada coisa

- [STATUS.md](STATUS.md): estado atual, próximo passo, decisões abertas e armadilhas. **É a primeira leitura** de qualquer agente.
- [REGISTRO_TRABALHO.md](REGISTRO_TRABALHO.md): somente o índice (uma linha por PR) e a **única** fotografia Git vigente.
- `docs/registro/<ID>.md`: a ficha do PR e todos os seus eventos. `GERAL.md` guarda eventos de várias frentes; o conteúdo anterior a esta versão foi movido sem alteração, e o guia está em [docs/registro/README.md](docs/registro/README.md).

Ao retomar: STATUS → linha do PR → `docs/registro/<ID>.md` → Git e código da versão indicada. A conferência de raiz, branch, HEAD, status e alterações locais da seção 10 continua obrigatória.

### 11.2. Escrever uma vez

- Cada atuação acrescenta **um evento curto** (até ~25 linhas, formato em `docs/registro/README.md`) ao arquivo do PR. O evento é o relatório da seção 8: não se cria arquivo de relatório separado nem se repete o evento no chat, que traz até 10 linhas e aponta para o evento.
- A ficha só muda quando o estado do ciclo muda; a linha do índice e o `STATUS.md` idem. A fotografia Git vigente é **substituída**, sem acumular histórica.
- Prompts citam caminhos, commit e evento; não colam listas de hashes nem eventos anteriores. Quando o usuário precisa levar o resultado a outro agente, cola o evento (ou o link).

### 11.3. Git

- Com autorização do usuário para a entrega, executor e revisor podem commitar e dar push na branch de trabalho depois dos testes passarem, e devem incluir o registro no mesmo commit. A autorização dada na sessão continua válida dentro do seu escopo; registrar trabalho não concede autorização.
- Entrega commitada é identificada pelo hash do commit e por `git diff base..commit`. Enquanto houver alterações locais, registre HEAD, `git status`, diff local e arquivos não rastreados. Use SHA-256 quando necessário para fixar a versão de um arquivo ainda sem commit.
- Continuam dependendo de ordem do usuário: abrir ou fechar PR, merge, escrever na branch padrão, reescrever histórico, reset, stash e apagar branches. Registrar o hash do próprio commit do registro não exige novo commit.
- Trabalho em paralelo usa worktree isolado. O venv compartilhado pode ter instalação editável apontando para outra pasta: use `python backend/scripts/sondar.py ...` ou `PYTHONPATH=<checkout>/backend`, e rode `pytest` dentro de `backend/` do checkout.

### 11.4. Revisão proporcional ao risco

- **Nível A (lógica nova de associação, negação, índices, contrato público, segurança):** Sonnet executa, Opus revisa e corrige, Codex verifica. Exemplos: B14, B16, B17, B19, rotas de áudio.
- **Nível B (vocabulário, documentação, testes, scripts, ajustes sem regra nova):** Sonnet executa e Codex verifica; o Opus entra se o Codex encontrar achado impeditivo. Exemplo: B15.
- O Codex indica o nível no cartão ou no prompt. PRs podem compartilhar branch somente por decisão expressa da coordenação, após conferir dependências, base e critérios de aceite separados. Igual nível ou arquivos em comum não bastam. A premissa de B19 deve ser revista à luz das evidências aninhadas de B12 antes de liberá-lo.

### 11.5. Contraprovas obrigatórias nos cartões

Todo cartão que cria ou muda uma regra que **suprime, rejeita ou limita** um sinal traz uma lista de contraprovas, e o executor escreve o teste de cada uma: (1) o sinal válido vizinho sobrevive (ex.: B13-R01, uma ação alheia depois não pode apagar a intenção anterior); (2) a mesma entrada afirmativa curta continua produzindo o sinal; (3) a regra não altera outro serviço (churn, sentimento, catálogo). Achado desse tipo na revisão é falha do cartão e do teste, não só do código.

### 11.6. Sondagem reproduzível

`python backend/scripts/sondar.py "frase" ...` passa pela composição real, imprime sentimento, churn, oportunidades e recomendações, e falha se algum recorte de evidência não for literal ou se uma referência não existir. Use-o em vez de escrever scripts avulsos; `--vinculo` e `--json` estão disponíveis.
