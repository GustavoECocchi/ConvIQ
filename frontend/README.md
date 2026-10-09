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

## Cliente da API (F02-B)

`src/services/api.ts` envia `POST /analises/texto` (contrato C01) e devolve a resposta tipada, sem recalcular sinais. Ainda não é usado pela interface (formulário e resultado vêm em F03–F06).

- **Endereço da API:** variável `VITE_API_BASE_URL`, com o prefixo `/api`. Valor local em [`.env.example`](.env.example) (`http://localhost:8000/api`, o mesmo que a API usa por padrão); para trocar, copie para `.env.local` (ignorado pelo Git). Sem a variável, vale o padrão local. A base é juntada ao caminho com uma só barra, com ou sem barra final, e o cliente não acrescenta `/api` por conta própria.
- **Uso:** `analisarTexto(pedido, { signal })`; o `AbortSignal` é repassado ao `fetch`. Para testes, `criarClienteApi({ baseUrl, fetchImpl })`.
- **Falhas:** toda rejeição é um `ErroDaApi` com `falha.tipo`: `validacao` (HTTP 422 com `{"erro": {"codigo", "mensagem"}}`, que traz o código e a mensagem da API), `http` (outro status, com `status`), `rede` (o `fetch` falhou ou a conexão caiu durante a leitura do corpo), `cancelado` (o sinal foi acionado, não é falha de rede) e `resposta_invalida` (corpo completo de 200 ou 422 fora do schema de C01; um 422 malformado nunca vira erro de campo). Um 200 só é aceito se seguir o schema de C01: textos obrigatórios preenchidos, `inicio >= 0` e `fim > inicio` em cada evidência, IDs de evidência únicos e toda referência apontando para uma evidência existente. O cliente não confere o recorte literal nem regras de produto, como o próprio schema; o mesmo ID pode ser citado por listas diferentes. `mensagemDaFalha(falha)` devolve uma mensagem em português para o usuário, sem corpo nem detalhes internos do servidor.
- **CORS:** a API só libera por padrão a origem `http://localhost:5173`; abrir a página em `http://127.0.0.1:5173` é outra origem e o navegador bloqueia. A conferência real no navegador fica para F06-A.
- **Testes:** `npm test` usa `fetch` simulado (sem servidor).

## Decisões de interface

O [registro de referências de UX](docs/UX_REFERENCIAS.md) documenta a inspiração visual, a hierarquia de informação e os cuidados previstos para os próximos cartões. Prévia: [desktop](docs/preview-f01-desktop.png) e [celular](docs/preview-f01-mobile.png). A página usa rótulos diretos e um exemplo textual para explicar a ligação entre sinal e evidência. Gráficos e contadores serão usados apenas se os dados disponíveis sustentarem uma comparação real.

## Próximos cartões

F02 adicionará tipos e cliente HTTP conforme o contrato C01 em `../docs/contratos/analise-texto.md`. F03 e F04 entregarão formulário e card; F05, consulta de evidências; F06, a integração de texto com `POST /api/analises/texto`. Os cartões futuros devem manter a navegação superior, os estados claros e a ligação literal aos trechos da transcrição.
