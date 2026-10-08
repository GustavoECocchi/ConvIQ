# Relatório do Sonnet para o Codex — B13

Preparado pelo Claude Sonnet em 07/10/2026, a pedido direto do usuário, como
retorno do executor ao coordenador (seção 9.3 da governança, com o relatório
da seção 8). Fonte completa: `REGISTRO_TRABALHO.md`, ficha B13 (bloco
"Entrega do executor — B13-01") e evento B13-01.

---

O **Sonnet** entregou **B13 — Oportunidade somente com intenção comercial**.
Analise conforme `SISTEMA_GOVERNANCIA_CONVIQ.md` e o cartão B13 de
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md`.

**Referência da entrega:** worktree `/home/gustavoecocchi/Documents/CONVIQ-b13`,
branch `fix/b13-intencao-oportunidade`, HEAD = base
`9921f579481fdfac098576de425b7ed19df8ef8d` + **diff local não commitado**
(`git diff 9921f57`). A base é a branch padrão `feat/b01-fundacao-api`,
confirmada no servidor nesta atuação (contém o merge `e31e6ba` de B11/B12).

```text
PR lógico ou tarefa e título: B13 — Oportunidade somente com intenção comercial
Data e agente/papel: 07/10/2026, Claude Sonnet / executor
Entrega do executor: FINALIZADA
Estado do ciclo: ENTREGUE — aguarda análise do Codex (revisão não feita)
Pasta e branch: /home/gustavoecocchi/Documents/CONVIQ-b13; fix/b13-intencao-oportunidade
Base e HEAD: 9921f57 (ambos); entrega = diff local
Destino / principal: feat/b01-fundacao-api (servidor); origin/main local (8d48e75) não é destino
```

## Entrega

`_ocorrencias_oportunidade` (em `sinais_comerciais.py`) substitui
`_REGEX_OPORTUNIDADE`. Um gatilho gera oportunidade quando:
1. não está no escopo de negação de B11; e
2. um objeto comercial é o núcleo do seu complemento na mesma oração, pela
   ligação ação–objeto de B12 (`_fim_do_objeto_da_acao`, agora parametrizada
   por regex de objeto e palavras puláveis).

- **Gatilhos:** interesse, interessado, conhecer, avaliar, contratar,
  adquirir, implantar, expandir, ampliar, integrar, automatizar. `módulo`
  deixou de ser gatilho.
- **Objetos:** produtos do catálogo e 19 substantivos (módulo, solução,
  sistema, plataforma, software, ferramenta, produto, serviço, licença,
  integração, automação, faturamento, proposta, filial, unidade, usuário).
- **Querer/precisar** (quero, queremos, precisamos, gostaríamos...): logo antes
  do gatilho, entram no recorte; sem gatilho depois na oração, valem como
  gatilho ("Queremos o Fluig").
- **Evidência:** a intenção inteira, do início ao fim do objeto, recorte
  literal e contínuo.
- **Churn:** só as oportunidades aceitas contam em `_ha_conteudo_comercial`.
- **Versão:** `versao_analise` `0.3` → `0.4`. Formato C01 inalterado.

## Critérios do prompt (seção 3)

| # | Entrada | Resultado (serviço, composição e servidor real) |
|---|---|---|
| 1 | Não temos interesse em conhecer o Fluig. | sem oportunidade/evidência/recomendação; `produtos=["Fluig"]`; churn sem_sinal_detectado |
| 2 | O módulo atual está instalado. | nada; churn informacao_insuficiente |
| 3 | Queremos conhecer o Fluig. | evidência "Queremos conhecer o Fluig" |
| 4 | Precisamos automatizar o faturamento. | evidência "Precisamos automatizar o faturamento" (0–36) |
| 5 | Quero conhecer a cidade. | nada; churn informacao_insuficiente |
| 6 | Não queremos o Fluig, mas temos interesse no Protheus. | só "interesse no Protheus"; `produtos=["Fluig","Protheus"]` |
| 7 | Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig. | churn "insatisfeitos com o suporte" (e2) + oportunidade "Queremos conhecer o Fluig" (e3); recomendações [e2], [e3] |

Contraexemplos cobertos: negação de "queremos", "sem interesse", negação que
não alcança a frase seguinte, repetição (posições distintas), palavras
parecidas (conheceram, interessante, integrado, automação), concorrente
isolado, prospect, duas ações na mesma frase.

## Mudanças observáveis (informar ao frontend F05)

1. Interesse negado e menção solta deixam de gerar oportunidade, evidência e
   recomendação; o produto citado continua em `produtos`.
2. A evidência da oportunidade é a intenção inteira; a `descricao` cita esse
   trecho.
3. Texto cuja única ocorrência era uma oportunidade rejeitada passa de
   sem_sinal_detectado a informacao_insuficiente em `churn`.
4. "Temos interesse em conhecer o Fluig." mantém duas oportunidades, agora com
   recortes distintos ("interesse em conhecer o Fluig" e "conhecer o Fluig");
   o agrupamento é B17.

## Limites (README e testes que os pinam)

- **Falsos positivos:** objeto coordenado ("Queremos conhecer a cidade e o
  Fluig."); "sistema" fora do sentido comercial ("sistema solar"); autoria da
  fala não identificada ("O analista vai conhecer o Fluig."); "avaliar o
  serviço".
- **Falsos negativos:** vírgula entre gatilho e objeto ("Queremos muito
  conhecer, no mês que vem, o Fluig."); objetos fora da lista ("suporte
  técnico", "processo"); ironia e discurso indireto.
- A negação de B11 fecha no "e": "Não queremos o Fluig e conhecer o Protheus."
  gera "conhecer o Protheus".
- Descrição segue genérica (B18).

## Decisões que ficam com o Codex

- Vocabulário escolhido pelo executor além do que existia: gatilhos avaliar,
  contratar, adquirir, implantar, ampliar; formas de querer/precisar; lista
  de 19 objetos. Aceitar, reduzir ou ampliar.
- Aceitar os falsos positivos acima ou pedir nova rodada.

## Arquivos e SHA-256

```text
4a7ba07abd1abf47ae54048bb7f1b8eb8b8b0fb46128689d569bc26875328b69  backend/app/services/sinais_comerciais.py
061454cdf42d31cc386c97986524ef9c2b8db35fe03de9d62cb6699515c87b5c  backend/app/services/analise.py
8dc2815b482cf3a9b49ef5244898f0f683ff17ba9833c4c10689b1ce2e06a4f3  backend/tests/test_sinais_comerciais.py
3f0eadbc4ce6bae9264f10b49b1a66166cedba7a71ac7fb44a814866f7cc202e  backend/tests/test_analise.py
adb9aca44a8b59956e5d3475e4d88479b9d33de3f520114f04d399614b422ab9  backend/tests/test_analises_rota.py
90391c157fc9a03b414f85ff4bb042451bea1ff780bcf137b72bab3c04e24264  backend/README.md
dd10657803301d7bd8beb111d42f96501e71ea987447971b76a59d6c9c094475  docs/contratos/analise-texto.md
```

`analise.py` mudou só a versão. Sem diferença contra `9921f57` em
`negacao.py`, `sentimento.py`, `texto.py`, schemas, API, `pyproject.toml` e
`test_sentimento.py`. Churn de B12 (`_ocorrencias_risco`) e catálogos
inalterados. O hash do `REGISTRO_TRABALHO.md` não é fixado (arquivo vivo).

## Validação (Sonnet, em `backend/` do worktree)

| Verificação | Resultado |
|---|---|
| Suíte da base antes de editar | 212 passed |
| `timeout --signal=INT --kill-after=5s 30s .../python -m pytest -q tests/test_sentimento.py tests/test_sinais_comerciais.py tests/test_analise.py` | 205 passed |
| `timeout --signal=INT --kill-after=5s 60s .../python -m pytest -q` | 255 passed, 2 avisos de depreciação; sem travamento do `TestClient` neste ambiente |
| Testes contra cópia da base `9921f57` | 48 falham (novos e atualizados): discriminam a mudança |
| Servidor real `uvicorn` 127.0.0.1:8099 | saúde ok; 7 critérios pela rota, recortes e referências conferidos; `versao_analise` 0.4; processo encerrado |
| `git diff --check`; linhas > 120 colunas | limpo; nenhuma |

Os 43 testes novos (255 − 212) cobrem serviço, composição (4) e rota (2). Nove
testes existentes falharam por mudança intencional e foram atualizados com
justificativa: versão `0.4` (5 asserts) e recorte da oportunidade (5 testes
de composição). Nenhum removido.

**Atenção ao reexecutar:** o venv da pasta raiz tem instalação editável
apontando para `/home/gustavoecocchi/Documents/CONVIQ/backend`. Rode
`pytest` a partir de `backend/` do worktree (`pythonpath=["."]` o prioriza) e,
para scripts avulsos, use `PYTHONPATH=<worktree>/backend`; confira
`app.__file__`. Um script meu sem isso mostrou o comportamento antigo.

**Sugestão de verificação:** (1) `sha256sum -c` acima; (2) os comandos da
tabela; (3) ler `_ocorrencias_oportunidade` e a parametrização de
`_fim_do_objeto_da_acao`; (4) sondar os critérios e os limites; (5) conferir
que B12 (`_ocorrencias_risco`) não mudou.

## Não executado

Verificação do Codex; B14/B17/B18/B19; frontend; consulta a PR remoto.

## Git

- **Entrega B13:** `NAO_COMMITADO` — diff local de 7 arquivos sobre `9921f57`.
- **Publicação:** `NAO_PUBLICADA`. **PR remoto:** `NAO_ABERTO`.
  **Integração:** `NAO_INTEGRADA` (destino previsto `feat/b01-fundacao-api`).
- **Registro:** `REGISTRO_TRABALHO.md` do worktree (ficha, índice, fotografia e
  evento B13-01) e este relatório, `NAO_COMMITADOS`.
- **Pasta raiz preservada:** `/home/gustavoecocchi/Documents/CONVIQ`, em
  `fix/b12-contexto-risco` (`b14f0a5`), com `PLANO_DESENVOLVIMENTO.md`,
  `REGISTRO_TRABALHO.md`, cartão de refinamento e `prompt.md` modificados e
  dois arquivos não rastreados — intocados. O registro do worktree não
  incorpora as modificações locais do Codex nessa pasta.
- Nenhum commit, push, PR, merge, reset ou stash.

**Próximo responsável:** Codex analisa B13 e decide aceite, nova rodada ou
revisão do Opus; o usuário decide commit/push/PR depois. B14/B17 não iniciados.
