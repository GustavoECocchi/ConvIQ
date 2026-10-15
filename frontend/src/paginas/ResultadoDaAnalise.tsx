import { Link, useNavigate } from 'react-router'
import { useAnaliseEmMemoria } from '../analise/useAnaliseEmMemoria.ts'
import { PAGINAS } from '../destinos.ts'
import { ResultadoAnalise } from '../resultado/ResultadoAnalise.tsx'

/**
 * Resultado da análise recebida da API (F06-A), lida da memória da sessão. Sem análise em memória
 * (abertura direta, recarga, "Editar dados", "Nova análise") mostra só um aviso com o caminho de
 * volta: nunca uma fixture no lugar da resposta real. O acabamento desse caso fica em F06-B.
 */
export function ResultadoDaAnalise() {
  const { analise, esquecerAnalise, recomecar } = useAnaliseEmMemoria()
  const navegar = useNavigate()

  if (!analise) {
    return (
      <>
        <section className="page-intro" aria-labelledby="page-title">
          <div>
            <p className="eyebrow">RESULTADO DA ANÁLISE</p>
            <h1 id="page-title" tabIndex={-1}>Resultado da análise</h1>
            <p>Não há nenhuma análise para mostrar nesta página.</p>
          </div>
        </section>
        <div className="panel resultado-ausente">
          <p>O resultado fica só na memória da página e não é salvo: ele some ao recarregar ou depois de editar os dados. Envie a reunião de novo para analisá-la.</p>
          <p><Link className="action-link" to={PAGINAS.novaAnalise.caminho}>Ir para Nova análise</Link></p>
        </div>
      </>
    )
  }

  const { pedido, resposta } = analise
  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">RESULTADO DA ANÁLISE</p>
          <h1 id="page-title" tabIndex={-1}>Resultado da análise</h1>
          <p>Reunião “{pedido.titulo}”, com {pedido.empresa}. Resposta recebida da API; não foi salva.</p>
        </div>
        <div className="resultado-acoes">
          <button
            type="button"
            className="intro-tag guide-back"
            onClick={() => {
              // O texto digitado fica; a análise sai da memória para não parecer a do texto editado.
              esquecerAnalise()
              void navegar(PAGINAS.novaAnalise.caminho)
            }}
          >
            ← Editar dados
          </button>
          <button
            type="button"
            className="intro-tag guide-back"
            onClick={() => {
              recomecar()
              void navegar(PAGINAS.novaAnalise.caminho)
            }}
          >
            Nova análise
          </button>
        </div>
      </section>

      <ResultadoAnalise entrada={pedido} resposta={resposta} />
    </>
  )
}
