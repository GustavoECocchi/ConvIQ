# B11 — Negação simples no sentimento — Claude Sonnet

Implemente somente B11 do ConvIQ, primeiro PR da frente de refinamento da
análise. O pedido do usuário foi melhorar as capacidades já implementadas
em PRs pequenos; o roteiro completo está em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md`. Não execute a série toda.

## Leitura e retomada

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md`, índice/fichas
PLN02 e B11 em `REGISTRO_TRABALHO.md`, a seção de refinamento no
`PLANO_DESENVOLVIMENTO.md`, o cartão B11 e as regras comuns do novo roteiro,
`docs/contratos/analise-texto.md`, README e serviços/testes de texto.

- Pasta: `/home/gustavoecocchi/Documents/CONVIQ`.
- Base de aplicação disponível: `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`,
  contendo B01–B04/C01 aprovados tecnicamente. Não refazer essas entregas.
- Branch observada no planejamento: `spike/b07-a-viabilidade-whisper`.
  B07-A continua PARCIAL, com scripts/relatório/amostra ainda não commitados.
- Também existem mudanças locais de PLN01, ANA02 e PLN02 no plano,
  governança, registro, prompt e roteiros de planejamento. Conferir o status
  real incluindo não rastreados; não atribuir esse conteúdo ao HEAD.
- Branch proposta para B11: `fix/b11-negacao-sentimento`, ainda não criada.
  Confirmar base antes de criar/reutilizar; uma branch por PR. Ao receber
  este prompt, preparar trabalho e branch locais preservando o que já existe;
  se optar por worktree, levar explicitamente as instruções locais necessárias.
  Não descartar alterações ou usar stash/reset automático. Não incluir
  implementação de Whisper na entrega B11.
- Principal, destino, publicação e PR remoto atuais: NAO_VERIFICADO;
  referência local de remoto não comprova integração.
- Este prompt não autoriza commit, push, abertura de PR remoto ou merge.
  O prompt B07-A anterior foi preservado em
  `docs/planejamento/PROMPT_B07_A_VIABILIDADE_WHISPER.md` para retomada;
  não foi cancelado, finalizado nem aprovado por esta troca de foco.

Registre divergências de branch/base/arquivos antes de editar. Preserve o
histórico dos agentes. Execute somente o escopo de sentimento descrito abaixo.

## Problema reproduzido e objetivo

Na versão atual, `compor_analise_texto` recebe “Não estamos satisfeitos com o
suporte.” e devolve sentimento positivo, com evidência apenas “satisfeitos”.
O README e `test_sentimento.py` registram essa limitação aceita em B02.
O novo pedido permite corrigi-la com regras locais explícitas, sem API paga,
modelo de linguagem ou ampliação arbitrária do vocabulário.

## Casos obrigatórios

| Entrada isolada | Sentimento esperado |
|---|---|
| Estamos satisfeitos. | positivo |
| Não estamos satisfeitos. | negativo |
| Gostei do atendimento. | positivo |
| Não gostei do atendimento. | negativo |
| Estamos insatisfeitos. | negativo |
| Não estamos insatisfeitos. | informacao_insuficiente |
| Sem problemas. | informacao_insuficiente |
| Nenhum problema até agora. | informacao_insuficiente |
| Não foi ruim. | informacao_insuficiente |
| Não houve atraso. Estamos satisfeitos. | positivo |
| Não só estamos satisfeitos, como adoramos o atendimento. | positivo |
| Bom dia a todos. | informacao_insuficiente |

A política é conservadora: negação explícita de satisfação/agrado conta como
insatisfação, mas negar um problema não é prova de elogio. Sem outros sinais,
usar informação insuficiente nos casos acima; não marcar neutro por ausência.
“neutro” continua sendo empate de sinais positivos/negativos aceitos.

Limitar a negação à expressão/oração pertinente, com tratamento explícito de
pontuação e “não só”. Não inverter todos os sinais porque existe “não” em
qualquer lugar da transcrição. Incluir teste com duas orações em que uma
negação não apague o sinal independente da outra. Documentar construções não
cobertas; não prometer interpretação geral de português.

Evidência que sustenta sentimento negativo por negação deve conter o trecho
negado, incluindo “não”, e seus índices exatos na `transcricao` devolvida.
Manter ocorrências repetidas em posições diferentes e IDs válidos. Não usar
paráfrase no campo `trecho` nem normalizar o texto ecoado para facilitar recorte.

## Arquivos e limites

- `backend/app/services/sentimento.py`.
- Auxiliar pequeno em `backend/app/services/texto.py` ou módulo específico
  de contexto, apenas se necessário para não espalhar a regra.
- Testes de sentimento, utilitário e composição/rota afetados.
- `backend/app/services/analise.py`: apenas versão do método, inicialmente
  `0.2` sobre a base `0.1`, e compatibilidade estritamente necessária.
- README, notas pertinentes de C01 e registro da tarefa.

Não alterar schemas/enums/rotas públicas, normalização Unicode (B14), churn
(B12), oportunidades (B13), catálogo, agrupamento ou recomendações. Ao testar
pela API, ainda podem existir limitações comerciais da versão anterior:
registrá-las para B12/B13, não incorporá-las silenciosamente em B11.
Não corrigir ironia, contexto histórico, negação dupla geral ou a frase
“o problema foi resolvido” nesta entrega.

## Validação e entrega

Reproduzir o resultado atual antes de mudar. Substituir as expectativas dos
testes que fixavam a limitação apenas para construções cobertas por B11;
preservar os demais ou explicar a mudança. Escrever testes de comportamento
com pares afirmativo/negado, casos de fronteira, repetição, exceção “não só” e
recortes literais. Evitar testes que só reflitam detalhes internos da regra.

Rodar os testes afetados e a suíte do backend. Registrar comandos e resultado
real; não apresentar os 100 testes antigos como se fossem execução própria.
Manter prospect sem churn aplicável, concorrente isolado sem risco presumido,
risco e oportunidade coexistindo e referências de evidência consistentes.
Atualizar `versao_analise`, documentar o alcance limitado da melhoria e preservar
C01 compatível. Não apagar o histórico da limitação anterior para esconder a mudança.

Antes de devolver, atualizar índice/ficha B11 e acrescentar evento próprio em
`REGISTRO_TRABALHO.md`: execução, revisão, arquivos, evidências, pendências,
branch/base/HEAD, commit, push, PR e integração separados. Mudanças locais de
outras tarefas devem ser listadas à parte. Entregar relatório de critérios
atendidos e limites que continuam presentes.

Próximo responsável: Codex examina a entrega e prepara revisão pelo Opus.
Não se autoaprovar, integrar ou iniciar B12 automaticamente.
