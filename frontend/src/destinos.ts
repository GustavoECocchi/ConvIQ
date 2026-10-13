/** Destinos implementados. Menu, marca e links de conteúdo só podem apontar para estes caminhos. */
export const PAGINAS = {
  visaoGeral: { caminho: '/', rotulo: 'Visão geral', titulo: 'ConvIQ — Visão geral' },
  comoLer: { caminho: '/como-ler', rotulo: 'Como ler os sinais', titulo: 'ConvIQ — Como ler os sinais' },
  novaAnalise: { caminho: '/analises/nova', rotulo: 'Nova análise', titulo: 'ConvIQ — Nova análise' },
} as const

export const TITULO_NAO_ENCONTRADA = 'ConvIQ — Página não encontrada'

/** Itens do menu superior, na ordem de leitura. Nova análise é alcançada pelo CTA, não pelo menu. */
export const ITENS_DO_MENU = [PAGINAS.visaoGeral, PAGINAS.comoLer] as const

export const CAMINHOS_CONHECIDOS: readonly string[] = [...ITENS_DO_MENU, PAGINAS.novaAnalise].map((pagina) => pagina.caminho)

/** Dados de cada rota guardados em `handle` e lidos pelo layout (título do documento). */
export interface DadosDaRota {
  titulo: string
}
