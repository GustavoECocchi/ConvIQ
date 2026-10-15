// Teste ponta a ponta da jornada de texto (F06-B): Chromium real, frontend em http://localhost:5173 e a API real do
// próprio checkout em http://localhost:8000. Sem serviço externo. Rode com `npm run e2e` (ver frontend/README.md).
//
// O único trecho simulado é o erro HTTP 500: a API não tem como produzi-lo sob demanda, então `page.route` o responde.
// Todo o resto (200, 422 e a falha de rede) vem da API real ou do navegador.
import { spawn } from 'node:child_process'
import { existsSync, readdirSync } from 'node:fs'
import net from 'node:net'
import { homedir } from 'node:os'
import path from 'node:path'
import { after, before, describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'

const FRONTEND = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const BACKEND = path.resolve(FRONTEND, '..', 'backend')
const ORIGEM = 'http://localhost:5173'
const API = 'http://localhost:8000/api'
const LARGURAS = (process.env.E2E_LARGURAS ?? '320,1440').split(',').map(Number)

const TRANSCRICAO_CLIENTE =
  'Estamos insatisfeitos com o suporte. Se o suporte continuar assim, vamos cancelar o contrato. Queremos conhecer o Fluig.'
const TRANSCRICAO_PROSPECT = 'Queremos conhecer o Fluig. Hoje usamos uma planilha manual.'

/** Chromium: `CHROME_PATH`, o headless shell mais novo do cache do Playwright, ou o padrão do Playwright. */
function localizarChromium() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH
  const cache = path.join(homedir(), '.cache', 'ms-playwright')
  if (!existsSync(cache)) return undefined
  const pastas = readdirSync(cache).filter((nome) => nome.startsWith('chromium_headless_shell-')).sort().reverse()
  for (const pasta of pastas) {
    const executavel = path.join(cache, pasta, 'chrome-headless-shell-linux64', 'chrome-headless-shell')
    if (existsSync(executavel)) return executavel
  }
  return undefined
}

const portaOcupada = (porta) =>
  new Promise((resolver) => {
    const socket = net.connect(porta, 'localhost')
    socket.once('connect', () => (socket.destroy(), resolver(true)))
    socket.once('error', () => resolver(false))
  })

async function esperar(url, rotulo, saida) {
  for (let i = 0; i < 120; i += 1) {
    try {
      if ((await fetch(url)).ok) return
    } catch {
      // ainda subindo
    }
    await new Promise((resolver) => setTimeout(resolver, 250))
  }
  throw new Error(`${rotulo} não respondeu em ${url}.\n${saida()}`)
}

const processos = []
function iniciar(comando, args, opcoes, rotulo) {
  let log = ''
  const filho = spawn(comando, args, { ...opcoes, stdio: ['ignore', 'pipe', 'pipe'] })
  filho.stdout.on('data', (dado) => (log += dado))
  filho.stderr.on('data', (dado) => (log += dado))
  processos.push(filho)
  return { filho, log: () => `[${rotulo}]\n${log}` }
}

let navegador

before(async () => {
  for (const porta of [8000, 5173]) {
    assert.equal(await portaOcupada(porta), false, `A porta ${porta} já está em uso: o teste precisa subir a API e o Vite deste checkout.`)
  }
  const python = process.env.CONVIQ_PYTHON ?? 'python3'
  const api = iniciar(python, ['-m', 'uvicorn', 'app.main:app', '--host', 'localhost', '--port', '8000'], { cwd: BACKEND, env: { ...process.env, PYTHONPATH: BACKEND } }, 'api')
  const vite = iniciar(process.execPath, [path.join('node_modules', 'vite', 'bin', 'vite.js'), '--host', 'localhost', '--port', '5173', '--strictPort'], { cwd: FRONTEND, env: { ...process.env, VITE_API_BASE_URL: '' } }, 'vite')
  await esperar(`${API}/health`, 'A API', api.log)
  await esperar(`${ORIGEM}/`, 'O Vite', vite.log)
  navegador = await chromium.launch({ executablePath: localizarChromium() })
})

after(async () => {
  await navegador?.close()
  for (const filho of processos) filho.kill('SIGTERM')
})

process.on('exit', () => processos.forEach((filho) => filho.kill('SIGTERM')))

// --- utilidades de página ---------------------------------------------------------------------------------------

async function abrir(largura, altura = 900) {
  const contexto = await navegador.newContext({ viewport: { width: largura, height: altura } })
  const page = await contexto.newPage()
  const posts = []
  const erros = []
  page.on('request', (r) => r.method() === 'POST' && r.url().startsWith(`${API}/analises/texto`) && posts.push(r))
  page.on('pageerror', (e) => erros.push(e.message))
  const cdp = await contexto.newCDPSession(page)
  return { contexto, page, cdp, posts, erros }
}

const preencher = async (page, v) => {
  await page.fill('#campo-titulo', v.titulo)
  await page.fill('#campo-empresa', v.empresa)
  await page.selectOption('#campo-vinculo', v.vinculo)
  await page.fill('#campo-transcricao', v.transcricao)
}
const valores = async (page) => {
  await page.waitForSelector('#campo-titulo')
  return page.evaluate(() => ['titulo', 'empresa', 'vinculo', 'transcricao'].map((c) => document.getElementById(`campo-${c}`).value))
}
const enviar = (page) => page.click('button[type=submit]')
/** O título do documento é atualizado por um efeito, depois da renderização: espere-o em vez de lê-lo na hora. */
const esperarTitulo = (page, esperado) => page.waitForFunction((t) => document.title === t, esperado, { timeout: 5000 })
const focoNoH1 = (page) => page.evaluate(() => document.activeElement?.tagName === 'H1' && document.activeElement.closest('main') !== null)
const semRolagemHorizontal = (page) => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
const emPontosDeCodigo = (texto, inicio, fim) => Array.from(texto).slice(inicio, fim).join('')

const PEDIDO = { titulo: '  Renovação Acme  ', empresa: 'Acme', vinculo: 'cliente', transcricao: TRANSCRICAO_CLIENTE }

/** Envia pelo formulário e espera a resposta real da API e a página de resultado. */
async function enviarComSucesso(page, pedido = PEDIDO) {
  await preencher(page, pedido)
  const resposta = page.waitForResponse((r) => r.url().startsWith(`${API}/analises/texto`) && r.request().method() === 'POST')
  await enviar(page)
  const api = await resposta
  assert.equal(api.status(), 200)
  await page.waitForURL('**/analises/resultado')
  await page.getByRole('heading', { level: 1, name: 'Resultado da análise' }).waitFor()
  return api.json()
}

/** Observa se o aviso de "sem análise" chega a entrar no DOM, mesmo por um quadro. */
async function vigiarAviso(page) {
  await page.evaluate(() => {
    window.__aviso = { vezes: 0 }
    let presente = false
    const ver = () => document.body.textContent.includes('Não há nenhuma análise')
    new MutationObserver(() => {
      const agora = ver()
      if (agora && !presente) window.__aviso.vezes += 1
      presente = agora
    }).observe(document.body, { childList: true, subtree: true, characterData: true })
  })
}
const avisos = (page) => page.evaluate(() => window.__aviso.vezes)

const ocultosPorRolagem = (page) => page.evaluate(() => ({ y: window.scrollY, topo: document.activeElement?.getBoundingClientRect().top, base: document.activeElement?.getBoundingClientRect().bottom, altura: window.innerHeight, tag: document.activeElement?.tagName }))

// --- a jornada, em cada largura -----------------------------------------------------------------------------------

for (const largura of LARGURAS) {
  describe(`jornada de texto a ${largura} px`, () => {
    it('visão geral → formulário → envio → resultado → evidência → editar → nova análise', async () => {
      const { contexto, page, cdp, posts, erros } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/`)
        await esperarTitulo(page, 'ConvIQ — Visão geral')
        await page.getByRole('link', { name: 'Nova análise' }).first().click()
        await page.waitForURL('**/analises/nova')
        await esperarTitulo(page, 'ConvIQ — Nova análise')
        assert.ok(await focoNoH1(page), 'o foco vai ao h1 do formulário')

        // Envio sob latência: estado visível, acessível e um só POST mesmo com Enter, clique e Enter.
        await preencher(page, PEDIDO)
        await cdp.send('Network.enable')
        await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 1200, downloadThroughput: -1, uploadThroughput: -1 })
        const resposta = page.waitForResponse((r) => r.url().startsWith(`${API}/analises/texto`) && r.request().method() === 'POST')
        await page.focus('button[type=submit]')
        await page.keyboard.press('Enter')
        await page.click('button[type=submit]', { force: true, noWaitAfter: true })
        await page.focus('#campo-titulo')
        await page.keyboard.press('Enter')
        const durante = await page.evaluate(() => ({
          botao: document.querySelector('button[type=submit]').textContent,
          ariaDisabled: document.querySelector('button[type=submit]').getAttribute('aria-disabled'),
          busy: document.querySelector('form').getAttribute('aria-busy'),
          status: document.querySelector('[role=status]').textContent,
          somenteLeitura: ['titulo', 'empresa', 'transcricao'].every((c) => document.getElementById(`campo-${c}`).readOnly),
          vinculo: document.getElementById('campo-vinculo').getAttribute('aria-disabled'),
        }))
        assert.equal(durante.botao, 'Enviando…')
        assert.equal(durante.ariaDisabled, 'true')
        assert.equal(durante.busy, 'true')
        assert.match(durante.status, /Enviando a transcrição.*somente leitura/)
        assert.ok(durante.somenteLeitura, 'campos de texto somente leitura durante o envio')
        assert.equal(durante.vinculo, 'true')
        const api = await (await resposta).json()
        await page.waitForURL('**/analises/resultado')
        await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 })
        assert.equal(posts.length, 1, 'um só POST')
        assert.deepEqual(JSON.parse(posts[0].postData()), { titulo: 'Renovação Acme', empresa: 'Acme', vinculo: 'cliente', transcricao: TRANSCRICAO_CLIENTE })

        // CORS na origem real: a resposta ecoa exatamente localhost:5173.
        const cabecalhos = await (await posts[0].response()).allHeaders()
        assert.equal(cabecalhos['access-control-allow-origin'], ORIGEM)

        // Resultado: título, foco, identificação → sinais → recomendações → transcrição, e a resposta exata da API.
        await page.getByRole('heading', { level: 1, name: 'Resultado da análise' }).waitFor()
        await esperarTitulo(page, 'ConvIQ — Resultado da análise')
        assert.ok(await focoNoH1(page))
        const titulos = await page.locator('main h2').allTextContents()
        const ordem = ['Reunião analisada', 'Sinais da conversa', 'Recomendações', 'Transcrição'].map((nome) => titulos.findIndex((t) => t.includes(nome)))
        assert.ok(ordem.every((i) => i >= 0), `seções esperadas: ${titulos}`)
        assert.deepEqual([...ordem].sort((a, b) => a - b), ordem, 'ordem identificação → sinais → recomendações → transcrição')
        const tela = await page.evaluate(() => ({
          intro: document.querySelector('.page-intro').textContent,
          eco: document.querySelector('.transcricao-texto').textContent,
          sentimento: document.querySelector('[data-sentimento]')?.getAttribute('data-sentimento'),
          churn: document.querySelector('[data-churn]')?.getAttribute('data-churn'),
          corpo: document.body.textContent,
        }))
        assert.match(tela.intro, /Renovação Acme/)
        assert.equal(tela.eco, api.transcricao)
        assert.equal(tela.sentimento, api.sentimento)
        assert.equal(tela.churn, api.churn.situacao)
        assert.equal(api.churn.situacao, 'sinal_detectado')
        assert.ok(api.oportunidades.length > 0, 'risco e oportunidade coexistem nesta reunião')
        for (const item of [...api.recomendacoes.map((r) => r.texto), ...api.oportunidades.map((o) => o.descricao)]) assert.ok(tela.corpo.includes(item), item)
        assert.ok(!/EXEMPLO ILUSTRATIVO|Empresa Exemplo/.test(tela.corpo), 'nenhuma fixture no lugar da resposta')
        assert.ok(await semRolagemHorizontal(page), 'sem rolagem horizontal no resultado')

        // Ver evidência: seleciona o trecho literal do eco da API e foca a marca; Voltar ao sinal devolve o foco.
        await page.getByRole('button', { name: /^Ver evidência( 1)?: risco de cancelamento$/ }).click()
        await page.getByRole('button', { name: 'Voltar ao sinal' }).waitFor()
        const selecao = await page.evaluate(() => ({ marcas: document.querySelectorAll('mark[data-selecionada]').length, foco: document.activeElement?.tagName, texto: document.activeElement?.textContent }))
        assert.ok(selecao.marcas > 0)
        assert.equal(selecao.foco, 'MARK')
        const evidenciasDoRisco = api.evidencias.filter((e) => api.churn.evidencias.includes(e.id))
        for (const e of evidenciasDoRisco) assert.equal(emPontosDeCodigo(api.transcricao, e.inicio, e.fim), e.trecho, `índices de ${e.id} apontam o trecho literal`)
        assert.ok(evidenciasDoRisco.some((e) => e.trecho.includes(selecao.texto)), 'a marca focada pertence a uma evidência do risco')
        await page.getByRole('button', { name: 'Voltar ao sinal' }).click()
        assert.match(await page.evaluate(() => document.activeElement?.getAttribute('aria-label') ?? ''), /Ver evidência( 1)?: risco de cancelamento/)

        // Editar dados: formulário preenchido, nenhum POST novo, sem o aviso "sem análise" nem com CPU 6× mais lenta.
        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 6 })
        await vigiarAviso(page)
        await page.getByRole('link', { name: '← Editar dados' }).click()
        await page.waitForURL('**/analises/nova')
        await page.waitForTimeout(800)
        assert.deepEqual(await valores(page), [PEDIDO.titulo, 'Acme', 'cliente', TRANSCRICAO_CLIENTE])
        assert.equal(posts.length, 1, 'Editar dados não envia nada')
        assert.equal(await avisos(page), 0, 'o aviso de ausência não aparece ao editar')
        assert.ok(await focoNoH1(page))

        // Reenviar com título novo: só a identificação nova, e uma segunda análise não herda a seleção.
        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 })
        await page.fill('#campo-titulo', 'Segunda reunião')
        await enviar(page)
        await page.waitForURL('**/analises/resultado')
        await page.getByRole('heading', { level: 1, name: 'Resultado da análise' }).waitFor()
        assert.match(await page.textContent('.page-intro'), /Segunda reunião/)
        assert.ok(!(await page.textContent('body')).includes('Renovação Acme'))
        assert.equal(await page.locator('mark[data-selecionada]').count(), 0)
        assert.equal(posts.length, 2)

        // Nova análise do resultado: formulário vazio, sem aviso intermediário.
        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 6 })
        await vigiarAviso(page)
        await page.getByRole('link', { name: 'Nova análise' }).click()
        await page.waitForURL('**/analises/nova')
        await page.waitForTimeout(800)
        assert.deepEqual(await valores(page), ['', '', '', ''])
        assert.equal(await avisos(page), 0, 'o aviso de ausência não aparece em Nova análise')
        assert.ok(await focoNoH1(page))
        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 })

        assert.deepEqual(erros, [])
      } finally {
        await contexto.close()
      }
    })

    it('a "Nova análise" da visão geral limpa o rascunho, como a do resultado', async () => {
      const { contexto, page } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        await preencher(page, PEDIDO)
        await page.getByRole('link', { name: 'Voltar à visão geral' }).click()
        await page.waitForURL(`${ORIGEM}/`)
        await page.getByRole('link', { name: 'Nova análise' }).first().click()
        await page.waitForURL('**/analises/nova')
        assert.deepEqual(await valores(page), ['', '', '', ''])
      } finally {
        await contexto.close()
      }
    })

    it('prospect recebe churn não aplicável e a oportunidade continua sendo mostrada', async () => {
      const { contexto, page } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        const api = await enviarComSucesso(page, { titulo: 'Primeira reunião', empresa: 'Prospect SA', vinculo: 'prospect', transcricao: TRANSCRICAO_PROSPECT })
        assert.equal(api.churn.situacao, 'nao_aplicavel')
        assert.ok(api.oportunidades.length > 0)
        assert.equal(await page.locator('[data-churn]').getAttribute('data-churn'), 'nao_aplicavel')
        assert.ok((await page.textContent('body')).includes(api.oportunidades[0].descricao))
        assert.ok(await semRolagemHorizontal(page))
      } finally {
        await contexto.close()
      }
    })

    it('resultado ausente: abertura direta e recarga mostram o aviso, sem fixture, com caminho para Nova análise', async () => {
      const { contexto, page } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/resultado`)
        const texto = async () => page.textContent('body')
        await esperarTitulo(page, 'ConvIQ — Resultado da análise')
        assert.match(await texto(), /Não há nenhuma análise aberta/)
        assert.ok(!(await texto()).includes('Empresa Exemplo'))
        assert.equal(await page.locator('mark').count(), 0)

        await page.goto(`${ORIGEM}/analises/nova`)
        await enviarComSucesso(page)
        await page.reload()
        assert.match(await texto(), /Não há nenhuma análise aberta/)
        assert.ok(!(await texto()).includes('Renovação Acme'), 'a recarga não traz a análise anterior')
        assert.ok(await semRolagemHorizontal(page))
        await page.getByRole('link', { name: 'Nova análise' }).click()
        await page.waitForURL('**/analises/nova')
        assert.deepEqual(await valores(page), ['', '', '', ''])
      } finally {
        await contexto.close()
      }
    })

    it('422 real da API: mensagem anunciada, campos preservados, um POST, sem resultado', async () => {
      const { contexto, page, posts } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        // U+001F: o trim do JavaScript não o remove, o do Python remove; a API responde 422.
        await preencher(page, { titulo: 'Teste 422', empresa: 'Acme', vinculo: 'cliente', transcricao: '\u001f' })
        await enviar(page)
        const alerta = await page.waitForSelector('[role=alert]')
        assert.match(await alerta.textContent(), /Informe a transcrição para continuar\./)
        assert.deepEqual(await valores(page), ['Teste 422', 'Acme', 'cliente', '\u001f'])
        assert.equal(posts.length, 1)
        assert.ok(page.url().endsWith('/analises/nova'))
        assert.equal(await page.textContent('button[type=submit]'), 'Analisar reunião')
        assert.equal(await page.textContent('[role=status]'), '')
        assert.equal(await page.locator('#campo-empresa').evaluate((el) => el.readOnly), false)

        // Corrigir e reenviar: usa o valor corrente e chega ao resultado.
        await page.fill('#campo-transcricao', TRANSCRICAO_CLIENTE)
        await enviar(page)
        await page.waitForURL('**/analises/resultado')
        assert.equal(posts.length, 2)
        assert.equal(JSON.parse(posts[1].postData()).transcricao, TRANSCRICAO_CLIENTE)
      } finally {
        await contexto.close()
      }
    })

    it('falha de rede real: mensagem clara, campos preservados e nova tentativa com os valores atuais', async () => {
      const { contexto, page, posts } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        await preencher(page, PEDIDO)
        await contexto.setOffline(true)
        await enviar(page)
        const alerta = await page.waitForSelector('[role=alert]')
        assert.match(await alerta.textContent(), /Não foi possível falar com o servidor/)
        assert.deepEqual(await valores(page), [PEDIDO.titulo, 'Acme', 'cliente', TRANSCRICAO_CLIENTE])
        await contexto.setOffline(false)
        await page.fill('#campo-empresa', 'Acme Brasil')
        assert.equal(await page.locator('[role=alert]').count(), 0, 'editar retira o aviso')
        await enviar(page)
        await page.waitForURL('**/analises/resultado')
        assert.equal(posts.length, 2)
        assert.equal(JSON.parse(posts[1].postData()).empresa, 'Acme Brasil')
      } finally {
        await contexto.close()
      }
    })

    it('erro HTTP do servidor (500 simulado): aviso sem detalhes internos, sem duplicar POST nem ressuscitar resultado', async () => {
      const { contexto, page, posts } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        await enviarComSucesso(page)
        await page.getByRole('link', { name: '← Editar dados' }).click()
        await page.waitForURL('**/analises/nova')
        await page.route(`${API}/analises/texto`, (rota) => rota.fulfill({ status: 500, contentType: 'application/json', headers: { 'access-control-allow-origin': ORIGEM }, body: '{"detalhe":"Traceback (most recent call last): segredo interno"}' }))
        await enviar(page)
        const alerta = await page.waitForSelector('[role=alert]')
        const texto = await alerta.textContent()
        assert.match(texto, /O servidor não conseguiu concluir a análise/)
        assert.ok(!/Traceback|segredo/.test(texto), 'nenhum detalhe interno do servidor')
        assert.equal(posts.length, 2, 'um POST por envio')
        assert.deepEqual(await valores(page), [PEDIDO.titulo, 'Acme', 'cliente', TRANSCRICAO_CLIENTE])

        // O resultado anterior não volta; a nova tentativa, já com a API real, funciona.
        await page.goto(`${ORIGEM}/analises/resultado`)
        assert.match(await page.textContent('body'), /Não há nenhuma análise aberta/)
      } finally {
        await contexto.close()
      }
    })

    it('sair da página durante o envio cancela o pedido e a resposta tardia não navega', async () => {
      const { contexto, page, cdp, posts } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/analises/nova`)
        await preencher(page, PEDIDO)
        await cdp.send('Network.enable')
        await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 2000, downloadThroughput: -1, uploadThroughput: -1 })
        const falhou = page.waitForEvent('requestfailed', (r) => r.url().startsWith(`${API}/analises/texto`))
        await enviar(page)
        await page.waitForTimeout(150)
        await page.getByRole('link', { name: 'Voltar à visão geral' }).click()
        assert.match((await falhou).failure()?.errorText ?? '', /ERR_ABORTED/)
        await page.waitForTimeout(2600)
        assert.equal(new URL(page.url()).pathname, '/')
        assert.equal(posts.length, 1)
        await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 })
        await page.getByRole('link', { name: 'Nova análise' }).first().click()
        await page.waitForURL('**/analises/nova')
        assert.equal(await page.textContent('button[type=submit]'), 'Analisar reunião', 'o botão volta livre')
      } finally {
        await contexto.close()
      }
    })

    it('voltar para uma página rolada: o foco acompanha a área visível, não um h1 fora da janela', async () => {
      const { contexto, page } = await abrir(largura, 500) // janela baixa: a página de guia rola também a 1440 px
      try {
        await page.goto(`${ORIGEM}/como-ler`)
        // `behavior: 'instant'`: o CSS pode ter rolagem suave, e a leitura de scrollY logo depois veria 0.
        await page.evaluate(() => window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }))
        const rolagem = await page.evaluate(() => window.scrollY)
        assert.ok(rolagem > 300, `a página precisa ser longa para o teste (scrollY=${rolagem})`)
        await page.evaluate(() => document.querySelector('a[href="/analises/nova"], a[href="/"]:not(.brand)')?.click())
        // Como uma pessoa, espere a página nova assentar (a rolagem suave ao topo termina); voltar no meio dela perde a posição salva.
        await page.waitForFunction(() => window.scrollY === 0 && !window.location.pathname.includes('como-ler'))
        const destino = new URL(page.url()).pathname
        assert.notEqual(destino, '/como-ler')
        // `history.back()` e não `page.goBack()`: o goBack do CDP não restaura a rolagem neste Chromium; o popstate é o mesmo.
        await page.evaluate(() => history.back())
        await page.waitForURL('**/como-ler')
        // A restauração é animada: espere a rolagem parar (e o foco ser escolhido) antes de medir.
        let anterior = -1
        for (let i = 0; i < 40; i += 1) {
          await page.waitForTimeout(150)
          const agora = await page.evaluate(() => window.scrollY)
          if (agora > 0 && agora === anterior) break
          anterior = agora
        }
        await page.waitForTimeout(400)
        const estado = await ocultosPorRolagem(page)
        assert.ok(estado.y > 0, `o navegador restaurou a rolagem (scrollY=${estado.y})`)
        assert.ok(estado.base > 0 && estado.topo < estado.altura, `o foco (${estado.tag}) está na janela: ${JSON.stringify(estado)}`)
        await esperarTitulo(page, 'ConvIQ — Como ler os sinais')
      } finally {
        await contexto.close()
      }
    })

    it('o link de pular, a carga inicial e a navegação comum seguem como antes', async () => {
      const { contexto, page } = await abrir(largura)
      try {
        await page.goto(`${ORIGEM}/como-ler`)
        assert.equal(await page.evaluate(() => document.activeElement?.tagName), 'BODY', 'carga inicial não move o foco')
        await page.keyboard.press('Tab')
        assert.equal(await page.evaluate(() => document.activeElement?.className), 'skip-link')
        await page.keyboard.press('Enter')
        assert.equal(await page.evaluate(() => document.activeElement?.id), 'conteudo')
        assert.equal(new URL(page.url()).pathname, '/como-ler')

        await page.getByRole('link', { name: 'Visão geral' }).first().click()
        await page.waitForURL(`${ORIGEM}/`)
        await esperarTitulo(page, 'ConvIQ — Visão geral')
        assert.ok(await focoNoH1(page))
      } finally {
        await contexto.close()
      }
    })
  })
}
