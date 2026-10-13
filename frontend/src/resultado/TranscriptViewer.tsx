import type { AnaliseTextoResponse } from '../types/analise.ts'
import { segmentarTranscricao } from './segmentos.ts'

/**
 * Transcrição com os trechos de evidência destacados (F05-A). Usa só os índices de C01 sobre o
 * `transcricao` devolvido pela API — nunca procura o trecho no texto — e não consulta a API.
 * O texto exibido é exatamente a transcrição; cada destaque guarda os IDs que o cobrem em
 * `data-evidencias`, e um trecho coberto por mais de uma evidência (aninhadas, sobrepostas ou iguais) recebe
 * `data-sobrepostas` (destaque mais forte).
 * Sem ações nem rolagem até um trecho: a ação "Ver evidência" é de F05-B, e os IDs não são
 * mostrados como texto. O sentimento não tem IDs em C01 e não é ligado a nenhum trecho.
 */
export interface TranscriptViewerProps {
  resposta: Pick<AnaliseTextoResponse, 'transcricao' | 'evidencias'>
}

export function TranscriptViewer({ resposta }: TranscriptViewerProps) {
  const segmentos = segmentarTranscricao(resposta.transcricao, resposta.evidencias)

  return (
    <section className="panel transcricao" aria-labelledby="transcricao-titulo">
      <h2 id="transcricao-titulo">Transcrição</h2>
      <p className="detalhe-nota detalhe-nota-topo">
        {resposta.evidencias.length > 0
          ? 'Texto da reunião como foi analisado. Os trechos destacados são as evidências encontradas; um destaque mais forte marca um trecho que pertence a mais de uma evidência.'
          : 'Texto da reunião como foi analisado. Nenhum trecho foi destacado porque a análise não encontrou evidências.'}
      </p>
      <p className="transcricao-texto">
        {segmentos.map((segmento, indice) =>
          segmento.evidencias.length === 0 ? (
            segmento.texto
          ) : (
            <mark
              key={indice}
              data-evidencias={segmento.evidencias.join(' ')}
              data-sobrepostas={segmento.evidencias.length > 1 ? 'sim' : undefined}
            >
              {segmento.texto}
            </mark>
          ),
        )}
      </p>
    </section>
  )
}
