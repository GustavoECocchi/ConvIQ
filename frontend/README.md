# Frontend do ConvIQ

Base React, TypeScript e Vite do cartão F01. A página inicial usa um dashboard horizontal com navegação superior e cartões amplos. O exemplo de evidência é identificado como ilustrativo e independente da análise real. Desde F06-A, `/analises/nova` envia a transcrição à API e `/analises/resultado` mostra a resposta, só em memória.

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
- **Memória, não armazenamento:** `src/analise/` guarda pedido, resposta e o texto digitado no `Layout`, acima das páginas. Nada vai a `localStorage`, `sessionStorage`, IndexedDB nem à URL; recarregar apaga tudo. **Editar dados** volta ao formulário preenchido e esquece a análise; **Nova análise** limpa também o texto. Enviar de novo esquece a análise anterior antes de pedir a nova.
- **Sem análise em memória** (abertura direta, recarga), `/analises/resultado` mostra um aviso simples com o caminho para Nova análise, nunca uma fixture. O acabamento desse caso e da jornada fica em F06-B.
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

## Próximos cartões

F06-B fecha a jornada: resultado ausente após recarga, 422/rede/servidor em toda a jornada, títulos e foco, desktop/celular e o teste ponta a ponta no navegador. Os cartões futuros devem manter a navegação superior, os estados claros e a ligação literal aos trechos da transcrição.
