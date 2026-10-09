# PRs pequenos — navegação do usuário no frontend de texto

Planejado em 09/10/2026 pelo Codex. Este refinamento subdivide F02–F06 do PLANO_DESENVOLVIMENTO.md; conserva os critérios originais e não altera F07–F11 (áudio, histórico e revisão final). F01 está implementado apenas como diff local no worktree CONVIQ-f01, branch feat/f01-fundacao-react, base b688afb. F02-A começa depois de F01 ter uma versão própria revisada e commitada, para que cada PR tenha diff isolável. Nenhum cartão abaixo está implementado ou liberado por este documento.

## Jornada de texto que deve existir em F06-B

| Etapa | Caminho/estado | Ação e resposta visível |
|---|---|---|
| Orientação | / | Dashboard horizontal no desktop, CTA Nova análise e explicação breve; nenhum indicador de reunião inventado. |
| Entendimento | /como-ler | Explica sentimento, risco, oportunidades e evidências, com exemplo identificado como ilustrativo e retorno claro. |
| Entrada | /analises/nova | Título, empresa, vínculo e transcrição com rótulos, instruções e validação compatíveis com C01. |
| Envio | /analises/nova | Analisar transcrição anuncia andamento e impede envio duplicado; os dados digitados permanecem acessíveis. |
| Resultado | /analises/resultado | Identificação da reunião, resumo dos sinais, detalhe, recomendações e transcrição; ações Ver evidência, Editar dados e Nova análise. |
| Evidência | resultado, seção Transcrição | A ação no item que traz IDs de evidência seleciona o ID, leva ao intervalo literal no eco da API e mantém contexto; teclado e foco funcionam. |
| Falha | /analises/nova | Erro de campo, HTTP ou rede em texto claro; correção e nova tentativa sem perder entrada. |
| Resultado ausente | /analises/resultado sem estado em memória | Explica que não há análise aberta e oferece Nova análise. Não sugere histórico salvo. |
| Endereço desconhecido | qualquer outro caminho | Página não encontrada com retorno para a visão geral. |

O resultado é temporário em memória nesta fase: sem banco, histórico, login ou áudio. Ao recarregar a rota de resultado, o estado ausente é explícito. Nunca exibir um resultado fictício como se tivesse sido gerado da transcrição enviada. A rota de exemplo pode existir como material didático, mas precisa manter o rótulo EXEMPLO ILUSTRATIVO. Não pôr no menu itens de áudio, histórico ou configurações ainda inoperantes.

No desktop, manter a navegação superior horizontal de F01 e apresentar resumo e transcrição em regiões largas e legíveis. No celular, empilhar na ordem identificação → sinais → recomendações → transcrição. A ordem de foco deve acompanhar a leitura; o mesmo rótulo deve designar a mesma ação nas páginas. Ao navegar, atualizar título da página e levar foco ao conteúdo principal; estados de envio e erro devem ser anunciados. As decisões seguem as orientações de navegação consistente, ordem de foco e mensagens da W3C, e de retorno/erros do GOV.UK:
- https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html
- https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html
- https://www.w3.org/WAI/WCAG21/Understanding/status-messages.html
- https://www.w3.org/WAI/tutorials/forms/validation/
- https://design-system.service.gov.uk/components/back-link/
- https://design-system.service.gov.uk/components/error-summary/
- https://reactrouter.com/start/declarative/routing

## Cortes de PR

Um branch por cartão, a partir da versão integrada do predecessor; se houver dependência ainda aberta, declarar a base e revisar o diff próprio. Cada PR registra evento em docs/registro/<ID>.md e valida typecheck, lint, build, mais testes de interação quando houver comportamento novo. Capturas desktop/celular acompanham mudanças visuais. Não agrupar cartões por conveniência sem decisão da coordenação.

| Ordem | PR / nível | Entrega única e critério verificável | Depende de |
|---|---|---|---|
| 0 | F01 / B | Revisar a fundação já local: página abre, navegação atual é honesta, layout desktop/celular e teclado coerentes. Sem incluir rotas/formulário. | base b688afb |
| 1 | F02-A / B | Tipos TypeScript de entrada, resposta, enums e erro de C01; exemplos fictícios tipados e rotulados, inclusive prospect e informação insuficiente. Sem chamada HTTP. | F01, C01 |
| 2 | F02-B / A | Cliente POST /analises/texto com base configurável, AbortSignal, erro 422 padronizado, HTTP inesperado e falha de rede distintos; testes com fetch simulado. Sem UI. | F02-A |
| 3 | F03-A / B | Shell de rotas / e /como-ler, menu superior com estado ativo correto, 404, título/foco ao navegar. Em 320 px, menu legível sem quebra irregular nem rolagem horizontal com barra clássica; links só para destinos existentes. Resolva F01-04. | F01 |
| 4 | F03-B / B | Página /analises/nova e MeetingForm com quatro campos, validação local C01, mensagens junto aos campos, preservação dos valores e contrato de callback. Até F06, ação válida informa que a análise não foi enviada; não simula classificação. | F03-A, F02-A |
| 5 | F04-A / B | Resumo de resultado com identificação da reunião, sentimento e todos os estados de churn; dados vêm de props/fixture rotulada, sem classificação no navegador. | F02-A, F03-A |
| 6 | F04-B / B | Detalhe de oportunidades, produtos, concorrentes e recomendações, com listas vazias honestas; exemplo didático completo acessível pelo guia. | F04-A |
| 7 | F05-A / A | TranscriptViewer por índices de C01: recorte literal do eco, mesmo trecho repetido, emoji antes do sinal, acento NFD, IDs compartilhados e intervalos aninhados. Sem busca por texto. | F04-B |
| 8 | F05-B / B | Ação Ver evidência junto de churn, oportunidade ou recomendação com ID seleciona, rola e leva foco ao trecho, permite voltar ao contexto; uso por teclado e leitor de tela. | F05-A |
| 9 | F06-A / A | Submissão real, estados inicial/enviando/sucesso/erro, navegação para resultado em memória, voltar para editar e tentar novamente. Conferir CORS/origem real e rota no servidor. | F02-B, F03-B, F05-B, B04 |
| 10 | F06-B / B | Fechar jornada com resultado ausente, nova análise, 422/rede/servidor, títulos/foco, desktop/celular e teste ponta a ponta no navegador com a API real. Documentar execução e limites. | F06-A |

F03-A pode ser desenvolvido em paralelo ao cliente, mas sua integração deve manter a sequência de branches explícita. F04-A/B podem usar fixtures antes da ligação HTTP. F06-B é o marco de primeira jornada de texto utilizável; F07–F09 seguem para áudio quando C02 e backend estiverem prontos. F10 depende de persistência e listagem reais; F11 continua revisão visual final da jornada incluída na apresentação.

## Contraprovas de aceitação ao longo da série

- Prospect mostra churn não aplicável; informação insuficiente nunca parece risco baixo confirmado. Risco e oportunidade podem coexistir, com suas evidências separadas ou compartilhadas.
- A API usa índices Python de caracteres Unicode; JavaScript usa unidades UTF-16 em slice. Para localizar evidência, segmentar o eco por pontos de código (por exemplo, Array.from), sem procurar a primeira ocorrência do trecho. Conferir trecho literal, repetições, emoji e NFD.
- B19 pode reutilizar um ID nas referências expostas por C01; a interface não deve criar cópias falsas. O enum sentimento não traz IDs de evidência no contrato atual: não inventar uma ligação direta. Sobreposições e intervalos aninhados permanecem distintos.
- Formulário rejeita espaços vazios e título/empresa com mais de 200 caracteres; preserva conteúdo após erro e não dispara duas chamadas no mesmo envio. A API ainda valida tudo.
- Servidor atualmente permite por padrão a origem http://localhost:5173; http://127.0.0.1:5173 é outra origem. Em F06-A, alinhar o endereço usado no navegador com CORS configurado e verificar o POST real.
- F03-A verifica em 320 px com barra clássica: sem rolagem horizontal e sem quebra irregular dos links; aria-current deve seguir a rota atual, não ficar sempre na visão geral.
- Nenhuma tela promete salvar, recuperar, transcrever áudio, medir confiança ou comparar reuniões antes de existir contrato e backend para isso.
