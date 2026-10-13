// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PAGINAS } from './destinos.ts'
import { rotas } from './rotas.tsx'
import { ROTULO_EXEMPLO, exemplos } from './services/mocks/exemplos.ts'

let fetchEspiao: ReturnType<typeof vi.fn>

beforeEach(() => {
  fetchEspiao = vi.fn()
  vi.stubGlobal('fetch', fetchEspiao)
  document.title = ''
  ;(document.activeElement as HTMLElement | null)?.blur()
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function abrir(caminho: string) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] })
  render(<RouterProvider router={roteador} />)
  return roteador
}

const h1 = () => screen.getByRole('heading', { level: 1 })
const CAMINHO = PAGINAS.exemploResultado.caminho

describe('rota didática /exemplo/resultado', () => {
  it('mostra o rótulo ilustrativo e o aviso antes do resumo', () => {
    abrir(CAMINHO)
    const aviso = screen.getByRole('note')
    const resumo = screen.getByRole('region', { name: 'Reunião analisada' })

    expect(aviso.textContent).toContain(ROTULO_EXEMPLO)
    expect(aviso.textContent).toContain('não é uma análise enviada')
    expect(aviso.compareDocumentPosition(resumo) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('injeta a fixture: identificação, sentimento e churn do exemplo', () => {
    abrir(CAMINHO)
    const { entrada } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!

    expect(screen.getByText(entrada.titulo)).toBeTruthy()
    expect(screen.getByText(entrada.empresa)).toBeTruthy()
    expect(document.querySelector('[data-sentimento="negativo"]')).not.toBeNull()
    expect(document.querySelector('[data-churn="sinal_detectado"]')).not.toBeNull()
  })

  it('título do documento, h1 único e landmarks coerentes com as outras páginas', () => {
    abrir(CAMINHO)

    expect(document.title).toBe(PAGINAS.exemploResultado.titulo)
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(h1().textContent).toBe('Exemplo de resultado')
    expect(h1().getAttribute('tabindex')).toBe('-1')
    expect(screen.getByRole('main').id).toBe('conteudo')
    // Fora do menu, nenhum item fica atual.
    const menu = within(screen.getByRole('navigation', { name: 'Navegação principal' }))
    expect(menu.getAllByRole('link').map((l) => l.textContent)).toEqual(['Visão geral', 'Como ler os sinais'])
    expect(menu.getAllByRole('link').filter((l) => l.getAttribute('aria-current') === 'page')).toHaveLength(0)
  })

  it('ao navegar até ela, título e foco vão para o h1; o retorno ao guia funciona', async () => {
    const roteador = abrir('/como-ler')
    await act(async () => {
      await roteador.navigate(CAMINHO)
    })

    expect(document.title).toBe(PAGINAS.exemploResultado.titulo)
    expect(document.activeElement).toBe(h1())

    fireEvent.click(screen.getAllByRole('link', { name: /Voltar ao guia/ })[0])

    expect(roteador.state.location.pathname).toBe('/como-ler')
    expect(document.title).toBe(PAGINAS.comoLer.titulo)
    expect(document.activeElement).toBe(h1())
  })

  it('não faz pedido HTTP', () => {
    abrir(CAMINHO)

    expect(fetchEspiao).not.toHaveBeenCalled()
  })

  it('links internos só apontam para destinos implementados', () => {
    abrir(CAMINHO)
    const destinos = [...document.querySelectorAll<HTMLAnchorElement>('a[href]')]
      .map((a) => a.getAttribute('href')!)
      .filter((href) => !href.startsWith('#'))

    expect(destinos.every((d) => d === '/' || d === '/como-ler')).toBe(true)
  })
})

describe('isolamento da rota didática', () => {
  it.each(['/', '/como-ler', '/analises/nova', '/nao-existe'])('nenhum link em %s aponta para ela', (caminho) => {
    abrir(caminho)
    const hrefs = [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href'))

    expect(hrefs).not.toContain(CAMINHO)
  })

  it('o formulário preenchido e conferido não leva ao exemplo nem mostra resultado', () => {
    const roteador = abrir('/analises/nova')
    fireEvent.change(screen.getByLabelText('Título da reunião'), { target: { value: 'Reunião' } })
    fireEvent.change(screen.getByLabelText('Empresa'), { target: { value: 'Empresa' } })
    fireEvent.change(screen.getByLabelText('Vínculo com a empresa'), { target: { value: 'cliente' } })
    fireEvent.change(screen.getByLabelText('Transcrição da reunião'), { target: { value: 'Texto da reunião.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Conferir dados' }))

    expect(roteador.state.location.pathname).toBe('/analises/nova')
    expect(screen.queryByText(ROTULO_EXEMPLO)).toBeNull()
    expect(screen.queryByRole('region', { name: 'Reunião analisada' })).toBeNull()
    expect(fetchEspiao).not.toHaveBeenCalled()
  })

  it.each(['/exemplo', '/exemplo/resultado/extra', '/analises/resultado'])('%s continua sendo 404', (caminho) => {
    abrir(caminho)

    expect(h1().textContent).toBe('Página não encontrada')
    expect(screen.queryByText(ROTULO_EXEMPLO)).toBeNull()
  })
})
