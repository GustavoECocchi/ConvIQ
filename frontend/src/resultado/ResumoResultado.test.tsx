// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { SENTIMENTOS, SITUACOES_CHURN, VINCULOS } from '../types/analise.ts'
import type { ChurnSituacao, Sentimento, Vinculo } from '../types/analise.ts'
import { ResumoResultado } from './ResumoResultado.tsx'

afterEach(cleanup)

function montar({
  vinculo = 'cliente',
  sentimento = 'neutro',
  situacao = 'sem_sinal_detectado',
  titulo = 'Acompanhamento',
  empresa = 'Empresa Teste',
}: { vinculo?: Vinculo; sentimento?: Sentimento; situacao?: ChurnSituacao; titulo?: string; empresa?: string } = {}) {
  render(<ResumoResultado entrada={{ titulo, empresa, vinculo }} resposta={{ sentimento, churn: { situacao } }} />)
  const cartao = (nome: string) => screen.getByRole('heading', { level: 3, name: nome }).closest('article')!
  return { sentimento: cartao('Sentimento'), churn: cartao('Risco de cancelamento') }
}

const ROTULO_SENTIMENTO: Record<Sentimento, string> = {
  positivo: 'Positivo',
  neutro: 'Neutro',
  negativo: 'Negativo',
  informacao_insuficiente: 'Informação insuficiente',
}
const ROTULO_CHURN: Record<ChurnSituacao, string> = {
  sinal_detectado: 'Sinal detectado',
  sem_sinal_detectado: 'Sem sinal detectado',
  nao_aplicavel: 'Não aplicável',
  informacao_insuficiente: 'Informação insuficiente',
}
const ROTULO_VINCULO: Record<Vinculo, string> = { cliente: 'Cliente', prospect: 'Prospect', nao_informado: 'Não informado' }

describe('identificação da reunião', () => {
  it('mostra título, empresa e vínculo declarado', () => {
    montar({ titulo: 'Reunião de renovação', empresa: 'Acme S.A.', vinculo: 'cliente' })
    const dados = within(screen.getByRole('region', { name: 'Reunião analisada' }))

    expect(dados.getByText('Reunião de renovação')).toBeTruthy()
    expect(dados.getByText('Acme S.A.')).toBeTruthy()
    expect(dados.getByText('Cliente')).toBeTruthy()
  })

  it.each(VINCULOS)('vínculo %s aparece com o próprio rótulo e sem apresentar outro', (vinculo) => {
    montar({ vinculo })
    const secao = screen.getByRole('region', { name: 'Reunião analisada' })

    expect(within(secao).getByText(ROTULO_VINCULO[vinculo])).toBeTruthy()
    for (const outro of VINCULOS.filter((v) => v !== vinculo)) {
      expect(within(secao).queryByText(ROTULO_VINCULO[outro])).toBeNull()
    }
  })

  it('nao_informado não vira cliente nem prospect', () => {
    montar({ vinculo: 'nao_informado' })
    const texto = screen.getByRole('region', { name: 'Reunião analisada' }).textContent!

    expect(texto).toContain('Não informado')
    expect(texto).toContain('nada foi presumido')
    expect(texto).not.toMatch(/\bCliente\b|\bProspect\b/)
  })
})

describe('sentimento', () => {
  it.each(SENTIMENTOS)('%s mostra só o próprio estado', (sentimento) => {
    const { sentimento: cartao } = montar({ sentimento })
    const rotulo = cartao.querySelector('.resumo-estado')!.textContent

    expect(rotulo).toBe(ROTULO_SENTIMENTO[sentimento])
    expect(cartao.getAttribute('data-sentimento')).toBe(sentimento)
  })

  it('informacao_insuficiente não é apresentado como neutro', () => {
    const { sentimento } = montar({ sentimento: 'informacao_insuficiente' })

    expect(sentimento.textContent).toContain('não quer dizer que a conversa foi neutra')
    expect(sentimento.querySelector('.resumo-estado')!.textContent).not.toBe('Neutro')
  })

  it('não atribui IDs de evidência ao sentimento, mesmo que o churn os tenha', () => {
    render(
      <ResumoResultado
        entrada={{ titulo: 'T', empresa: 'E', vinculo: 'cliente' }}
        resposta={{ sentimento: 'negativo', churn: { situacao: 'sinal_detectado', evidencias: ['e1', 'e2'] } as never }}
      />,
    )
    const cartao = screen.getByRole('heading', { level: 3, name: 'Sentimento' }).closest('article')!

    expect(cartao.textContent).not.toMatch(/\be\d+\b/)
    expect(document.body.textContent).not.toMatch(/\be\d+\b/)
    expect(cartao.querySelector('a, button')).toBeNull()
  })
})

describe('situação de churn', () => {
  it.each(SITUACOES_CHURN)('%s mostra só o próprio estado', (situacao) => {
    const { churn } = montar({ situacao })

    expect(churn.querySelector('.resumo-estado')!.textContent).toBe(ROTULO_CHURN[situacao])
    expect(churn.getAttribute('data-churn')).toBe(situacao)
  })

  it('sem_sinal_detectado não vira risco baixo', () => {
    const { churn } = montar({ situacao: 'sem_sinal_detectado' })

    expect(churn.textContent).toContain('Isso não confirma')
    expect(churn.textContent).not.toMatch(/baixo/i)
    expect(churn.textContent).not.toMatch(/0\s?%|\d/)
  })

  it('informacao_insuficiente não vira sem sinal nem ausência de risco confirmada', () => {
    const { churn } = montar({ situacao: 'informacao_insuficiente' })

    expect(churn.querySelector('.resumo-estado')!.textContent).toBe('Informação insuficiente')
    expect(churn.textContent).not.toMatch(/sem sinal|nenhum sinal|baixo/i)
    expect(churn.textContent).toContain('Não é o mesmo que ausência de risco')
  })

  it('nao_aplicavel explica o prospect e não vira risco', () => {
    const { churn } = montar({ vinculo: 'prospect', situacao: 'nao_aplicavel' })

    expect(churn.textContent).toContain('prospect')
    expect(churn.textContent).toContain('ainda não tem contrato a cancelar')
    expect(churn.textContent).not.toMatch(/sinal detectado|indicam risco|baixo/i)
  })

  it('sinal_detectado não promete cancelamento nem mostra trechos', () => {
    const { churn } = montar({ situacao: 'sinal_detectado' })

    expect(churn.textContent).toContain('não é uma previsão')
    expect(churn.querySelector('blockquote, mark, a, button')).toBeNull()
  })
})

describe('estrutura', () => {
  it('h2 para reunião e sinais, h3 para os dois cartões, sem números de risco ou confiança', () => {
    montar({ situacao: 'sinal_detectado', sentimento: 'negativo' })

    expect(screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)).toEqual(['Reunião analisada', 'Sinais da conversa'])
    expect(screen.getAllByRole('heading', { level: 3 }).map((h) => h.textContent)).toEqual(['Sentimento', 'Risco de cancelamento'])
    expect(document.body.textContent).not.toMatch(/\d+\s?%|confiança|pontuação|score/i)
  })

  it('não inclui oportunidades, produtos, concorrentes ou recomendações', () => {
    montar()
    const texto = document.body.textContent!

    expect(texto).not.toMatch(/oportunidade|produto|concorrente|recomenda/i)
  })
})

describe('ação Ver evidência (F05-B)', () => {
  const entrada = { titulo: 'T', empresa: 'E', vinculo: 'cliente' } as const

  it('sem callback não há botão, mesmo com IDs de evidência', () => {
    render(<ResumoResultado entrada={entrada} resposta={{ sentimento: 'negativo', churn: { situacao: 'sinal_detectado', evidencias: ['e1'] } }} />)

    expect(screen.queryAllByRole('button')).toHaveLength(0)
  })

  it('com callback, só o risco detectado com IDs ganha botão e ele entrega ID e origem', () => {
    const chamadas: Array<[string, HTMLElement]> = []
    render(
      <ResumoResultado
        entrada={entrada}
        resposta={{ sentimento: 'negativo', churn: { situacao: 'sinal_detectado', evidencias: ['e7'] } }}
        aoVerEvidencia={(id, origem) => chamadas.push([id, origem])}
      />,
    )
    const botao = screen.getByRole('button', { name: 'Ver evidência: risco de cancelamento' })
    fireEvent.click(botao)

    expect(screen.getAllByRole('button')).toHaveLength(1)
    expect(chamadas).toEqual([['e7', botao]])
  })

  it.each(['sem_sinal_detectado', 'nao_aplicavel', 'informacao_insuficiente'] as const)('%s não ganha botão, mesmo que a resposta traga IDs', (situacao) => {
    render(
      <ResumoResultado
        entrada={entrada}
        resposta={{ sentimento: 'neutro', churn: { situacao, evidencias: ['e1'] } }}
        aoVerEvidencia={() => {}}
      />,
    )

    expect(screen.queryAllByRole('button')).toHaveLength(0)
  })

  it('sinal detectado sem IDs não ganha botão', () => {
    render(
      <ResumoResultado entrada={entrada} resposta={{ sentimento: 'negativo', churn: { situacao: 'sinal_detectado', evidencias: [] } }} aoVerEvidencia={() => {}} />,
    )

    expect(screen.queryAllByRole('button')).toHaveLength(0)
  })
})
