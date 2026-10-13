import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AnaliseTextoRequest } from '../types/analise.ts'
import { BASE_API_PADRAO, ErroDaApi, analisarTexto, criarClienteApi, juntarUrl, mensagemDaFalha, resolverBaseApi } from './api.ts'
import type { FalhaApi, FetchLike } from './api.ts'
import { exemplos } from './mocks/exemplos.ts'

const exemplo = exemplos[0]
const pedido: AnaliseTextoRequest = exemplo.entrada

const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { 'Content-Type': 'application/json' } })

const erroDeAborto = () => new DOMException('The operation was aborted.', 'AbortError')

/** Cliente com `fetch` simulado; devolve também o simulador para inspecionar as chamadas. */
function cliente(resposta: () => Promise<Response> | Response, baseUrl = 'http://api.teste/api') {
  const fetchImpl = vi.fn<FetchLike>(async () => resposta())
  return { fetchImpl, ...criarClienteApi({ baseUrl, fetchImpl }) }
}

async function falhaDe(promessa: Promise<unknown>): Promise<FalhaApi> {
  try {
    await promessa
  } catch (erro) {
    expect(erro).toBeInstanceOf(ErroDaApi)
    return (erro as ErroDaApi).falha
  }
  throw new Error('esperava uma rejeição com ErroDaApi')
}

afterEach(() => {
  vi.unstubAllEnvs()
  vi.unstubAllGlobals()
})

describe('requisição', () => {
  it('envia POST com cabeçalhos e corpo JSON do pedido, na URL da base configurada', async () => {
    const { fetchImpl, analisarTexto: enviar } = cliente(() => json(exemplo.resposta))

    await enviar(pedido)

    expect(fetchImpl).toHaveBeenCalledTimes(1)
    const [url, init] = fetchImpl.mock.calls[0]
    expect(url).toBe('http://api.teste/api/analises/texto')
    expect(init.method).toBe('POST')
    expect(init.headers).toMatchObject({ 'Content-Type': 'application/json', Accept: 'application/json' })
    expect(JSON.parse(init.body as string)).toEqual(pedido)
  })

  it('repassa o AbortSignal recebido ao fetch', async () => {
    const controle = new AbortController()
    const { fetchImpl, analisarTexto: enviar } = cliente(() => json(exemplo.resposta))

    await enviar(pedido, { signal: controle.signal })

    expect(fetchImpl.mock.calls[0][1].signal).toBe(controle.signal)
  })

  it.each([
    ['http://api.teste/api', 'http://api.teste/api/analises/texto'],
    ['http://api.teste/api/', 'http://api.teste/api/analises/texto'],
    ['http://api.teste/api///', 'http://api.teste/api/analises/texto'],
    ['/api', '/api/analises/texto'],
    ['http://localhost:8000', 'http://localhost:8000/analises/texto'],
  ])('junta a base %s com o caminho sem duplicar barra nem /api', async (base, esperada) => {
    const { fetchImpl, analisarTexto: enviar } = cliente(() => json(exemplo.resposta), base)

    await enviar(pedido)

    expect(fetchImpl.mock.calls[0][0]).toBe(esperada)
    expect(esperada.match(/\/api\//g)?.length ?? 0).toBeLessThanOrEqual(1)
  })

  it('juntarUrl aceita caminho com ou sem barra inicial', () => {
    expect(juntarUrl('http://x/api', '/analises/texto')).toBe('http://x/api/analises/texto')
    expect(juntarUrl('http://x/api/', 'analises/texto')).toBe('http://x/api/analises/texto')
  })
})

describe('configuração da base', () => {
  it('usa o valor informado, depois VITE_API_BASE_URL, depois o padrão local', () => {
    vi.stubEnv('VITE_API_BASE_URL', 'http://ambiente.teste/api')
    expect(resolverBaseApi('http://explicito.teste/api')).toBe('http://explicito.teste/api')
    expect(resolverBaseApi()).toBe('http://ambiente.teste/api')
    vi.stubEnv('VITE_API_BASE_URL', '')
    expect(resolverBaseApi()).toBe(BASE_API_PADRAO)
    expect(resolverBaseApi('   ')).toBe(BASE_API_PADRAO)
    expect(BASE_API_PADRAO).toBe('http://localhost:8000/api')
  })

  it('o cliente padrão lê VITE_API_BASE_URL e o fetch global a cada chamada', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'http://ambiente.teste/api/')
    const fetchGlobal = vi.fn<FetchLike>(async () => json(exemplo.resposta))
    vi.stubGlobal('fetch', fetchGlobal)

    await analisarTexto(pedido)

    expect(fetchGlobal.mock.calls[0][0]).toBe('http://ambiente.teste/api/analises/texto')
  })
})

describe('resposta 200', () => {
  it('devolve o corpo tipado e intacto, sem recalcular nem reordenar', async () => {
    const corpo = JSON.parse(JSON.stringify(exemplo.resposta))
    const { analisarTexto: enviar } = cliente(() => json(corpo))

    const resposta = await enviar(pedido)

    expect(resposta).toEqual(exemplo.resposta)
    expect(resposta.versao_analise).toBe(exemplo.resposta.versao_analise)
    expect(resposta.evidencias.map((e) => e.id)).toEqual(['e1', 'e2', 'e3'])
  })

  it.each(exemplos.map((e) => [e.chave, e] as const))('aceita o exemplo %s', async (_chave, e) => {
    const { analisarTexto: enviar } = cliente(() => json(e.resposta))

    expect(await enviar(e.entrada)).toEqual(e.resposta)
  })

  it.each([
    ['texto que não é JSON', () => new Response('<html>oops</html>', { status: 200 })],
    ['corpo vazio', () => new Response('', { status: 200 })],
    ['JSON que não é objeto', () => json([1, 2, 3])],
    ['sem campo obrigatório', () => json({ ...exemplo.resposta, churn: undefined })],
    ['enum fora de C01', () => json({ ...exemplo.resposta, sentimento: 'misto' })],
    ['evidência sem índices', () => json({ ...exemplo.resposta, evidencias: [{ id: 'e1', trecho: 'x' }] })],
    ['lista que não é lista', () => json({ ...exemplo.resposta, produtos: 'Fluig' })],
    ['versão ausente', () => json({ ...exemplo.resposta, versao_analise: undefined })],
  ])('rejeita 200 inválido: %s', async (_nome, resposta) => {
    const { analisarTexto: enviar } = cliente(resposta)

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'resposta_invalida', status: 200 })
  })
})

describe('falhas', () => {
  it('422 com o envelope de C01 vira validação, com código e mensagem da API', async () => {
    const envelope = { erro: { codigo: 'TITULO_OBRIGATORIO', mensagem: 'Informe o título para continuar.' } }
    const { analisarTexto: enviar } = cliente(() => json(envelope, 422))

    const falha = await falhaDe(enviar(pedido))

    expect(falha).toEqual({ tipo: 'validacao', status: 422, erro: envelope.erro })
    expect(mensagemDaFalha(falha)).toBe('Informe o título para continuar.')
  })

  it.each([
    ['sem envelope', () => json({ detail: [{ loc: ['body', 'titulo'], msg: 'x' }] }, 422)],
    ['texto puro', () => new Response('Unprocessable', { status: 422 })],
    ['código vazio', () => json({ erro: { codigo: '', mensagem: 'x' } }, 422)],
    ['mensagem ausente', () => json({ erro: { codigo: 'DADOS_INVALIDOS' } }, 422)],
    ['erro que não é objeto', () => json({ erro: 'campo inválido' }, 422)],
  ])('422 malformado (%s) não vira erro de campo inventado', async (_nome, resposta) => {
    const { analisarTexto: enviar } = cliente(resposta)

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'resposta_invalida', status: 422 })
  })

  it.each([500, 502, 503, 404, 401, 400, 429])('HTTP %i vira erro http com o status', async (status) => {
    const { analisarTexto: enviar } = cliente(() => json({ erro: { codigo: 'X', mensagem: 'y' } }, status))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'http', status })
  })

  it('não expõe o corpo nem detalhes internos do servidor na mensagem', async () => {
    const segredo = 'Traceback (most recent call last): File "/srv/conviq/app.py", line 42'
    const { analisarTexto: enviar } = cliente(() => new Response(segredo, { status: 500 }))

    const falha = await falhaDe(enviar(pedido))
    const mensagem = mensagemDaFalha(falha)

    expect(mensagem).toContain('500')
    expect(mensagem).not.toContain('Traceback')
    expect(JSON.stringify(falha)).not.toContain('/srv/conviq')
  })

  it('rejeição do fetch (sem conexão, CORS) vira falha de rede', async () => {
    const { analisarTexto: enviar } = cliente(() => Promise.reject(new TypeError('Failed to fetch')))

    const falha = await falhaDe(enviar(pedido))

    expect(falha).toEqual({ tipo: 'rede' })
    expect(mensagemDaFalha(falha)).not.toContain('Failed to fetch')
  })

  it('AbortError do fetch vira cancelamento, não falha de rede', async () => {
    const { analisarTexto: enviar } = cliente(() => Promise.reject(erroDeAborto()))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'cancelado' })
  })

  it('sinal já acionado vira cancelamento mesmo se o fetch rejeitar com outro erro', async () => {
    const controle = new AbortController()
    controle.abort()
    const { analisarTexto: enviar } = cliente(() => Promise.reject(new TypeError('Failed to fetch')))

    expect(await falhaDe(enviar(pedido, { signal: controle.signal }))).toEqual({ tipo: 'cancelado' })
  })

  it('cancelar durante o envio, com o fetch honrando o sinal, vira cancelamento', async () => {
    const controle = new AbortController()
    const fetchImpl: FetchLike = (_url, init) =>
      new Promise((_resolve, rejeitar) => {
        init.signal?.addEventListener('abort', () => rejeitar(erroDeAborto()))
      })
    const { analisarTexto: enviar } = criarClienteApi({ baseUrl: 'http://api.teste/api', fetchImpl })

    const promessa = enviar(pedido, { signal: controle.signal })
    controle.abort()

    expect(await falhaDe(promessa)).toEqual({ tipo: 'cancelado' })
  })

  it('cancelar durante a leitura do corpo também é cancelamento', async () => {
    const controle = new AbortController()
    const resposta = new Response('{}', { status: 200 })
    vi.spyOn(resposta, 'json').mockImplementation(async () => {
      controle.abort()
      throw erroDeAborto()
    })
    const { analisarTexto: enviar } = cliente(() => resposta)

    expect(await falhaDe(enviar(pedido, { signal: controle.signal }))).toEqual({ tipo: 'cancelado' })
  })

  it('cada tipo de falha tem mensagem própria e útil', () => {
    const mensagens = [
      mensagemDaFalha({ tipo: 'http', status: 500 }),
      mensagemDaFalha({ tipo: 'rede' }),
      mensagemDaFalha({ tipo: 'cancelado' }),
      mensagemDaFalha({ tipo: 'resposta_invalida', status: 200 }),
    ]

    expect(new Set(mensagens).size).toBe(mensagens.length)
    for (const mensagem of mensagens) expect(mensagem.length).toBeGreaterThan(10)
  })
})

describe('independência entre chamadas', () => {
  it('uma falha não altera uma chamada seguinte válida', async () => {
    const respostas: Array<() => Promise<Response> | Response> = [
      () => Promise.reject(new TypeError('Failed to fetch')),
      () => json({ erro: { codigo: 'DADOS_INVALIDOS', mensagem: 'Campo inválido: titulo.' } }, 422),
      () => new Response('erro', { status: 500 }),
      () => Promise.reject(erroDeAborto()),
      () => json(exemplo.resposta),
    ]
    let chamada = 0
    const fetchImpl = vi.fn<FetchLike>(async () => respostas[chamada++]())
    const { analisarTexto: enviar } = criarClienteApi({ baseUrl: 'http://api.teste/api', fetchImpl })

    const falhas = []
    for (let i = 0; i < 4; i += 1) falhas.push((await falhaDe(enviar(pedido))).tipo)
    const resposta = await enviar(pedido)

    expect(falhas).toEqual(['rede', 'validacao', 'http', 'cancelado'])
    expect(resposta).toEqual(exemplo.resposta)
    expect(fetchImpl).toHaveBeenCalledTimes(5)
    for (const [url, init] of fetchImpl.mock.calls) {
      expect(url).toBe('http://api.teste/api/analises/texto')
      expect(JSON.parse(init.body as string)).toEqual(pedido)
    }
  })

  it('o pedido não é alterado pelo cliente', async () => {
    const copia = JSON.parse(JSON.stringify(pedido))
    const { analisarTexto: enviar } = cliente(() => json(exemplo.resposta))

    await enviar(pedido)

    expect(pedido).toEqual(copia)
  })
})

// Revisão F02-B (Opus) ---------------------------------------------------------

/** Resposta válida de C01 alterada por `mudar`, sem tocar no exemplo original. */
function variante(mudar: (r: ReturnType<typeof copiaDoExemplo>) => void) {
  const copia = copiaDoExemplo()
  mudar(copia)
  return copia
}

function copiaDoExemplo() {
  return JSON.parse(JSON.stringify(exemplo.resposta)) as {
    transcricao: string
    metodo: string
    versao_analise: string
    churn: { situacao: string; evidencias: string[] }
    oportunidades: Array<{ descricao: string; evidencias: string[] }>
    recomendacoes: Array<{ texto: string; evidencias: string[] }>
    evidencias: Array<{ id: unknown; trecho: unknown; inicio: unknown; fim: unknown }>
  }
}

describe('F02-B-R01 — resposta 200 fora do schema de C01', () => {
  it.each([
    ['inicio negativo', variante((r) => { r.evidencias[0].inicio = -1 })],
    ['fim zero', variante((r) => { r.evidencias[0].inicio = 0; r.evidencias[0].fim = 0 })],
    ['fim igual a inicio', variante((r) => { r.evidencias[0].inicio = 5; r.evidencias[0].fim = 5 })],
    ['fim menor que inicio', variante((r) => { r.evidencias[0].inicio = 9; r.evidencias[0].fim = 4 })],
    ['índice fracionário', variante((r) => { r.evidencias[0].fim = 21.5 })],
    ['id de evidência vazio', variante((r) => { r.evidencias[0].id = '' })],
    ['id de evidência que não é texto', variante((r) => { r.evidencias[0].id = 1 })],
    ['id de evidência duplicado', variante((r) => { r.evidencias[1].id = 'e1' })],
    ['trecho vazio', variante((r) => { r.evidencias[0].trecho = '' })],
    ['churn cita evidência inexistente', variante((r) => { r.churn.evidencias = ['e99'] })],
    ['oportunidade cita evidência inexistente', variante((r) => { r.oportunidades[0].evidencias = ['e99'] })],
    ['recomendação cita evidência inexistente', variante((r) => { r.recomendacoes[0].evidencias = ['e2', 'e99'] })],
    ['referência vazia', variante((r) => { r.churn.evidencias = [''] })],
    ['transcrição vazia', variante((r) => { r.transcricao = '' })],
    ['método vazio', variante((r) => { r.metodo = '' })],
    ['versão vazia', variante((r) => { r.versao_analise = '' })],
    ['descrição de oportunidade vazia', variante((r) => { r.oportunidades[0].descricao = '' })],
    ['texto de recomendação vazio', variante((r) => { r.recomendacoes[0].texto = '' })],
  ])('rejeita: %s', async (_nome, corpo) => {
    const { analisarTexto: enviar } = cliente(() => json(corpo))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'resposta_invalida', status: 200 })
  })

  it.each([
    ['intervalos aninhados (8–21 e 8–35)', copiaDoExemplo()],
    ['mesmo ID citado por churn e recomendação (B19)', variante((r) => { r.recomendacoes[0].evidencias = ['e2'] })],
    ['mesmo ID citado por churn e oportunidade', variante((r) => { r.oportunidades[0].evidencias = ['e2'] })],
    ['ID repetido na mesma lista (o schema não proíbe)', variante((r) => { r.churn.evidencias = ['e2', 'e2'] })],
    ['fim além do texto (o schema não confere)', variante((r) => { r.evidencias[2].fim = 999 })],
    ['trecho que não é o recorte (o schema não confere)', variante((r) => { r.evidencias[0].trecho = 'outro texto' })],
    ['sem evidências nem referências', variante((r) => {
      r.evidencias = []; r.churn = { situacao: 'informacao_insuficiente', evidencias: [] }; r.oportunidades = []; r.recomendacoes = []
    })],
  ])('aceita e devolve intacto: %s', async (_nome, corpo) => {
    const { analisarTexto: enviar } = cliente(() => json(corpo))

    expect(await enviar(pedido)).toEqual(corpo)
  })
})

describe('F02-B-R02 — falha durante a leitura do corpo', () => {
  const corpoQueFalha = (erro: unknown, status = 200) =>
    new Response(new ReadableStream({ start(controle) { controle.error(erro) } }), { status })

  it('conexão perdida no corpo de um 200 é falha de rede, não formato inesperado', async () => {
    const { analisarTexto: enviar } = cliente(() => corpoQueFalha(new TypeError('network error')))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'rede' })
  })

  it('conexão perdida no corpo de um 422 também é falha de rede', async () => {
    const { analisarTexto: enviar } = cliente(() => corpoQueFalha(new TypeError('terminated'), 422))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'rede' })
  })

  it('AbortError no stream do corpo continua cancelamento', async () => {
    const { analisarTexto: enviar } = cliente(() => corpoQueFalha(erroDeAborto()))

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'cancelado' })
  })

  it.each([
    ['JSON truncado', () => new Response('{"transcricao": "Estamos', { status: 200 })],
    ['corpo vazio', () => new Response('', { status: 200 })],
  ])('corpo completo mas inválido (%s) continua resposta inválida', async (_nome, resposta) => {
    const { analisarTexto: enviar } = cliente(resposta)

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'resposta_invalida', status: 200 })
  })

  it('uma leitura interrompida não afeta a chamada seguinte', async () => {
    const respostas = [() => corpoQueFalha(new TypeError('network error')), () => json(exemplo.resposta)]
    let chamada = 0
    const { analisarTexto: enviar } = criarClienteApi({
      baseUrl: 'http://api.teste/api',
      fetchImpl: async () => respostas[chamada++](),
    })

    expect(await falhaDe(enviar(pedido))).toEqual({ tipo: 'rede' })
    expect(await enviar(pedido)).toEqual(exemplo.resposta)
  })
})
