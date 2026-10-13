# F03-B — proposta de tela e critérios do formulário

Preparado pelo Codex em 09/10/2026 para o cartão F03-B do
[roteiro de navegação](PRS_FRONTEND_NAVEGACAO.md). É uma proposta de
implementação, sem código de tela entregue. O PR #7 (cliente HTTP) e o PR #9
(rotas e shell de F03-A) já foram integrados; F03-B ainda não tem código.

## Percurso da pessoa usuária

Visão geral → Nova análise → informar reunião → conferir dados → mensagem
“Dados prontos. A transcrição ainda não foi enviada.” A chamada à API,
o processamento e a tela de resultado entram em F06-A/F06-B. O texto
digitado permanece na tela depois de erro e de conferência válida.
O caminho direto /analises/nova mostra a mesma página; não promete
histórico, áudio ou salvamento.

## Proposta visual

Veja também o [wireframe desktop e celular](../../frontend/docs/proposta-f03b-desktop-mobile.svg), rotulado como proposta sem envio.

Desktop: manter a barra superior horizontal e uma área de conteúdo larga.
O formulário ocupa a coluna principal; uma coluna lateral curta explica
como preparar a transcrição e o que acontecerá depois, sem métricas fictícias.

    [ConvIQ]                         [Visão geral] [Como ler]
    ← Visão geral                  Nova análise por texto
    Organize os dados da reunião antes de conferir os sinais.
    ┌──────────────────────────────────────┐ ┌──────────────────────────┐
    │ Dados da reunião                     │ │ Antes de começar        │
    │ Título da reunião  [______________]  │ │ Cole a transcrição      │
    │ Empresa            [______________]  │ │ completa em texto.      │
    │ Vínculo            [Selecione      v] │ │ Os trechos sustentam    │
    │ Transcrição        [              ]  │ │ os sinais apresentados. │
    │                     [              ]  │ │ Sem envio nesta etapa.  │
    │                    [Conferir dados]   │ └──────────────────────────┘
    └──────────────────────────────────────┘

Celular (320–390 px): título, formulário e ajuda em uma coluna, nessa ordem.
Controles têm largura integral; a ajuda fica depois da ação, para não
interromper o preenchimento. Nenhum painel exige rolagem horizontal.

    [ConvIQ]
    [Visão geral] [Como ler]
    ← Visão geral
    Nova análise por texto
    [Título da reunião       ]
    [Empresa                 ]
    [Vínculo               v ]
    [Transcrição             ]
    [                        ]
    [Conferir dados          ]
    [Ajuda: antes de começar  ]

A página ganha uma entrada “Nova análise” na visão geral. O menu continua
com os dois destinos informativos de F03-A; assim o terceiro item não
quebra a barra de 320 px. Em /analises/nova, nenhum dos dois itens do menu
recebe aria-current. A rota define título de documento e h1, seguindo o
tratamento de foco de F03-A.

## Campos e validação

| Campo | Controle e rótulo | Regra local espelhada de C01 | Mensagem proposta |
|---|---|---|---|
| titulo | Texto, “Título da reunião” | Obrigatório; 1–200 pontos de código após remover espaços das pontas | “Informe o título da reunião.” / “Use até 200 caracteres no título.” |
| empresa | Texto, “Empresa” | Obrigatória; 1–200 pontos de código após remover espaços das pontas | “Informe a empresa.” / “Use até 200 caracteres no nome da empresa.” |
| vinculo | Select, “Vínculo com a empresa”; opção inicial “Selecione o vínculo” sem valor | cliente, prospect ou nao_informado | “Selecione o vínculo com a empresa.” |
| transcricao | Textarea, “Transcrição da reunião” | Pelo menos 1 caractere após remover espaços das pontas; sem teto local inventado | “Cole a transcrição da reunião.” |

Opções visíveis do vínculo: Cliente, Prospect, Não informado. A opção
“Não informado” é uma escolha real do contrato, distinta da opção inicial
vazia. Os quatro campos são obrigatórios. Não usar maxlength nativo nos
dois textos curtos: JavaScript conta unidades UTF-16, mas o backend conta
pontos de código; a validação local deve contar Array.from(valor.trim()).length
para não rejeitar prematuramente um emoji. A API continua sendo a autoridade
final para validação e pode devolver 422 em F06.

Ao submeter, apresentar um resumo “Confira os dados” acima dos campos, com
um link para cada campo inválido e texto idêntico ao erro ao lado do campo.
Mover o foco para o resumo. Cada controle inválido tem aria-invalid e
aria-describedby apontando para seu erro; corrigir um campo atualiza sua
mensagem sem apagar os demais valores. A documentação do
[W3C sobre formulários](https://www.w3.org/WAI/tutorials/forms/validation/)
e o [GOV.UK Error summary](https://design-system.service.gov.uk/components/error-summary/)
orientam esse padrão.

## Contrato interno e estados

MeetingForm recebe onSubmit(pedido: AnaliseTextoRequest). Só chama o
callback quando os quatro campos forem válidos, com os três textos
aparados nas pontas e o vínculo tipado. O componente não chama fetch,
não classifica texto e não navega ao resultado. A página F03-B usa o
callback para mostrar um status acessível: “Dados prontos. A transcrição
ainda não foi enviada.” O botão nesta fase se chama “Conferir dados”;
F06-A o conectará ao cliente real e passará a informar envio/erro.

Estados da tela: inicial, campos inválidos, dados conferidos. Não há
estado “enviando” nem resultado sintético. Ações de edição após a mensagem
mantêm todos os valores e retiram o status de conferência até nova
validação.

## Contraprovas de aceite para F03-B

1. Abrir /analises/nova diretamente e pelo CTA da visão geral mostra o
   mesmo formulário, título correto e foco no h1 ao navegar.
2. Quatro campos vazios ou com só espaços produzem quatro erros,
   nenhum callback e nenhum pedido HTTP; resumo recebe foco.
3. Título/empresa com 200 pontos de código passam; 201 falham.
   Incluir emoji e Unicode NFD nessa fronteira.
4. Vínculo inicial vazio falha; “Não informado” passa como
   nao_informado, sem virar prospect ou cliente.
5. Uma falha não apaga texto, opção selecionada ou transcrição; corrigir
   somente um campo preserva os demais.
6. Dados válidos chamam o callback uma vez com textos aparados,
   mostram a mensagem de não envio e não exibem sinais nem resultado.
7. Erros e controles são ligados por aria-describedby; links do resumo
   levam aos campos. Testar Tab, Enter e foco com navegador real.
8. Em 320, 390 e desktop com barra clássica, não há rolagem horizontal;
   ordem visual e de teclado segue título → formulário → ajuda.
9. / e /como-ler conservam os comportamentos de F03-A; rota 404
   continua honesta. A ausência de backend não muda o estado da tela.
