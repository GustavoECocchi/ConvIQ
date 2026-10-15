/** Destinos implementados. Menu, marca e links de conteúdo só podem apontar para estes caminhos. */
export const PAGINAS = {
  visaoGeral: { caminho: '/', rotulo: 'Visão geral', titulo: 'ConvIQ — Visão geral' },
  comoLer: { caminho: '/como-ler', rotulo: 'Como ler os sinais', titulo: 'ConvIQ — Como ler os sinais' },
  novaAnalise: { caminho: '/analises/nova', rotulo: 'Nova análise', titulo: 'ConvIQ — Nova análise' },
  resultado: { caminho: '/analises/resultado', rotulo: 'Resultado da análise', titulo: 'ConvIQ — Resultado da análise' },
  exemploResultado: { caminho: '/exemplo/resultado', rotulo: 'Exemplo de resultado', titulo: 'ConvIQ — Exemplo de resultado' },
} as const

export const TITULO_NAO_ENCONTRADA = 'ConvIQ — Página não encontrada'

/** Itens do menu superior, na ordem de leitura. Nova análise é alcançada pelo CTA; o exemplo didático, pelo guia. */
export const ITENS_DO_MENU = [PAGINAS.visaoGeral, PAGINAS.comoLer] as const

export const CAMINHOS_CONHECIDOS: readonly string[] = [...ITENS_DO_MENU, PAGINAS.novaAnalise, PAGINAS.resultado, PAGINAS.exemploResultado].map((pagina) => pagina.caminho)

/** Dados de cada rota guardados em `handle` e lidos pelo layout (título do documento). */
export interface DadosDaRota {
  titulo: string
}
