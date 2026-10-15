# Frontend do ConvIQ

Base React, TypeScript e Vite do cartão F01. A página inicial usa um dashboard horizontal com navegação superior e cartões amplos. O exemplo de evidência é identificado como ilustrativo e independente da análise real. Desde F06-A, `/analises/nova` envia a transcrição à API e `/analises/resultado` mostra a resposta, só em memória; F06-B fechou a jornada (ver a seção F06-B e o teste ponta a ponta).

## Requisitos

- Node.js 20.19+ ou 22.12+ (conforme o Vite 8).
- npm 10+.

## Executar

```bash
cd frontend
npm ci
npm run dev
```

Abra o endereço mostrado pelo Vite (normalmente `http://localhost:5173`). Para conferir a entrega:

```bash
npm run typecheck
npm run lint
npm run build
```

`npm run preview` serve os arquivos produzidos em `dist/`. `dist/` e `node_modules/` são ignoradas pelo Git.

## Rotas e navegação (F03-A)

Navegação de cliente com [React Router 7](https://reactrouter.com/start/declarative/routing) (`react-router`, escolhido pela extensibilidade para F03-B/F04 e por ser compatível com Node 20; a série 8 exige Node 22). As rotas ficam em `src/rotas.tsx`, os destinos em `src/destinos.ts`.

| Caminho | Página |
|---|---|
| `/` | Visão geral |
| `/como-ler` | Como ler os sinais: sentimento, os quatro estados de risco, oportunidades e evidências, com exemplo ilustrativo e retorno à visão geral |
| qualquer outro | Página não encontrada (404), com retorno à visão geral; não há redirecionamento silencioso |

- **Menu:** `aria-current="page"` em exatamente um item nas rotas conhecidas; na 404, em nenhum. A marca e os links do conteúdo só apontam para destinos que existem.
- **A cada navegação** (inclusive voltar e avançar): o título do documento acompanha a rota e o foco vai para o `h1` da página (`tabIndex={-1}`). Na carga inicial o foco não é movido, e o primeiro Tab continua em "Pular para o conteúdo". Mudar só o hash (o link de pular) não conta como navegação.
- **Acesso direto e atualizar a página:** `npm run dev` e `npm run preview` devolvem o app para qualquer caminho. Em outro servidor de arquivos, configure o mesmo fallback (todo caminho serve `index.html`). O `<title>` do HTML estático é o da visão geral até o app carregar.
- **Largura (F01-04):** de 320 px a desktop, inclusive com barra de rolagem clássica, não há rolagem horizontal; abaixo de ~370 px o menu vai para uma linha própria, com os dois itens sem quebra.
- **Testes:** `npm test` inclui `src/navegacao.test.tsx` (roteador em memória + jsdom): rotas diretas, 404, título, foco, `aria-current`, voltar/avançar, links só para destinos existentes e landmarks. Largura e rolagem horizontal **não** são cobertas por testes automáticos; foram conferidas no navegador (ver `docs/registro/F03-A.md`).
- **Fora do escopo:** formulário (`/analises/nova`, F03-B), cards de resultado (F04), evidências interativas (F05) e envio à API (F06). Capturas: [Como ler (desktop)](docs/preview-f03a-como-ler-desktop.png), [Como ler (celular)](docs/preview-f03a-como-ler-mobile.png), [menu em 320 px](docs/preview-f03a-320-menu.png) e [404](docs/preview-f03a-404-desktop.png).

## Cliente da API (F02-B)

`src/services/api.ts` envia `POST /analises/texto` (contrato C01) e devolve a resposta tipada, sem recalcular sinais. É usado por `/analises/nova` desde F06-A (ver a seção abaixo).

- **Endereço da API:** variável `VITE_API_BASE_URL`, com o prefixo `/api`. Valor local em [`.env.example`](.env.example) (`http://localhost:8000/api`, o mesmo que a API usa por padrão); para trocar, copie para `.env.local` (ignorado pelo Git). Sem a variável, vale o padrão local. A base é juntada ao caminho com uma só barra, com ou sem barra final, e o cliente não acrescenta `/api` por conta própria.
- **Uso:** `analisarTexto(pedido, { signal })`; o `AbortSignal` é repassado ao `fetch`. Para testes, `criarClienteApi({ baseUrl, fetchImpl })`.
- **Falhas:** toda rejeição é um `ErroDaApi` com `falha.tipo`: `validacao` (HTTP 422 com `{"erro": {"codigo", "mensagem"}}`, que traz o código e a mensagem da API), `http` (outro status, com `status`), `rede` (o `fetch` falhou ou a conexão caiu durante a leitura do corpo), `cancelado` (o sinal foi acionado, não é falha de rede) e `resposta_invalida` (corpo completo de 200 ou 422 fora do schema de C01; um 422 malformado nunca vira erro de campo). Um 200 só é aceito se seguir o schema de C01: textos obrigatórios preenchidos, `inicio >= 0` e `fim > inicio` em cada evidência, IDs de evidência únicos e toda referência apontando para uma evidência existente. O cliente não confere o recorte literal nem regras de produto, como o próprio schema; o mesmo ID pode ser citado por listas diferentes. `mensagemDaFalha(falha)` devolve uma mensagem em português para o usuário, sem corpo nem detalhes internos do servidor.
- **CORS:** a API só libera por padrão a origem `http://localhost:5173`; abrir a página em `http://127.0.0.1:5173` é outra origem e o navegador bloqueia. Conferido no navegador em F06-A (seção abaixo).
- **Testes:** `npm test` usa `fetch` simulado (sem servidor).

## Decisões de interface

O [registro de referências de UX](docs/UX_REFERENCIAS.md) documenta a inspiração visual, a hierarquia de informação e os cuidados previstos para os próximos cartões. Prévia: [desktop](docs/preview-f01-desktop.png) e [celular](docs/preview-f01-mobile.png). A página usa rótulos diretos e um exemplo textual para explicar a ligação entre sinal e evidência. Gráficos e contadores serão usados apenas se os dados disponíveis sustentarem uma comparação real.

## Integração real por texto (F06-A)

`/analises/nova` envia a reunião com `analisarTexto` (`src/services/api.ts`, sem replicar `fetch` nem regras) e, ao receber a resposta, navega para `/analises/resultado`, que mostra a identificação da reunião e o `ResultadoAnalise` com a resposta exata da API.

- **Estados do envio:** inicial; enviando (`role="status"`, botão "Enviando…" com `aria-disabled`, sem perder o foco, campos congelados e um só POST); erro (`role="alert"` com `mensagemDaFalha`, campos preservados, nova tentativa com os dados correntes); sucesso (navegação, foco no `h1`).
- **Memória, não armazenamento:** `src/analise/` guarda pedido, resposta e o texto digitado no `Layout`, acima das páginas. Nada vai a `localStorage`, `sessionStorage`, IndexedDB nem à URL; recarregar apaga tudo. **Editar dados** volta ao formulário preenchido; **Nova análise** limpa também o texto. A análise anterior sai da memória quando o formulário abre (ver F06-B), então nem um erro de envio a traz de volta.
- **Sem análise em memória** (abertura direta, recarga), `/analises/resultado` mostra um aviso simples com o caminho para Nova análise, nunca uma fixture (acabamento em F06-B).
- **Pedido obsoleto:** sair da página cancela o pedido (`AbortController`); uma resposta ou falha que chegue depois é ignorada.
- **Troca de resposta (O2 de F05-B):** `ResultadoAnalise` remonta quando recebe outro objeto de resposta, e seleção, anúncio, aviso e botão de origem recomeçam.

### Reproduzir com a API real

Dois terminais, a partir da raiz do checkout (o venv da pasta raiz tem instalação editável de outra pasta; por isso `PYTHONPATH`):

```bash
# API em http://localhost:8000
cd backend
PYTHONPATH=$PWD <venv>/bin/uvicorn app.main:app --port 8000

# Frontend em http://localhost:5173 (a base padrão da API já é http://localhost:8000/api)
cd frontend
npm ci
npm run dev -- --port 5173 --strictPort
```

Abra `http://localhost:5173/analises/nova`, preencha e envie. Essa origem está no CORS padrão do backend. `http://127.0.0.1:5173` é **outra origem**: sem configuração o navegador bloqueia o POST e a tela mostra o erro de rede. Para usá-la, suba a API com `ORIGENS_CORS='["http://127.0.0.1:5173"]'` e abra o Vite com `--host 127.0.0.1`. Para outra porta de API, defina `VITE_API_BASE_URL` (com `/api`) ao iniciar o Vite. Nada depende de serviço externo.

Um 422 real, sem alterar o servidor: uma transcrição só com o caractere de controle U+001F passa pela validação local (o `trim` do JavaScript não o remove) e o Python o apara, então a API responde 422.

## Jornada de texto completa (F06-B)

Orientação (`/`) → formulário (`/analises/nova`) → envio à API real → resultado (`/analises/resultado`) → Ver evidência / Voltar ao sinal → Editar dados ou Nova análise. O resultado continua só em memória; `/exemplo/resultado` segue identificado como ilustrativo.

- **Nova análise é uma só ação:** na visão geral, no resultado e no aviso de resultado ausente ela é o mesmo link (`LinkNovaAnalise`) e abre o formulário **vazio**. **Editar dados** é outra ação, com outro rótulo: reabre o formulário com o que foi digitado.
- **Sem aviso enganoso:** "Editar dados" e "Nova análise" são links, e a análise só sai da memória quando o formulário abre. A página de resultado fica na tela até ser trocada, então o aviso "não há análise" não aparece nem por um quadro (F06-A-04 O1; medido no Chromium com CPU 6× mais lenta). Um erro de envio não ressuscita o resultado anterior.
- **Falhas:** 422, rede e HTTP 4xx/5xx mostram um `role="alert"` com `mensagemDaFalha` (sem corpo nem detalhes do servidor), preservam os campos, e a nova tentativa envia os valores correntes, com um só POST por envio. O cliente de F02-B continua dono do `fetch` e da interpretação do contrato.
- **Durante o envio** (F06-A-04 O4): os campos de texto ficam `readOnly`, o vínculo recebe `aria-disabled="true"` (um `select` não tem `readonly`; a troca é ignorada), o formulário `aria-busy`, e o status diz que os campos ficam somente leitura até a resposta. O botão usa `aria-disabled` e mantém o foco.
- **Foco ao voltar em página rolada** (F04-B-02 O2): em voltar/avançar o navegador restaura a rolagem, e com `scroll-behavior: smooth` essa restauração é animada. O `Layout` espera a rolagem assentar (120 ms sem evento `scroll`, limite de 1,5 s) e então leva o foco ao `h1` se ele estiver visível, ou ao primeiro título visível (`h2`–`h4`) sem rolar; na carga inicial, no link de pular, na mudança só de hash e na navegação comum nada muda (foco no `h1`).
- **Limpeza de F06-A (O3):** `AnaliseRecebida.id` e o retorno de `receber`, que ninguém usava, foram removidos.

## Teste ponta a ponta (F06-B)

`npm run e2e` (`e2e/jornada.e2e.mjs`, executor `node --test` + `playwright-core`, sem serviço externo) sobe **a API deste checkout** em `http://localhost:8000` e o Vite em `http://localhost:5173`, abre o Chromium a 320 e 1440 px e percorre a jornada: envio sob latência (estado, um só POST, CORS da origem real), resultado com a resposta exata da API (ordem identificação → sinais → recomendações → transcrição, risco e oportunidade coexistindo, sem rolagem horizontal), Ver evidência e Voltar ao sinal, Editar dados e Nova análise (sem o aviso intermediário, com CPU 6× mais lenta), prospect (churn não aplicável), resultado ausente (abertura direta e recarga), 422 real, falha de rede real, HTTP 500, saída durante o envio e foco ao voltar em página rolada.

```bash
cd frontend
npm ci
# opcional: PYTHONPATH não é necessário; o teste o define. Use CONVIQ_PYTHON para outro Python (padrão: python3,
# com fastapi, uvicorn e pydantic-settings, ver ../backend/pyproject.toml).
# opcional: CHROME_PATH=/caminho/do/chrome ; E2E_LARGURAS=320,1440
npm run e2e
```

- **Portas:** 8000 e 5173 precisam estar livres (o teste falha dizendo qual está ocupada); ele sobe e encerra os dois processos. Fixas porque o CORS padrão da API só libera `http://localhost:5173`; `http://127.0.0.1:5173` é outra origem e fica fora deste teste.
- **Navegador:** `playwright-core` não baixa navegador. O teste usa `CHROME_PATH`, senão o `chrome-headless-shell` mais novo de `~/.cache/ms-playwright` (`npx playwright install chromium-headless-shell` o cria), senão o padrão do Playwright.
- **Limites:** só Chromium; sem leitor de tela, Firefox, Safari, aparelho real ou CI. O HTTP 500 é simulado com `page.route` (a API não o produz sob demanda); 200, 422 e a falha de rede são reais. Para voltar, o teste usa `history.back()` e espera a página nova assentar: o `page.goBack()` do CDP não restaura a rolagem neste Chromium, e voltar no meio da rolagem suave da página nova perde a posição salva (comportamento do navegador, não do app).
- `npm test` (Vitest/jsdom) não executa o E2E; o quadro único do aviso de ausência e a restauração animada de rolagem só aparecem num navegador real, por isso o E2E os cobre.

## Próximos cartões

Os cartões futuros devem manter a navegação superior, os estados claros e a ligação literal aos trechos da transcrição.
