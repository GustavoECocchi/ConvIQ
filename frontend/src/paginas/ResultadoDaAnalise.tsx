import { Link } from 'react-router'
import { LinkNovaAnalise } from '../analise/LinkNovaAnalise.tsx'
import { useAnaliseEmMemoria } from '../analise/useAnaliseEmMemoria.ts'
import { PAGINAS } from '../destinos.ts'
import { ResultadoAnalise } from '../resultado/ResultadoAnalise.tsx'

/**
 * Resultado da análise recebida da API, lida da memória da sessão. Sem análise em memória (abertura direta,
 * recarga, formulário reaberto) mostra só o aviso com o caminho para uma nova: nunca uma fixture no lugar da
 * resposta real. "Editar dados" e "Nova análise" são links: a análise só sai da memória quando o formulário
 * abre (`NovaAnalise`), então esta página não troca de conteúdo antes de a navegação acontecer.
 */
export function ResultadoDaAnalise() {
  const { analise } = useAnaliseEmMemoria()

  if (!analise) {
    return (
      <>
        <section className="page-intro" aria-labelledby="page-title">
          <div>
            <p className="eyebrow">RESULTADO DA ANÁLISE</p>
            <h1 id="page-title" tabIndex={-1}>Resultado da análise</h1>
            <p>Não há nenhuma análise aberta nesta página.</p>
          </div>
        </section>
        <div className="panel resultado-ausente">
          <p>O ConvIQ não guarda resultados: a análise fica só na memória da página e some ao recarregá-la, ao abrir este endereço direto ou ao voltar ao formulário. Este endereço nunca mostra um resultado de exemplo no lugar do seu.</p>
          <p>Para ver os sinais de uma reunião, envie a transcrição de novo.</p>
          <p><LinkNovaAnalise className="action-link" /></p>
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
          <Link className="intro-tag guide-back" to={PAGINAS.novaAnalise.caminho}>← Editar dados</Link>
          <LinkNovaAnalise className="intro-tag guide-back" />
        </div>
      </section>

      <ResultadoAnalise entrada={pedido} resposta={resposta} />
    </>
  )
}
