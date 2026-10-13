import type { RouteObject } from 'react-router'
import { PAGINAS, TITULO_NAO_ENCONTRADA } from './destinos.ts'
import type { DadosDaRota } from './destinos.ts'
import { Layout } from './layout/Layout.tsx'
import { ComoLer } from './paginas/ComoLer.tsx'
import { ExemploResultado } from './paginas/ExemploResultado.tsx'
import { NaoEncontrada } from './paginas/NaoEncontrada.tsx'
import { NovaAnalise } from './paginas/NovaAnalise.tsx'
import { VisaoGeral } from './paginas/VisaoGeral.tsx'

const dados = (titulo: string): { handle: DadosDaRota } => ({ handle: { titulo } })

export const rotas: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      { path: PAGINAS.visaoGeral.caminho, element: <VisaoGeral />, ...dados(PAGINAS.visaoGeral.titulo) },
      { path: PAGINAS.comoLer.caminho, element: <ComoLer />, ...dados(PAGINAS.comoLer.titulo) },
      { path: PAGINAS.novaAnalise.caminho, element: <NovaAnalise />, ...dados(PAGINAS.novaAnalise.titulo) },
      { path: PAGINAS.exemploResultado.caminho, element: <ExemploResultado />, ...dados(PAGINAS.exemploResultado.titulo) },
      // Caminho desconhecido mostra 404 com retorno, sem redirecionar em silêncio.
      { path: '*', element: <NaoEncontrada />, ...dados(TITULO_NAO_ENCONTRADA) },
    ],
  },
]
