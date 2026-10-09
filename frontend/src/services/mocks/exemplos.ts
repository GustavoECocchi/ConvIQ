/**
 * EXEMPLOS ILUSTRATIVOS do contrato C01 — **não são resultado de uma análise
 * real**. Servem de fixture para tipos, testes e para o material didático do
 * guia de leitura; nunca devem aparecer na interface como resultado de uma
 * transcrição que o usuário enviou.
 *
 * Os valores foram conferidos com a saída real da rota atual
 * (`compor_analise_texto`, `versao_analise` "0.5", sem a união de evidências
 * de B19 ainda não integrada) e não copiam cegamente os exemplos históricos do
 * contrato: por exemplo, para o prospect abaixo a rota não devolve oportunidade.
 */
import type { AnaliseTextoRequest, AnaliseTextoResponse } from '../../types/analise.ts'

export const ROTULO_EXEMPLO = 'EXEMPLO ILUSTRATIVO' as const

export interface ExemploIlustrativo {
  /** Sempre `EXEMPLO ILUSTRATIVO`: a interface deve exibir este rótulo junto do exemplo. */
  rotulo: typeof ROTULO_EXEMPLO
  /** Identificador estável para escolher o exemplo. */
  chave: string
  descricao: string
  entrada: AnaliseTextoRequest
  resposta: AnaliseTextoResponse
}

const cliente = 'Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.'
const emoji = '😀 Estamos insatisfeitos com o suporte.'

export const exemplos: readonly ExemploIlustrativo[] = [
  {
    rotulo: ROTULO_EXEMPLO,
    chave: 'cliente-risco-e-oportunidade',
    descricao: 'Cliente com risco de cancelamento e oportunidade na mesma reunião.',
    entrada: {
      titulo: 'Acompanhamento comercial',
      empresa: 'Empresa Exemplo',
      vinculo: 'cliente',
      transcricao: cliente,
    },
    resposta: {
      transcricao: cliente,
      sentimento: 'negativo',
      churn: { situacao: 'sinal_detectado', evidencias: ['e2'] },
      oportunidades: [
        { descricao: 'Interesse comercial sinalizado por "Queremos conhecer o Fluig".', evidencias: ['e3'] },
      ],
      produtos: ['Fluig'],
      concorrentes: [],
      evidencias: [
        { id: 'e1', trecho: 'insatisfeitos', inicio: 8, fim: 21 },
        { id: 'e2', trecho: 'insatisfeitos com o suporte', inicio: 8, fim: 35 },
        { id: 'e3', trecho: 'Queremos conhecer o Fluig', inicio: 37, fim: 62 },
      ],
      recomendacoes: [
        { texto: 'Investigar o risco de cancelamento identificado na conversa.', evidencias: ['e2'] },
        { texto: 'Dar seguimento ao interesse comercial identificado nesta oportunidade.', evidencias: ['e3'] },
      ],
      metodo: 'regras',
      versao_analise: '0.5',
    },
  },
  {
    rotulo: ROTULO_EXEMPLO,
    chave: 'prospect-churn-nao-aplicavel',
    descricao: 'Prospect: não há contrato a cancelar, então o risco não se aplica; sem sinais, as listas ficam vazias.',
    entrada: {
      titulo: 'Primeira reunião comercial',
      empresa: 'Prospect Exemplo LTDA',
      vinculo: 'prospect',
      transcricao: 'Vocês trabalham com integração via API? Hoje usamos uma planilha manual.',
    },
    resposta: {
      transcricao: 'Vocês trabalham com integração via API? Hoje usamos uma planilha manual.',
      sentimento: 'informacao_insuficiente',
      churn: { situacao: 'nao_aplicavel', evidencias: [] },
      oportunidades: [],
      produtos: [],
      concorrentes: [],
      evidencias: [],
      recomendacoes: [],
      metodo: 'regras',
      versao_analise: '0.5',
    },
  },
  {
    rotulo: ROTULO_EXEMPLO,
    chave: 'informacao-insuficiente',
    descricao: 'Sem conteúdo avaliável: informação insuficiente não é o mesmo que risco baixo confirmado.',
    entrada: {
      titulo: 'Reunião de alinhamento',
      empresa: 'Empresa Exemplo',
      vinculo: 'cliente',
      transcricao: 'Bom dia a todos. Vamos seguir a pauta de hoje.',
    },
    resposta: {
      transcricao: 'Bom dia a todos. Vamos seguir a pauta de hoje.',
      sentimento: 'informacao_insuficiente',
      churn: { situacao: 'informacao_insuficiente', evidencias: [] },
      oportunidades: [],
      produtos: [],
      concorrentes: [],
      evidencias: [],
      recomendacoes: [],
      metodo: 'regras',
      versao_analise: '0.5',
    },
  },
  {
    rotulo: ROTULO_EXEMPLO,
    chave: 'emoji-antes-do-sinal',
    descricao:
      'Emoji antes do sinal: os índices contam pontos de código, então o recorte por UTF-16 (`slice`) erra por uma posição.',
    entrada: {
      titulo: 'Retorno do cliente',
      empresa: 'Empresa Exemplo',
      vinculo: 'cliente',
      transcricao: emoji,
    },
    resposta: {
      transcricao: emoji,
      sentimento: 'negativo',
      churn: { situacao: 'sinal_detectado', evidencias: ['e2'] },
      oportunidades: [],
      produtos: [],
      concorrentes: [],
      evidencias: [
        { id: 'e1', trecho: 'insatisfeitos', inicio: 10, fim: 23 },
        { id: 'e2', trecho: 'insatisfeitos com o suporte', inicio: 10, fim: 37 },
      ],
      recomendacoes: [{ texto: 'Investigar o risco de cancelamento identificado na conversa.', evidencias: ['e2'] }],
      metodo: 'regras',
      versao_analise: '0.5',
    },
  },
]
