# B07-A — Viabilidade do Whisper gratuito — Claude Sonnet

Execute apenas B07-A do ConvIQ e entregue para revisão. O restante do roteiro
é contexto, não autorização para desenvolver todos os PRs de uma vez.

## Pedido e decisões do usuário

O usuário pediu PRs pequenos para concluir o backend de áudio. Validou:
transcrição somente gratuita, podendo usar Whisper; persistência dispensada
na demonstração e desejada depois; acesso por link no navegador como objetivo,
com execução/hospedagem A_RESOLVER. Codex estruturou isso em PLN01.

Sua tarefa é verificar a implementação aberta do Whisper no ambiente disponível,
com áudio real fictício em português, e recomendar configuração reproduzível.
Não usar API paga, créditos promocionais ou fallback pago. Software gratuito
não comprova hospedagem gratuita. Não escolher ou publicar hospedagem agora.

## Leitura obrigatória e versão

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md`, índice e fichas
PLN01/B07-A em `REGISTRO_TRABALHO.md`, etapa 4 do `PLANO_DESENVOLVIMENTO.md`,
`docs/planejamento/PRS_BACKEND_AUDIO.md` (decisões, base e cartão B07-A),
`backend/README.md`, `backend/pyproject.toml` e o contrato C01 em
`docs/contratos/analise-texto.md`.

- Pasta: `/home/gustavoecocchi/Documents/CONVIQ`.
- Base de código observada pelo Codex em 18/09/2026:
  `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`, na branch
  `feat/b01-fundacao-api`. Contém B01–B04/C01 com aceite técnico.
- Base local anterior `master`: `3c52ea3ed0d3c3d38de5b9adf2a4a4ff320a1842`.
  Não partir dela sem as entregas de texto. Não refazer B01–B04.
- Destino/principal, publicação e PR atuais no servidor: NAO_VERIFICADO.
  Referência local `origin/feat/b01-fundacao-api` no mesmo hash não basta
  para afirmar push ou integração atual.
- O planejamento PLN01 está em alterações locais de `PLANO_DESENVOLVIMENTO.md`,
  `SISTEMA_GOVERNANCIA_CONVIQ.md`, `REGISTRO_TRABALHO.md`, este `prompt.md`
  e no novo `docs/planejamento/PRS_BACKEND_AUDIO.md`. Preservar esse material;
  não atribuí-lo ao commit 6169fec nem incluí-lo silenciosamente em outra entrega.
- Conferência anterior do Codex: 33/33 entradas de
  `docs/revisoes/2026-09-18-aceite-b04.sha256` conferem. Manifesto é histórico,
  não deve ser sobrescrito. A última suíte registrada de aplicação é 100/100
  em B04-04; nenhum teste foi reexecutado durante este planejamento.

Confira raiz, branch, HEAD, status inclusive não rastreados, diff e índice.
Se o estado mudou, registre a divergência antes de editar. Uma branch por
entrega: proposta `spike/b07-a-viabilidade-whisper`, a partir da base confirmada
com B04/C01. Ao encaminhar este prompt, o escopo é trabalho local e branch
local da tarefa, preservando mudanças existentes; não há autorização neste
prompt para commit, push, abertura de PR remoto, merge ou implantação.
Se a branch proposta já existir, inspecione antes de reutilizar. Não troque
para uma base incompatível, descarte alterações ou use stash/reset automático.
A eventual criação da branch não publica nem integra as dependências.

## Entrega pequena e verificável

1. Inventariar Python, CPU/RAM, GPU quando disponível, FFmpeg/FFprobe e espaço
   livre, sem imprimir segredos. O ambiente da API foi observado com Python
   3.14; não presumir compatibilidade dos pacotes de transcrição com ele.
2. Preparar experimento em ambiente virtual separado. Dependências opcionais
   de áudio não entram em `backend/pyproject.toml` nesta tarefa. Se precisar
   de outra versão Python, usar instalação isolada já disponível ou registrar
   a necessidade; não alterar o runtime da API ou pacotes globais. Downloads
   devem ser explícitos, nos diretórios adequados, com limites de recurso
   razoáveis; cumprir as permissões da ferramenta quando exigidas.
3. Começar com modelo multilíngue pequeno, como `base`, configurável pelo script.
   Registrar versões, origem dos pesos e comandos reproduzíveis de preparação
   e execução. Pesos, cache e ambientes virtuais não entram no Git. Nada de
   download/carregamento ao importar a aplicação FastAPI.
4. Usar áudio falado real fictício em português (curto, inicialmente 30–60s)
   com termos comerciais e texto esperado conhecido. Reutilizar amostra local
   adequada se houver; senão, usar amostra pública com licença/origem registrada
   ou solicitar uma gravação fictícia ao usuário. Não substituir a prova por
   mock; amostra sintetizada, se usada como apoio, deve ser identificada e não
   substitui o ensaio falado. Não enviar áudio privado a serviços externos.
5. Medir duração do áudio, tempo de transcrição, memória observada ou limite
   dessa medição, texto reconhecido e divergências relevantes. Testar também
   silêncio e arquivo inválido. Não inventar métricas de precisão, falantes ou
   timestamps. Não concluir capacidade para áudio longo a partir de clipe curto.
6. Recomendar modelo/runtime, executor com concorrência e timeout controlados,
   formatos e limites iniciais conservadores para C02-A. O ambiente disponível
   comprova apenas esse ambiente; acesso por link e infraestrutura final ficam
   a resolver. Se a máquina não suportar execução viável, descrever o bloqueio
   e opções gratuitas a avaliar, sem escolher serviço pago.

## Arquivos previstos

- `docs/decisoes/transcricao-whisper.md`: relatório de viabilidade com comandos,
  ambiente, versões/modelo, evidência real, limites e recomendação para C02-A.
- `backend/scripts/verificar_whisper.py` (ou nome equivalente): entrada CLI
  para o experimento, sem importação pelas rotas. Pequeno e reproduzível.
- Arquivo de dependências experimentais separado e instruções de instalação.
- `.gitignore` somente se faltar exclusão específica para os novos artefatos.
- `REGISTRO_TRABALHO.md`: atualizar ficha B07-A/índice e acrescentar evento próprio.

Não criar banco, rotas de áudio, frontend, executor de produção ou histórico.
Não reformular o analisador de regras nem alterar o contrato de texto.
Não introduzir infraestrutura de avaliação maior que este experimento.

## Aceite e validação

B07-A está completo quando outra pessoa consegue reproduzir uma transcrição
Whisper real de áudio fictício em português, com configuração gratuita e
limitações documentadas, e usar o relatório para definir C02-A. Conferir que
os arquivos da API/contrato C01 não mudaram. Testes novos só onde houver lógica
relevante no script; mocks não demonstram qualidade nem viabilidade do modelo.

Se faltarem amostra, runtime, recursos ou acesso indispensável, concluir o
inventário e o roteiro independentes, registrar entrega PARCIAL/BLOQUEADA com
o motivo e a próxima ação concreta. Não dizer que Whisper foi validado apenas
porque o script ou as instruções foram escritos. Se a evidência real já for
suficiente, não ampliar para vários modelos ou benchmark extenso.

## Fontes oficiais

- https://github.com/openai/whisper
- https://github.com/openai/whisper/blob/main/model-card.md

Consultar as versões atuais quando escolher pacotes. O código e os pesos
abertos têm licença MIT; FFmpeg é necessário. O modelo pode repetir ou
inventar texto, especialmente em entradas difíceis: registrar o observado,
sem prometer ausência desses erros.

## Registro e devolução

Antes de entregar, atualizar a ficha B07-A e o índice, acrescentando evento
com data/agente, ação, arquivos, comandos/resultados, uso de áudio real ou
simulação, pendências e próximo responsável. Preservar eventos anteriores.
Informar separadamente execução finalizada/parcial, revisão pendente, Git
commitado ou não, branch/base/HEAD, publicação e integração. Não se aprovar
como conclusão do ciclo nem iniciar C02-A automaticamente.

Entregar resumo com configuração testada, evidências reais, limites propostos,
arquivos e pendências. Próximo responsável: Codex analisar a entrega e preparar
a revisão pelo Opus. C02-A só recebe próximo encaminhamento após essa avaliação.
