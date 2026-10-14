import { useLayoutEffect, useRef } from 'react'

/** Botão que pediu a evidência: o sinal a que pertence e a sua posição entre os botões do sinal. */
export interface AcaoEvidencia {
  sinal: string
  indice: number
}

/** Chamado ao pedir uma evidência; `origem` é o botão que pediu, para devolver o foco depois. */
export type AoVerEvidencia = (id: string, origem: HTMLElement, acao: AcaoEvidencia) => void

/** Último pedido cuja evidência não pôde ser localizada; `vez` muda a cada pedido, para reanunciar o aviso. */
export interface FalhaEvidencia extends AcaoEvidencia {
  vez: number
}

/**
 * Ação "Ver evidência" de um sinal (F05-B): um botão por ID de evidência citado pelo sinal. O texto
 * visível é o mesmo em todas as telas ("Ver evidência", numerado só quando o sinal cita mais de uma);
 * o nome acessível acrescenta a que sinal o botão pertence, começando pelo texto visível. Sem IDs
 * não mostra nada — ausência de sinal nunca ganha uma evidência.
 *
 * Se `falha` é deste sinal, o aviso aparece junto dos botões, onde a pessoa está, sem mover o foco.
 * É um `role="alert"` remontado a cada pedido (`key` = `vez`), para que leitores de tela o anunciem
 * também quando o mesmo pedido se repete.
 */
export function BotoesEvidencia({ ids, sinal, aoVerEvidencia, falha }: { ids: string[]; sinal: string; aoVerEvidencia: AoVerEvidencia; falha?: FalhaEvidencia }) {
  if (ids.length === 0) return null
  const desteSinal = falha?.sinal === sinal ? falha : undefined
  return (
    <span className="evidencia-acoes">
      {ids.map((id, indice) => {
        const visivel = ids.length > 1 ? `Ver evidência ${indice + 1}` : 'Ver evidência'
        return (
          <button
            key={`${id}-${indice}`}
            type="button"
            className="link-evidencia"
            aria-label={`${visivel}: ${sinal}`}
            onClick={(evento) => aoVerEvidencia(id, evento.currentTarget, { sinal, indice })}
          >
            {visivel}
          </button>
        )
      })}
      {desteSinal ? (
        <AvisoFalha key={desteSinal.vez}>
          {ids.length > 1
            ? `Não foi possível localizar a evidência ${desteSinal.indice + 1} na transcrição.`
            : 'Não foi possível localizar esta evidência na transcrição.'}
        </AvisoFalha>
      ) : null}
    </span>
  )
}

/**
 * Aviso de evidência não localizada. Inteiro na área visível, não rola. Cortado ou fora dela (ex.: botão
 * tocado na borda inferior a 320 px), rola só o necessário para mostrar o grupo do sinal, botões e aviso
 * juntos: `nearest`, sem animação mesmo com `scroll-behavior: smooth` na página, e sem mexer no foco.
 */
function AvisoFalha({ children }: { children: string }) {
  const aviso = useRef<HTMLSpanElement>(null)
  useLayoutEffect(() => {
    const elemento = aviso.current
    if (!elemento) return
    const { top, bottom } = elemento.getBoundingClientRect()
    const altura = document.documentElement.clientHeight || window.innerHeight
    if (top >= 0 && bottom <= altura) return
    ;(elemento.parentElement ?? elemento).scrollIntoView?.({ block: 'nearest', inline: 'nearest', behavior: 'instant' })
  }, [])
  return (
    <span ref={aviso} role="alert" className="evidencia-falha">
      {children}
    </span>
  )
}
