import type { Evidencia } from '../types/analise.ts'

/** Pedaço contíguo da transcrição e os IDs das evidências que o cobrem (vazio = texto sem destaque). */
export interface Segmento {
  texto: string
  evidencias: string[]
}

/** Evidência usada para localizar: `trecho` é opcional e, se vier, o recorte pelos índices precisa ser igual a ele. */
type EvidenciaLocalizavel = Pick<Evidencia, 'id' | 'inicio' | 'fim'> & Partial<Pick<Evidencia, 'trecho'>>

interface Intervalo {
  id: string
  de: number
  ate: number
}

/**
 * Separa as evidências que podem ser localizadas das que não podem. Uma evidência só é localizada
 * quando os índices são inteiros, `0 <= inicio < fim <= total` (em pontos de código) e, se `trecho`
 * foi informado, o recorte da transcrição nesses índices é exatamente o `trecho`. Isso **confere**
 * o recorte, nunca procura o trecho no texto. Fora disso a evidência é descartada, em vez de ser
 * limitada ao texto: um destaque inventado seria apresentado como evidência.
 */
function localizar(pontos: string[], evidencias: readonly EvidenciaLocalizavel[]) {
  const total = pontos.length
  const intervalos: Intervalo[] = []
  const naoLocalizadas: string[] = []

  for (const { id, inicio, fim, trecho } of evidencias) {
    const valida =
      Number.isInteger(inicio) &&
      Number.isInteger(fim) &&
      inicio >= 0 &&
      inicio < fim &&
      fim <= total &&
      (trecho === undefined || pontos.slice(inicio, fim).join('') === trecho)
    if (valida) intervalos.push({ id, de: inicio, ate: fim })
    else naoLocalizadas.push(id)
  }
  return { intervalos, naoLocalizadas }
}

/** IDs das evidências que não podem ser localizadas na transcrição (índices inválidos ou recorte diferente do trecho). */
export function idsNaoLocalizados(transcricao: string, evidencias: readonly EvidenciaLocalizavel[]): string[] {
  return localizar(Array.from(transcricao), evidencias).naoLocalizadas
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
 * - Evidências que não podem ser localizadas (ver `localizar`) são ignoradas: não geram destaque.
 */
export function segmentarTranscricao(transcricao: string, evidencias: readonly EvidenciaLocalizavel[]): Segmento[] {
  const pontos = Array.from(transcricao)
  const { intervalos } = localizar(pontos, evidencias)

  const fronteiras = [...new Set([0, pontos.length, ...intervalos.flatMap(({ de, ate }) => [de, ate])])].sort((a, b) => a - b)

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
