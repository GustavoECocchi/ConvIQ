# B19 — revisão independente da evidência compartilhada (Opus)

Você é Claude Opus, revisor/corretor do B19 no ConvIQ. Trabalhe no worktree
`/home/gustavoecocchi/Documents/CONVIQ-b19`, branch
`fix/b19-unificar-evidencias`, HEAD/base
`b688afb7bdaa63a7ac8e8905301d29075f3a4dcc` (merge do PR #4 na branch
padrão `feat/b01-fundacao-api`). A entrega B19 é **diff local não commitado**
sobre essa base. Antes de editar, confira branch, HEAD, alterações locais,
arquivos não rastreados e a identidade do `app` importado. Preserve a
preparação B19-00, o registro B19-01/B19-02 e os outros worktrees.

Leia `STATUS.md`, a linha B19 do `REGISTRO_TRABALHO.md`,
`docs/registro/B19.md`, o cartão B19 em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md`, a seção 11 de
`SISTEMA_GOVERNANCIA_CONVIQ.md`, `backend/README.md` e a nota B19 do contrato
`docs/contratos/analise-texto.md`. Revise o diff técnico com
`git diff b688afb -- backend docs/contratos`. O SHA-256 desse diff binário
na análise inicial do Codex foi
`5b7bee5209fa28a03822fb3f56115688a25ad8dfb97382949bd4936bd74379ee`;
se divergir, identifique a mudança antes de concluir. B19 é nível A: após
sua revisão/correção, Codex fará a verificação final.

## Revisão solicitada

1. Verifique independentemente a composição em
   `backend/app/services/analise.py`. Evidências só devem compartilhar ID
   quando `(inicio, fim, trecho)` forem iguais. Duplicata não adjacente também
   deve unir; intervalos aninhados ou apenas sobrepostos e ocorrências em
   posições diferentes devem continuar separados. Confirme ordem estável
   por posição, sentimento antes do comercial em empate e IDs `e1..eN` sem
   lacunas.
2. Confira o remapeamento de todas as referências de churn, oportunidades
   e recomendações: IDs existentes, sem repetição em cada lista, preservando
   a primeira ordem. Um ID pode servir a sentimento e churn. Não altere a
   detecção, classificação, catálogo, número/descrição das oportunidades ou
   conteúdo das recomendações. Prospect mantém churn `nao_aplicavel`.
3. Execute contraprovas: `Estamos insatisfeitos.` (uma evidência 8–21),
   `Não estamos satisfeitos.` (uma, inclusive NFD com recorte literal),
   `Estamos insatisfeitos com o suporte.` (duas: 8–21 e 8–35), duas frases
   curtas iguais em offsets distintos, emoji/espaços à esquerda, risco e
   oportunidade vizinha, prospect, texto sem sinal e menção de catálogo.
   Gere casos próprios se revelarem uma falha real. Confirme
   `transcricao[inicio:fim] == trecho` e referências contra o eco da rota.
4. Revise se testes cobrem duplicata não adjacente e referências repetidas;
   valide schema/API/formato C01 e `versao_analise` `0.6`. Verifique README
   e nota de contrato. O frontend F05 deve saber que um ID pode ser
   compartilhado, enquanto aninhamentos permanecem como dois destaques.

O Codex conferiu o código, `git diff --check`, a suíte completa (**344
passed**, dois avisos já conhecidos) e sondas pela composição para curta,
aninhada, repetida, NFD e sinal vizinho. Os 289 testes afetados, 19 falhas
contra a base, fuzz de 8.000 análises e oito casos em servidor real foram
**relatados pelo Sonnet**, ainda não repetidos pelo Codex. Faça verificação
independente proporcional ao risco; rode os testes relevantes e a suíte
completa a partir de `backend/`, usando timeout. Para scripts avulsos,
use `backend/scripts/sondar.py` ou `PYTHONPATH` do worktree e confira
`app.__file__`, pois o venv da raiz tem instalação editável para outra pasta.
Se confirmar defeito, corrija com teste discriminante e revalide. Se não
houver defeito, mantenha o código intacto e registre o aceite da revisão.
Separe no registro o que você observou do que veio dos relatos anteriores.

## Registro e Git

Atualize a ficha B19, a linha do índice, `STATUS.md` e a fotografia Git se
mudarem; escreva um evento curto **B19-03** em `docs/registro/B19.md`, com
achados, arquivos, validação, limites e próximo responsável. Registre
separadamente entrega, revisão, commit, push, PR e integração. O usuário
autorizou esta etapa local, **sem autorização para commit, push, PR ou
merge do B19**. Deixe eventuais correções como diff local para a
verificação final do Codex. Não inicie B15. Responda com resumo curto e o
caminho do evento.
