import { useEffect, useRef } from 'react'
import type { AnaliseTextoResponse } from '../types/analise.ts'
import { idsNaoLocalizados, segmentarTranscricao } from './segmentos.ts'

/**
 * Transcrição com os trechos de evidência destacados (F05-A) e seleção de uma evidência (F05-B).
 * Usa só os índices de C01 sobre o `transcricao` devolvido pela API — nunca procura o trecho no
 * texto — e não consulta a API. O texto exibido é exatamente a transcrição; cada destaque guarda os
 * IDs que o cobrem em `data-evidencias`, e um trecho coberto por mais de uma evidência (aninhadas,
 * sobrepostas ou iguais) recebe `data-sobrepostas` (destaque mais forte). Os IDs não são mostrados
 * como texto. O sentimento não tem IDs em C01 e não é ligado a nenhum trecho.
 *
 * Seleção: quando `selecionada` muda (um novo objeto a cada pedido, mesmo para o mesmo ID), todos
 * os destaques daquele ID ganham `data-selecionada`, o primeiro recebe o foco e é levado à vista, e
 * uma região de status anuncia o trecho. Se a evidência não puder ser localizada, a seleção é ignorada:
 * nada é destacado nem anunciado aqui, pois o aviso cabe a quem pediu, junto da ação (`ResultadoAnalise`).
 * `aoVoltar` devolve o usuário ao sinal de onde ele veio.
 */
export interface TranscriptViewerProps {
  resposta: Pick<AnaliseTextoResponse, 'transcricao' | 'evidencias'>
  selecionada?: { id: string }
  aoVoltar?: () => void
}

const reduzMovimento = () => typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function TranscriptViewer({ resposta, selecionada, aoVoltar }: TranscriptViewerProps) {
  const { transcricao, evidencias } = resposta
  const segmentos = segmentarTranscricao(transcricao, evidencias)
  const naoLocalizadas = idsNaoLocalizados(transcricao, evidencias)
  const texto = useRef<HTMLParagraphElement>(null)

  const idSelecionado = selecionada?.id
  const evidenciaSelecionada = idSelecionado === undefined ? undefined : evidencias.find((e) => e.id === idSelecionado)
  const localizada = evidenciaSelecionada !== undefined && !naoLocalizadas.includes(evidenciaSelecionada.id)

  useEffect(() => {
    if (!selecionada || !localizada) return
    const primeiro = [...(texto.current?.querySelectorAll('mark') ?? [])].find((marca) =>
      marca.dataset.evidencias?.split(' ').includes(selecionada.id),
    )
    if (!primeiro) return
    primeiro.focus({ preventScroll: true })
    primeiro.scrollIntoView?.({ block: 'center', behavior: reduzMovimento() ? 'auto' : 'smooth' })
  }, [selecionada, localizada])

  const status = localizada ? `Evidência selecionada: “${evidenciaSelecionada.trecho}”.` : ''

  return (
    <section className="panel transcricao" aria-labelledby="transcricao-titulo">
      <h2 id="transcricao-titulo">Transcrição</h2>
      <p className="detalhe-nota detalhe-nota-topo">
        {evidencias.length > 0
          ? 'Texto da reunião como foi analisado. Os trechos destacados são as evidências encontradas; um destaque mais forte, com barra grossa embaixo, marca um trecho que pertence a mais de uma evidência.'
          : 'Texto da reunião como foi analisado. Nenhum trecho foi destacado porque a análise não encontrou evidências.'}
      </p>
      <div className="transcricao-status">
        <p role="status">{status}</p>
        {localizada && aoVoltar ? (
          <button type="button" className="link-evidencia" onClick={aoVoltar}>Voltar ao sinal</button>
        ) : null}
      </div>
      <p className="transcricao-texto" ref={texto}>
        {segmentos.map((segmento, indice) => {
          if (segmento.evidencias.length === 0) return segmento.texto
          const sobrepostas = segmento.evidencias.length > 1
          return (
            <mark
              key={indice}
              tabIndex={-1}
              aria-roledescription={sobrepostas ? 'evidências sobrepostas' : 'evidência'}
              data-evidencias={segmento.evidencias.join(' ')}
              data-sobrepostas={sobrepostas ? 'sim' : undefined}
              data-selecionada={idSelecionado !== undefined && segmento.evidencias.includes(idSelecionado) ? 'sim' : undefined}
            >
              {segmento.texto}
            </mark>
          )
        })}
      </p>
    </section>
  )
}
