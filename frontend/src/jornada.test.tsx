// @vitest-environment jsdom
import { StrictMode } from 'react'
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PAGINAS } from './destinos.ts'
import { rotas } from './rotas.tsx'
import { MeetingForm } from './formulario/MeetingForm.tsx'
import { exemplos } from './services/mocks/exemplos.ts'
import type { AnaliseTextoResponse } from './types/analise.ts'

// F06-A: envio real de /analises/nova (fetch simulado) e resultado em memória de /analises/resultado.

const respostaA = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!.resposta
const respostaB = exemplos.find((e) => e.chave === 'prospect-churn-nao-aplicavel')!.resposta
const URL_API = 'http://localhost:8000/api/analises/texto'

const json = (corpo: unknown, status = 200) => new Response(JSON.stringify(corpo), { status, headers: { 'Content-Type': 'application/json' } })

/** Resposta que só chega quando o teste mandar: permite observar o estado "enviando". */
function pendente() {
  let resolver!: (r: Response) => void
  let rejeitar!: (e: unknown) => void
  const promessa = new Promise<Response>((res, rej) => {
    resolver = res
    rejeitar = rej
  })
  return { promessa, resolver, rejeitar }
}

let fetchEspiao: ReturnType<typeof vi.fn>

beforeEach(() => {
  fetchEspiao = vi.fn()
  vi.stubGlobal('fetch', fetchEspiao)
  document.title = ''
  localStorage.clear()
  sessionStorage.clear()
  ;(document.activeElement as HTMLElement | null)?.blur()
  Element.prototype.scrollIntoView = vi.fn()
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function abrir(caminho: string = PAGINAS.novaAnalise.caminho, { estrito = false } = {}) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [caminho] })
  const arvore = <RouterProvider router={roteador} />
  render(estrito ? <StrictMode>{arvore}</StrictMode> : arvore)
  return roteador
}

const campo = (nome: string) => screen.getByLabelText(nome) as HTMLInputElement
const digitar = (el: HTMLElement, valor: string) => fireEvent.change(el, { target: { value: valor } })
const botaoEnviar = () => screen.getByRole('button', { name: /^(Analisar reunião|Enviando…)$/ })
const enviar = () => fireEvent.click(botaoEnviar())
const status = () => screen.getByRole('status').textContent
const erroDeEnvio = () => screen.queryByRole('alert')
const h1 = () => screen.getByRole('heading', { level: 1 }).textContent

function preencher(troca: Partial<Record<'titulo' | 'empresa' | 'vinculo' | 'transcricao', string>> = {}) {
  const v = { titulo: '  Renovação Acme  ', empresa: 'Acme', vinculo: 'cliente', transcricao: ' Estamos insatisfeitos com o suporte. ', ...troca }
  digitar(campo('Título da reunião'), v.titulo)
  digitar(campo('Empresa'), v.empresa)
  digitar(campo('Vínculo com a empresa'), v.vinculo)
  digitar(campo('Transcrição da reunião'), v.transcricao)
}

const corpoEnviado = (chamada = 0) => JSON.parse(fetchEspiao.mock.calls[chamada][1].body as string)
const concluir = (resposta: AnaliseTextoResponse = respostaA) => waitFor(() => expect(h1()).toBe('Resultado da análise')).then(() => resposta)

describe('estados do envio', () => {
  it('inicial: sem aviso, sem pedido, com o botão de envio e a ajuda sem prometer que nada é enviado', () => {
    abrir()

    expect(status()).toBe('')
    expect(erroDeEnvio()).toBeNull()
    expect(botaoEnviar().textContent).toBe('Analisar reunião')
    expect(botaoEnviar().hasAttribute('aria-disabled')).toBe(false)
    expect(fetchEspiao).not.toHaveBeenCalled()
    expect(document.body.textContent).not.toMatch(/nada é enviado|ainda não foi enviada|apenas confere/i)
    expect(document.body.textContent).toContain('o texto vai para a API do ConvIQ')
  })

  it('enviando: anuncia no status, o botão fica indisponível sem perder o foco e os campos não mudam', () => {
    const espera = pendente()
    fetchEspiao.mockReturnValue(espera.promessa)
    abrir()
    preencher()
    botaoEnviar().focus()
    enviar()

    expect(status()).toContain('Enviando a transcrição para análise')
    expect(botaoEnviar().textContent).toBe('Enviando…')
    expect(botaoEnviar().getAttribute('aria-disabled')).toBe('true')
    expect(botaoEnviar().hasAttribute('disabled')).toBe(false)
    expect(document.activeElement).toBe(botaoEnviar())
    expect(document.querySelector('form')!.getAttribute('aria-busy')).toBe('true')

    digitar(campo('Empresa'), 'Outra')
    expect(campo('Empresa').value).toBe('Acme')
  })

  it('envio duplicado (dois cliques e Enter no formulário) faz um só POST', () => {
    fetchEspiao.mockReturnValue(pendente().promessa)
    abrir()
    preencher()
    enviar()
    enviar()
    fireEvent.submit(document.querySelector('form')!)

    expect(fetchEspiao).toHaveBeenCalledTimes(1)
  })

  it('dois envios antes de a tela atualizar (mesmo lote) também fazem um só POST', () => {
    fetchEspiao.mockReturnValue(pendente().promessa)
    abrir()
    preencher()
    act(() => {
      fireEvent.click(botaoEnviar())
      fireEvent.click(botaoEnviar())
    })

    expect(fetchEspiao).toHaveBeenCalledTimes(1)
  })

  it('o formulário, com envio em andamento, não chama onSubmit nem aceita edição', () => {
    cleanup()
    const onSubmit = vi.fn()
    render(<MeetingForm onSubmit={onSubmit} enviando valoresIniciais={{ titulo: 'T', empresa: 'E', vinculo: 'cliente', transcricao: 'X' }} />)
    fireEvent.click(screen.getByRole('button', { name: 'Enviando…' }))
    digitar(campo('Empresa'), 'Outra')

    expect(onSubmit).not.toHaveBeenCalled()
    expect(campo('Empresa').value).toBe('E')
  })

  it('o POST usa o cliente de F02-B: URL, método, JSON com textos aparados e sinal de cancelamento', () => {
    fetchEspiao.mockReturnValue(pendente().promessa)
    abrir()
    preencher()
    enviar()

    const [url, init] = fetchEspiao.mock.calls[0]
    expect(url).toBe(URL_API)
    expect(init.method).toBe('POST')
    expect(corpoEnviado()).toEqual({ titulo: 'Renovação Acme', empresa: 'Acme', vinculo: 'cliente', transcricao: 'Estamos insatisfeitos com o suporte.' })
    expect(init.signal).toBeInstanceOf(AbortSignal)
  })

  it('dados inválidos não chamam a API', () => {
    abrir()
    preencher({ empresa: '  ' })
    enviar()

    expect(fetchEspiao).not.toHaveBeenCalled()
    expect(screen.getByRole('group', { name: 'Confira os dados' })).toBeTruthy()
  })

  it('sucesso: navega para o resultado, com título do documento e foco no h1', async () => {
    fetchEspiao.mockResolvedValue(json(respostaA))
    const roteador = abrir()
    preencher()
    enviar()
    await concluir()

    expect(roteador.state.location.pathname).toBe('/analises/resultado')
    expect(document.title).toBe(PAGINAS.resultado.titulo)
    expect(document.activeElement).toBe(screen.getByRole('heading', { level: 1 }))
  })
})

describe('falhas e nova tentativa', () => {
  it.each([
    ['validação 422', () => json({ erro: { codigo: 'validacao', mensagem: 'A transcrição é longa demais.' } }, 422), 'A transcrição é longa demais.'],
    ['erro HTTP 500', () => json({ detalhe: 'x' }, 500), 'erro 500'],
    ['resposta fora do contrato', () => json({ transcricao: 'x' }), 'formato inesperado'],
  ])('%s: mostra a mensagem do cliente, preserva os campos e libera nova tentativa', async (_nome, resposta, trecho) => {
    fetchEspiao.mockResolvedValueOnce(resposta())
    const roteador = abrir()
    preencher()
    enviar()

    const alerta = await screen.findByRole('alert')
    expect(alerta.textContent).toContain(trecho)
    expect(alerta.textContent).toContain('Seus dados continuam no formulário')
    expect(status()).toBe('')
    expect(screen.getAllByRole('alert')).toHaveLength(1)
    expect(roteador.state.location.pathname).toBe('/analises/nova')
    expect(campo('Título da reunião').value).toBe('  Renovação Acme  ')
    expect(campo('Transcrição da reunião').value).toBe(' Estamos insatisfeitos com o suporte. ')
    expect(botaoEnviar().textContent).toBe('Analisar reunião')
    expect(botaoEnviar().hasAttribute('aria-disabled')).toBe(false)
  })

  it('falha de rede: mensagem de rede e nova tentativa com os dados correntes até o sucesso', async () => {
    fetchEspiao.mockRejectedValueOnce(new TypeError('Failed to fetch')).mockResolvedValueOnce(json(respostaA))
    abrir()
    preencher()
    enviar()

    expect((await screen.findByRole('alert')).textContent).toContain('Não foi possível falar com o servidor')

    digitar(campo('Empresa'), 'Acme Brasil')
    expect(erroDeEnvio()).toBeNull()
    enviar()
    await concluir()

    expect(fetchEspiao).toHaveBeenCalledTimes(2)
    expect(corpoEnviado(0).empresa).toBe('Acme')
    expect(corpoEnviado(1).empresa).toBe('Acme Brasil')
  })

  it('nova tentativa sem editar reenvia os mesmos dados', async () => {
    fetchEspiao.mockResolvedValueOnce(json({}, 503)).mockResolvedValueOnce(json(respostaA))
    abrir()
    preencher()
    enviar()
    await screen.findByRole('alert')
    enviar()
    await concluir()

    expect(corpoEnviado(1)).toEqual(corpoEnviado(0))
  })
})

describe('resultado em memória', () => {
  async function enviarComSucesso(resposta: AnaliseTextoResponse = respostaA, troca = {}) {
    fetchEspiao.mockResolvedValueOnce(json(resposta))
    const roteador = abrir()
    preencher(troca)
    enviar()
    await concluir()
    return roteador
  }

  it('mostra a identificação do pedido e a resposta exata da API: sinais, transcrição devolvida e Ver evidência', async () => {
    await enviarComSucesso()

    expect(screen.getByText('Renovação Acme')).toBeTruthy()
    expect(screen.getByText('Acme', { selector: '.resumo-reuniao *' })).toBeTruthy()
    expect(document.querySelector('[data-sentimento="negativo"]')).not.toBeNull()
    expect(document.querySelector('[data-churn="sinal_detectado"]')).not.toBeNull()
    const transcricao = screen.getByRole('region', { name: 'Transcrição' })
    expect(transcricao.querySelector('.transcricao-texto')!.textContent).toBe(respostaA.transcricao)
    expect(screen.queryByText(/exemplo didático/i)).toBeNull()
    expect(screen.queryByRole('note')).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Ver evidência: risco de cancelamento' }))
    expect([...transcricao.querySelectorAll('mark[data-selecionada]')].length).toBeGreaterThan(0)
    expect(document.activeElement!.tagName).toBe('MARK')
  })

  it('não grava em armazenamento persistente', async () => {
    await enviarComSucesso()

    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)
  })

  it('Editar dados: volta ao formulário preenchido, sem pedido novo, e a análise some da memória', async () => {
    const roteador = await enviarComSucesso()
    fetchEspiao.mockClear()
    fireEvent.click(screen.getByRole('button', { name: '← Editar dados' }))

    expect(roteador.state.location.pathname).toBe('/analises/nova')
    expect(campo('Título da reunião').value).toBe('  Renovação Acme  ')
    expect(campo('Empresa').value).toBe('Acme')
    expect(campo('Vínculo com a empresa').value).toBe('cliente')
    expect(campo('Transcrição da reunião').value).toBe(' Estamos insatisfeitos com o suporte. ')
    expect(fetchEspiao).not.toHaveBeenCalled()

    await act(async () => {
      await roteador.navigate(PAGINAS.resultado.caminho)
    })
    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
    expect(document.body.textContent).toContain('Não há nenhuma análise')
  })

  it('Nova análise: formulário limpo, e voltar ao resultado não traz a análise anterior', async () => {
    const roteador = await enviarComSucesso()
    fireEvent.click(screen.getByRole('button', { name: 'Nova análise' }))

    expect(roteador.state.location.pathname).toBe('/analises/nova')
    for (const nome of ['Título da reunião', 'Empresa', 'Vínculo com a empresa', 'Transcrição da reunião']) {
      expect(campo(nome).value).toBe('')
    }
    await act(async () => {
      await roteador.navigate(PAGINAS.resultado.caminho)
    })
    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
  })

  it('editar e reenviar mostra só a resposta nova, com a identificação nova', async () => {
    await enviarComSucesso()
    fireEvent.click(screen.getByRole('button', { name: '← Editar dados' }))
    fetchEspiao.mockResolvedValueOnce(json(respostaB))
    digitar(campo('Título da reunião'), 'Segunda reunião')
    enviar()
    await waitFor(() => expect(screen.getByText('Segunda reunião')).toBeTruthy())

    expect(screen.queryByText('Renovação Acme')).toBeNull()
    expect(screen.getByRole('region', { name: 'Transcrição' }).querySelector('.transcricao-texto')!.textContent).toBe(respostaB.transcricao)
    expect(document.querySelector('[data-churn="nao_aplicavel"]')).not.toBeNull()
  })

  it('durante um novo envio a análise anterior não aparece como se fosse a do pedido novo', async () => {
    const roteador = await enviarComSucesso()
    fireEvent.click(screen.getByRole('button', { name: '← Editar dados' }))
    fetchEspiao.mockReturnValue(pendente().promessa)
    enviar()
    await act(async () => {
      await roteador.navigate(PAGINAS.resultado.caminho)
    })

    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
    expect(document.body.textContent).toContain('Não há nenhuma análise')
  })

  it('voltar ao formulário sem usar "Editar dados" e reenviar: a análise anterior sai da memória enquanto espera', async () => {
    const roteador = await enviarComSucesso()
    await act(async () => {
      await roteador.navigate(PAGINAS.novaAnalise.caminho)
    })
    fetchEspiao.mockReturnValue(pendente().promessa)
    enviar()
    await act(async () => {
      await roteador.navigate(PAGINAS.resultado.caminho)
    })

    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
  })

  it('sem estado (abertura direta ou recarga): aviso simples, nenhuma fixture, caminho de volta', async () => {
    await enviarComSucesso()
    cleanup() // recarregar a página: tudo em memória se perde
    abrir(PAGINAS.resultado.caminho)

    expect(h1()).toBe('Resultado da análise')
    expect(document.title).toBe(PAGINAS.resultado.titulo)
    expect(screen.queryByRole('region', { name: 'Reunião analisada' })).toBeNull()
    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
    expect(document.body.textContent).not.toContain('Empresa Exemplo')
    expect(document.body.textContent).toContain('ele some ao recarregar')
    expect(screen.getByRole('link', { name: 'Ir para Nova análise' }).getAttribute('href')).toBe('/analises/nova')
  })
})

describe('pedido obsoleto', () => {
  it('sair da página cancela o pedido e a resposta tardia não navega nem guarda análise', async () => {
    const espera = pendente()
    fetchEspiao.mockReturnValue(espera.promessa)
    const roteador = abrir()
    preencher()
    enviar()
    const sinal = fetchEspiao.mock.calls[0][1].signal as AbortSignal
    expect(sinal.aborted).toBe(false)

    await act(async () => {
      await roteador.navigate('/')
    })
    expect(sinal.aborted).toBe(true)

    await act(async () => {
      espera.resolver(json(respostaA))
      await espera.promessa
    })
    expect(roteador.state.location.pathname).toBe('/')

    await act(async () => {
      await roteador.navigate(PAGINAS.resultado.caminho)
    })
    expect(screen.queryByRole('region', { name: 'Transcrição' })).toBeNull()
  })

  it('o cancelamento e a falha tardia depois de sair não geram erro nem atualização', async () => {
    const espera = pendente()
    fetchEspiao.mockReturnValue(espera.promessa)
    const erros = vi.spyOn(console, 'error').mockImplementation(() => {})
    const roteador = abrir()
    preencher()
    enviar()
    await act(async () => {
      await roteador.navigate('/')
    })
    await act(async () => {
      espera.rejeitar(new DOMException('abortado', 'AbortError'))
      await espera.promessa.catch(() => {})
    })

    expect(erros).not.toHaveBeenCalled()
    erros.mockRestore()
  })

  it('voltar à página depois de sair começa livre: novo envio funciona e usa o texto guardado', async () => {
    fetchEspiao.mockReturnValueOnce(pendente().promessa).mockResolvedValueOnce(json(respostaA))
    const roteador = abrir()
    preencher()
    enviar()
    await act(async () => {
      await roteador.navigate('/')
    })
    await act(async () => {
      await roteador.navigate(PAGINAS.novaAnalise.caminho)
    })

    expect(campo('Empresa').value).toBe('Acme')
    expect(botaoEnviar().textContent).toBe('Analisar reunião')
    enviar()
    await concluir()
    expect(fetchEspiao).toHaveBeenCalledTimes(2)
  })

  it('em StrictMode o envio continua único e o resultado chega', async () => {
    fetchEspiao.mockResolvedValue(json(respostaA))
    abrir(PAGINAS.novaAnalise.caminho, { estrito: true })
    preencher()
    enviar()
    await concluir()

    expect(fetchEspiao).toHaveBeenCalledTimes(1)
  })
})

describe('anúncios', () => {
  it('o erro é anunciado uma vez, só por role=alert; o status de envio é retirado', async () => {
    fetchEspiao.mockResolvedValueOnce(json({}, 500))
    abrir()
    preencher()
    enviar()
    const alerta = await screen.findByRole('alert')

    expect(screen.getAllByRole('alert')).toHaveLength(1)
    expect(within(alerta).getAllByText(/./)).not.toHaveLength(0)
    expect(screen.getByRole('status').textContent).toBe('')
  })
})
