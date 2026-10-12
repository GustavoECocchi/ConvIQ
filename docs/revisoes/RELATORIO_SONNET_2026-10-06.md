# Relatório do Sonnet para o Codex — estado atual e próximos passos

Preparado pelo Claude Sonnet em 06/10/2026, a pedido direto do usuário
("manda um relatório para o codex entender qual o estado atual e os próximos
passos com base na documentação"). É um retorno de análise: **nenhum código,
teste ou configuração foi alterado**, e nenhuma operação Git de escrita foi
feita. Não substitui `prompt.md` (que segue com o prompt B12-02, ainda não
executado e desatualizado — ver item 3).

## 1. Fontes e limites da leitura

Lidos: `AGENTS.md`, `CLAUDE.md`, índice e fichas de B07-A/B11/B12 em
`REGISTRO_TRABALHO.md` (arquivo de 330 KB: lido por trechos), `prompt.md`
(início), roteiro B11–B21 em `PLANO_DESENVOLVIMENTO.md`. Não relidos por
completo: `SISTEMA_GOVERNANCIA_CONVIQ.md` (só a seção 8) e
`PRS_REFINAMENTO_ANALISE.md`. A referência geral
`/home/gustavoecocchi/Documents/GOVERNANCA/` **não existe** e o projeto não
tem `docs/governanca/`; seguiram-se só as regras locais.

## 2. Git observado (consulta local em 06/10/2026)

- Pasta `/home/gustavoecocchi/Documents/CONVIQ`; branch `fix/b12-contexto-risco`;
  HEAD `d5fb40a50e444b5920a5693df4ea477ef2ba6a6c`, igual a
  `origin/fix/b12-contexto-risco` (referência local; **consulta atual ao
  servidor não feita nesta atuação**).
- `d5fb40a` é um commit único com três frentes: B07-A-06, B11 e B12. Pai
  `cc61925`. `fix/b11-negacao-sentimento` e `spike/b07-a-viabilidade-whisper`
  continuam em `cc61925`, sem commit próprio.
- `origin/main` (referência local) está em `8d48e75`, "primeiro commit".
  `master` local em `3c52ea3`. Nenhuma frente integrada; PR remoto
  `NAO_ABERTO`/`NAO_VERIFICADO`. Destino previsto: `NAO_VERIFICADO`.
- Árvore de trabalho: só `REGISTRO_TRABALHO.md` modificado (registro do
  commit+push; já documentado pelo Sonnet, **não commitado**). Índice vazio.
- Suíte do backend (`backend/.venv`, `pytest -q`): **143 passed em 0,39 s**.
  O travamento em 137 testes relatado em B12-02 não se reproduziu; causa
  continua não diagnosticada, provavelmente do ambiente daquela execução.

## 3. Estado por frente (conforme o registro)

| Frente | Entrega | Ciclo | Observação |
|---|---|---|---|
| B01–B04 | FINALIZADA | APROVADO (Codex) | commit `6169fec`; não integradas |
| B07-A | PARCIAL | EM_REVISAO | P01 (fala real) pendente; Opus concluiu B07-A-06; aguarda Codex |
| B11 | FINALIZADA + corrigida (B11-03) | EM_REVISAO | aguarda verificação final do Codex; B12 depende dela |
| B12 | FINALIZADA (B12-01) | EM_REVISAO | R02/R03/R04 **sem correção**; revisão do Opus foi interrompida antes de editar |

Achados abertos de B12 (reproduzidos pelo Codex em B12-02):
- **R02** — `Vamos cancelar a reunião sobre o contrato.` e outros três
  exemplos geram sinal e retenção; `_ocorrencias_risco`/`_mesma_oracao` em
  `sinais_comerciais.py` aceitam qualquer objeto comercial na oração.
- **R03** — evidência de churn reduzida a `cancelar`; `Não estamos satisfeitos
  com o suporte.` omite `com o suporte`. Testes e README fixam o recorte curto.
- **R04** — `Estamos insatisfeitos com o clima.` / `almoço` geram risco;
  avaliar regra herdada de B03 × caminho novo de negação.

## 4. Divergências e riscos que o Codex deve conhecer

1. **`prompt.md` desatualizado.** Cita HEAD `cc61925`, diff B12 não commitado e
   hashes de entrada de nove arquivos. Hoje o HEAD é `d5fb40a` e o conteúdo
   está commitado; os hashes de entrada precisam ser reconferidos e o prompt
   reescrito antes de ir ao Opus.
2. **Isolamento de B12 perdido.** Com B07-A-06, B11 e B12 num commit só, o
   diff B12 não sai de uma comparação de branches. Separar em commits/branches
   por frente exige reconstrução de histórico (rebase/cherry-pick), que o
   Sonnet deliberadamente não fez. Decisão da coordenação/usuário.
3. **Registro editado depois do commit.** A atualização do registro em
   disco é posterior ao commit/push e está `NAO_COMMITADA`.
4. **Aceites pendentes em cascata.** B11 e B07-A-06 não têm aceite do Codex;
   o commit/push **não** é aprovação técnica de nenhuma frente.
5. **Registro com ~4.900 linhas.** Já não cabe numa leitura única; considerar
   arquivar fichas históricas aprovadas (decisão do Codex, não feita).

## 5. Próximos passos propostos (ordem do plano e do registro)

1. Codex decide a estrutura Git: manter o commit único ou separar B07-A-06,
   B11 e B12 antes de qualquer PR. Registrar a decisão.
2. Codex regera `prompt.md` para B12-02 sobre `d5fb40a`, com hashes atuais e
   R02/R03/R04; Opus confirma, corrige no escopo e registra.
3. Codex verifica B11 (dependência) e a devolução de B12; só então B12 pode
   ser aprovada.
4. Codex verifica B07-A-06; P01 (áudio de fala real) segue como pendência
   que condiciona o bloco de áudio em `PRS_BACKEND_AUDIO.md`.
5. Depois de B11/B12 aprovadas, a ordem do plano é B13 → B14 → B19 (prioridade
   inicial B11–B14 e B19), com B15–B18, B20 e B21 em seguida. Nenhuma
   liberação automática: B13 só inicia por encaminhamento.
6. Decidir o destino de integração (`main` remoto ainda em `8d48e75`) e abrir
   PR(s) somente com pedido do usuário.

## 6. Não feito nesta atuação

Código, testes, commits, push, PR, consulta ao servidor, atualização de
`prompt.md`, releitura integral da governança e do roteiro de refinamento.
Nenhuma aprovação ou revisão foi presumida.

## 7. Git desta atualização

Este relatório e o evento correspondente em `REGISTRO_TRABALHO.md` são
`NAO_COMMITADOS`/`NAO_PUBLICADOS`. Próximo responsável: Codex.
