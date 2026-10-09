/**
 * Tipos do contrato C01 (`docs/contratos/analise-texto.md`) para
 * `POST /api/analises/texto`.
 *
 * Seguem os schemas do backend (`backend/app/schemas/`): campos que o backend
 * exige não são opcionais, e as listas da resposta chegam sempre presentes
 * (vazias quando não há itens). Os enums são listas `as const` — em vez de
 * `enum` — porque o projeto usa `erasableSyntaxOnly`.
 *
 * Posições de evidência: `inicio`/`fim` são índices em **pontos de código**
 * Unicode (como `str` em Python), com `fim` exclusivo, relativos ao campo
 * `transcricao` devolvido na resposta. Em JavaScript, `String.prototype.slice`
 * usa unidades UTF-16 e erra a posição depois de um emoji; ver
 * `recortarPorPontosDeCodigo`.
 */

export const VINCULOS = ['cliente', 'prospect', 'nao_informado'] as const
export type Vinculo = (typeof VINCULOS)[number]

export const SENTIMENTOS = ['positivo', 'neutro', 'negativo', 'informacao_insuficiente'] as const
export type Sentimento = (typeof SENTIMENTOS)[number]

export const SITUACOES_CHURN = [
  'sinal_detectado',
  'sem_sinal_detectado',
  'nao_aplicavel',
  'informacao_insuficiente',
] as const
export type ChurnSituacao = (typeof SITUACOES_CHURN)[number]

/** Corpo de `POST /api/analises/texto`. Textos já chegam sem espaços nas pontas. */
export interface AnaliseTextoRequest {
  /** 1 a 200 caracteres. */
  titulo: string
  /** 1 a 200 caracteres. */
  empresa: string
  vinculo: Vinculo
  /** Pelo menos 1 caractere. */
  transcricao: string
}

/** Trecho literal do eco da transcrição que sustenta um sinal. */
export interface Evidencia {
  /** Único dentro da resposta; é o que `churn`, oportunidades e recomendações referenciam. */
  id: string
  trecho: string
  /** Ponto de código em que o trecho começa (0 = início da `transcricao`). */
  inicio: number
  /** Ponto de código em que o trecho termina, exclusivo; sempre maior que `inicio`. */
  fim: number
}

export interface Churn {
  situacao: ChurnSituacao
  /** IDs de `evidencias`; vazio quando `nao_aplicavel`, sem sinal ou informação insuficiente. */
  evidencias: string[]
}

export interface Oportunidade {
  descricao: string
  /** IDs de `evidencias`. */
  evidencias: string[]
}

export interface Recomendacao {
  texto: string
  /** IDs de `evidencias`. */
  evidencias: string[]
}

/** Resposta 200 de `POST /api/analises/texto`. */
export interface AnaliseTextoResponse {
  /** Eco da transcrição enviada; as evidências apontam para este texto. */
  transcricao: string
  sentimento: Sentimento
  churn: Churn
  oportunidades: Oportunidade[]
  /** Menções a produtos, sem duplicar nomes. */
  produtos: string[]
  /** Menções a concorrentes; menção isolada não implica troca. */
  concorrentes: string[]
  evidencias: Evidencia[]
  recomendacoes: Recomendacao[]
  /** Método da análise, por exemplo `regras`. */
  metodo: string
  /** Versão do método; muda com a análise, por isso é `string` e não um valor fixo. */
  versao_analise: string
}

/** Códigos de erro que a API devolve hoje (tabela "Erros HTTP" de C01). */
export const CODIGOS_ERRO = [
  'TITULO_OBRIGATORIO',
  'TITULO_INVALIDO',
  'EMPRESA_OBRIGATORIA',
  'EMPRESA_INVALIDA',
  'TRANSCRICAO_VAZIA',
  'VINCULO_INVALIDO',
  'DADOS_INVALIDOS',
] as const
export type CodigoErroConhecido = (typeof CODIGOS_ERRO)[number]

export interface ErroDetalhe {
  /** Código conhecido; o `(string & {})` mantém a lista no editor e aceita códigos futuros. */
  codigo: CodigoErroConhecido | (string & {})
  mensagem: string
}

/** Envelope de erro de validação (HTTP 422): `{"erro": {"codigo", "mensagem"}}`. */
export interface ErroResposta {
  erro: ErroDetalhe
}

/**
 * Recorta `texto` por índices em pontos de código Unicode (`fim` exclusivo),
 * como a API os define. Não use `texto.slice(inicio, fim)`: depois de um emoji
 * ele desloca a posição em uma unidade para cada ponto fora do plano básico.
 */
export function recortarPorPontosDeCodigo(texto: string, inicio: number, fim: number): string {
  return Array.from(texto).slice(inicio, fim).join('')
}
