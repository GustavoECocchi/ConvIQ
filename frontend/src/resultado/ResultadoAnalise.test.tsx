// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { exemplos } from '../services/mocks/exemplos.ts'
import type { AnaliseTextoResponse } from '../types/analise.ts'
import { ResultadoAnalise } from './ResultadoAnalise.tsx'

const { entrada, resposta } = exemplos.find((e) => e.chave === 'cliente-risco-e-oportunidade')!

let rolar: ReturnType<typeof vi.fn>

beforeEach(() => {
  rolar = vi.fn()
  Element.prototype.scrollIntoView = rolar as unknown as typeof Element.prototype.scrollIntoView
  ;(document.activeElement as HTMLElement | null)?.blur()
})
afterEach(cleanup)

function montar(r: AnaliseTextoResponse = resposta) {
  render(<ResultadoAnalise entrada={entrada} resposta={r} />)
}

const botao = (nome: string) => screen.getByRole('button', { name: nome })
const transcricao = () => screen.getByRole('region', { name: 'Transcrição' })
const marcas = () => [...transcricao().querySelectorAll('mark')] as HTMLElement[]
const selecionadas = () => marcas().filter((m) => m.hasAttribute('data-selecionada'))
const status = () => within(transcricao()).getByRole('status').textContent
const clicar = (nome: string) => fireEvent.click(botao(nome))

describe('botões Ver evidência', () => {
  it('um por sinal que cita evidência, com o mesmo texto visível e nome acessível que diz a que sinal pertence', () => {
    montar()
    const botoes = screen.getAllByRole('button', { name: /^Ver evidência/ })

    expect(botoes.map((b) => b.textContent)).toEqual(Array(4).fill('Ver evidência'))
    expect(botoes.map((b) => b.getAttribute('aria-label'))).toEqual([
      'Ver evidência: risco de cancelamento',
      'Ver evidência: oportunidade 1',
      'Ver evidência: recomendação 1',
      'Ver evidência: recomendação 2',
    ])
  })

  it('o sentimento não tem botão: C01 não lhe dá IDs de evidência', () => {
    montar()
    const cartao = screen.getByRole('heading', { level: 3, name: 'Sentimento' }).closest('article')!

    expect(cartao.querySelector('button')).toBeNull()
  })

  it.each([
    ['sem risco detectado', 'informacao-insuficiente'],
    ['prospect com churn não aplicável', 'prospect-churn-nao-aplicavel'],
  ])('%s: nenhum botão, e nenhum trecho é destacado', (_nome, chave) => {
    montar(exemplos.find((e) => e.chave === chave)!.resposta)

    expect(screen.queryAllByRole('button')).toHaveLength(0)
    expect(marcas()).toHaveLength(0)
  })

  it('sem seleção: nada selecionado, status vazio e sem "Voltar ao sinal"', () => {
    montar()

    expect(selecionadas()).toHaveLength(0)
    expect(status()).toBe('')
    expect(screen.queryByRole('button', { name: 'Voltar ao sinal' })).toBeNull()
  })

  it('um sinal com várias evidências numera os botões', () => {
    montar({
      ...resposta,
      churn: { situacao: 'sinal_detectado', evidencias: ['e1', 'e3'] },
    })

    expect(screen.getAllByRole('button', { name: /^Ver evidência \d: risco de cancelamento$/ }).map((b) => b.textContent)).toEqual([
      'Ver evidência 1',
      'Ver evidência 2',
    ])
  })
})

describe('selecionar uma evidência', () => {
  it('risco: seleciona todos os trechos do ID, leva o foco ao primeiro e anuncia o trecho', () => {
    montar()
    clicar('Ver evidência: risco de cancelamento')

    expect(selecionadas().map((m) => m.textContent)).toEqual(['insatisfeitos', ' com o suporte'])
    expect(document.activeElement).toBe(marcas()[0])
    expect(document.activeElement!.textContent).toBe('insatisfeitos')
    expect(rolar).toHaveBeenCalledWith({ block: 'center', behavior: 'smooth' })
    expect(status()).toBe('Evidência selecionada: “insatisfeitos com o suporte”.')
  })

  it('oportunidade: seleciona só o trecho dela', () => {
    montar()
    clicar('Ver evidência: oportunidade 1')

    expect(selecionadas().map((m) => m.textContent)).toEqual(['Queremos conhecer o Fluig'])
    expect(document.activeElement!.textContent).toBe('Queremos conhecer o Fluig')
    expect(status()).toBe('Evidência selecionada: “Queremos conhecer o Fluig”.')
  })

  it('IDs compartilhados: risco e recomendação 1 apontam para o mesmo trecho, cada um com o seu retorno', () => {
    montar()
    clicar('Ver evidência: recomendação 1')

    expect(selecionadas().map((m) => m.textContent)).toEqual(['insatisfeitos', ' com o suporte'])
    expect(status()).toBe('Evidência selecionada: “insatisfeitos com o suporte”.')

    fireEvent.click(screen.getByRole('button', { name: 'Voltar ao sinal' }))
    expect(document.activeElement).toBe(botao('Ver evidência: recomendação 1'))

    clicar('Ver evidência: risco de cancelamento')
    fireEvent.click(screen.getByRole('button', { name: 'Voltar ao sinal' }))
    expect(document.activeElement).toBe(botao('Ver evidência: risco de cancelamento'))
  })

  it('trocar de sinal move a seleção sem acumular', () => {
    montar()
    clicar('Ver evidência: risco de cancelamento')
    clicar('Ver evidência: oportunidade 1')

    expect(selecionadas().map((m) => m.textContent)).toEqual(['Queremos conhecer o Fluig'])
  })

  it('pedir de novo a mesma evidência devolve o foco ao trecho', () => {
    montar()
    clicar('Ver evidência: oportunidade 1')
    ;(document.activeElement as HTMLElement).blur()
    rolar.mockClear()
    clicar('Ver evidência: oportunidade 1')

    expect(document.activeElement!.textContent).toBe('Queremos conhecer o Fluig')
    expect(rolar).toHaveBeenCalledTimes(1)
  })

  it('o texto da transcrição continua exatamente igual depois de selecionar', () => {
    montar()
    clicar('Ver evidência: risco de cancelamento')

    expect(transcricao().querySelector('.transcricao-texto')!.textContent).toBe(resposta.transcricao)
  })
})

describe('voltar ao contexto', () => {
  it('devolve foco e rolagem ao botão que pediu a evidência', () => {
    montar()
    clicar('Ver evidência: oportunidade 1')
    rolar.mockClear()
    fireEvent.click(screen.getByRole('button', { name: 'Voltar ao sinal' }))

    expect(document.activeElement).toBe(botao('Ver evidência: oportunidade 1'))
    expect(rolar).toHaveBeenCalledWith({ block: 'center', behavior: 'smooth' })
  })

  it('a seleção continua visível depois de voltar', () => {
    montar()
    clicar('Ver evidência: oportunidade 1')
    fireEvent.click(screen.getByRole('button', { name: 'Voltar ao sinal' }))

    expect(selecionadas()).toHaveLength(1)
  })
})

describe('movimento reduzido', () => {
  it('com prefers-reduced-motion a rolagem não é suave', () => {
    vi.stubGlobal('matchMedia', (consulta: string) => ({ matches: consulta.includes('reduce'), media: consulta }))
    montar()
    clicar('Ver evidência: oportunidade 1')

    expect(rolar).toHaveBeenCalledWith({ block: 'center', behavior: 'auto' })
    vi.unstubAllGlobals()
  })
})

describe('evidência que não pode ser localizada', () => {
  const quebrada: AnaliseTextoResponse = {
    ...resposta,
    // índices que apontam para outro texto: o recorte não é o trecho. e2 é citada pelo risco e pela recomendação 1.
    evidencias: [
      { id: 'e1', trecho: 'insatisfeitos', inicio: 8, fim: 21 },
      { id: 'e2', trecho: 'insatisfeitos com o suporte', inicio: 9, fim: 36 },
      { id: 'e3', trecho: 'Queremos conhecer o Fluig', inicio: 37, fim: 62 },
    ],
  }
  const RISCO = 'Ver evidência: risco de cancelamento'
  const RECOMENDACAO = 'Ver evidência: recomendação 1'
  const OPORTUNIDADE = 'Ver evidência: oportunidade 1'
  const AVISO = 'Não foi possível localizar esta evidência na transcrição.'
  const avisos = () => screen.queryAllByRole('alert')
  const grupo = (nome: string) => botao(nome).parentElement!
  const voltarAoSinal = () => screen.queryByRole('button', { name: 'Voltar ao sinal' })

  it('risco (resumo): avisa junto do botão, sem destacar, mover foco nem rolar, e a transcrição não repete o aviso', () => {
    montar(quebrada)
    expect(marcas().map((m) => m.textContent)).toEqual(['insatisfeitos', 'Queremos conhecer o Fluig'])
    expect(avisos()).toHaveLength(0)

    botao(RISCO).focus()
    clicar(RISCO)

    expect(avisos().map((a) => a.textContent)).toEqual([AVISO])
    expect(grupo(RISCO).contains(avisos()[0])).toBe(true)
    expect(document.activeElement).toBe(botao(RISCO))
    expect(selecionadas()).toHaveLength(0)
    expect(rolar).not.toHaveBeenCalled()
    expect(status()).toBe('')
    expect(voltarAoSinal()).toBeNull()
  })

  it('recomendação (detalhe): o aviso fica no item dela, não no risco que cita o mesmo ID', () => {
    montar(quebrada)
    clicar(RECOMENDACAO)

    expect(avisos()).toHaveLength(1)
    expect(grupo(RECOMENDACAO).contains(avisos()[0])).toBe(true)
    expect(grupo(RISCO).querySelector('[role="alert"]')).toBeNull()
  })

  it('pedir em outro sinal move o aviso, sem acumular', () => {
    montar(quebrada)
    clicar(RISCO)
    clicar(RECOMENDACAO)

    expect(avisos()).toHaveLength(1)
    expect(grupo(RECOMENDACAO).contains(avisos()[0])).toBe(true)
  })

  it('repetir o mesmo pedido troca o aviso por um novo, para que seja anunciado de novo', () => {
    montar(quebrada)
    clicar(RISCO)
    const primeiro = avisos()[0]
    clicar(RISCO)

    expect(avisos()).toHaveLength(1)
    expect(avisos()[0]).not.toBe(primeiro)
    expect(primeiro.isConnected).toBe(false)
    expect(avisos()[0].textContent).toBe(AVISO)
  })

  it('uma evidência válida depois apaga o aviso, seleciona, foca, rola e volta ao botão certo', () => {
    montar(quebrada)
    clicar(RISCO)
    clicar(OPORTUNIDADE)

    expect(avisos()).toHaveLength(0)
    expect(selecionadas().map((m) => m.textContent)).toEqual(['Queremos conhecer o Fluig'])
    expect(document.activeElement!.textContent).toBe('Queremos conhecer o Fluig')
    expect(rolar).toHaveBeenCalledTimes(1)
    expect(status()).toBe('Evidência selecionada: “Queremos conhecer o Fluig”.')

    fireEvent.click(voltarAoSinal()!)
    expect(document.activeElement).toBe(botao(OPORTUNIDADE))
  })

  it('uma inválida depois de uma válida desfaz a seleção, sem mover foco nem rolar', () => {
    montar(quebrada)
    clicar(OPORTUNIDADE)
    botao(RISCO).focus()
    rolar.mockClear()
    clicar(RISCO)

    expect(selecionadas()).toHaveLength(0)
    expect(status()).toBe('')
    expect(voltarAoSinal()).toBeNull()
    expect(document.activeElement).toBe(botao(RISCO))
    expect(rolar).not.toHaveBeenCalled()
    expect(avisos().map((a) => a.textContent)).toEqual([AVISO])
  })

  it('sinal com várias evidências: o aviso diz qual delas falhou', () => {
    montar({ ...quebrada, churn: { situacao: 'sinal_detectado', evidencias: ['e1', 'e2'] } })
    clicar('Ver evidência 2: risco de cancelamento')

    expect(avisos().map((a) => a.textContent)).toEqual(['Não foi possível localizar a evidência 2 na transcrição.'])
  })

  it('um ID citado que não está entre as evidências também avisa', () => {
    montar({ ...resposta, churn: { situacao: 'sinal_detectado', evidencias: ['e9'] } })
    clicar(RISCO)

    expect(avisos().map((a) => a.textContent)).toEqual([AVISO])
    expect(selecionadas()).toHaveLength(0)
  })

  it('os sinais vizinhos continuam funcionando', () => {
    montar(quebrada)
    clicar(OPORTUNIDADE)

    expect(selecionadas().map((m) => m.textContent)).toEqual(['Queremos conhecer o Fluig'])
  })

  describe('aviso que nasce fora da área visível (toque na borda inferior a 320 px)', () => {
    // O jsdom não tem layout: a posição do aviso é simulada aqui e a geometria real é conferida no navegador.
    const ALTURA = window.innerHeight
    let aviso = { top: 0, bottom: 0 }
    let rolados: Element[]

    beforeEach(() => {
      rolados = []
      rolar.mockImplementation(function (this: Element) {
        rolados.push(this)
      })
      vi.spyOn(Element.prototype, 'getBoundingClientRect').mockImplementation(function (this: Element) {
        const { top, bottom } = this.getAttribute('role') === 'alert' ? aviso : { top: 0, bottom: 0 }
        return { top, bottom, left: 0, right: 0, x: 0, y: top, width: 0, height: bottom - top, toJSON: () => ({}) }
      })
    })
    afterEach(() => vi.restoreAllMocks())

    it('inteiro na área visível, mesmo encostado na borda inferior: não rola', () => {
      aviso = { top: ALTURA - 39, bottom: ALTURA }
      montar(quebrada)
      botao(RISCO).focus()
      clicar(RISCO)

      expect(avisos()).toHaveLength(1)
      expect(rolar).not.toHaveBeenCalled()
    })

    it('cortado embaixo: revela o grupo do botão com o menor deslocamento, sem animação, e o foco fica no botão', () => {
      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      montar(quebrada)
      botao(RISCO).focus()
      clicar(RISCO)

      expect(rolar).toHaveBeenCalledTimes(1)
      expect(rolar).toHaveBeenCalledWith({ block: 'nearest', inline: 'nearest', behavior: 'instant' })
      expect(rolados).toEqual([grupo(RISCO)])
      expect(grupo(RISCO).contains(avisos()[0])).toBe(true)
      expect(document.activeElement).toBe(botao(RISCO))
      expect(selecionadas()).toHaveLength(0)
      expect(status()).toBe('')
    })

    it('um pixel além da borda já conta como cortado, em cima ou embaixo', () => {
      aviso = { top: ALTURA - 38, bottom: ALTURA + 1 }
      montar(quebrada)
      clicar(RISCO)
      aviso = { top: -1, bottom: 38 }
      clicar(RISCO)

      expect(rolar).toHaveBeenCalledTimes(2)
    })

    it('a rolagem do erro nunca é suave, com ou sem movimento reduzido', () => {
      vi.stubGlobal('matchMedia', (consulta: string) => ({ matches: consulta.includes('reduce'), media: consulta }))
      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      montar(quebrada)
      clicar(RISCO)
      vi.unstubAllGlobals()

      expect(rolar).toHaveBeenCalledWith({ block: 'nearest', inline: 'nearest', behavior: 'instant' })
    })

    it('recomendação (detalhe): revela o grupo dela, não o do risco que cita o mesmo ID', () => {
      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      montar(quebrada)
      clicar(RECOMENDACAO)

      expect(rolados).toEqual([grupo(RECOMENDACAO)])
    })

    it('repetir o pedido rola de novo só se o novo aviso também nascer fora da área visível', () => {
      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      montar(quebrada)
      clicar(RISCO)
      aviso = { top: ALTURA - 47, bottom: ALTURA - 8 }
      clicar(RISCO)
      expect(rolar).toHaveBeenCalledTimes(1)

      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      clicar(RISCO)
      expect(rolar).toHaveBeenCalledTimes(2)
      expect(avisos()).toHaveLength(1)
    })

    it('só ao nascer: se a pessoa rolar para longe, um novo render não traz o aviso de volta', () => {
      aviso = { top: ALTURA - 47, bottom: ALTURA - 8 }
      const { rerender } = render(<ResultadoAnalise entrada={entrada} resposta={quebrada} />)
      clicar(RISCO)
      aviso = { top: ALTURA + 300, bottom: ALTURA + 339 }
      rerender(<ResultadoAnalise entrada={entrada} resposta={quebrada} />)

      expect(avisos()).toHaveLength(1)
      expect(rolar).not.toHaveBeenCalled()
    })

    it('a evidência válida depois mantém a rolagem dela até o trecho', () => {
      aviso = { top: ALTURA + 4, bottom: ALTURA + 43 }
      montar(quebrada)
      clicar(RISCO)
      rolar.mockClear()
      rolados = []
      clicar(OPORTUNIDADE)

      expect(avisos()).toHaveLength(0)
      expect(rolar).toHaveBeenCalledTimes(1)
      expect(rolar).toHaveBeenCalledWith({ block: 'center', behavior: 'smooth' })
      expect(rolados).toEqual([document.activeElement])
    })
  })
})

describe('acessibilidade e limites', () => {
  it('os destaques anunciam o papel de evidência; o forte diz que há mais de uma', () => {
    montar()

    expect(marcas().map((m) => m.getAttribute('aria-roledescription'))).toEqual(['evidências sobrepostas', 'evidência', 'evidência'])
  })

  it('a região de status é uma live region e existe antes da seleção', () => {
    montar()

    expect(within(transcricao()).getByRole('status')).toBeTruthy()
  })

  it('os destaques são alvos programáticos (tabindex -1), não paradas de Tab', () => {
    montar()

    expect(marcas().every((m) => m.getAttribute('tabindex') === '-1')).toBe(true)
  })

  it('nenhum ID de evidência aparece como texto e não há pedido HTTP', () => {
    const fetchEspiao = vi.fn()
    vi.stubGlobal('fetch', fetchEspiao)
    montar()
    clicar('Ver evidência: risco de cancelamento')

    expect(document.body.textContent).not.toMatch(/\be\d+\b/)
    expect(fetchEspiao).not.toHaveBeenCalled()
    vi.unstubAllGlobals()
  })
})
