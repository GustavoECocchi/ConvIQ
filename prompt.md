# B13 — Oportunidade somente com intenção comercial — Claude Sonnet

Você é o executor de B13 do ConvIQ. Implemente somente este PR lógico e
entregue a versão para a revisão coordenada pelo Codex. Não inicie B14/B17
nem declare aprovação final ou integração.

## 1. Leitura e versão de partida

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md`,
`REGISTRO_TRABALHO.md` (índice, INT01, B11/B12 e ficha B13),
`PLANO_DESENVOLVIMENTO.md` (refinamento B11–B21), o cartão B13 em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md`, `backend/README.md` e
`docs/contratos/analise-texto.md`.

- Projeto: `/home/gustavoecocchi/Documents/CONVIQ`.
- Branch de trabalho proposta: `fix/b13-intencao-oportunidade`.
- Base: **branch padrão remota `feat/b01-fundacao-api`**, no HEAD atual que
  contenha o merge de B11/B12 `e31e6ba81692c61e0b0615d349972e2b3a0c459d`.
  Confirme o hash atual no servidor e registre o hash usado antes de criar
  a branch. Não use a referência local `origin/main` como destino.
- Dependências: B01–B04/C01 estão na branch padrão; B11/B12 foram
  integrados pelo PR [#1](https://github.com/GustavoECocchi/ConvIQ/pull/1),
  merge `e31e6ba`. B07-A permanece parcial e não bloqueia B13.
- A pasta raiz pode estar em `fix/b12-contexto-risco`, com `prompt.md` e
  `REGISTRO_TRABALHO.md` modificados e relatório Sonnet não rastreado.
  Confira o estado real. Preserve tudo. Crie um worktree isolado a partir
  da branch padrão confirmada, sem trocar a branch ou limpar os arquivos
  preexistentes.

Se branch, base, arquivos ou registro divergirem, documente a divergência
antes de implementar. Não atribua ao HEAD conteúdo só presente na pasta
de trabalho. Os estados históricos de B11/B12 em outros commits não
substituem a verificação da base escolhida.

## 2. Objetivo e escopo

Hoje `_REGEX_OPORTUNIDADE` em `backend/app/services/sinais_comerciais.py`
gera uma oportunidade para cada palavra como `interesse`, `conhecer` ou
`módulo`, mesmo quando o interesse é negado, a palavra é só uma menção ou
o objeto não tem relação comercial. B13 exige uma **intenção afirmativa e
local** de conhecer/avaliar/contratar/expandir/integrar uma solução ou uma
necessidade comercial concreta, sem inferência generativa.

Implemente a regra em `sinais_comerciais.py`, com testes pertinentes em
`backend/tests/test_sinais_comerciais.py`, testes de composição/rota onde
o comportamento público mudar, README e nota no contrato C01. Reutilize,
quando couber, o escopo de negação de B11 e a normalização atual sem alterar
seus contratos. Avalie `_ha_conteudo_comercial`: uma ocorrência rejeitada
como oportunidade não deve, só por essa ocorrência, tornar churn avaliável;
produto, concorrente ou outro contexto comercial independente continuam
seguindo as regras existentes.

Para toda oportunidade, a evidência deve ser um recorte literal contínuo da
transcrição ecoada, com `inicio`/`fim` e referência válidos, que mostre a
intenção afirmativa e o contexto que a torna comercial. Preserve a
independência entre risco e oportunidade. O catálogo de produtos pode
listar uma marca mencionada mesmo quando a intenção relativa a ela é
negada; B13 muda a lista de oportunidades, não apaga nomes citados.

Atualize `versao_analise` de `0.3` para `0.4` pela mudança observável, sem
alterar o formato JSON de C01. Atualize README e a nota do contrato com
exemplos e limites da regra. Comunique a mudança na quantidade e no
conteúdo das evidências ao frontend F05.

## 3. Critérios verificáveis

Cubra no serviço e, quando pertinente, na composição `compor_analise_texto`
e na rota real:

1. `Não temos interesse em conhecer o Fluig.` → nenhuma oportunidade nem
   recomendação de oportunidade. A menção a Fluig pode permanecer em
   `produtos`.
2. `O módulo atual está instalado.` → nenhuma oportunidade. Uma menção
   nominal isolada não é intenção.
3. `Queremos conhecer o Fluig.` → oportunidade com evidência da intenção
   afirmativa e do objeto comercial.
4. `Precisamos automatizar o faturamento.` → oportunidade com evidência da
   necessidade comercial.
5. `Quero conhecer a cidade.` → nenhuma oportunidade.
6. `Não queremos o Fluig, mas temos interesse no Protheus.` → somente a
   intenção afirmativa sobre Protheus gera oportunidade; `produtos` pode
   conter Fluig e Protheus. A negação anterior não alcança a oração após
   `mas`.
7. `Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.` →
   risco de B12 e oportunidade de B13 coexistem, com evidências e
   recomendações corretamente referenciadas.

Acrescente contraexemplos próprios para negação, limite de oração,
repetição e palavras parecidas, sem transformar a suíte numa cópia da
implementação. Preserve `prospect → churn.nao_aplicavel`, concorrente
isolado sem risco presumido, ausência de sinal versus informação
insuficiente e os aceites de B11/B12. Não exija deduplicação de intenções
na mesma frase: esse agrupamento é B17. Documente falsos positivos e
negativos residuais de uma regra local, sem prometer interpretação geral.

## 4. Fora do escopo

- B14 (Unicode/NFD e mapa de índices), B17 (agrupar sinais da mesma
  intenção), B18 (descrição publicamente vinculada a produto/necessidade),
  B19 (deduplicação de intervalos) e mudanças nas regras de churn de B12.
- Novo modelo ou serviço pago, probabilidade de venda, diarização,
  atribuição de fala, histórico remoto, áudio, frontend e persistência.
- Reestruturar schemas ou alterar o contrato HTTP além da versão e dos
  exemplos/documentação da análise. Se encontrar uma mudança contratual
  indispensável, registre e devolva à coordenação antes de aplicá-la.

## 5. Validação e entrega

Rode os testes afetados e a suíte completa do backend. Se o `TestClient`
travar no sandbox, registre o comando/resultado e reexecute fora dele
quando permitido; não apresente uma suíte interrompida como aprovada.
Confira `git diff --check`, o diff contra a base real, o status de arquivos
não rastreados e os recortes literais/referências da API. Documente
comandos executados e seus resultados; se não puder executar algo, diga
explicitamente o que ficou pendente.

Ações Git autorizadas nesta atribuição: criar branch/worktree isolado e
trabalhar localmente. **Não faça commit, push, PR remoto ou merge** sem
orientação posterior do usuário. Preserve alterações preexistentes,
inclusive `prompt.md`, relatórios e B07-A parcial.

Antes de devolver, atualize a ficha B13, o índice e um evento próprio em
`REGISTRO_TRABALHO.md`, identificando agente, data, branch/base/HEAD,
arquivos, validação, limites, pendências e próximo responsável. Informe
separadamente implementação finalizada ou parcial, revisão pendente,
alterações commitadas ou não, publicação e integração. Entregue o relatório
da seção 8 da governança e aguarde a análise do Codex.
