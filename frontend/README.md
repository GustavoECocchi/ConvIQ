# Frontend do ConvIQ

Base React, TypeScript e Vite do cartão F01. A página inicial usa um dashboard horizontal com navegação superior e cartões amplos. O exemplo de evidência é identificado como ilustrativo; a página ainda não envia transcrições nem mostra resultados da API.

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

## Decisões de interface

O [registro de referências de UX](docs/UX_REFERENCIAS.md) documenta a inspiração visual, a hierarquia de informação e os cuidados previstos para os próximos cartões. Prévia: [desktop](docs/preview-f01-desktop.png) e [celular](docs/preview-f01-mobile.png). A página usa rótulos diretos e um exemplo textual para explicar a ligação entre sinal e evidência. Gráficos e contadores serão usados apenas se os dados disponíveis sustentarem uma comparação real.

## Próximos cartões

F02 adicionará tipos e cliente HTTP conforme o contrato C01 em `../docs/contratos/analise-texto.md`. F03 e F04 entregarão formulário e card; F05, consulta de evidências; F06, a integração de texto com `POST /api/analises/texto`. Os cartões futuros devem manter a navegação superior, os estados claros e a ligação literal aos trechos da transcrição.
