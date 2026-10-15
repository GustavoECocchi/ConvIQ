import { useEffect, useRef } from 'react'
import { Link, NavLink, Outlet, useLocation, useMatches } from 'react-router'
import { ITENS_DO_MENU, PAGINAS } from '../destinos.ts'
import type { DadosDaRota } from '../destinos.ts'
import { AnaliseEmMemoriaProvider } from '../analise/AnaliseEmMemoria.tsx'

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
    if (!hash) {
      focarTitulo()
      return
    }

    // Ao voltar para uma entrada com #conteudo, o navegador pode restaurar o
    // foco da âncora depois do efeito React. Foque o título no quadro seguinte.
    // O URL pode mudar antes de a nova rota ser renderizada; não foque o título antigo.
    const quadro = requestAnimationFrame(() => {
      if (window.location.pathname === pathname) focarTitulo()
    })
    return () => cancelAnimationFrame(quadro)
  }, [pathname, hash])
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
