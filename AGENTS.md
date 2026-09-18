# Instruções do ConvIQ para agentes

Antes de atuar, leia `SISTEMA_GOVERNANCIA_CONVIQ.md`, `REGISTRO_TRABALHO.md`
e a seção pertinente de `PLANO_DESENVOLVIMENTO.md`. Confira o Git e a ficha
da tarefa; registros de outra branch ou versão não comprovam o estado atual.

## Registro obrigatório — Codex e Claude

- Cada agente registra sua própria atuação em `REGISTRO_TRABALHO.md` antes
  de passar o trabalho ou encerrar a resposta. Isso inclui planejamento,
  implementação, revisão, correção, verificações e operações Git.
- Atualize a ficha da tarefa e acrescente um evento ao histórico, identificando
  agente, data, ação, arquivos, evidências, pendências e próximo responsável.
  Preserve os eventos anteriores. Uma resposta no chat não substitui o registro.
- Para cada PR, informe separadamente: entrega finalizada ou pendente, estado
  da revisão, alterações commitadas ou não, branch, hashes, push e integração.
  Commit em uma branch de trabalho não significa integração na principal.
- Registre alterações parcialmente commitadas e arquivos não rastreados.
  Não atribua ao `HEAD` conteúdo que ainda está apenas na pasta de trabalho.
- Confirme os nomes reais da branch de trabalho, da base e do destino. Não
  presuma `main` ou `master`. Diferencie referência remota local de consulta
  atual ao servidor; use `NAO_VERIFICADO` quando não houver evidência.
- Ao retomar, compare ficha, branch, commits e alterações locais. Se houver
  divergência, registre-a antes de continuar. Não troque de branch para
  procurar trabalho sem preservar as alterações locais existentes.
- Se o registro não puder ser editado, informe essa limitação e entregue o
  texto do evento para incorporação; não diga que ele foi salvo.
- `prompt.md` é o arquivo de rascunho oficial para prompts. Sempre que o
  usuário pedir para gerar ou preparar um prompt, escreva o prompt completo
  nesse arquivo para o Claude ler. Substitua o prompt anterior, salvo quando
  o usuário pedir explicitamente uma versão acumulada. Não trate `prompt.md`
  como histórico: registre a geração e a substituição em
  `REGISTRO_TRABALHO.md`; preserve cópias nomeadas somente quando forem úteis
  para rastreabilidade (por exemplo, `PROMPT_REVISAO_B01_OPUS.md`).

Codex coordena e verifica; Claude implementa e revisa conforme o papel atribuído.
Uma atribuição diferente do usuário prevalece. Registrar trabalho não concede,
por si só, autorização para commit, push ou merge; valem as autorizações da sessão.

## Referência geral

Se existir `docs/governanca/REGRAS.md`, leia essa versão adotada e os registros
pertinentes. Caso contrário, consulte
`/home/gustavoecocchi/Documents/GOVERNANCA/REGRAS.md`. Se estiver indisponível,
informe brevemente e siga as instruções e documentos disponíveis. Não atualize
automaticamente uma versão adotada. Instruções superiores, pedidos do usuário
e convenções específicas do projeto prevalecem sobre a referência geral.
