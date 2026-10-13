import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'

const estadosDeRisco = [
  {
    nome: 'Sinal detectado',
    texto: 'Há trechos que indicam risco de cancelamento, como insatisfação com o suporte ou a intenção de encerrar um contrato. Cada trecho aparece como evidência.',
  },
  {
    nome: 'Sem sinal detectado',
    texto: 'A conversa tratou da relação comercial e nenhum sinal de risco apareceu. Isso não confirma que o risco é baixo: a análise só vê o que está no texto.',
  },
  {
    nome: 'Não aplicável',
    texto: 'Usado quando a reunião é com um prospect: ainda não há contrato a cancelar.',
  },
  {
    nome: 'Informação insuficiente',
    texto: 'O texto não traz conteúdo comercial suficiente para avaliar o risco. Também não é o mesmo que risco baixo.',
  },
] as const

const tiposDeSentimento = [
  ['Positivo', 'predominam trechos de satisfação ou elogio.'],
  ['Negativo', 'predominam trechos de insatisfação ou reclamação.'],
  ['Neutro', 'há sinais positivos e negativos na mesma quantidade.'],
  ['Informação insuficiente', 'o texto não traz sinais de sentimento.'],
] as const

export function ComoLer() {
  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">ENTENDA O RESULTADO</p>
          <h1 id="page-title" tabIndex={-1}>Como ler os sinais</h1>
          <p>O que cada parte da análise quer dizer e como conferir de onde ela veio.</p>
        </div>
        <Link className="intro-tag guide-back" to={PAGINAS.visaoGeral.caminho}>← Voltar à visão geral</Link>
      </section>

      <div className="guide-grid">
        <section className="panel guide-panel sentiment" aria-labelledby="guia-sentimento">
          <p className="signal-label">Leitura da conversa</p>
          <h2 id="guia-sentimento">Sentimento</h2>
          <p>O tom geral do texto, a partir das palavras e expressões encontradas nele.</p>
          <dl className="guide-list">
            {tiposDeSentimento.map(([nome, texto]) => (
              <div key={nome}><dt>{nome}</dt><dd>{texto}</dd></div>
            ))}
          </dl>
        </section>

        <section className="panel guide-panel risk" aria-labelledby="guia-risco">
          <p className="signal-label">Atenção à relação</p>
          <h2 id="guia-risco">Risco de cancelamento</h2>
          <p>Um aviso para investigar a relação comercial, com quatro situações possíveis:</p>
          <dl className="guide-list">
            {estadosDeRisco.map((estado) => (
              <div key={estado.nome}><dt>{estado.nome}</dt><dd>{estado.texto}</dd></div>
            ))}
          </dl>
        </section>

        <section className="panel guide-panel opportunity" aria-labelledby="guia-oportunidades">
          <p className="signal-label">Próximo passo possível</p>
          <h2 id="guia-oportunidades">Oportunidades</h2>
          <p>
            Intenções comerciais expressas na reunião, como querer conhecer, avaliar ou contratar
            uma solução. Cada oportunidade mostra o trecho que a sustenta.
          </p>
          <p>É um indício para dar seguimento, não uma venda confirmada. Risco e oportunidade podem aparecer na mesma reunião.</p>
        </section>

        <section className="panel guide-panel evidence-guide" aria-labelledby="guia-evidencias">
          <p className="signal-label">Como conferir</p>
          <h2 id="guia-evidencias">Evidências</h2>
          <p>
            Uma evidência é um trecho copiado literalmente do texto da reunião. Cada sinal indica
            quais evidências o sustentam, e a leitura começa pelo contexto, depois pela classificação.
          </p>
          <div className="example-box">
            <p className="example-label">EXEMPLO ILUSTRATIVO</p>
            <blockquote>“Estamos <mark>insatisfeitos com o suporte</mark>.”</blockquote>
            <div className="example-annotation">
              <span className="signal-tag risk-tag">Risco de cancelamento</span>
              <span>Trecho da transcrição</span>
            </div>
          </div>
          <p className="evidence-note">
            Uma mesma evidência pode sustentar mais de um sinal, e trechos podem se sobrepor: um
            maior pode conter outro menor. Ambos continuam visíveis.
          </p>
        </section>
      </div>

      <aside className="reading-note" aria-label="Limite da análise">
        <span className="reading-note-icon" aria-hidden="true">i</span>
        <p><strong>A análise segue regras sobre o texto.</strong> Não mede probabilidades nem confiança, e o que não está escrito na transcrição não entra no resultado.</p>
      </aside>

      <div className="guide-footer guide-acoes">
        <Link className="action-link" to={PAGINAS.exemploResultado.caminho}>Ver exemplo de resultado</Link>
        <Link className="intro-tag guide-back" to={PAGINAS.visaoGeral.caminho}>Voltar à visão geral</Link>
      </div>
    </>
  )
}
