import { describe, expect, it } from 'vitest'
import { exemplos } from '../services/mocks/exemplos.ts'
import { recortarPorPontosDeCodigo } from '../types/analise.ts'
import { segmentarTranscricao } from './segmentos.ts'

/** Metade de um par substituto (UTF-16) sem a outra: sinal de que um emoji foi partido. */
const SUBSTITUTO_SOLTO = /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/
const ev = (id: string, inicio: number, fim: number) => ({ id, inicio, fim })
const textos = (segmentos: ReturnType<typeof segmentarTranscricao>) => segmentos.map((s) => s.texto)
const comIds = (segmentos: ReturnType<typeof segmentarTranscricao>) => segmentos.map((s) => [s.texto, s.evidencias])

describe('casos básicos', () => {
  it('sem evidências devolve a transcrição inteira, sem destaque', () => {
    expect(comIds(segmentarTranscricao('Bom dia a todos.', []))).toEqual([['Bom dia a todos.', []]])
  })

  it('uma evidência no meio gera três segmentos', () => {
    expect(comIds(segmentarTranscricao('abc DEF ghi', [ev('e1', 4, 7)]))).toEqual([
      ['abc ', []],
      ['DEF', ['e1']],
      [' ghi', []],
    ])
  })

  it('evidência no começo e no fim não gera segmentos vazios', () => {
    expect(comIds(segmentarTranscricao('abcdef', [ev('a', 0, 2), ev('b', 4, 6)]))).toEqual([
      ['ab', ['a']],
      ['cd', []],
      ['ef', ['b']],
    ])
  })

  it('evidência cobrindo tudo marca o texto inteiro', () => {
    expect(comIds(segmentarTranscricao('abc', [ev('e1', 0, 3)]))).toEqual([['abc', ['e1']]])
  })

  it('transcrição vazia devolve lista vazia', () => {
    expect(segmentarTranscricao('', [])).toEqual([])
  })

  it('não altera a lista de evidências recebida', () => {
    const lista = [ev('e2', 3, 5), ev('e1', 0, 4)]
    const copia = structuredClone(lista)
    segmentarTranscricao('abcdefg', lista)

    expect(lista).toEqual(copia)
  })
})

describe('mesmo trecho repetido: só os índices localizam', () => {
  it('destaca apenas a segunda ocorrência, sem procurar o texto', () => {
    const texto = 'falha no suporte. outra falha no suporte.'
    const segunda = texto.indexOf('falha no suporte', 5)
    const segmentos = segmentarTranscricao(texto, [ev('e1', segunda, segunda + 'falha no suporte'.length)])

    expect(comIds(segmentos)).toEqual([
      ['falha no suporte. outra ', []],
      ['falha no suporte', ['e1']],
      ['.', []],
    ])
  })

  it('duas ocorrências com IDs diferentes ficam cada uma no seu lugar', () => {
    const texto = 'sim. sim.'
    expect(comIds(segmentarTranscricao(texto, [ev('b', 5, 8), ev('a', 0, 3)]))).toEqual([
      ['sim', ['a']],
      ['. ', []],
      ['sim', ['b']],
      ['.', []],
    ])
  })
})

describe('Unicode: índices em pontos de código', () => {
  it('emoji antes do sinal: o destaque cai no trecho certo e `slice` (UTF-16) erraria', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'emoji-antes-do-sinal')!
    const segmentos = segmentarTranscricao(resposta.transcricao, resposta.evidencias)
    const marcados = segmentos.filter((s) => s.evidencias.length > 0)
    const longa = resposta.evidencias.find((e) => e.id === 'e2')!

    expect(textos(segmentos)[0]).toBe('😀 Estamos ')
    expect(marcados.map((s) => s.texto).join('')).toBe('insatisfeitos com o suporte')
    expect(resposta.transcricao.slice(longa.inicio, longa.fim)).not.toBe(longa.trecho)
  })

  it('emoji dentro do trecho não é partido ao meio', () => {
    const texto = 'a 😀 b'
    const segmentos = segmentarTranscricao(texto, [ev('e1', 2, 3)])

    expect(comIds(segmentos)).toEqual([
      ['a ', []],
      ['😀', ['e1']],
      [' b', []],
    ])
    for (const { texto: t } of segmentos) expect(t).not.toMatch(SUBSTITUTO_SOLTO)
  })

  it('acento decomposto (NFD): cada marca combinante conta como ponto próprio e o recorte acompanha a API', () => {
    const texto = 'Estamos insatisfeitos com a sua atenção. Não aceitamos.'.normalize('NFD')
    const trecho = 'atenção'.normalize('NFD')
    const inicio = Array.from(texto.slice(0, texto.indexOf(trecho))).length
    const fim = inicio + Array.from(trecho).length

    // ç e ã viram duas unidades cada: 7 letras → 9 pontos de código (em NFC seriam 7).
    expect(Array.from(trecho).length).toBe(9)
    expect(Array.from('atenção'.normalize('NFC')).length).toBe(7)
    expect(recortarPorPontosDeCodigo(texto, inicio, fim)).toBe(trecho)

    const segmentos = segmentarTranscricao(texto, [ev('e1', inicio, fim)])
    expect(segmentos.find((s) => s.evidencias.length > 0)!.texto).toBe(trecho)
    expect(textos(segmentos).join('')).toBe(texto)
  })

  it('NFC e NFD da mesma frase destacam o mesmo trecho visível', () => {
    const base = 'Muita insatisfação aqui.'
    for (const forma of ['NFC', 'NFD'] as const) {
      const texto = base.normalize(forma)
      const alvo = 'insatisfação'.normalize(forma)
      const inicio = Array.from(texto.slice(0, texto.indexOf(alvo))).length
      const segmentos = segmentarTranscricao(texto, [ev('e1', inicio, inicio + Array.from(alvo).length)])

      expect(segmentos.find((s) => s.evidencias.length > 0)!.texto).toBe(alvo)
      expect(segmentos.find((s) => s.evidencias.length > 0)!.texto.normalize('NFC')).toBe('insatisfação')
    }
  })
})

describe('intervalos que se encontram', () => {
  it('IDs compartilhados: dois intervalos iguais viram um segmento com os dois IDs, na ordem recebida', () => {
    expect(comIds(segmentarTranscricao('abcdef', [ev('b', 1, 4), ev('a', 1, 4)]))).toEqual([
      ['a', []],
      ['bcd', ['b', 'a']],
      ['ef', []],
    ])
  })

  it('aninhados continuam distintos: o interno tem os dois IDs, o resto do externo só o externo', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!

    expect(comIds(segmentarTranscricao(resposta.transcricao, resposta.evidencias))).toEqual([
      ['Estamos ', []],
      ['insatisfeitos', ['e1', 'e2']],
      [' com o suporte', ['e2']],
      ['. ', []],
      ['Queremos conhecer o Fluig', ['e3']],
      ['.', []],
    ])
  })

  it('aninhados em três níveis', () => {
    expect(comIds(segmentarTranscricao('0123456789', [ev('x', 0, 10), ev('y', 2, 8), ev('z', 4, 6)]))).toEqual([
      ['01', ['x']],
      ['23', ['x', 'y']],
      ['45', ['x', 'y', 'z']],
      ['67', ['x', 'y']],
      ['89', ['x']],
    ])
  })

  it('sobrepostos parcialmente: a faixa comum tem os dois IDs', () => {
    expect(comIds(segmentarTranscricao('abcdefgh', [ev('a', 0, 5), ev('b', 3, 8)]))).toEqual([
      ['abc', ['a']],
      ['de', ['a', 'b']],
      ['fgh', ['b']],
    ])
  })

  it('adjacentes não se fundem nem se sobrepõem', () => {
    expect(comIds(segmentarTranscricao('abcdef', [ev('a', 0, 3), ev('b', 3, 6)]))).toEqual([
      ['abc', ['a']],
      ['def', ['b']],
    ])
  })
})

describe('robustez com índices fora do contrato', () => {
  it('limita ao texto o que passa do fim ou começa antes do início', () => {
    expect(comIds(segmentarTranscricao('abcd', [ev('a', -3, 2), ev('b', 3, 99)]))).toEqual([
      ['ab', ['a']],
      ['c', []],
      ['d', ['b']],
    ])
  })

  it.each([
    ['vazio', ev('x', 2, 2)],
    ['invertido', ev('x', 3, 1)],
    ['fora do texto', ev('x', 50, 60)],
    ['não inteiro', ev('x', 0.5, 2)],
    ['NaN', ev('x', Number.NaN, 2)],
  ])('ignora intervalo %s sem quebrar nem perder texto', (_nome, invalido) => {
    const segmentos = segmentarTranscricao('abcd', [invalido, ev('ok', 0, 1)])

    expect(comIds(segmentos)).toEqual([
      ['a', ['ok']],
      ['bcd', []],
    ])
  })
})

describe('invariantes sobre todas as fixtures', () => {
  describe.each(exemplos.map((exemplo) => [exemplo.chave, exemplo.resposta] as const))('%s', (_chave, resposta) => {
    const segmentos = segmentarTranscricao(resposta.transcricao, resposta.evidencias)

    it('a concatenação reproduz exatamente a transcrição', () => {
      expect(textos(segmentos).join('')).toBe(resposta.transcricao)
    })

    it('para cada evidência, os segmentos que a citam reconstroem o trecho literal da API', () => {
      for (const evidencia of resposta.evidencias) {
        const doId = segmentos.filter((s) => s.evidencias.includes(evidencia.id)).map((s) => s.texto).join('')
        expect(doId).toBe(evidencia.trecho)
      }
    })

    it('nenhum segmento é vazio', () => {
      expect(segmentos.every((s) => s.texto.length > 0)).toBe(true)
    })
  })
})
