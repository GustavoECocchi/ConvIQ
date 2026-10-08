# B14 — Revisão independente da normalização Unicode e dos índices

Você é Claude Opus, revisor e corretor de B14 (nível A) no ConvIQ. Trabalhe
no worktree `/home/gustavoecocchi/Documents/CONVIQ-b14`, branch
`fix/b14-unicode-evidencias`, HEAD/base
`4063830db9b5f8400b60b8c09e9413b35115b106`. A entrega de Sonnet
(B14-01) é **diff local não commitado** sobre essa base: 11 arquivos
rastreados em `backend/` e `docs/contratos/`, mais o não rastreado
`backend/tests/test_texto.py`. Preserve as alterações locais de preparação
e registro. Confira Git antes de editar; não use a pasta raiz para o código.

Leia `STATUS.md`, a linha B14 em `REGISTRO_TRABALHO.md`, a ficha e os eventos
B14-01/B14-02 em `docs/registro/B14.md`, a seção 11 de
`SISTEMA_GOVERNANCIA_CONVIQ.md`, o cartão B14 em
`docs/planejamento/PRS_REFINAMENTO_ANALISE.md` e o contrato C01. Revise o
diff `git diff 4063830 -- backend docs/contratos` e o teste novo. Para
identificar a versão examinada pelo Codex, o SHA-256 do diff binário técnico
foi `9e35397cdb8eb6f56bca58c45ba02ed13e114791b6eb8c7eac0e4cec34328ca0`
e o de `backend/tests/test_texto.py` foi
`67c97757c497e2fe7496eef89514da13772aa63005caa79bac11569eefd715fc`.

O Codex não encontrou impeditivo na análise inicial. Conferiu a suíte
completa (**330 passed**, 2 avisos), seis sondas na composição real,
`git diff --check`, branch padrão remota em `4063830` e ausência de branch/PR
B14. A fuzz de 8.000 análises, os 29 testes discriminadores e seis casos
em servidor real são evidências **relatadas pelo Sonnet**, ainda não
reproduzidas pelo Codex. Sua revisão deve ser independente.

## Verificações principais

1. Revise `TextoNormalizado`/`normalizar_com_mapa`: mapeamento de começo e fim
   exclusivo, combinantes após letras, forma mista NFC/NFD, múltiplos
   combinantes, caractere de compatibilidade que expande (ex.: `ﬁ`),
   combinante órfão, início/fim do texto e monotonicidade dos intervalos.
   Faça contraprovas próprias; avalie se os limites documentados são aceitáveis
   para o escopo em português ou causam defeito material.
2. Revise todos os consumidores (`sentimento.py`, `negacao.py`,
   `sinais_comerciais.py`, `analise.py`). Confirme que regex/escopos usam
   coordenadas normalizadas, enquanto cada `Evidencia` pública usa índices
   Python do eco de C01. Verifique a distinção `e`/`é` em NFC/NFD, inclusive
   conjunção nominal e escopo de negação; nenhum índice pode ser recuperado
   pela primeira ocorrência de `find`.
3. Teste pares NFC/NFD para `péssimo`, `ótimo`, `Não estamos satisfeitos`,
   `Não só`, `Não é ruim, é ótimo`; depois um sinal válido precedido de
   combinantes e outro após trecho negado. Preserve as regras de B11–B13:
   prospect, cancelamento com objeto comercial, tema alheio, intenção
   afirmativa com objeto comercial, catálogos, coexistência de risco e
   oportunidade, repetições, IDs e referências de recomendações.
4. Confira limites da rota e do contrato: eco sem normalização, `inicio`/`fim`
   relativos ao eco, recortes literais, `versao_analise="0.5"`, schema
   inalterado. Use `backend/scripts/sondar.py` e `app.__file__` para não
   importar a instalação editável da pasta raiz. Rode testes afetados e suíte
   completa a partir de `backend/`; use timeout. O TestClient pode travar
   dentro do sandbox; se ocorrer, reexecute fora dele. Confira
   `git diff --check` e, se possível, a rota num servidor real.

Confirme qualquer achado com entrada, saída observada, saída esperada,
impacto e teste que falha antes da correção. Corrija apenas defeitos
comprovados dentro de B14, com teste de regressão e contraprova do sinal
vizinho. Se não achar defeito, conclua a revisão sem mudança artificial.
Mantenha os limites aceitos documentados. Não inicie B19.

Atualize a ficha B14, índice/STATUS apenas se o estado mudar, a fotografia
Git se mudar, e acrescente **um** evento curto B14-03 em
`docs/registro/B14.md`. Separe verificação própria de evidência relatada;
separe entrega, revisão, commit, push, PR e integração. Esta instrução
**não autoriza commit, push, abertura de PR nem merge**: deixe eventual
correção local para a verificação final do Codex. Entregue ao usuário um
resumo curto com o caminho do evento.
