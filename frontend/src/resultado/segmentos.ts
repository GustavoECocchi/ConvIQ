import type { Evidencia } from '../types/analise.ts'

/** Pedaço contíguo da transcrição e os IDs das evidências que o cobrem (vazio = texto sem destaque). */
export interface Segmento {
  texto: string
  evidencias: string[]
}

/**
 * Divide `transcricao` em segmentos pelos intervalos de C01 (`inicio`/`fim` em pontos de código
 * Unicode, `fim` exclusivo, relativos a esta mesma `transcricao`). Nunca procura o `trecho` no
 * texto: só os índices localizam a evidência, então um trecho repetido destaca apenas a
 * ocorrência certa.
 *
 * - Intervalos iguais, aninhados ou sobrepostos continuam distintos: cada segmento lista todos
 *   os IDs que o cobrem, na ordem de `evidencias`.
 * - A concatenação dos segmentos é sempre exatamente `transcricao`.
 * - Segmentar por `Array.from` mantém emoji e acentos decompostos (NFD) inteiros nas fronteiras.
 * - O contrato garante índices válidos; por robustez, valores fora de `[0, total]` são limitados
 *   e intervalos vazios, invertidos ou não inteiros são ignorados em vez de quebrar a tela.
 */
export function segmentarTranscricao(
  transcricao: string,
  evidencias: readonly Pick<Evidencia, 'id' | 'inicio' | 'fim'>[],
): Segmento[] {
  const pontos = Array.from(transcricao)
  const total = pontos.length

  const intervalos = evidencias.flatMap(({ id, inicio, fim }) => {
    if (!Number.isInteger(inicio) || !Number.isInteger(fim)) return []
    const de = Math.max(0, inicio)
    const ate = Math.min(total, fim)
    return de < ate ? [{ id, de, ate }] : []
  })

  const fronteiras = [...new Set([0, total, ...intervalos.flatMap(({ de, ate }) => [de, ate])])].sort((a, b) => a - b)

  const segmentos: Segmento[] = []
  for (let i = 0; i < fronteiras.length - 1; i++) {
    const [a, b] = [fronteiras[i], fronteiras[i + 1]]
    segmentos.push({
      texto: pontos.slice(a, b).join(''),
      evidencias: intervalos.filter(({ de, ate }) => de <= a && ate >= b).map(({ id }) => id),
    })
  }
  return segmentos
}
