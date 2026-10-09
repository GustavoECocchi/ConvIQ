import { describe, expect, it } from 'vitest'
import { SENTIMENTOS, SITUACOES_CHURN, VINCULOS, recortarPorPontosDeCodigo } from '../../types/analise.ts'
import { ROTULO_EXEMPLO, exemplos } from './exemplos.ts'

/** Índices de C01 contam pontos de código; `length` e `slice` contam unidades UTF-16. */
const pontosDeCodigo = (texto: string) => Array.from(texto).length

describe('exemplos ilustrativos de C01', () => {
  it('são identificados como ilustrativos e têm chaves únicas', () => {
    expect(exemplos.length).toBeGreaterThanOrEqual(3)
    for (const exemplo of exemplos) {
      expect(exemplo.rotulo).toBe(ROTULO_EXEMPLO)
    }
    const chaves = exemplos.map((exemplo) => exemplo.chave)
    expect(new Set(chaves).size).toBe(chaves.length)
  })

  it('cobrem cliente com risco e oportunidade, prospect e informação insuficiente', () => {
    const situacoes = exemplos.map((exemplo) => exemplo.resposta.churn.situacao)
    const vinculos = exemplos.map((exemplo) => exemplo.entrada.vinculo)

    expect(situacoes).toContain('sinal_detectado')
    expect(situacoes).toContain('nao_aplicavel')
    expect(situacoes).toContain('informacao_insuficiente')
    expect(exemplos.some((e) => e.resposta.churn.situacao === 'sinal_detectado' && e.resposta.oportunidades.length > 0)).toBe(true)
    expect(vinculos).toContain('prospect')
  })

  describe.each(exemplos.map((exemplo) => [exemplo.chave, exemplo] as const))('%s', (_chave, exemplo) => {
    const { entrada, resposta } = exemplo

    it('ecoa a transcrição da entrada e usa só valores dos enums de C01', () => {
      expect(resposta.transcricao).toBe(entrada.transcricao)
      expect(VINCULOS).toContain(entrada.vinculo)
      expect(SENTIMENTOS).toContain(resposta.sentimento)
      expect(SITUACOES_CHURN).toContain(resposta.churn.situacao)
      expect(entrada.transcricao).toBe(entrada.transcricao.trim())
      expect(entrada.titulo.length).toBeGreaterThan(0)
      expect(entrada.empresa.length).toBeLessThanOrEqual(200)
    })

    it('recorta cada evidência literalmente da transcrição, por pontos de código', () => {
      const total = pontosDeCodigo(resposta.transcricao)
      for (const evidencia of resposta.evidencias) {
        expect(evidencia.inicio).toBeGreaterThanOrEqual(0)
        expect(evidencia.fim).toBeGreaterThan(evidencia.inicio)
        expect(evidencia.fim).toBeLessThanOrEqual(total)
        expect(recortarPorPontosDeCodigo(resposta.transcricao, evidencia.inicio, evidencia.fim)).toBe(evidencia.trecho)
      }
    })

    it('tem IDs de evidência únicos e todo ID referenciado existe, sem repetir na mesma lista', () => {
      const ids = resposta.evidencias.map((evidencia) => evidencia.id)
      expect(new Set(ids).size).toBe(ids.length)

      const listas = [
        resposta.churn.evidencias,
        ...resposta.oportunidades.map((oportunidade) => oportunidade.evidencias),
        ...resposta.recomendacoes.map((recomendacao) => recomendacao.evidencias),
      ]
      for (const lista of listas) {
        expect(new Set(lista).size).toBe(lista.length)
        for (const id of lista) {
          expect(ids).toContain(id)
        }
      }
    })

    it('respeita as regras de produto: prospect sem churn aplicável e sem evidência sem sinal', () => {
      if (entrada.vinculo === 'prospect') {
        expect(resposta.churn.situacao).toBe('nao_aplicavel')
      }
      if (resposta.churn.situacao !== 'sinal_detectado') {
        expect(resposta.churn.evidencias).toEqual([])
      }
      if (resposta.evidencias.length === 0) {
        expect(resposta.oportunidades).toEqual([])
        expect(resposta.recomendacoes).toEqual([])
      }
    })
  })

  it('o exemplo com emoji prova que `slice` (UTF-16) erra e o recorte por pontos de código acerta', () => {
    const exemplo = exemplos.find((e) => e.chave === 'emoji-antes-do-sinal')
    expect(exemplo).toBeDefined()
    const { transcricao, evidencias } = exemplo!.resposta
    const longa = evidencias.find((evidencia) => evidencia.id === 'e2')!

    expect(transcricao.length).toBeGreaterThan(pontosDeCodigo(transcricao))
    expect(transcricao.slice(longa.inicio, longa.fim)).not.toBe(longa.trecho)
    expect(recortarPorPontosDeCodigo(transcricao, longa.inicio, longa.fim)).toBe(longa.trecho)
  })

  it('evidências aninhadas continuam distintas, sem serem fundidas pelos exemplos', () => {
    const exemplo = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const [curta, longa] = exemplo.resposta.evidencias

    expect(longa.inicio).toBe(curta.inicio)
    expect(longa.fim).toBeGreaterThan(curta.fim)
    expect(longa.trecho.startsWith(curta.trecho)).toBe(true)
    expect(exemplo.resposta.churn.evidencias).toEqual([longa.id])
  })
})
