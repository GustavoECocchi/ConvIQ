import './App.css'

const signals = [
  {
    kind: 'sentiment',
    label: 'Leitura da conversa',
    title: 'Sentimento',
    description: 'Mostra o tom identificado no texto e o trecho que sustenta a leitura.',
  },
  {
    kind: 'risk',
    label: 'Atenção à relação',
    title: 'Risco de cancelamento',
    description: 'Destaca sinais ligados à relação comercial quando há contexto suficiente.',
  },
  {
    kind: 'opportunity',
    label: 'Próximo passo possível',
    title: 'Oportunidades',
    description: 'Reúne intenções comerciais expressas na reunião, com sua evidência.',
  },
] as const

function ArrowIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 12h15m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function App() {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#conteudo">Pular para o conteúdo</a>

      <header className="topbar">
        <div className="layout topbar-inner">
          <a className="brand" href="#visao-geral" aria-label="ConvIQ, visão geral">
            <span className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 40 40" fill="none">
                <path d="M7 10h26v19H18l-7 5v-5H7V10Z" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
                <path d="M14 18h12M14 23h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
              </svg>
            </span>
            <span>Conv<span className="brand-iq">IQ</span></span>
          </a>

          <nav className="topnav" aria-label="Navegação principal">
            <a className="topnav-link is-active" href="#visao-geral" aria-current="page">Visão geral</a>
            <a className="topnav-link" href="#como-ler">Como ler os sinais</a>
          </nav>

          <span className="topbar-caption">Inteligência de reuniões</span>
        </div>
      </header>

      <main className="layout main-content" id="conteudo">
        <section className="page-intro" id="visao-geral" aria-labelledby="page-title">
          <div>
            <p className="eyebrow">SEU ESPAÇO DE ANÁLISE</p>
            <h1 id="page-title">Visão geral</h1>
            <p>Entenda os sinais de uma reunião e confira sempre de onde vieram.</p>
          </div>
          <span className="intro-tag"><span aria-hidden="true" /> Análise por texto</span>
        </section>

        <section className="overview-grid" aria-label="Introdução à análise">
          <article className="panel start-panel" aria-labelledby="start-title">
            <div className="panel-heading">
              <div className="heading-group">
                <span className="panel-icon blue-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M5 5h14v11H9l-4 3V5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 9h6m-6 3h4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>
                </span>
                <div><p className="card-kicker">PONTO DE PARTIDA</p><h2 id="start-title">Análise de reunião</h2></div>
              </div>
              <span className="soft-badge">Transcrição</span>
            </div>

            <div className="start-content">
              <p className="start-lead">Da conversa aos sinais que merecem atenção.</p>
              <p className="card-description">
                O ConvIQ organiza o que foi dito em uma leitura de sentimento,
                risco e oportunidades. Cada sinal pode ser conferido no texto original.
              </p>
            </div>

            <div className="start-footer">
              <ol className="mini-flow" aria-label="Etapas da análise">
                <li><span>01</span> Transcrição</li>
                <li><span>02</span> Sinais</li>
                <li><span>03</span> Evidências</li>
              </ol>
              <a className="action-link" href="#como-ler">Entenda o resultado <ArrowIcon /></a>
            </div>
          </article>

          <article className="panel evidence-panel" aria-labelledby="evidence-title">
            <div className="panel-heading">
              <div className="heading-group">
                <span className="panel-icon dark-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M6 5h12v14H6V5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 9h6m-6 4h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>
                </span>
                <div><p className="card-kicker">COMO CONFERIR</p><h2 id="evidence-title">A evidência acompanha o sinal</h2></div>
              </div>
            </div>
            <div className="example-box">
              <p className="example-label">EXEMPLO ILUSTRATIVO</p>
              <blockquote>“Estamos <mark>insatisfeitos com o suporte</mark>.”</blockquote>
              <div className="example-annotation">
                <span className="signal-tag risk-tag">Risco de cancelamento</span>
                <span>Trecho da transcrição</span>
              </div>
            </div>
            <p className="evidence-note">O rótulo diz o que foi identificado; o trecho mostra por quê.</p>
          </article>
        </section>

        <section className="signals-section" id="como-ler" aria-labelledby="signals-title">
          <div className="section-header">
            <div><p className="eyebrow">LEITURA EM CAMADAS</p><h2 id="signals-title">O que você verá no resultado</h2></div>
            <p>Os cartões separam os tipos de sinal para facilitar a leitura. O texto da reunião continua sendo a referência.</p>
          </div>
          <div className="signal-grid">
            {signals.map((signal) => (
              <article className={`panel signal-card ${signal.kind}`} key={signal.title}>
                <span className="signal-icon" aria-hidden="true" />
                <p className="signal-label">{signal.label}</p>
                <h3>{signal.title}</h3>
                <p>{signal.description}</p>
              </article>
            ))}
          </div>
        </section>

        <aside className="reading-note" aria-label="Princípio de leitura">
          <span className="reading-note-icon" aria-hidden="true">i</span>
          <p><strong>Leia o contexto, depois a classificação.</strong> Um sinal é uma indicação para investigar a conversa, com o trecho de origem sempre acessível.</p>
        </aside>
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

export default App
