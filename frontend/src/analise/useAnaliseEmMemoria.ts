import { createContext, useContext } from 'react'
import type { ValoresDoFormulario } from '../formulario/validacao.ts'
import type { AnaliseTextoRequest, AnaliseTextoResponse } from '../types/analise.ts'

/** Pedido enviado e a resposta exata da API. `id` muda a cada análise recebida; só existe em memória. */
export interface AnaliseRecebida {
  id: number
  pedido: AnaliseTextoRequest
  resposta: AnaliseTextoResponse
}

export interface AnaliseEmMemoria {
  /** Última análise recebida, ou `undefined` (nunca enviada, reinício da página, "Editar dados" ou "Nova análise"). */
  analise: AnaliseRecebida | undefined
  /** Guarda a resposta recebida; devolve o `id` dado a ela. */
  receber: (pedido: AnaliseTextoRequest, resposta: AnaliseTextoResponse) => number
  /** Esquece a análise recebida, mas preserva o que foi digitado (editar dados, novo envio em andamento). */
  esquecerAnalise: () => void
  /** Esquece análise e texto digitado (nova análise). */
  recomecar: () => void
  /** Valores digitados no formulário, para voltar a eles depois de um erro ou de "Editar dados". */
  lerRascunho: () => ValoresDoFormulario
  guardarRascunho: (valores: ValoresDoFormulario) => void
}

export const Contexto = createContext<AnaliseEmMemoria | undefined>(undefined)

export function useAnaliseEmMemoria(): AnaliseEmMemoria {
  const valor = useContext(Contexto)
  if (!valor) throw new Error('useAnaliseEmMemoria fora de AnaliseEmMemoriaProvider')
  return valor
}
