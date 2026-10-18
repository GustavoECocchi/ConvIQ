import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'
import { useAnaliseEmMemoria } from './useAnaliseEmMemoria.ts'

interface LinkNovaAnaliseProps {
  className: string
  /** Texto do link; padrão: o rótulo de `Nova análise`. Uma só ação, onde quer que apareça. */
  children?: string
}

/** "Nova análise" começa do zero em qualquer página: descarta o texto digitado e abre o formulário vazio. */
export function LinkNovaAnalise({ className, children = PAGINAS.novaAnalise.rotulo }: LinkNovaAnaliseProps) {
  const { recomecar } = useAnaliseEmMemoria()
  return (
    <Link className={className} to={PAGINAS.novaAnalise.caminho} onClick={recomecar}>
      {children}
    </Link>
  )
}
