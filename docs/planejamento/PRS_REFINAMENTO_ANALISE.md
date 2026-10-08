# Refinamento das capacidades de análise — PRs pequenos

Planejamento do Codex em 19/09/2026, a pedido do usuário (PLN02).
Objetivo: melhorar a confiabilidade e a utilidade da análise já implementada,
sem depender do áudio, de banco ou de serviços pagos. Os identificadores
B11–B21 são identificadores de PRs lógicos. B11/B12 foram integrados pelo
PR #1; B13 está preparado para execução e os demais seguem planejados. O
estado remoto atual fica no registro de trabalho.

## Base e problemas reproduzidos

Base de aplicação: `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`, com
B01–B04/C01 aprovados tecnicamente. Branch observada nesta preparação:
`spike/b07-a-viabilidade-whisper`; o experimento B07-A continua parcial e
fora do commit. Publicação, principal e destino atuais: `NAO_VERIFICADO`.

Codex executou os exemplos abaixo em `compor_analise_texto`, usando vínculo
`cliente`. São observações do código atual, não problemas hipotéticos nem
afirmações de que os refinamentos já foram feitos.

| Entrada | Resultado atual relevante | Refinamento |
|---|---|---|
| “Não estamos satisfeitos com o suporte.” | Sentimento positivo | B11 |
| “Não vamos cancelar o contrato.” | Sinal de churn e recomendação de retenção | B12 |
| “Vamos cancelar a reunião de amanhã.” | Sinal de churn | B12 |
| “Não temos interesse em conhecer o Fluig.” | Duas oportunidades e duas recomendações | B13 |
| “O módulo atual está instalado.” | Uma oportunidade, só pela palavra “módulo” | B13 |
| “O suporte é péssimo.” com acentos decompostos (NFD) | Sentimento insuficiente | B14 |
| “O suporte foi frustrante.” | Sentimento insuficiente | B15 |
| “O analista sênior apresentou o sistema.” | Concorrente Senior | B16 |
| “Temos interesse em conhecer o Fluig.” | Duas oportunidades sem associação explícita ao produto e sugestões iguais | B17, B18, B20 |
| “Estamos insatisfeitos com o suporte.” | Duas evidências do mesmo intervalo | B19 |

As limitações de B02–B04 foram aceitas no escopo anterior. Este pedido
autoriza planejar sua evolução; não invalida os aceites históricos.

## Decisões de escopo

- Priorizar falsos positivos e sentido da frase antes de ampliar vocabulário.
- Continuar com regras locais e determinísticas nesta rodada. Manter
  `metodo="regras"`; alterar `versao_analise` quando o comportamento mudar.
  Nenhuma contratação, API paga, treinamento ou dependência de modelo novo.
- Preservar formato, enums e rotas de C01. Usar estruturas internas para
  intenção/ocorrência/produto quando necessário; não acrescentar campos públicos
  silenciosamente. Exemplos e descrição do comportamento mudam com cada PR.
- Negar um problema não prova satisfação; negar cancelamento não garante baixo
  risco real. Preferir ausência de sinal ou informação insuficiente conforme
  o contexto disponível, sem inventar confiança, porcentagens ou intensidade.
- Cada regra de negação deve ter alcance limitado à expressão/oração relevante;
  pontuação e mudança de oração importam. Não aplicar “há um não na reunião,
  então inverter tudo”. Os cartões fixam casos mínimos, sem prometer interpretar
  qualquer frase em português, ironia, discurso indireto ou autoria das falas.
- Não adicionar resumo livre, tarefas, responsáveis, grupos ou aprendizagem
  automática. São novas capacidades futuras, não correção do analisador atual.
- A evidência deve incluir o contexto que muda o sentido (por exemplo, o “não”)
  quando necessário. Sempre recortar da transcrição devolvida, sem paráfrase
  no campo `trecho`. Índices continuam caracteres Python, fim exclusivo.

Essas escolhas técnicas permitem estruturar os PRs sem nova decisão obrigatória
do usuário. Expandir para modelo de linguagem, novo contrato ou probabilidades
exige proposta separada, com objetivo e avaliação definidos antes da adoção.

## Ordem, prioridade e dependências

| Ordem | PR | Entrega | Dependências |
|---|---|---|---|
| 1 | B11 | Negação no sentimento | B04, C01 |
| 2 | B12 | Risco de cancelamento com contexto local | B11 |
| 3 | B13 | Oportunidade somente com intenção comercial | B11 |
| 4 | B14 | Acentos/Unicode com posições corretas | B11, B12, B13 |
| 5 | B19 | Unificar evidências idênticas | B14 |
| 6 | B15 | Vocabulário de sentimento com cobertura controlada | B11 |
| 7 | B16 | Menções de produtos/concorrentes menos ambíguas | B04, C01 |
| 8 | B17 | Agrupar sinais da mesma oportunidade | B13 |
| 9 | B18 | Associar oportunidade ao produto explícito | B16, B17 |
| 10 | B20 | Recomendações específicas e sem repetição | B12, B18, B19 |
| 11 | B21 | Avaliação reproduzível da análise refinada | B15, B20 |

B11–B14 são a prioridade de confiabilidade. B19 tem baixo acoplamento à
semântica e vem logo depois. A sequência sugerida reduz edições concorrentes
em `sinais_comerciais.py` e `analise.py`; independência lógica não autoriza
dois executores a editar os mesmos arquivos ao mesmo tempo.

Todos os cartões: **PLANEJADO / execução NAO_INICIADA / revisão pendente /
SEM_ALTERACOES de implementação / sem commit próprio / branch proposta não
criada / sem publicação ou integração por esta atuação**. Destino/principal
e PR remoto devem ser confirmados na execução, nunca inferidos pelo ID lógico.

## Cartões de execução

### B11 — Interpretar negação simples no sentimento

- **Branch:** `fix/b11-negacao-sentimento`.
- **Problema:** palavra positiva gera classificação positiva mesmo quando negada.
- **Escopo/arquivos:** `services/sentimento.py`, auxiliar pequeno de contexto em
  `services/texto.py` ou módulo específico, testes de sentimento/composição,
  README e notas do contrato. Em B11, só sentimento consome a nova regra.
- **Política verificável:** “Não estamos satisfeitos.” e “Não gostei do
  atendimento.” → negativo. “Sem problemas.”, “Nenhum problema até agora.”
  e “Não foi ruim.” isolados → `informacao_insuficiente`, sem contar a palavra
  negativa como reclamação e sem inventar elogio. “Não houve atraso. Estamos
  satisfeitos.” → positivo; o primeiro “não” não alcança a segunda frase.
  “Não só estamos satisfeitos, como adoramos o atendimento.” mantém os elogios.
- **Aceite/testes:** pares afirmativo/negado, pontuação, frase seguinte,
  repetição e construção “não só”; evidência negativa contém a expressão
  negada e recorta exatamente a resposta. Preservar empate e ausência de sinal.
  Atualizar os testes que hoje fixam a limitação, explicando a nova expectativa.
- **Exclusões:** churn, oportunidades, inferência de ironia, negação dupla
  geral, resolver “o problema foi resolvido” ou normalização NFD (B14).
  Não remover o sentido negativo de toda frase apenas pela presença de “sem”.

### B12 — Avaliar risco no contexto da relação comercial

- **Branch:** `fix/b12-contexto-risco`.
- **Problema:** “cancelar” é suficiente para gerar churn, qualquer que seja
  o objeto ou a negação. O contexto comercial atual também aceita termos
  genéricos como “sistema” fora do domínio.
- **Escopo/arquivos:** detecção de risco e contexto em `sinais_comerciais.py`,
  reutilizando limites de contexto de B11; testes comerciais e de composição.
  Regras locais explícitas para cancelamento/reavaliação/rescisão de contrato,
  serviço ou fornecedor, e insatisfação atual com essa relação.
- **Aceite/testes:** “Não vamos cancelar o contrato.” → `sem_sinal_detectado`;
  “Vamos cancelar a reunião.” → `informacao_insuficiente` quando isolada;
  “Vamos cancelar o contrato.” → sinal; “Se o suporte continuar assim,
  vamos cancelar o contrato.” → sinal, preservando ameaça condicional real.
  “Vamos reavaliar a pauta.” e “O sistema solar é extenso.” não tornam uma
  conversa comercial. Insatisfação com o suporte pode continuar sinalizando
  risco, inclusive “Não estamos satisfeitos com o suporte.”; não exigir sempre
  a palavra “cancelar”. Cada caso positivo tem evidência do contexto relevante.
- **Limite:** história remota, citação e atribuição de quem fala exigem análise
  mais ampla e ficam declaradas. Não prometer que frases não cobertas serão
  todas entendidas. Prospect continua `nao_aplicavel`; concorrente isolado
  não implica troca; não zerar oportunidades quando existe risco.
- **Exclusões:** escore/probabilidade de churn, diarização e classificador novo.

### B13 — Exigir intenção para sinalizar oportunidade

- **Branch:** `fix/b13-intencao-oportunidade`.
- **Problema:** substantivos e interesse negado geram oportunidade comercial.
- **Escopo/arquivos:** padrões de intenção em `sinais_comerciais.py`, testes
  comerciais/composição e exemplos. Exigir expressão afirmativa de interesse,
  avaliação comercial, expansão, contratação ou necessidade de solução,
  limitada à oração; reconhecer pedidos simples, sem inferência generativa.
- **Aceite/testes:** “Não temos interesse em conhecer o Fluig.” e “O módulo
  atual está instalado.” → nenhuma oportunidade. “Queremos conhecer o Fluig.”
  e “Precisamos automatizar o faturamento.” → oportunidade. “Quero conhecer
  a cidade.” não é comercial. “Não queremos o Fluig, mas temos interesse no
  Protheus.” mantém somente a intenção afirmativa sobre Protheus; a lista de
  produtos citados ainda pode conter ambos. Sinais de risco podem coexistir.
- **Exclusões:** agrupamento de intenções (B17), associação pública a produto
  (B18), previsão de venda e oportunidades baseadas apenas em catálogo.

### B14 — Normalizar texto sem perder os índices originais

- **Branch:** `fix/b14-unicode-evidencias`.
- **Problema:** acentos decompostos não casam com os padrões atuais; normalizar
  removendo caracteres sem mapa quebraria os destaques no frontend.
- **Escopo/arquivos:** `texto.py`, adaptação dos consumidores de normalização,
  testes do utilitário/sentimento/sinais/composição. Retornar texto para busca
  e mapa de intervalos para a transcrição original, mantendo o eco de C01.
- **Aceite/testes:** NFC e NFD de “péssimo”/“ótimo” têm a mesma classificação;
  recortes incluem os caracteres combinantes corretos. “Não”/“não só” em NFD
  preservam a negação, sua exceção e o escopo; um sinal válido depois de NFD
  ou depois de trecho negado não desaparece. Repetições, emoji antes do sinal,
  quebras de linha e limites de expressão permanecem corretos.
  Nenhum ID/trecho é obtido por busca da primeira ocorrência com `find`.
- **Exclusões:** mudar índices para bytes/UTF-16, alterar transcrição ecoada,
  timestamps e limpeza destrutiva de palavras/pontuação.

### B15 — Ampliar vocabulário de sentimento com exemplos negativos de controle

- **Branch:** `feat/b15-vocabulario-sentimento`.
- **Problema:** expressões comuns como “frustrante” e “reclamou” ficam sem sinal.
- **Escopo/arquivos:** léxico de `sentimento.py`, tabela pequena e explícita
  de exemplos em testes/fixtures e README. Primeira ampliação limitada às
  famílias “frustrante”, “decepcionado/decepcionante”, “reclamou/reclamaram” e
  “satisfeitíssimo”; registrar grafias/flexões aceitas, sem dicionário ilimitado.
- **Aceite/testes:** “O suporte foi frustrante.” → negativo;
  “Estamos satisfeitíssimos.” → positivo; negação continua respeitada,
  inclusive “Não estamos satisfeitíssimos.”. Palavra parecida não casa por
  substring; novos sinais não alteram churn por simples mudança de sentimento.
  Cada padrão novo vem com frase de uso e contraexemplo pertinente.
- **Exclusões:** expandir ao mesmo tempo léxico de risco/produtos, sentimentos
  por participante, intensidade numérica ou alegação de cobertura geral.

### B16 — Reduzir ambiguidade nas menções do catálogo

- **Branch:** `fix/b16-mencoes-catalogo`.
- **Problema:** “sênior” como cargo vira concorrente Senior; termos genéricos
  e siglas curtas também podem coincidir com marcas do catálogo atual.
- **Escopo/arquivos:** padrões/aliases internos do catálogo em
  `sinais_comerciais.py`, testes e critérios documentados. Manter nomes
  canônicos e as listas de strings do contrato; não consultar catálogo externo.
- **Aceite/testes:** “analista sênior” não gera Senior; “software da Senior”
  gera Senior. “TOTVS RM”/“sistema RM” geram RM, mas “exame de RM” não.
  “Analytics” genérico sem contexto de produto não basta; “produto Analytics”
  permite a menção. Protheus, Datasul, Fluig, SAP, Oracle e Sankhya continuam
  reconhecidos nos contextos explícitos já cobertos. Ordem e nomes únicos
  preservados; menção isolada continua sem implicar churn ou oportunidade.
- **Exclusões:** reconhecimento arbitrário de marcas, correção aproximada de
  nomes transcritos pelo Whisper, evidências públicas novas para entidades.
  Alias novo exige exemplo inequívoco e sua justificativa, sem inventar marcas.

### B17 — Agrupar palavras que expressam a mesma oportunidade

- **Branch:** `fix/b17-agrupar-oportunidades`.
- **Problema:** “interesse em conhecer” produz duas oportunidades para uma ação.
- **Escopo/arquivos:** montagem de oportunidades em `sinais_comerciais.py`,
  testes e exemplos. Agrupar gatilhos da mesma intenção local, mantendo suas
  evidências. Documentar chave de agrupamento e limites da oração/ação.
- **Aceite/testes:** “Temos interesse em conhecer o Fluig.” → uma oportunidade;
  “Queremos conhecer o Fluig e expandir as licenças do Protheus.” mantém duas
  ações. Ocorrências em frases distintas preservam suas evidências e não
  são colapsadas só por ter o mesmo texto. Não agrupar toda a reunião num item.
- **Exclusões:** escolher produto por proximidade global, reescrever ações ou
  alterar a regra de sentimento/churn. B18 associa a referência explícita.

### B18 — Descrever a oportunidade com seu objeto explícito

- **Branch:** `feat/b18-oportunidade-produto`.
- **Problema:** a descrição atual repete uma palavra, sem dizer a que se refere.
- **Escopo/arquivos:** contexto interno das oportunidades e montagem de
  `descricao` em `sinais_comerciais.py`, testes de composição e contrato.
  Associar somente produto/necessidade explicitamente ligados à intenção na
  oração; registrar metadados internos reutilizáveis pela composição B20.
- **Aceite/testes:** interesse em conhecer Fluig → descrição cita Fluig e a
  intenção; necessidade de automatizar faturamento → descreve a necessidade
  sem inventar produto. “Usamos Protheus. Queremos conhecer o Fluig.” não
  associa Protheus à intenção da segunda frase. Alvos explicitamente múltiplos
  podem ser descritos juntos ou separados por ação, segundo regra documentada;
  alvo ambíguo mantém descrição genérica baseada no trecho, sem adivinhar.
- **Exclusões:** novos campos públicos, resolver pronomes entre falas, atribuir
  proposta, orçamento ou prazo ausente. `produtos` continua sendo menções,
  não lista de produtos que o cliente certamente vai comprar.

### B19 — Compartilhar uma evidência entre os sinais que a utilizam

- **Branch:** `fix/b19-unificar-evidencias`.
- **Problema:** sentimento e churn podem devolver cópias do mesmo intervalo.
- **Escopo/arquivos:** `analise.py`, testes de composição/schema/HTTP e nota
  do contrato. Unificar por `(inicio, fim, trecho)` e remapear todas as
  referências para o ID resultante, preservando ordem determinística.
- **Aceite/testes:** duplicata exata vira uma evidência; churn, oportunidades
  e recomendações mantêm referências existentes e sem repetição interna de
  ID. Duas ocorrências iguais em posições diferentes permanecem distintas;
  intervalos apenas sobrepostos não são unidos automaticamente. Recortes de
  C01 válidos, inclusive NFD de B14. Schema/OpenAPI mantêm o formato atual.
- **Exclusões:** alterar sinal detectado, deduplicar somente pelo texto,
  acrescentar campo de origem ou depender de ID fixo entre versões de análise.

### B20 — Gerar recomendações específicas e sustentadas

- **Branch:** `feat/b20-recomendacoes-contextuais`.
- **Problema:** sugestões genéricas se repetem e pouco ajudam a agir.
- **Escopo/arquivos:** composição/recomendações em `analise.py`, metadados
  internos de B12/B18 se necessários, testes e exemplos. Templates pequenos
  por intenção e contexto explícitos; fallback genérico quando faltar contexto.
  Não interpretar o texto de uma descrição gerada como se fosse dado estruturado.
- **Aceite/testes:** interesse em conhecer Fluig → sugerir apresentação do
  Fluig; risco associado ao suporte → sugerir investigar a insatisfação com
  o suporte. Cada sugestão cita evidência que sustenta ação e objeto; uma
  intenção não gera sugestões idênticas. Risco e oportunidade mantêm suas
  ações; prospect nunca recebe recomendação de retenção baseada em churn.
- **Exclusões:** executar ação, mandar mensagem, marcar reunião, atribuir
  responsáveis/prazos/valores ou inventar causa não presente na transcrição.
  Não converter sugestão em diagnóstico ou promessa de resultado comercial.

### B21 — Medir os ganhos com um conjunto pequeno de avaliação

- **Branch:** `test/b21-avaliacao-analise`.
- **Problema:** passar nos testes de implementação não demonstra qualidade
  em reuniões diferentes das frases usadas para construir cada regra.
- **Escopo/arquivos:** `backend/tests/fixtures/avaliacao_analise.json`, um
  avaliador simples em `backend/scripts/` se os testes existentes não bastarem,
  e relatório em `docs/validacao/qualidade-analise.md`. Manter um conjunto de
  regressão e outro de frases inéditas para avaliação, rotulados explicitamente.
- **Aceite/validação:** cobrir afirmação/negação, risco/oportunidade simultâneos,
  prospect, silêncio textual/sem sinal, catálogo ambíguo, Unicode, repetição
  e contexto insuficiente. Pelo menos duas variantes por categoria, evitando
  só copiar os exemplos dos cartões. Registrar contagens de falsos positivos,
  falsos negativos e classificações por campo; taxas sempre com denominador.
  Identificar versão/commit/diff avaliado e comparar à base quando executável
  isoladamente. Casos obrigatórios de cada PR e integridade das evidências
  devem passar; falhas novas viram achados, não regras adicionadas escondidas.
- **Exclusões:** declarar precisão de produção a partir de amostra pequena,
  usar dados privados sem autorização, treinar modelo, mexer em heurísticas
  neste mesmo PR ou refazer B07-A. Nenhum desempenho de áudio é inferido daqui.

## Validação e entrega comuns

Cada PR deve incluir testes do comportamento que muda e de seus contraexemplos,
não testes que apenas copiem a implementação. Rodar os testes afetados e a
suíte de backend antes da entrega, pois os serviços compartilham texto e evidências.
Não esconder regressão removendo testes sem justificar a regra que mudou.

**Contraprovas obrigatórias (governança 11.5).** Todo cartão que cria ou muda
uma regra que suprime, rejeita ou limita um sinal traz o teste de: (1) o sinal
válido vizinho sobrevive à regra (uma ação alheia, negada ou sem objeto no
mesmo texto não apaga outra intenção ou sinal legítimos); (2) a entrada
afirmativa curta continua produzindo o sinal, com e sem o contexto extra; (3)
serviços e regras não relacionados (churn, sentimento, catálogo) não mudam.
Cartões de nível A (11.4) são revisados pelo Opus; os de nível B seguem só
com o Codex, salvo achado impeditivo. B14, B16, B17 e B19 são nível A; B15 é
nível B. Agrupamento depende de decisão expressa do Codex após conferir
dependências e critérios; B18, B20 e B21 são classificados ao preparar o prompt.

As invariantes de produto continuam: prospect sem churn aplicável; concorrente
isolado sem risco de troca presumido; risco e oportunidade podem coexistir;
ausência de sinal difere de informação insuficiente; sugestões são sugestões;
evidência deve existir na transcrição devolvida com referências válidas.

Para toda mudança observável, atualizar `versao_analise` (B11 começa em `0.2`;
os seguintes escolhem a próxima versão a partir da base real), README e notas
de C01 sem alterar os exemplos históricos silenciosamente. Comunicar ao frontend
mudanças no conteúdo/quantidade de evidências e oportunidades, mesmo mantendo
o JSON compatível. Nunca prometer IDs persistentes entre execuções/versões.

Claude Sonnet executa **um PR por vez**, Opus revisa e Codex verifica conforme
a governança. Uma branch por PR, com base real conferida e dependências disponíveis;
PRs empilhados precisam declarar ordem e base. Preservar PLN01/B07-A locais,
sem descarte, stash automático ou reescrita dos commits anteriores. Trabalho
documental desta rodada não autoriza commit, push, PR remoto ou integração.

## Relação com os demais trabalhos

- Áudio permanece no [roteiro existente](PRS_BACKEND_AUDIO.md), começando pela
  conclusão de B07-A. Refinamento de texto não depende de fechar essa amostra;
  este plano não cancela nem aprova o experimento parcial.
- B08-B continuará chamando o mesmo `compor_analise_texto`; refinamentos
  revisados poderão beneficiar as transcrições de áudio sem duplicar o motor.
  C02 não deve congelar o valor literal da versão do analisador.
- Persistência/histórico ficam posteriores e execução por link em H01 continua
  **A_RESOLVER**, conforme decisão já recebida. Frontend/F06 não foi comprovado
  nesta cópia; não declarar card ou fluxo pelo navegador pronto por estes PRs.
- Limitações que continuam depois desta série: ironia, autoria das falas,
  relações entre falas distantes, interpretação de histórico e compreensão
  ampla. Caso necessário, planejar avaliação de modelo aberto em outra tarefa,
  comparando ganhos e recursos; não há decisão de substituir as regras agora.

Próxima implementação desta frente: **B13**, agora com B11/B12 integrados
no merge `e31e6ba` da branch padrão. O prompt vigente está em
[prompt.md](../../prompt.md).
O [prompt de B11](PROMPT_B11_NEGACAO_SENTIMENTO.md) permanece como histórico
da execução já aprovada tecnicamente. A instrução original de B07-A está
preservada em [cópia de retomada](PROMPT_B07_A_VIABILIDADE_WHISPER.md),
pois a tarefa continua parcial.
Estado atual e eventos ficam em [REGISTRO_TRABALHO.md](../../REGISTRO_TRABALHO.md);
este roteiro complementa o [plano geral](../../PLANO_DESENVOLVIMENTO.md).
