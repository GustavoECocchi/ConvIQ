# Prompt para Claude Opus — revisão e correção de B01

Preparado em 17/09/2026 pelo subagente Codex `prompt_opus_b01`, por solicitação
do usuário e sob coordenação do Codex. Encaminhe este arquivo ao Claude Opus
com acesso à mesma pasta de trabalho. O prompt prepara a revisão; não afirma
que o Opus já revisou ou aprovou a entrega.

---

Você é o **Claude Opus, revisor e corretor de B01 — Fundação da API do ConvIQ**.
Revise a entrega do Sonnet, confirme os achados abaixo e corrija os problemas
comprovados dentro do escopo. Faça também sua própria revisão: os achados
iniciais não substituem a inspeção do conjunto entregue.

## Leitura e contexto obrigatórios

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` — especialmente
seções 4.4, 5, 6 e 8 —, a ficha B01 e o evento B01-02 em
`REGISTRO_TRABALHO.md`, e B01 na seção de PRs de `PLANO_DESENVOLVIMENTO.md`.
Os eventos posteriores de análise complementam o relato do executor.

Se existir `docs/governanca/REGRAS.md`, leia essa versão adotada. Caso
contrário, consulte `/home/gustavoecocchi/Documents/GOVERNANCA/REGRAS.md`.
Essa referência geral estava indisponível nesta preparação; sua ausência
não impede a revisão pelas instruções disponíveis. Não crie documentos de
governança nem atualize uma versão adotada por causa desta revisão.

O usuário decidiu concluir primeiro a análise de reuniões. Grupos, contexto
por equipe, personalização com IA, identificação de participantes, extração
de tarefas e notificações estão registrados como **evolução futura** e não
fazem parte desta entrega.

## Pasta, versão e autorização

- **Pasta:** `/home/gustavoecocchi/Documents/CONVIQ`.
- **Branch atual da tarefa:** `feat/b01-fundacao-api`.
- **Base local:** `master`, hash `3c52ea3ed0d3c3d38de5b9adf2a4a4ff320a1842`.
- **HEAD observado:** o mesmo hash. Ele contém a base inicial, **não a
  implementação de B01**, que está na pasta de trabalho e não foi commitada.
- **Versão a revisar:** os 17 arquivos não rastreados de `backend/` do
  manifesto SHA-256 no final deste prompt. Leia todos; `git diff` sozinho
  não os mostra. `.gitignore` é preexistente, também não rastreado, e deve
  ser conferido como suporte necessário à entrega.
- **Destino de integração e branch principal:** `NAO_VERIFICADO`. Existe
  referência local `origin/main` em `8d48e75`, que não foi usada como base.
  DOC01-04 contém um relato do Sonnet sobre consulta anterior ao servidor;
  esta preparação não refez a consulta. Não trate essa ref local como prova
  atual da principal ou do servidor, nem recupere o backend antigo daquele
  commit: a implementação do zero foi uma decisão explícita do usuário.
- **Situação da entrega examinada:** `NAO_COMMITADO`, `NAO_PUBLICADO`,
  `NAO_INTEGRADO`. PR remoto: Sonnet relatou `NAO_ABERTO`; existência/estado
  no servidor `NAO_VERIFICADO` por esta preparação. B01 é um ID lógico.
- **Autorizado nesta rodada:** revisão, correções necessárias, testes e
  documentação **locais, na mesma branch**. Não criar commit, fazer push,
  abrir PR remoto, trocar de branch ou integrar. Uma autorização posterior
  e explícita do usuário prevalece, se concedida; registre-a.

Antes de editar, confira raiz, branch, HEAD, status completo, diff da pasta
de trabalho e diff preparado para commit. Confira os arquivos não rastreados
e o manifesto. Se algo divergir, registre a versão realmente disponível e
a divergência; não sobrescreva mudanças para restaurar a fotografia antiga.

Preserve as alterações de DOC01/PROD01 e de outros agentes: `prompt.md`
modificado e documentos de coordenação não rastreados. Atualize apenas o
registro pertinente, documentação de B01 e arquivos necessários à correção.
Não atribua a B01 a autoria de `.gitignore` ou dos documentos preexistentes.

Comandos de inspeção, executados na raiz:

```bash
git status --short --branch --untracked-files=all
git rev-parse HEAD master
git branch -avv
git diff
git diff --cached
git ls-files --others --exclude-standard backend .gitignore
git check-ignore -v backend/.venv backend/.pytest_cache backend/app/__pycache__ backend/.env
```

## Escopo e critérios originais

B01 não tem dependências. O objetivo é uma fundação FastAPI executável e
documentada, pronta para a revisão de contratos em C01.

1. Projeto FastAPI em `backend/`, dependências declaradas e instalação/
   inicialização reproduzíveis conforme `backend/README.md`.
2. Configuração por ambiente, documentada em `.env.example` e no README.
3. `GET /api/health` responde com sucesso na configuração padrão e tem
   teste pertinente passando. A implementação também oferece prefixo de
   API e origens CORS configuráveis; confira o comportamento já entregue.
4. Schemas iniciais de reunião/análise e seus limites claramente registrados,
   sem apresentá-los como contrato final aprovado.
5. Arquivos de ambiente local, ambientes virtuais e caches cobertos pelo
   `.gitignore`, preservando `.env.example` como arquivo entregável.
6. Importar/inicializar a API não executa `conviq_datascience.py`.

Ficam fora do escopo frontend, contratos definitivos de C01, serviços B02/B03,
`POST /api/analises/texto` e padronização HTTP de erros de B04, transcrição,
persistência, publicação e as capacidades futuras de grupos/tarefas/IA.
Não implemente esses recursos como correção de B01.

## Relatório do Sonnet e evidências conferidas

A fonte do relato é a ficha B01 e o evento **B01-02**, no registro local.
Sonnet declarou a execução finalizada, sem aprovação, commit, push ou merge:
FastAPI, configuração `AMBIENTE`/`PREFIXO_API`/`ORIGENS_CORS`, rota de saúde,
schemas provisórios, testes e instruções. Relatou instalação em ambiente
virtual novo, 10 testes aprovados, saúde via Uvicorn/curl, OpenAPI e cobertura
dos artefatos pelo `.gitignore`.

Esta preparação **conferiu diretamente**:

- Python 3.14.7; dependências instaladas coincidem com as versões diretas de
  `pyproject.toml`: FastAPI 0.141.1, Uvicorn 0.53.0, Pydantic 2.13.3,
  pydantic-settings 2.14.1, pytest 9.0.3 e httpx 0.28.1.
- Em `backend/`, `.venv/bin/python -m pip check`: `No broken requirements found`.
- `timeout 30s .venv/bin/python -m pytest -q`: **10 passaram, 2 avisos**,
  executado fora do sandbox após bloqueio do TestClient dentro do isolamento.
- Os avisos observados são: uso de `httpx` por `starlette.testclient` e alias
  `anyio.abc.BlockingPortal` depreciados. São avisos, não falhas de B01; não
  atualize dependências sem necessidade demonstrada.
- `timeout 15s .venv/bin/python -m pytest -q tests/test_schemas.py`:
  **8 passaram** também dentro do sandbox.
- Importar `app.main` e gerar `app.openapi()` funciona; o OpenAPI contém
  somente `/api/health`. `conviq_datascience` não foi carregado em
  `sys.modules`; a leitura do código não encontrou importação do experimento.
- Saúde no TestClient padrão retorna 200 com
  `{"status":"ok","ambiente":"desenvolvimento"}`; `/health` retorna 404.
- As execuções com configuração externa reproduziram B01-R01 abaixo.
- Git confirma os 17 arquivos `backend/` sem commit e a cobertura dos caches,
  venv e `.env` pelo `.gitignore`. O índice Git estava sem alterações.

**Limites da preparação:** não reinstalou dependências em ambiente limpo,
não repetiu Uvicorn/curl, não validou outra versão de Python/OS, CORS via
navegador ou estado atual do servidor Git. A instalação nova e o servidor
real permanecem relatos do Sonnet até sua reprodução. O bloqueio inicial
do TestClient foi contornado por execução autorizada fora do sandbox, onde
a suíte terminou; não o classifique como bug da aplicação.

## Achados para confirmar e tratar

### B01-R01 — testes de saúde dependem da configuração externa

- **Localização:** `backend/tests/test_health.py:3–12`; interação com
  `backend/app/main.py:9–21` e cache em `backend/app/config.py:23–27`.
- **Confirmado:** o módulo importa a aplicação e cria o TestClient durante
  a coleta, mas o teste exige sempre `/api/health` e `desenvolvimento`.
  Configurações válidas documentadas fazem o teste reprovar quando a API
  está obedecendo à configuração corretamente.
- **Reproduções em `backend/`, fora do sandbox:**

  ```bash
  AMBIENTE=homologacao timeout 30s .venv/bin/python -m pytest -q tests/test_health.py
  PREFIXO_API=/v1 timeout 30s .venv/bin/python -m pytest -q tests/test_health.py
  ```

  Primeiro comando: **1 falhou, 1 passou**; linha 12 esperava
  `desenvolvimento`, mas a API respondeu `homologacao`. Segundo comando:
  **1 falhou, 1 passou**; linha 11 recebeu 404 porque o teste continuou
  chamando `/api/health`, apesar do prefixo configurado como `/v1`.
- **Impacto:** falha de isolamento/reprodutibilidade da validação de B01,
  cuja entrega permite configuração externa. Não foi constatada falha da
  rota na configuração padrão. Prioridade média: tratar antes de devolver
  a revisão, sem transformar isso numa reformulação da arquitetura.
- **Correção esperada:** controlar explicitamente as configurações dos
  cenários de teste, incluindo `.env` local e cache; evitar que importação
  global torne um ajuste posterior de fixture ineficaz. Acrescentar uma
  verificação pequena e pertinente de configuração alternativa. Escolha
  a alteração mínima adequada, sem enfraquecer os asserts para apenas
  copiar o valor atual de produção e sem obrigatoriedade de criar fábrica
  de aplicação se isso não for necessário.
- **Validação:** suíte padrão passa; ambos os comandos acima passam após
  isolamento; testes específicos comprovam ambiente/prefixo alternativos
  e não deixam configuração/cache contaminando outros cenários. A API real
  deve continuar respeitando a configuração do usuário.

### B01-R02 — inventário documental informa 16 arquivos, mas contém 17

- **Localização:** ficha B01 de `REGISTRO_TRABALHO.md`, campos “Arquivos
  criados”, “Validação executada” e “Git da entrega” — linhas 104, 148 e
  164 na fotografia inicial; evento **B01-02**, item “Validação”. Use as
  âncoras e textos, pois as linhas podem mudar com novos eventos.
- **Confirmado:** o próprio inventário lista **17** arquivos de backend;
  `git ls-files --others --exclude-standard backend` e o manifesto abaixo
  confirmam essa contagem. Não há evidência de arquivo funcional faltando.
- **Impacto:** inconsistência leve de rastreabilidade; não é falha funcional
  nem exige alterar código. A governança exige identificação correta da
  entrega ainda sem commit.
- **Correção esperada:** atualizar a ficha atual com contagem/lista reais
  da versão que você devolver. Se criar arquivos durante a correção, use
  a nova contagem. Preserve o evento histórico do Sonnet e acrescente uma
  retificação no seu próprio evento, sem reescrever sua autoria ou relato.
- **Validação:** comparar lista/contagem da ficha, arquivos entregues e
  status Git; registrar separadamente backend, documentos e preexistências.

### Limitações conhecidas que não são novos defeitos de B01

O README já identifica schemas como rascunho, ausência de rota de análise,
aceitação de espaços em branco nas entradas, validação ainda parcial das
posições/referências de evidências, ausência de unicidade dos IDs e ausência
de regra cruzada prospect/churn. Também documenta que o schema de erro ainda
não é um manipulador HTTP. Esses pontos pertencem à consolidação C01 ou aos
serviços/rota posteriores. Preserve a visibilidade das limitações, sem
concluir que estão implementadas e sem antecipar aqueles PRs.

Se encontrar outro problema real de B01, atribua o próximo ID `B01-R03`,
localize o problema, reproduza quando viável e justifique impacto e correção.
Se discordar de um achado, apresente código/cenário que fundamente sua
conclusão. Não produza alterações artificiais para aparentar revisão.

## Execução e entrega esperadas

1. Confirme versão, escopo e situação Git antes de editar; registre divergências.
2. Faça revisão própria de configuração, instalação, inicialização, rota,
   schemas provisórios, testes e documentação. Confirme os achados.
3. Corrija apenas problemas comprovados de B01 e acrescente testes
   proporcionais ao comportamento corrigido.
4. Rode a suíte e as reproduções afetadas. Para instalação limpa, use
   ambiente temporário separado da `.venv` existente se precisar reproduzir
   esse critério. Registre comandos, diretórios, resultados e limitações.
   Respeite as permissões do ambiente; diferencie falhas de infraestrutura
   de falhas do código. Não publique nem faça operações Git além das
   autorizadas para a rodada.
5. Se executar Uvicorn, use porta disponível, registre os resultados HTTP
   e encerre apenas o processo que você iniciou. Verifique que inicializar
   a API não executa o experimento acadêmico.
6. Antes de devolver, **atualize a ficha B01, o índice e acrescente seu evento
   em `REGISTRO_TRABALHO.md`**, preservando o histórico e os registros de
   outros agentes. Registre a revisão também se não mudar código.
7. Entregue o relatório da seção 8 da governança, com: critérios → evidências;
   cada achado → confirmado/corrigido/não confirmado/pendente; arquivos;
   testes; não executado; limitações; versão final identificada; branch/base/
   HEAD; Git da entrega; publicação; PR remoto; integração no destino e na
   principal; Git do próprio registro; próximo responsável e ID do evento.

Separe **entrega do executor finalizada**, **revisão concluída**, **aprovação
final pelo Codex**, **commit**, **push** e **integração**. Nesta rodada o resultado
normal é uma entrega local revisada/corrigida, ainda `NAO_COMMITADO` na branch
`feat/b01-fundacao-api`, `NAO_PUBLICADO` e `NAO_INTEGRADO`; a atualização do
registro também estará sem commit. Use `NAO_VERIFICADO` onde faltar evidência.
Não marque `APROVADO` ou `INTEGRADO`; devolva ao Codex para verificação final
e aguarde coordenação, sem iniciar C01 ou outro PR.

## Manifesto da versão examinada na preparação

SHA-256 dos bytes dos 17 arquivos de `backend/` e do `.gitignore` preexistente,
capturado antes da revisão do Opus. Isto identifica a entrega local; não é
hash de commit. Compare antes de editar; depois identifique a versão final.
Arquivos ignorados e documentação de outras tarefas não integram este manifesto.

```text
9d0141d9227fcc17848b1d913309d3a575580c69055127c21c37a49217a6bfc9  backend/.env.example
810bcfb755e84e591a4549684c181751a76449e56dde6a673a3def9eab496948  backend/README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/__init__.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/api/__init__.py
bbf278518f1c7c68f6cfb2c8d3dbcfe046cee1f4a0938bd1432f60438f4535c0  backend/app/api/health.py
7a3f446c0eb0ee0c9097e1181bea1cb8fa34b1b158c30086f7f842f778c4e071  backend/app/config.py
462d9c5b7346fc2886fa387e46a14e0a47d9749682970d7129ecd5779606e37f  backend/app/main.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/app/schemas/__init__.py
6536bdbe96a55266f3970a1de654a2d364c2fa4c2bde25290d8333f50ad99172  backend/app/schemas/analise.py
8ef0cf6a37ac8d7094e10d7f882ac6f6b900a271430c270a000f646dcc9d2606  backend/app/schemas/comum.py
b245001f0aacc401ef3fd49ee365ed5f9b29e4e484eb1f679363943f924563a2  backend/app/schemas/erro.py
fec3a17ae89e48a06c6c9eb109659b7f7c58c0b473a66f7b036d85fa2f7defcc  backend/app/schemas/reuniao.py
5a57cc8f2074b08e1d1144b1cd823107433146590e873cfb9bc1f0ea1733597b  backend/app/schemas/saude.py
0345ccb5fd065fef0f53b0518913588cb8b5b7e4307699ca4c307179ffaee533  backend/pyproject.toml
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  backend/tests/__init__.py
fd027229ca2ee7360bf3a6ccb8fda443e1868becd7d8f59404de2a3d7c54853f  backend/tests/test_health.py
59319417301ad4c1a7a75d1f932aebe900ca75a6f1f4d72b5769d0cc6f5abed9  backend/tests/test_schemas.py
1aa25e874ab84b42c813dfe393fc77292946becce0d2bc3744674ac9a21568b6  .gitignore
```
