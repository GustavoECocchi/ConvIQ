// @vitest-environment jsdom
import { StrictMode } from 'react'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { CAMINHOS_CONHECIDOS, ITENS_DO_MENU, PAGINAS, TITULO_NAO_ENCONTRADA } from './destinos.ts'
import { rotas } from './rotas.tsx'

function abrir(caminho: string, { estrito = false } = {}) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] })
  const arvore = <RouterProvider router={roteador} />
  render(estrito ? <StrictMode>{arvore}</StrictMode> : arvore)
  return roteador
}

const titulo = () => screen.getByRole('heading', { level: 1 })
const itensAtuais = () =>
  within(screen.getByRole('navigation', { name: 'Navegação principal' }))
    .queryAllByRole('link')
    .filter((link) => link.getAttribute('aria-current') === 'page')
    .map((link) => link.textContent)

async function voltar(roteador: ReturnType<typeof abrir>, passos = -1) {
  await act(async () => {
    await roteador.navigate(passos)
  })
}

beforeEach(() => {
  document.title = ''
  ;(document.activeElement as HTMLElement | null)?.blur()
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('destinos', () => {
  it('menu e títulos usam só caminhos implementados e sem repetição', () => {
    expect(new Set(CAMINHOS_CONHECIDOS).size).toBe(CAMINHOS_CONHECIDOS.length)
    expect(CAMINHOS_CONHECIDOS).toEqual(['/', '/como-ler', '/analises/nova'])
    expect(ITENS_DO_MENU.map((item) => item.titulo)).toEqual([PAGINAS.visaoGeral.titulo, PAGINAS.comoLer.titulo])
    expect(new Set([...ITENS_DO_MENU.map((item) => item.titulo), PAGINAS.novaAnalise.titulo, TITULO_NAO_ENCONTRADA]).size).toBe(4)
  })
})

describe('rotas diretas', () => {
  it.each([
    ['/', 'Visão geral', PAGINAS.visaoGeral.titulo],
    ['/como-ler', 'Como ler os sinais', PAGINAS.comoLer.titulo],
  ])('abrir %s direto mostra a página, o título do documento e o item atual do menu', (caminho, h1, tituloDoc) => {
    abrir(caminho)

    expect(titulo().textContent).toBe(h1)
    expect(document.title).toBe(tituloDoc)
    expect(itensAtuais()).toEqual([h1])
  })

  it('na carga inicial o foco não é movido: o primeiro Tab continua no link de pular', () => {
    abrir('/como-ler', { estrito: true })

    expect(document.activeElement).toBe(document.body)
  })

  it('um caminho desconhecido mostra 404, sem item atual e sem redirecionar', () => {
    const roteador = abrir('/nao-existe')

    expect(titulo().textContent).toBe('Página não encontrada')
    expect(document.title).toBe(TITULO_NAO_ENCONTRADA)
    expect(itensAtuais()).toEqual([])
    expect(roteador.state.location.pathname).toBe('/nao-existe')
  })

  it.each(['/analises/nova/extra', '/analises', '/como-ler/extra', '/COMO-LER-X'])('%s (destino não implementado) é 404', (caminho) => {
    abrir(caminho)

    expect(titulo().textContent).toBe('Página não encontrada')
    expect(itensAtuais()).toEqual([])
  })
})

describe('navegação entre páginas', () => {
  it('ir de / para /como-ler e voltar: título, foco e item atual acompanham a rota', async () => {
    const roteador = abrir('/')
    expect(itensAtuais()).toEqual(['Visão geral'])

    fireEvent.click(within(screen.getByRole('navigation')).getByRole('link', { name: 'Como ler os sinais' }))

    expect(roteador.state.location.pathname).toBe('/como-ler')
    expect(document.title).toBe(PAGINAS.comoLer.titulo)
    expect(titulo().textContent).toBe('Como ler os sinais')
    expect(document.activeElement).toBe(titulo())
    expect(itensAtuais()).toEqual(['Como ler os sinais'])

    await voltar(roteador)

    expect(roteador.state.location.pathname).toBe('/')
    expect(document.title).toBe(PAGINAS.visaoGeral.titulo)
    expect(titulo().textContent).toBe('Visão geral')
    expect(document.activeElement).toBe(titulo())
    expect(itensAtuais()).toEqual(['Visão geral'])
  })

  it('Voltar para uma entrada com hash recupera o foco do título após a restauração da âncora', async () => {
    const quadros: FrameRequestCallback[] = []
    vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
      quadros.push(callback)
      return quadros.length
    })
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    const roteador = createMemoryRouter(rotas, {
      initialEntries: ['/#conteudo', '/como-ler'],
      initialIndex: 1,
    })
    render(<RouterProvider router={roteador} />)

    await voltar(roteador)
    expect(roteador.state.location.pathname).toBe('/')
    expect(roteador.state.location.hash).toBe('#conteudo')

    // O navegador pode restaurar o foco da âncora depois do efeito React.
    const principal = screen.getByRole('main')
    principal.focus()
    expect(document.activeElement).toBe(principal)
    expect(quadros).toHaveLength(1)
    act(() => quadros[0](performance.now()))
    expect(document.activeElement).toBe(titulo())
  })

  it('não foca o título antigo se o URL mudar antes do quadro pendente', async () => {
    const quadros: FrameRequestCallback[] = []
    vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
      quadros.push(callback)
      return quadros.length
    })
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    const roteador = createMemoryRouter(rotas, {
      initialEntries: ['/#conteudo', '/como-ler'],
      initialIndex: 1,
    })
    render(<RouterProvider router={roteador} />)

    await voltar(roteador)
    const principal = screen.getByRole('main')
    principal.focus()
    expect(quadros).toHaveLength(1)

    // A URL da próxima navegação já mudou, mas React ainda mostra a rota anterior.
    vi.stubGlobal('location', { pathname: '/como-ler' })
    act(() => quadros[0](performance.now()))
    expect(document.activeElement).toBe(principal)
  })

  it('avançar depois de voltar também leva título, foco e item atual para a página certa', async () => {
    const roteador = abrir('/')
    fireEvent.click(screen.getByRole('link', { name: 'Entenda o resultado' }))
    await voltar(roteador)
    await voltar(roteador, 1)

    expect(roteador.state.location.pathname).toBe('/como-ler')
    expect(document.title).toBe(PAGINAS.comoLer.titulo)
    expect(document.activeElement).toBe(titulo())
    expect(itensAtuais()).toEqual(['Como ler os sinais'])
  })

  it('"Entenda o resultado" abre /como-ler (não uma âncora)', () => {
    const roteador = abrir('/')
    const link = screen.getByRole('link', { name: /Entenda o resultado/ })

    expect(link.getAttribute('href')).toBe('/como-ler')
    fireEvent.click(link)
    expect(roteador.state.location.pathname).toBe('/como-ler')
  })

  it('de uma página válida para 404 e de volta: nenhum item fica atual no 404 e a página anterior volta intacta', async () => {
    const roteador = abrir('/como-ler')
    await act(async () => {
      await roteador.navigate('/inexistente')
    })

    expect(titulo().textContent).toBe('Página não encontrada')
    expect(itensAtuais()).toEqual([])
    expect(document.activeElement).toBe(titulo())

    await voltar(roteador)

    expect(titulo().textContent).toBe('Como ler os sinais')
    expect(itensAtuais()).toEqual(['Como ler os sinais'])
    expect(document.title).toBe(PAGINAS.comoLer.titulo)
  })

  it('o retorno da 404 leva à visão geral com título e foco corretos', () => {
    const roteador = abrir('/nada')

    fireEvent.click(screen.getByRole('link', { name: 'Ir para a visão geral' }))

    expect(roteador.state.location.pathname).toBe('/')
    expect(document.title).toBe(PAGINAS.visaoGeral.titulo)
    expect(document.activeElement).toBe(titulo())
    expect(itensAtuais()).toEqual(['Visão geral'])
  })

  it('a marca leva à visão geral e não conta como item atual do menu', () => {
    const roteador = abrir('/como-ler')
    const marca = screen.getByRole('link', { name: 'ConvIQ, visão geral' })

    expect(marca.getAttribute('href')).toBe('/')
    expect(marca.getAttribute('aria-current')).toBeNull()
    fireEvent.click(marca)
    expect(roteador.state.location.pathname).toBe('/')
  })

  it('mudar só o hash (link de pular) não move o foco nem repete a navegação', async () => {
    const roteador = abrir('/como-ler')
    await act(async () => {
      await roteador.navigate('/como-ler#conteudo')
    })

    expect(document.activeElement).toBe(document.body)
    expect(document.title).toBe(PAGINAS.comoLer.titulo)
  })
})

describe('links e landmarks', () => {
  it.each(['/', '/como-ler', '/analises/nova', '/rota-qualquer'])('em %s todo link interno aponta para um destino implementado', (caminho) => {
    abrir(caminho)
    const links = [...document.querySelectorAll<HTMLAnchorElement>('a[href]')]

    expect(links.length).toBeGreaterThan(2)
    for (const link of links) {
      const destino = link.getAttribute('href')!
      if (destino.startsWith('#')) {
        expect(document.getElementById(destino.slice(1)), `alvo de ${destino}`).not.toBeNull()
      } else {
        expect(CAMINHOS_CONHECIDOS, `link "${link.textContent?.trim()}"`).toContain(destino)
      }
    }
  })

  it.each(['/', '/como-ler', '/analises/nova', '/nao-existe'])('em %s: link de pular, main focável, um h1 e landmarks', (caminho) => {
    abrir(caminho)
    const pular = screen.getByRole('link', { name: 'Pular para o conteúdo' })
    const principal = screen.getByRole('main')

    expect(pular.getAttribute('href')).toBe('#conteudo')
    expect(principal.id).toBe('conteudo')
    expect(principal.getAttribute('tabindex')).toBe('-1')
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(titulo().getAttribute('tabindex')).toBe('-1')
    expect(screen.getByRole('banner')).toBeTruthy()
    expect(screen.getByRole('contentinfo')).toBeTruthy()
    expect(screen.getByRole('navigation', { name: 'Navegação principal' })).toBeTruthy()
  })

  it('o menu lista os dois destinos, na ordem, com exatamente um item atual por rota conhecida', () => {
    abrir('/como-ler')
    const rotulos = within(screen.getByRole('navigation')).getAllByRole('link').map((link) => link.textContent)

    expect(rotulos).toEqual(ITENS_DO_MENU.map((item) => item.rotulo))
    expect(itensAtuais()).toHaveLength(1)
  })
})

describe('conteúdo de /como-ler', () => {
  it('explica sentimento, risco (quatro estados), oportunidades e evidências, com retorno e exemplo rotulado', () => {
    abrir('/como-ler')
    const nomes = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)

    expect(nomes).toEqual(['Sentimento', 'Risco de cancelamento', 'Oportunidades', 'Evidências'])
    for (const estado of ['Sinal detectado', 'Sem sinal detectado', 'Não aplicável', 'Informação insuficiente']) {
      expect(screen.getAllByText(estado).length).toBeGreaterThan(0)
    }
    expect(screen.getByText('EXEMPLO ILUSTRATIVO')).toBeTruthy()
    expect(screen.getAllByRole('link', { name: /Voltar à visão geral/ }).length).toBeGreaterThanOrEqual(1)
  })

  it('não mostra números, porcentagens nem resultado de análise do usuário', () => {
    abrir('/como-ler')
    const texto = document.querySelector('main')!.textContent!

    expect(texto).not.toMatch(/\d+\s?%/)
    expect(texto).not.toMatch(/\b\d{2,}\b/)
  })
})
