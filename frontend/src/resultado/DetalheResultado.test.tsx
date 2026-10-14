// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { exemplos } from '../services/mocks/exemplos.ts'
import type { DetalheResultadoProps } from './DetalheResultado.tsx'
import { DetalheResultado } from './DetalheResultado.tsx'

afterEach(cleanup)

type Resposta = DetalheResultadoProps['resposta']

const VAZIA: Resposta = {
  oportunidades: [],
  produtos: [],
  concorrentes: [],
  recomendacoes: [],
  metodo: 'regras',
  versao_analise: '0.6',
}

function montar(parcial: Partial<Resposta> = {}) {
  render(<DetalheResultado resposta={{ ...VAZIA, ...parcial }} />)
  const secao = (nome: string) => screen.getByRole('region', { name: nome })
  return {
    oportunidades: secao('Oportunidades'),
    mencoes: secao('Menções na conversa'),
    recomendacoes: secao('Recomendações'),
  }
}

const itens = (elemento: HTMLElement) => within(elemento).queryAllByRole('listitem').map((li) => li.textContent)

/** Bloco que segue o `h3` informado dentro de "Menções na conversa" (lista ou mensagem de vazio). */
function blocoDaMencao(mencoes: HTMLElement, nome: 'Produtos' | 'Concorrentes') {
  return within(mencoes).getByRole('heading', { level: 3, name: nome }).nextElementSibling as HTMLElement
}

describe('listas preenchidas', () => {
  it('mostra oportunidades, produtos, concorrentes e recomendações como chegaram, na mesma ordem', () => {
    const { oportunidades, mencoes, recomendacoes } = montar({
      oportunidades: [
        { descricao: 'Interesse comercial sinalizado por "Queremos conhecer o Fluig".', evidencias: ['e3'] },
        { descricao: 'Interesse comercial sinalizado por "avaliar o Protheus".', evidencias: ['e4'] },
      ],
      produtos: ['Fluig', 'Protheus'],
      concorrentes: ['SAP', 'Senior'],
      recomendacoes: [
        { texto: 'Investigar o risco de cancelamento identificado na conversa.', evidencias: ['e2'] },
        { texto: 'Dar seguimento ao interesse comercial identificado nesta oportunidade.', evidencias: ['e3'] },
      ],
    })

    expect(itens(oportunidades)).toEqual([
      'Interesse comercial sinalizado por "Queremos conhecer o Fluig".',
      'Interesse comercial sinalizado por "avaliar o Protheus".',
    ])
    expect(itens(blocoDaMencao(mencoes, 'Produtos'))).toEqual(['Fluig', 'Protheus'])
    expect(itens(blocoDaMencao(mencoes, 'Concorrentes'))).toEqual(['SAP', 'Senior'])
    expect(itens(recomendacoes)).toEqual([
      'Investigar o risco de cancelamento identificado na conversa.',
      'Dar seguimento ao interesse comercial identificado nesta oportunidade.',
    ])
  })

  it('não deduplica nem reescreve recomendações repetidas: a interface só apresenta', () => {
    const repetida = 'Dar seguimento ao interesse comercial identificado nesta oportunidade.'
    const { recomendacoes } = montar({
      recomendacoes: [
        { texto: repetida, evidencias: ['e1'] },
        { texto: repetida, evidencias: ['e2'] },
      ],
    })

    expect(itens(recomendacoes)).toEqual([repetida, repetida])
  })

  it('mostra método e versão recebidos, sem valor fixo', () => {
    montar({ metodo: 'regras', versao_analise: '9.1-teste' })
    const metodo = document.querySelector('.detalhe-metodo')!.textContent

    expect(metodo).toContain('regras')
    expect(metodo).toContain('9.1-teste')
  })
})

describe('listas vazias honestas', () => {
  it('cada lista vazia tem mensagem própria, sem item fantasma nem contagem zero', () => {
    const { oportunidades, mencoes, recomendacoes } = montar()

    expect(itens(oportunidades)).toEqual([])
    expect(itens(mencoes)).toEqual([])
    expect(itens(recomendacoes)).toEqual([])
    expect(oportunidades.textContent).toContain('Nenhuma oportunidade identificada no texto')
    expect(blocoDaMencao(mencoes, 'Produtos').textContent).toBe('Nenhum produto da lista conhecida foi citado.')
    expect(blocoDaMencao(mencoes, 'Concorrentes').textContent).toBe('Nenhum concorrente da lista conhecida foi citado.')
    expect(recomendacoes.textContent).toContain('Nenhuma recomendação')
    for (const secao of [oportunidades, mencoes, recomendacoes]) {
      expect(secao.textContent).not.toMatch(/\d/)
    }
  })

  it('oportunidade vazia não afirma que não há interesse', () => {
    const { oportunidades } = montar()

    expect(oportunidades.textContent).toContain('isso não quer dizer que não haja interesse')
  })

  it('recomendação vazia explica que nada é sugerido sem risco ou oportunidade', () => {
    const { recomendacoes } = montar()

    expect(recomendacoes.textContent).toContain('quando encontra um risco ou uma oportunidade')
  })

  it('uma lista vazia não esvazia as vizinhas', () => {
    const { oportunidades, mencoes, recomendacoes } = montar({ concorrentes: ['Oracle'] })

    expect(itens(blocoDaMencao(mencoes, 'Concorrentes'))).toEqual(['Oracle'])
    expect(blocoDaMencao(mencoes, 'Produtos').textContent).toContain('Nenhum produto')
    expect(oportunidades.textContent).toContain('Nenhuma oportunidade')
    expect(recomendacoes.textContent).toContain('Nenhuma recomendação')
  })
})

describe('contraprovas de linguagem', () => {
  it('produto citado sem intenção não vira oportunidade', () => {
    const { oportunidades, mencoes } = montar({ produtos: ['Fluig'] })

    expect(itens(blocoDaMencao(mencoes, 'Produtos'))).toEqual(['Fluig'])
    expect(oportunidades.textContent).not.toContain('Fluig')
    expect(oportunidades.textContent).toContain('Nenhuma oportunidade')
    expect(mencoes.textContent).toContain('Citar um produto não é o mesmo que querer contratá-lo')
  })

  it('concorrente citado não vira risco nem troca', () => {
    const { mencoes } = montar({ concorrentes: ['SAP'] })

    expect(mencoes.textContent).toContain('citar um concorrente não indica, sozinho, intenção de troca')
    expect(document.body.textContent).not.toMatch(/risco de cancelamento|sinal detectado|vai trocar/i)
  })

  it('não mostra IDs de evidência nem ações de evidência antes de F05', () => {
    montar({
      oportunidades: [{ descricao: 'Interesse comercial sinalizado por "Queremos o Fluig".', evidencias: ['e1', 'e2'] }],
      recomendacoes: [{ texto: 'Dar seguimento ao interesse comercial identificado nesta oportunidade.', evidencias: ['e1'] }],
    })

    expect(document.body.textContent).not.toMatch(/\be\d+\b/)
    expect(document.querySelector('a, button, blockquote, mark')).toBeNull()
  })

  it('não mostra pontuação, porcentagem nem confiança', () => {
    montar({
      oportunidades: [{ descricao: 'Interesse comercial sinalizado por "contratar o RM".', evidencias: ['e1'] }],
      produtos: ['RM'],
      recomendacoes: [{ texto: 'Dar seguimento ao interesse comercial identificado nesta oportunidade.', evidencias: ['e1'] }],
    })

    expect(document.body.textContent).not.toMatch(/\d+\s?%|confiança|pontuação|score|probabilidade/i)
  })
})

describe('estrutura', () => {
  it('h2 por bloco e h3 para produtos e concorrentes, na ordem de leitura', () => {
    montar()

    expect(screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)).toEqual([
      'Oportunidades',
      'Menções na conversa',
      'Recomendações',
    ])
    expect(screen.getAllByRole('heading', { level: 3 }).map((h) => h.textContent)).toEqual(['Produtos', 'Concorrentes'])
  })

  it('não repete identificação, sentimento nem churn do resumo', () => {
    montar()
    const texto = document.body.textContent!

    expect(texto).not.toMatch(/Reunião analisada|Sentimento|Vínculo|Sinal detectado|Sem sinal detectado/)
  })
})

describe.each(exemplos.map((exemplo) => [exemplo.chave, exemplo.resposta] as const))('fixture %s', (_chave, resposta) => {
  it('cada lista mostra o mesmo número de itens que a resposta', () => {
    const { oportunidades, mencoes, recomendacoes } = montar(resposta)

    expect(itens(oportunidades)).toEqual(resposta.oportunidades.map((o) => o.descricao))
    expect(itens(blocoDaMencao(mencoes, 'Produtos'))).toEqual(resposta.produtos)
    expect(itens(blocoDaMencao(mencoes, 'Concorrentes'))).toEqual(resposta.concorrentes)
    expect(itens(recomendacoes)).toEqual(resposta.recomendacoes.map((r) => r.texto))
  })
})

describe('ação Ver evidência (F05-B)', () => {
  const comSinais: Resposta = {
    ...VAZIA,
    oportunidades: [
      { descricao: 'Oportunidade A', evidencias: ['e3'] },
      { descricao: 'Oportunidade sem ID', evidencias: [] },
    ],
    recomendacoes: [{ texto: 'Recomendação com dois IDs', evidencias: ['e1', 'e2'] }],
  }

  it('sem callback não há botão e a nota mantém o texto de F05-A', () => {
    render(<DetalheResultado resposta={comSinais} />)

    expect(screen.queryAllByRole('button')).toHaveLength(0)
    expect(document.body.textContent).toContain('ainda sem indicar qual sugestão cada um sustenta')
  })

  it('com callback: um botão por ID citado, nenhum para item sem ID, e a nota passa a apontar para a ação', () => {
    const pedidos: string[] = []
    render(<DetalheResultado resposta={comSinais} aoVerEvidencia={(id) => pedidos.push(id)} />)
    const botoes = screen.getAllByRole('button')

    expect(botoes.map((b) => b.getAttribute('aria-label'))).toEqual([
      'Ver evidência: oportunidade 1',
      'Ver evidência 1: recomendação 1',
      'Ver evidência 2: recomendação 1',
    ])
    botoes.forEach((b) => fireEvent.click(b))
    expect(pedidos).toEqual(['e3', 'e1', 'e2'])
    expect(document.body.textContent).toContain('Use Ver evidência')
    expect(document.body.textContent).not.toContain('ainda sem indicar')
  })

  it('o botão fica dentro do item, depois do texto, e o texto do sinal continua intacto', () => {
    render(<DetalheResultado resposta={comSinais} aoVerEvidencia={() => {}} />)
    const item = screen.getByText('Oportunidade A').closest('li')!

    expect(item.firstChild!.textContent).toBe('Oportunidade A')
    expect(item.querySelector('button')).not.toBeNull()
  })

  it('item sem ID não deixa contêiner de ações vazio (ocuparia espaço sem ter ação)', () => {
    render(<DetalheResultado resposta={{ ...VAZIA, oportunidades: [{ descricao: 'Sem ID', evidencias: [] }] }} aoVerEvidencia={() => {}} />)

    expect(document.querySelector('.evidencia-acoes')).toBeNull()
  })

  it('listas vazias continuam sem botões', () => {
    render(<DetalheResultado resposta={VAZIA} aoVerEvidencia={() => {}} />)

    expect(screen.queryAllByRole('button')).toHaveLength(0)
  })
})
