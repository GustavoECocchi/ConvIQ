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

## Decisões de interface

O [registro de referências de UX](docs/UX_REFERENCIAS.md) documenta a inspiração visual, a hierarquia de informação e os cuidados previstos para os próximos cartões. Prévia: [desktop](docs/preview-f01-desktop.png) e [celular](docs/preview-f01-mobile.png). A página usa rótulos diretos e um exemplo textual para explicar a ligação entre sinal e evidência. Gráficos e contadores serão usados apenas se os dados disponíveis sustentarem uma comparação real.

## Próximos cartões

F02 adicionará tipos e cliente HTTP conforme o contrato C01 em `../docs/contratos/analise-texto.md`. F03 e F04 entregarão formulário e card; F05, consulta de evidências; F06, a integração de texto com `POST /api/analises/texto`. Os cartões futuros devem manter a navegação superior, os estados claros e a ligação literal aos trechos da transcrição.
