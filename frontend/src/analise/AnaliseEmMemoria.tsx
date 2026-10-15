import { useCallback, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { VALORES_INICIAIS } from '../formulario/validacao.ts'
import type { ValoresDoFormulario } from '../formulario/validacao.ts'
import type { AnaliseTextoRequest, AnaliseTextoResponse } from '../types/analise.ts'
import { Contexto } from './useAnaliseEmMemoria.ts'
import type { AnaliseRecebida } from './useAnaliseEmMemoria.ts'

/**
 * Estado da jornada de texto (F06-A), só em memória: nada vai para `localStorage`, `sessionStorage`,
 * IndexedDB nem URL, então recarregar a página o apaga (F06-B trata esse retorno com mais cuidado).
 * O rascunho fica numa referência, e não em estado, para que cada tecla não renderize a árvore toda.
 */
export function AnaliseEmMemoriaProvider({ children }: { children: ReactNode }) {
  const [analise, setAnalise] = useState<AnaliseRecebida | undefined>()
  const rascunho = useRef<ValoresDoFormulario>(VALORES_INICIAIS)

  const receber = useCallback((pedido: AnaliseTextoRequest, resposta: AnaliseTextoResponse) => setAnalise({ pedido, resposta }), [])
  const esquecerAnalise = useCallback(() => setAnalise(undefined), [])
  // Só a referência: não renderiza nada, então a tela de onde o usuário sai não muda antes da navegação.
  const recomecar = useCallback(() => {
    rascunho.current = VALORES_INICIAIS
  }, [])
  const lerRascunho = useCallback(() => rascunho.current, [])
  const guardarRascunho = useCallback((valores: ValoresDoFormulario) => {
    rascunho.current = valores
  }, [])

  const valor = useMemo(
    () => ({ analise, receber, esquecerAnalise, recomecar, lerRascunho, guardarRascunho }),
    [analise, receber, esquecerAnalise, recomecar, lerRascunho, guardarRascunho],
  )
  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>
}
