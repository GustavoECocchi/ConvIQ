// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PAGINAS } from '../destinos.ts'
import { rotas } from '../rotas.tsx'
import { MeetingForm } from './MeetingForm.tsx'
import { contarPontosDeCodigo } from './validacao.ts'

const NFD = 'é' // "é" decomposto: 2 pontos de código, 2 unidades UTF-16

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

function abrirPagina(caminho: string = PAGINAS.novaAnalise.caminho) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] })
  render(<RouterProvider router={roteador} />)
  return roteador
}

function abrirFormulario() {
  const onSubmit = vi.fn()
  const onEdit = vi.fn()
  render(<MeetingForm onSubmit={onSubmit} onEdit={onEdit} />)
  return { onSubmit, onEdit }
}

const campo = (nome: string) => screen.getByLabelText(nome) as HTMLInputElement
const titulo = () => campo('Título da reunião')
const empresa = () => campo('Empresa')
const vinculo = () => screen.getByLabelText('Vínculo com a empresa') as HTMLSelectElement
const transcricao = () => screen.getByLabelText('Transcrição da reunião') as HTMLTextAreaElement
const digitar = (el: HTMLElement, valor: string) => fireEvent.change(el, { target: { value: valor } })
const conferir = () => fireEvent.click(screen.getByRole('button', { name: 'Analisar reunião' }))
const resumo = () => screen.queryByRole('group', { name: 'Confira os dados' })

function preencher(sobrescrever: Partial<Record<'titulo' | 'empresa' | 'vinculo' | 'transcricao', string>> = {}) {
  const v = { titulo: 'Reunião de renovação', empresa: 'Acme', vinculo: 'cliente', transcricao: 'Estamos satisfeitos.', ...sobrescrever }
  digitar(titulo(), v.titulo)
  digitar(empresa(), v.empresa)
  digitar(vinculo(), v.vinculo)
  digitar(transcricao(), v.transcricao)
}

describe('contagem de pontos de código', () => {
  it('conta emoji e NFD como o backend (pontos de código, não unidades UTF-16)', () => {
    expect(contarPontosDeCodigo('😀'.repeat(200))).toBe(200)
    expect('😀'.repeat(200).length).toBe(400)
    expect(contarPontosDeCodigo(NFD)).toBe(2)
    expect(contarPontosDeCodigo('  ab  ')).toBe(2)
  })
})

describe('rota /analises/nova', () => {
  it('abrir direto mostra o formulário, o título do documento e nenhum item atual no menu', () => {
    abrirPagina()

    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('Nova análise por texto')
    expect(document.title).toBe(PAGINAS.novaAnalise.titulo)
    expect(screen.getByRole('button', { name: 'Analisar reunião' })).toBeTruthy()
    const menu = within(screen.getByRole('navigation', { name: 'Navegação principal' }))
    expect(menu.getAllByRole('link').map((l) => l.textContent)).toEqual(['Visão geral', 'Como ler os sinais'])
    expect(menu.getAllByRole('link').filter((l) => l.hasAttribute('aria-current'))).toEqual([])
    expect(document.activeElement).toBe(document.body)
  })

  it('o CTA da visão geral abre a página, com título e foco no h1', () => {
    const roteador = abrirPagina('/')
    const cta = screen.getByRole('link', { name: 'Nova análise' })

    expect(cta.getAttribute('href')).toBe('/analises/nova')
    fireEvent.click(cta)

    expect(roteador.state.location.pathname).toBe('/analises/nova')
    expect(document.title).toBe(PAGINAS.novaAnalise.titulo)
    expect(document.activeElement).toBe(screen.getByRole('heading', { level: 1 }))
  })

  it('a ordem do documento é título, formulário e ajuda; "Voltar" leva à visão geral', () => {
    const roteador = abrirPagina()
    const h1 = screen.getByRole('heading', { level: 1 })
    const formulario = screen.getByRole('form', { name: 'Dados da reunião' })
    const ajuda = screen.getByRole('complementary', { name: 'Antes de começar' })

    expect(h1.compareDocumentPosition(formulario) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(formulario.compareDocumentPosition(ajuda) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    fireEvent.click(screen.getByRole('link', { name: /Voltar à visão geral/ }))
    expect(roteador.state.location.pathname).toBe('/')
  })

  it('/ e /como-ler mantêm o item atual de F03-A; 404 continua honesta', () => {
    abrirPagina('/como-ler')
    expect(screen.getByRole('link', { name: 'Como ler os sinais' }).getAttribute('aria-current')).toBe('page')
    cleanup()
    abrirPagina('/analises/nova/extra')
    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('Página não encontrada')
  })
})

describe('campos e select', () => {
  it('tem quatro campos rotulados, ajuda associada e select começando vazio', () => {
    abrirFormulario()

    for (const rotulo of ['Título da reunião', 'Empresa', 'Vínculo com a empresa', 'Transcrição da reunião']) {
      expect(campo(rotulo).getAttribute('aria-describedby')).toMatch(/^ajuda-/)
    }
    expect(vinculo().value).toBe('')
    const opcoes = within(vinculo()).getAllByRole('option').map((o) => [o.textContent, (o as HTMLOptionElement).value])
    expect(opcoes).toEqual([
      ['Selecione o vínculo', ''],
      ['Cliente', 'cliente'],
      ['Prospect', 'prospect'],
      ['Não informado', 'nao_informado'],
    ])
    expect(titulo().hasAttribute('maxlength')).toBe(false)
    expect(empresa().hasAttribute('maxlength')).toBe(false)
  })

  it('"Não informado" é válido e chega como nao_informado; select vazio é inválido', () => {
    const { onSubmit } = abrirFormulario()
    preencher({ vinculo: '' })
    conferir()

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText('Selecione o vínculo com a empresa.', { selector: '.field-error' })).toBeTruthy()

    digitar(vinculo(), 'nao_informado')
    conferir()
    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(onSubmit.mock.calls[0][0].vinculo).toBe('nao_informado')
  })
})

describe('validação ao enviar', () => {
  it.each([
    ['vazios', ''],
    ['só espaços', '   \n\t  '],
  ])('quatro campos %s: quatro erros, resumo com foco, links e associação', (_nome, valor) => {
    const { onSubmit } = abrirFormulario()
    digitar(titulo(), valor)
    digitar(empresa(), valor)
    digitar(transcricao(), valor)
    conferir()

    expect(onSubmit).not.toHaveBeenCalled()
    expect(fetchEspiao).not.toHaveBeenCalled()
    const grupo = resumo()!
    expect(grupo).toBeTruthy()
    expect(within(grupo).getByRole('heading', { name: 'Confira os dados' })).toBeTruthy()
    expect(document.activeElement).toBe(grupo)

    const esperado: [string, () => HTMLElement, string][] = [
      ['titulo', titulo, 'Informe o título da reunião.'],
      ['empresa', empresa, 'Informe a empresa.'],
      ['vinculo', vinculo, 'Selecione o vínculo com a empresa.'],
      ['transcricao', transcricao, 'Cole a transcrição da reunião.'],
    ]
    const links = within(grupo).getAllByRole('link')
    expect(links.map((l) => l.textContent)).toEqual(esperado.map(([, , msg]) => msg))
    esperado.forEach(([nome, controle, mensagem], i) => {
      const el = controle()
      const erro = document.getElementById(`erro-${nome}`)!
      expect(erro.textContent).toBe(mensagem)
      expect(el.getAttribute('aria-invalid')).toBe('true')
      expect(el.getAttribute('aria-describedby')!.split(' ')).toContain(erro.id)
      expect(links[i].getAttribute('href')).toBe(`#${el.id}`)
      fireEvent.click(links[i])
      expect(document.activeElement).toBe(el)
    })
  })

  it('cada envio inválido devolve o foco ao resumo', () => {
    abrirFormulario()
    conferir()
    titulo().focus()
    conferir()

    expect(document.activeElement).toBe(resumo())
  })

  it.each([
    ['emoji', '😀'],
    ['letras simples', 'a'],
    ['Unicode NFD (2 pontos por letra)', NFD],
  ])('título e empresa: %s no limite de 200 pontos passa e 201 falha', (_nome, unidade) => {
    const dentro = unidade.repeat(200 / contarPontosDeCodigo(unidade))
    const fora = dentro + 'x' // 201 pontos de código

    const { onSubmit } = abrirFormulario()
    preencher({ titulo: dentro, empresa: dentro })
    conferir()
    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(resumo()).toBeNull()

    preencher({ titulo: fora, empresa: dentro })
    conferir()
    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(document.getElementById('erro-titulo')!.textContent).toBe('Use até 200 caracteres no título.')
    expect(document.getElementById('erro-empresa')).toBeNull()

    preencher({ titulo: dentro, empresa: fora })
    conferir()
    expect(document.getElementById('erro-empresa')!.textContent).toBe('Use até 200 caracteres no nome da empresa.')
  })

  it('espaços nas pontas não contam para o limite', () => {
    const { onSubmit } = abrirFormulario()
    preencher({ titulo: `  ${'a'.repeat(200)}  `, empresa: `\n${'b'.repeat(200)}\t` })
    conferir()

    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('a transcrição não tem limite máximo local', () => {
    const { onSubmit } = abrirFormulario()
    preencher({ transcricao: 'palavra '.repeat(50_000) })
    conferir()

    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(onSubmit.mock.calls[0][0].transcricao.length).toBe(50_000 * 8 - 1)
  })
})

describe('preservação e correção', () => {
  it('um envio inválido preserva todos os valores e corrigir um campo atualiza só o seu erro', () => {
    const { onSubmit } = abrirFormulario()
    preencher({ titulo: ' ', empresa: 'Acme', vinculo: 'prospect', transcricao: '' })
    conferir()

    expect(titulo().value).toBe(' ')
    expect(empresa().value).toBe('Acme')
    expect(vinculo().value).toBe('prospect')
    expect(document.getElementById('erro-titulo')).toBeTruthy()
    expect(document.getElementById('erro-transcricao')).toBeTruthy()

    digitar(titulo(), 'Renovação')
    expect(document.getElementById('erro-titulo')).toBeNull()
    expect(titulo().hasAttribute('aria-invalid')).toBe(false)
    expect(titulo().getAttribute('aria-describedby')).toBe('ajuda-titulo')
    expect(document.getElementById('erro-transcricao')).toBeTruthy()
    expect(transcricao().getAttribute('aria-invalid')).toBe('true')
    expect(empresa().value).toBe('Acme')
    expect(vinculo().value).toBe('prospect')
    expect(within(resumo()!).getAllByRole('link')).toHaveLength(1)

    // Reintroduzir um erro troca a mensagem do próprio campo.
    digitar(titulo(), 'x'.repeat(201))
    expect(document.getElementById('erro-titulo')!.textContent).toBe('Use até 200 caracteres no título.')

    digitar(titulo(), 'Renovação')
    digitar(transcricao(), 'Texto')
    expect(resumo()).toBeNull()
    expect(onSubmit).not.toHaveBeenCalled()
    conferir()
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('antes do primeiro envio, editar não mostra erros', () => {
    abrirFormulario()
    digitar(titulo(), '')
    digitar(empresa(), '   ')

    expect(resumo()).toBeNull()
    expect(document.querySelector('.field-error')).toBeNull()
  })
})

describe('envio válido', () => {
  it('chama o callback uma vez com textos aparados e o vínculo tipado, sem HTTP', () => {
    const { onSubmit } = abrirFormulario()
    preencher({ titulo: '  Reunião  ', empresa: '\tAcme S.A.\n', vinculo: 'cliente', transcricao: '\n  Olá, tudo bem?  \n' })
    conferir()

    expect(onSubmit).toHaveBeenCalledTimes(1)
    expect(onSubmit).toHaveBeenCalledWith({
      titulo: 'Reunião',
      empresa: 'Acme S.A.',
      vinculo: 'cliente',
      transcricao: 'Olá, tudo bem?',
    })
    expect(fetchEspiao).not.toHaveBeenCalled()
  })
})
