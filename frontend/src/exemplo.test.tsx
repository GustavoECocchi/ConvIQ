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

  it('mostra o exemplo completo: detalhe depois do resumo, com a lista vazia de concorrentes explicada', () => {
    abrir(CAMINHO)
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const resumo = screen.getByRole('region', { name: 'Sinais da conversa' })
    const oportunidades = screen.getByRole('region', { name: 'Oportunidades' })
    const mencoes = screen.getByRole('region', { name: 'Menções na conversa' })
    const recomendacoes = screen.getByRole('region', { name: 'Recomendações' })

    expect(resumo.compareDocumentPosition(oportunidades) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(oportunidades.compareDocumentPosition(recomendacoes) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(within(oportunidades).getByText(resposta.oportunidades[0].descricao)).toBeTruthy()
    expect(within(mencoes).getByText('Fluig')).toBeTruthy()
    expect(resposta.concorrentes).toEqual([])
    expect(within(mencoes).getByText('Nenhum concorrente da lista conhecida foi citado.')).toBeTruthy()
    expect(within(recomendacoes).getAllByRole('listitem').map((li) => li.textContent)).toEqual(resposta.recomendacoes.map((r) => r.texto))
    expect(document.querySelector('.detalhe-metodo')!.textContent).toContain(resposta.versao_analise)
    expect(document.body.textContent).not.toMatch(/\be\d+\b/)
  })

  it('mostra a transcrição do exemplo por último, com os trechos destacados pelos índices e sem pedido HTTP', () => {
    abrir(CAMINHO)
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const recomendacoes = screen.getByRole('region', { name: 'Recomendações' })
    const transcricao = screen.getByRole('region', { name: 'Transcrição' })
    const texto = transcricao.querySelector('.transcricao-texto')!

    expect(recomendacoes.compareDocumentPosition(transcricao) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(texto.textContent).toBe(resposta.transcricao)
    expect([...texto.querySelectorAll('mark')].map((m) => m.textContent)).toEqual([
      'insatisfeitos',
      ' com o suporte',
      'Queremos conhecer o Fluig',
    ])
    expect(transcricao.textContent).not.toMatch(/\be\d+\b/)
    expect(transcricao.querySelector('a, button')).toBeNull()
    expect(fetchEspiao).not.toHaveBeenCalled()
  })

  it('os avisos do exemplo não dizem mais que os trechos não aparecem', () => {
    abrir(CAMINHO)

    expect(document.body.textContent).not.toContain('ainda não aparecem')
    expect(document.body.textContent).toContain('aparecem destacados na transcrição')
  })

  it('o guia leva ao exemplo, com título e foco no h1', () => {
    const roteador = abrir('/como-ler')
    const link = screen.getByRole('link', { name: 'Ver exemplo de resultado' })

    expect(link.getAttribute('href')).toBe(CAMINHO)
    fireEvent.click(link)

    expect(roteador.state.location.pathname).toBe(CAMINHO)
    expect(document.title).toBe(PAGINAS.exemploResultado.titulo)
    expect(document.activeElement).toBe(h1())
    expect(screen.getByRole('note').textContent).toContain(ROTULO_EXEMPLO)
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
  it.each(['/', '/analises/nova', '/nao-existe'])('nenhum link em %s aponta para ela', (caminho) => {
    abrir(caminho)
    const hrefs = [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href'))

    expect(hrefs).not.toContain(CAMINHO)
  })

  it('só o guia aponta para ela, uma vez, fora do menu', () => {
    abrir('/como-ler')
    const hrefs = [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href'))
    const menu = within(screen.getByRole('navigation', { name: 'Navegação principal' }))

    expect(hrefs.filter((href) => href === CAMINHO)).toHaveLength(1)
    expect(menu.getAllByRole('link').map((l) => l.getAttribute('href'))).not.toContain(CAMINHO)
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
    expect(screen.queryByRole('region', { name: 'Recomendações' })).toBeNull()
    expect(fetchEspiao).not.toHaveBeenCalled()
  })

  it.each(['/exemplo', '/exemplo/resultado/extra', '/analises/resultado'])('%s continua sendo 404', (caminho) => {
    abrir(caminho)

    expect(h1().textContent).toBe('Página não encontrada')
    expect(screen.queryByText(ROTULO_EXEMPLO)).toBeNull()
  })
})
