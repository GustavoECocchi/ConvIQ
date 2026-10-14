import { useRef, useState } from 'react'
import type { AnaliseTextoRequest, AnaliseTextoResponse } from '../types/analise.ts'
import type { AoVerEvidencia, FalhaEvidencia } from './BotoesEvidencia.tsx'
import { DetalheResultado } from './DetalheResultado.tsx'
import { ResumoResultado } from './ResumoResultado.tsx'
import { idsNaoLocalizados } from './segmentos.ts'
import { TranscriptViewer } from './TranscriptViewer.tsx'

/**
 * Resultado completo (F05-B): resumo, detalhe e transcrição, com a ação "Ver evidência" ligando cada
 * sinal ao seu trecho. Guarda só a evidência selecionada e o botão de onde o usuário veio, para que
 * "Voltar ao sinal" devolva o foco e a rolagem àquele mesmo botão. Não classifica nem consulta a API:
 * tudo vem da resposta recebida.
 *
 * Se a evidência pedida não pode ser localizada, nada fica selecionado, o foco fica onde está e o aviso
 * aparece junto do botão que a pediu (`falha`), não na transcrição, fora da vista; a página só rola o
 * mínimo se o aviso nascer cortado (ver `BotoesEvidencia`).
 */
export interface ResultadoAnaliseProps {
  entrada: Pick<AnaliseTextoRequest, 'titulo' | 'empresa' | 'vinculo'>
  resposta: AnaliseTextoResponse
}

const reduzMovimento = () => typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function ResultadoAnalise({ entrada, resposta }: ResultadoAnaliseProps) {
  const [selecionada, setSelecionada] = useState<{ id: string } | undefined>()
  const [falha, setFalha] = useState<FalhaEvidencia | undefined>()
  const origem = useRef<HTMLElement | null>(null)

  const verEvidencia: AoVerEvidencia = (id, botao, acao) => {
    const { transcricao, evidencias } = resposta
    const localizavel = evidencias.some((e) => e.id === id) && !idsNaoLocalizados(transcricao, evidencias).includes(id)
    if (!localizavel) {
      setSelecionada(undefined)
      setFalha((anterior) => ({ ...acao, vez: (anterior?.vez ?? 0) + 1 }))
      return
    }
    origem.current = botao
    setFalha(undefined)
    setSelecionada({ id })
  }

  const voltar = () => {
    const botao = origem.current
    if (!botao) return
    botao.focus({ preventScroll: true })
    botao.scrollIntoView?.({ block: 'center', behavior: reduzMovimento() ? 'auto' : 'smooth' })
  }

  return (
    <>
      <ResumoResultado entrada={entrada} resposta={resposta} aoVerEvidencia={verEvidencia} falhaEvidencia={falha} />
      <DetalheResultado resposta={resposta} aoVerEvidencia={verEvidencia} falhaEvidencia={falha} />
      <TranscriptViewer resposta={resposta} selecionada={selecionada} aoVoltar={voltar} />
    </>
  )
}
