# Referências de interface para o ConvIQ

Pesquisa e decisões de 09/10/2026 para F01 e os cartões F02–F06. As fontes
servem como orientação de composição e compreensão; a interface do ConvIQ
usa conteúdo, componentes e marca próprios.

## Referência visual

- [Moneed Finance Dashboard — One Collective Design](https://dribbble.com/shots/27023128-Moneed-Finance-Dashboard-UI-Clarity-Meets-Control): navegação horizontal no topo, superfície clara, cartões modulares, destaque de uma informação principal e ações em posição consistente. No ConvIQ, o painel principal introduz a análise e um cartão adjacente explica a evidência. Não há saldo, gráfico ou indicador fictício.

## Técnicas aplicadas

1. **Hierarquia orientada à tarefa.** O [Carbon Design System — Dashboards](https://www.carbondesignsystem.com/building-blocks/data-visualization/dashboards) orienta priorizar as informações relevantes, limitar métricas e usar espaçamento para separar grupos. A leitura do ConvIQ começa com a reunião, segue para os sinais e termina nos trechos que os sustentam.
2. **Rótulo direto.** O [Carbon — Legends](https://www.carbondesignsystem.com/building-blocks/data-visualization/legends) prefere rotular dados diretamente quando possível. F04/F05 devem nomear sentimento, risco e oportunidade junto dos valores e evidências, sem depender de uma legenda distante.
3. **Cor acompanhada de texto.** A [W3C/WAI — Uso de cor](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) exige que cor não seja o único meio de comunicar significado. Cartões, etiquetas e estados mostram sempre texto; os acentos azul, âmbar e verde apenas ajudam a varrer a página.
4. **Explicação acessível de gráficos.** A [W3C/WAI — Imagens complexas](https://www.w3.org/WAI/tutorials/images/complex/) recomenda resumo e descrição textual para gráficos que tragam informação. Se gráficos entrarem em outra etapa, terão rótulos, resumo legível e dados equivalentes. F01 evita gráficos sem séries reais.
5. **Estado vazio honesto.** F01 usa linguagem introdutória e um trecho marcado como exemplo ilustrativo. F03–F06 devem distinguir vazio, carregamento, erro e resultado real; nenhuma classificação deve parecer derivada de uma reunião ainda não analisada.
6. **Contraste de leitura.** A [W3C/WAI — Contraste mínimo](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum) pede 4,5:1 para texto normal. Os textos secundários de F01 foram escurecidos para manter legibilidade nos cartões e no fundo cinza.

## Direção para o resultado real

- Desktop: cabeçalho horizontal, visão principal larga e cartões de leitura ao lado/abaixo. Em telas estreitas, os cartões passam a uma coluna, preservando a ordem de leitura.
- Hierarquia do resultado: identificação da reunião → síntese dos sinais → cada sinal e sua evidência → transcrição completa. A ação de consultar o trecho deve ficar junto do sinal.
- Cada categoria terá nome, classificação escrita e descrição em linguagem simples. Não introduzir porcentagens de confiança ou tendências que a API não fornece.
- Evidências usam o trecho e os índices literais do contrato C01. Um mesmo ID pode sustentar mais de um sinal (B19), e intervalos aninhados continuam distintos.
- Recomendações aparecem como sugestões ligadas aos sinais, com espaço para informação insuficiente e para risco e oportunidade coexistirem.
