import { useEffect, useRef } from 'react'
import { Link, NavLink, Outlet, useLocation, useMatches, useNavigationType } from 'react-router'
import { ITENS_DO_MENU, PAGINAS } from '../destinos.ts'
import type { DadosDaRota } from '../destinos.ts'
import { AnaliseEmMemoriaProvider } from '../analise/AnaliseEmMemoria.tsx'

/** Tem alguma parte na janela? */
const naJanela = (elemento: Element) => {
  const { top, bottom } = elemento.getBoundingClientRect()
  return bottom > 0 && top < window.innerHeight
}

/**
 * Ao voltar ou avançar o navegador restaura a rolagem da página. Levar o foco a um `h1` fora da janela
 * faria o foco apontar para um lugar e a vista para outro (O2 de F04-B-02): então o foco vai ao primeiro
 * título visível, sem rolar, e o teclado e o leitor de tela continuam de onde a pessoa está olhando.
 */
function focarContextoVisivel() {
  const titulo = document.querySelector<HTMLElement>('main h1')
  if (window.scrollY === 0 || !titulo || naJanela(titulo)) {
    titulo?.focus()
    return
  }
  const alvo = [...document.querySelectorAll<HTMLElement>('main h2, main h3, main h4')].find(naJanela) ?? document.querySelector<HTMLElement>('main')
  if (!alvo) return
  if (!alvo.hasAttribute('tabindex')) alvo.setAttribute('tabindex', '-1')
  alvo.focus({ preventScroll: true })
}

const SILENCIO_DA_ROLAGEM_MS = 120
const ESPERA_MAXIMA_DA_ROLAGEM_MS = 1500

/** Chama `acao` quando a rolagem fica `SILENCIO_DA_ROLAGEM_MS` sem mudar (ou após o limite). Devolve o cancelamento. */
function aoAssentarARolagem(acao: () => void) {
  let silencio = 0
  const limite = window.setTimeout(concluir, ESPERA_MAXIMA_DA_ROLAGEM_MS)
  const reiniciar = () => {
    window.clearTimeout(silencio)
    silencio = window.setTimeout(concluir, SILENCIO_DA_ROLAGEM_MS)
  }
  function cancelar() {
    window.clearTimeout(silencio)
    window.clearTimeout(limite)
    window.removeEventListener('scroll', reiniciar)
  }
  function concluir() {
    cancelar()
    acao()
  }
  window.addEventListener('scroll', reiniciar, { passive: true })
  reiniciar()
  return cancelar
}

/**
 * A cada navegação: atualiza o título do documento e leva o foco ao `h1` da página
 * (`main h1`, com `tabIndex={-1}`), para teclado e leitor de tela começarem pelo
 * conteúdo novo — inclusive em voltar/avançar. Na carga inicial o foco não é
 * movido: o primeiro Tab continua em "Pular para o conteúdo". Mudar só o hash
 * (o link de pular) não conta como navegação.
 */
function useTituloEFoco() {
  const { pathname, hash } = useLocation()
  const dados = useMatches().at(-1)?.handle as DadosDaRota | undefined
  const titulo = dados?.titulo
  const tipo = useNavigationType()
  const caminhoAnterior = useRef<string | null>(null)

  useEffect(() => {
    if (titulo) document.title = titulo
  }, [titulo])

  useEffect(() => {
    // Comparar com o caminho anterior evita mover o foco na carga inicial,
    // na dupla execução do StrictMode e quando só o hash muda.
    const mudouDePagina = caminhoAnterior.current !== null && caminhoAnterior.current !== pathname
    caminhoAnterior.current = pathname
    if (!mudouDePagina) return

    const focarTitulo = () => document.querySelector<HTMLElement>('main h1')?.focus()
    if (!hash && tipo !== 'POP') {
      focarTitulo()
      return
    }
    if (!hash) {
      // Voltar/avançar: o navegador restaura a rolagem depois da renderização, e com `scroll-behavior: smooth`
      // a restauração é animada. Só quando a rolagem para de mudar vale escolher o foco pelo que está visível.
      return aoAssentarARolagem(() => {
        if (window.location.pathname === pathname) focarContextoVisivel()
      })
    }

    // Ao voltar para uma entrada com #conteudo, o navegador pode restaurar o
    // foco da âncora depois do efeito React. Foque o título no quadro seguinte.
    // O URL pode mudar antes de a nova rota ser renderizada; não foque o título antigo.
    const quadro = requestAnimationFrame(() => {
      if (window.location.pathname === pathname) focarTitulo()
    })
    return () => cancelAnimationFrame(quadro)
  }, [pathname, hash, tipo])
}

/** O estado em memória da análise vive aqui, acima das páginas, para sobreviver à navegação entre elas. */
export function Layout() {
  return (
    <AnaliseEmMemoriaProvider>
      <Casca />
    </AnaliseEmMemoriaProvider>
  )
}

function Casca() {
  useTituloEFoco()

  return (
    <div className="app-shell">
      <a className="skip-link" href="#conteudo">Pular para o conteúdo</a>

      <header className="topbar">
        <div className="layout topbar-inner">
          <Link className="brand" to={PAGINAS.visaoGeral.caminho} aria-label="ConvIQ, visão geral">
            <span className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 40 40" fill="none">
                <path d="M7 10h26v19H18l-7 5v-5H7V10Z" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
                <path d="M14 18h12M14 23h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
              </svg>
            </span>
            <span>Conv<span className="brand-iq">IQ</span></span>
          </Link>

          <nav className="topnav" aria-label="Navegação principal">
            {ITENS_DO_MENU.map((item) => (
              <NavLink
                key={item.caminho}
                className={({ isActive }) => `topnav-link${isActive ? ' is-active' : ''}`}
                to={item.caminho}
                end
              >
                {item.rotulo}
              </NavLink>
            ))}
          </nav>

          <span className="topbar-caption">Inteligência de reuniões</span>
        </div>
      </header>

      <main className="layout main-content" id="conteudo" tabIndex={-1}>
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="layout footer-content">
          <span className="footer-brand">ConvIQ</span>
          <span>Inteligência de reuniões com origem verificável.</span>
        </div>
      </footer>
    </div>
  )
}
