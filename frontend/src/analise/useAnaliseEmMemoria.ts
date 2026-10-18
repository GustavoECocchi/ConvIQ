import { createContext, useContext } from 'react'
import type { ValoresDoFormulario } from '../formulario/validacao.ts'
import type { AnaliseTextoRequest, AnaliseTextoResponse } from '../types/analise.ts'

/** Pedido enviado e a resposta exata da API; só existem em memória. */
export interface AnaliseRecebida {
  pedido: AnaliseTextoRequest
  resposta: AnaliseTextoResponse
}

export interface AnaliseEmMemoria {
  /** Última análise recebida, ou `undefined` (nunca enviada, reinício da página ou formulário reaberto). */
  analise: AnaliseRecebida | undefined
  /** Guarda a análise recebida. */
  receber: (pedido: AnaliseTextoRequest, resposta: AnaliseTextoResponse) => void
  /**
   * Esquece a análise recebida e preserva o que foi digitado. Quem a chama é o formulário, ao abrir: assim
   * a página de resultado continua na tela até ser trocada, sem mostrar por um quadro o aviso de ausência.
   */
  esquecerAnalise: () => void
  /** Descarta só o texto digitado (início "do zero"); a análise sai da memória quando o formulário abre. */
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
