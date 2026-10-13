import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'

export function NaoEncontrada() {
  return (
    <section className="page-intro not-found" aria-labelledby="page-title">
      <div>
        <p className="eyebrow">ERRO 404</p>
        <h1 id="page-title" tabIndex={-1}>Página não encontrada</h1>
        <p>O endereço que você abriu não existe no ConvIQ. Volte à visão geral para continuar.</p>
        <p className="not-found-action">
          <Link className="action-link" to={PAGINAS.visaoGeral.caminho}>Ir para a visão geral</Link>
        </p>
      </div>
    </section>
  )
}
