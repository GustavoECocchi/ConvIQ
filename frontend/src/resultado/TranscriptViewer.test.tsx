// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { exemplos } from '../services/mocks/exemplos.ts'
import type { TranscriptViewerProps } from './TranscriptViewer.tsx'
import { TranscriptViewer } from './TranscriptViewer.tsx'

afterEach(cleanup)

type Resposta = TranscriptViewerProps['resposta']

function montar(resposta: Resposta) {
  render(<TranscriptViewer resposta={resposta} />)
  const secao = screen.getByRole('region', { name: 'Transcrição' })
  const texto = secao.querySelector('.transcricao-texto') as HTMLElement
  const marcas = [...texto.querySelectorAll('mark')] as HTMLElement[]
  return { secao, texto, marcas }
}

const dados = (marca: HTMLElement) => ({
  texto: marca.textContent,
  ids: marca.getAttribute('data-evidencias'),
  sobrepostas: marca.hasAttribute('data-sobrepostas'),
})

describe('texto exibido', () => {
  it('é exatamente a transcrição, com quebras de linha e espaços preservados', () => {
    const transcricao = 'Cliente: estamos insatisfeitos.\n\nVendedor:   vamos resolver.\n'
    const { texto } = montar({ transcricao, evidencias: [{ id: 'e1', trecho: 'insatisfeitos', inicio: 18, fim: 31 }] })

    expect(texto.textContent).toBe(transcricao)
  })

  it('só destaca os intervalos recebidos; o resto é texto simples', () => {
    const { marcas } = montar({
      transcricao: 'abc DEF ghi',
      evidencias: [{ id: 'e1', trecho: 'DEF', inicio: 4, fim: 7 }],
    })

    expect(marcas.map(dados)).toEqual([{ texto: 'DEF', ids: 'e1', sobrepostas: false }])
  })

  it('trecho repetido: destaca só a ocorrência indicada pelos índices', () => {
    const transcricao = 'não recomendo. não recomendo.'
    const { texto, marcas } = montar({ transcricao, evidencias: [{ id: 'e1', trecho: 'não recomendo', inicio: 15, fim: 28 }] })

    expect(marcas).toHaveLength(1)
    expect(texto.textContent!.indexOf(marcas[0].textContent!)).toBe(0)
    expect(texto.innerHTML.startsWith('não recomendo. <mark')).toBe(true)
  })

  it('emoji antes do sinal: destaca insatisfeitos com o suporte, não uma posição deslocada', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'emoji-antes-do-sinal')!
    const { marcas } = montar(resposta)

    expect(marcas.map(dados)).toEqual([
      { texto: 'insatisfeitos', ids: 'e1 e2', sobrepostas: true },
      { texto: ' com o suporte', ids: 'e2', sobrepostas: false },
    ])
  })

  it('intervalos aninhados ficam distintos, com destaque mais forte no trecho comum', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const { marcas } = montar(resposta)

    expect(marcas.map(dados)).toEqual([
      { texto: 'insatisfeitos', ids: 'e1 e2', sobrepostas: true },
      { texto: ' com o suporte', ids: 'e2', sobrepostas: false },
      { texto: 'Queremos conhecer o Fluig', ids: 'e3', sobrepostas: false },
    ])
  })

  it('IDs compartilhados: o mesmo intervalo citado por duas evidências é um único destaque', () => {
    const { marcas } = montar({
      transcricao: 'queremos o Fluig',
      evidencias: [
        { id: 'e1', trecho: 'Fluig', inicio: 11, fim: 16 },
        { id: 'e2', trecho: 'Fluig', inicio: 11, fim: 16 },
      ],
    })

    expect(marcas.map(dados)).toEqual([{ texto: 'Fluig', ids: 'e1 e2', sobrepostas: true }])
  })
})

describe('sem evidências', () => {
  it('mostra a transcrição sem destaque e explica por quê', () => {
    const { secao, texto, marcas } = montar({ transcricao: 'Bom dia a todos.', evidencias: [] })

    expect(marcas).toHaveLength(0)
    expect(texto.textContent).toBe('Bom dia a todos.')
    expect(secao.textContent).toContain('Nenhum trecho foi destacado porque a análise não encontrou evidências')
    expect(secao.textContent).not.toContain('destaque mais forte')
  })
})

describe('limites de F05-A', () => {
  it('sem seleção: não mostra IDs como texto nem oferece ação, link, busca ou campo', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const { secao } = montar(resposta)

    expect(secao.textContent).not.toMatch(/\be\d+\b/)
    expect(secao.querySelector('a, button, input, [role="button"], [tabindex]:not([tabindex="-1"])')).toBeNull()
    expect(secao.textContent).not.toMatch(/Ver evidência/i)
  })

  it('não liga sentimento nem risco a trechos e não mostra números de confiança', () => {
    const { resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!
    const { secao } = montar(resposta)

    expect(secao.textContent).not.toMatch(/sentimento|risco de cancelamento|\d+\s?%|confiança|pontuação/i)
  })

  it('h2 único, rótulo da região acessível', () => {
    montar({ transcricao: 'x', evidencias: [] })

    expect(screen.getAllByRole('heading').map((h) => [h.tagName, h.textContent])).toEqual([['H2', 'Transcrição']])
  })
})

describe('seleção que não pode ser localizada', () => {
  it('é ignorada: nada destacado, status vazio e sem "Voltar ao sinal" (o aviso fica com quem pediu)', () => {
    render(
      <TranscriptViewer
        resposta={{ transcricao: 'Estamos insatisfeitos.', evidencias: [{ id: 'e1', trecho: 'insatisfeitos', inicio: 9, fim: 22 }] }}
        selecionada={{ id: 'e1' }}
        aoVoltar={() => {}}
      />,
    )
    const secao = screen.getByRole('region', { name: 'Transcrição' })

    expect(secao.querySelector('mark')).toBeNull()
    expect(screen.getByRole('status').textContent).toBe('')
    expect(screen.queryByRole('button', { name: 'Voltar ao sinal' })).toBeNull()
  })
})

describe.each(exemplos.map((exemplo) => [exemplo.chave, exemplo.resposta] as const))('fixture %s', (_chave, resposta) => {
  it('o texto exibido é a transcrição e cada evidência é reconstruída pelos destaques que a citam', () => {
    const { texto, marcas } = montar(resposta)

    expect(texto.textContent).toBe(resposta.transcricao)
    for (const evidencia of resposta.evidencias) {
      const doId = marcas.filter((m) => m.getAttribute('data-evidencias')!.split(' ').includes(evidencia.id))
      expect(doId.map((m) => m.textContent).join('')).toBe(evidencia.trecho)
    }
  })
})
