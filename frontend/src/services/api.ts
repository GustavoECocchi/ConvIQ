/**
 * Cliente HTTP de `POST /analises/texto` (contrato C01, F02-B).
 *
 * Só envia a requisição e interpreta a resposta: não recalcula sinais, não
 * guarda estado entre chamadas e não monta UI. Toda falha vira um
 * `ErroDaApi` com uma `falha` discriminada por `tipo`, para a interface decidir
 * o que mostrar sem comparar mensagens:
 *
 * - `validacao`: HTTP 422 com o envelope `{"erro": {"codigo", "mensagem"}}` de C01;
 * - `http`: qualquer outro status que não seja 200 (inclui 4xx fora de 422 e 5xx);
 * - `rede`: o `fetch` rejeitou (sem conexão, servidor fora do ar, CORS) ou a
 *   conexão caiu durante a leitura do corpo;
 * - `cancelado`: o `AbortSignal` recebido foi acionado — não é falha de rede;
 * - `resposta_invalida`: status 200 ou 422 com corpo completo que não segue o
 *   schema de C01 (ver `ehAnaliseTextoResponse`).
 */
import type { AnaliseTextoRequest, AnaliseTextoResponse, ErroDetalhe } from '../types/analise.ts'
import { SENTIMENTOS, SITUACOES_CHURN } from '../types/analise.ts'

export const CAMINHO_ANALISE_TEXTO = '/analises/texto'
/** Base local padrão: a API sobe em `localhost:8000` com o prefixo `/api` (`backend/README.md`). */
export const BASE_API_PADRAO = 'http://localhost:8000/api'

export type FalhaApi =
  | { tipo: 'validacao'; status: 422; erro: ErroDetalhe }
  | { tipo: 'http'; status: number }
  | { tipo: 'rede' }
  | { tipo: 'cancelado' }
  | { tipo: 'resposta_invalida'; status: number }

/** Mensagem curta, em português, que pode ser mostrada ao usuário. Não carrega corpo nem detalhes do servidor. */
export function mensagemDaFalha(falha: FalhaApi): string {
  switch (falha.tipo) {
    case 'validacao':
      return falha.erro.mensagem
    case 'http':
      return `O servidor não conseguiu concluir a análise (erro ${falha.status}). Tente novamente em instantes.`
    case 'rede':
      return 'Não foi possível falar com o servidor. Confira sua conexão e se a API está em execução.'
    case 'cancelado':
      return 'O envio foi cancelado.'
    case 'resposta_invalida':
      return 'O servidor respondeu em um formato inesperado. Tente novamente.'
  }
}

export class ErroDaApi extends Error {
  readonly falha: FalhaApi

  constructor(falha: FalhaApi) {
    super(mensagemDaFalha(falha))
    this.name = 'ErroDaApi'
    this.falha = falha
  }
}

export type FetchLike = (url: string, init: RequestInit) => Promise<Response>

export interface OpcoesCliente {
  /** Base da API com o prefixo (`http://localhost:8000/api`); sem valor, usa `VITE_API_BASE_URL` e depois o padrão. */
  baseUrl?: string
  /** Substitui o `fetch` global (testes). */
  fetchImpl?: FetchLike
}

/** Escolhe a base: valor informado, senão `VITE_API_BASE_URL`, senão o padrão local. Vazio conta como ausente. */
export function resolverBaseApi(valor?: string): string {
  const candidato = (valor ?? import.meta.env.VITE_API_BASE_URL ?? '').trim()
  return candidato === '' ? BASE_API_PADRAO : candidato
}

/** Junta base e caminho com uma única barra, sem duplicar o prefixo nem a barra final da base. */
export function juntarUrl(base: string, caminho: string): string {
  return `${base.replace(/\/+$/, '')}/${caminho.replace(/^\/+/, '')}`
}

const ehObjeto = (valor: unknown): valor is Record<string, unknown> =>
  typeof valor === 'object' && valor !== null && !Array.isArray(valor)

const ehListaDe = <T>(valor: unknown, teste: (item: unknown) => item is T): valor is T[] =>
  Array.isArray(valor) && valor.every(teste)

const ehTexto = (valor: unknown): valor is string => typeof valor === 'string'
/** Texto com pelo menos um caractere, como `Field(min_length=1)` no backend. */
const ehTextoPreenchido = (valor: unknown): valor is string => ehTexto(valor) && valor !== ''
const ehInteiro = (valor: unknown): valor is number => Number.isInteger(valor)

/** `Evidencia` de C01: `id` e `trecho` preenchidos, `inicio >= 0` e `fim > inicio`. */
function ehEvidencia(valor: unknown): boolean {
  return (
    ehObjeto(valor) &&
    ehTextoPreenchido(valor.id) &&
    ehTextoPreenchido(valor.trecho) &&
    ehInteiro(valor.inicio) &&
    ehInteiro(valor.fim) &&
    valor.inicio >= 0 &&
    valor.fim > valor.inicio
  )
}

/** `Oportunidade`/`Recomendacao`: texto preenchido e lista de IDs de evidência. */
function ehComEvidencias(valor: unknown, campoTexto: string): boolean {
  return ehObjeto(valor) && ehTextoPreenchido(valor[campoTexto]) && ehListaDe(valor.evidencias, ehTexto)
}

/**
 * Confere a resposta contra o **schema** de C01 (`backend/app/schemas/analise.py`),
 * o que o `fetch` não garante: campos, tipos, enums, textos obrigatórios
 * preenchidos (`transcricao`, `metodo`, `versao_analise`, `descricao`, `texto`,
 * `id`, `trecho`), limites de `Evidencia` (`inicio >= 0`, `fim > inicio`), IDs de
 * evidência únicos e toda referência de `churn`, oportunidade e recomendação
 * apontando para uma evidência existente (revisão F02-B-R01).
 *
 * Fica de fora, como no próprio schema: o recorte literal
 * (`transcricao[inicio:fim] == trecho`), `fim` dentro do texto e as regras de
 * produto (prospect sem churn etc.). O mesmo ID pode ser citado por listas
 * diferentes (B19). A análise não é refeita.
 */
export function ehAnaliseTextoResponse(valor: unknown): valor is AnaliseTextoResponse {
  if (!ehObjeto(valor)) return false
  const { churn, oportunidades, recomendacoes, evidencias } = valor
  const formaValida =
    ehTextoPreenchido(valor.transcricao) &&
    (SENTIMENTOS as readonly unknown[]).includes(valor.sentimento) &&
    ehObjeto(churn) &&
    (SITUACOES_CHURN as readonly unknown[]).includes(churn.situacao) &&
    ehListaDe(churn.evidencias, ehTexto) &&
    Array.isArray(oportunidades) &&
    oportunidades.every((item) => ehComEvidencias(item, 'descricao')) &&
    ehListaDe(valor.produtos, ehTexto) &&
    ehListaDe(valor.concorrentes, ehTexto) &&
    Array.isArray(evidencias) &&
    evidencias.every(ehEvidencia) &&
    Array.isArray(recomendacoes) &&
    recomendacoes.every((item) => ehComEvidencias(item, 'texto')) &&
    ehTextoPreenchido(valor.metodo) &&
    ehTextoPreenchido(valor.versao_analise)
  if (!formaValida) return false

  const resposta = valor as unknown as AnaliseTextoResponse
  const ids = resposta.evidencias.map((evidencia) => evidencia.id)
  const existentes = new Set(ids)
  if (existentes.size !== ids.length) return false
  const referencias = [
    ...resposta.churn.evidencias,
    ...resposta.oportunidades.flatMap((oportunidade) => oportunidade.evidencias),
    ...resposta.recomendacoes.flatMap((recomendacao) => recomendacao.evidencias),
  ]
  return referencias.every((id) => existentes.has(id))
}

/** Envelope `{"erro": {"codigo", "mensagem"}}` com os dois textos preenchidos. */
function lerErroDetalhe(valor: unknown): ErroDetalhe | null {
  if (!ehObjeto(valor) || !ehObjeto(valor.erro)) return null
  const { codigo, mensagem } = valor.erro
  return ehTexto(codigo) && codigo !== '' && ehTexto(mensagem) && mensagem !== '' ? { codigo, mensagem } : null
}

const foiCancelamento = (erro: unknown, sinal?: AbortSignal): boolean =>
  sinal?.aborted === true || (erro instanceof Error && erro.name === 'AbortError')

/**
 * Lê o corpo como JSON. Devolve `undefined` se o corpo chegou inteiro mas não é
 * JSON (`SyntaxError`, inclusive corpo vazio). Se a leitura parar no meio, o
 * motivo decide (revisão F02-B-R02): sinal acionado ou `AbortError` → `cancelado`;
 * qualquer outra falha do stream (na especificação Fetch, `TypeError`: conexão
 * perdida durante o corpo) → `rede`, e não "formato inesperado".
 */
async function lerJson(resposta: Response, sinal?: AbortSignal): Promise<unknown> {
  try {
    return await resposta.json()
  } catch (erro) {
    if (foiCancelamento(erro, sinal)) throw new ErroDaApi({ tipo: 'cancelado' })
    if (erro instanceof SyntaxError) return undefined
    throw new ErroDaApi({ tipo: 'rede' })
  }
}

export function criarClienteApi(opcoes: OpcoesCliente = {}) {
  const buscar: FetchLike = opcoes.fetchImpl ?? ((url, init) => globalThis.fetch(url, init))

  /**
   * Envia a transcrição e devolve a resposta de C01 exatamente como veio.
   * Rejeita sempre com `ErroDaApi`. O `signal` é repassado ao `fetch`.
   */
  async function analisarTexto(
    pedido: AnaliseTextoRequest,
    { signal }: { signal?: AbortSignal } = {},
  ): Promise<AnaliseTextoResponse> {
    const url = juntarUrl(resolverBaseApi(opcoes.baseUrl), CAMINHO_ANALISE_TEXTO)

    let resposta: Response
    try {
      resposta = await buscar(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(pedido),
        signal,
      })
    } catch (erro) {
      throw new ErroDaApi({ tipo: foiCancelamento(erro, signal) ? 'cancelado' : 'rede' })
    }

    if (resposta.status === 422) {
      const erro = lerErroDetalhe(await lerJson(resposta, signal))
      if (erro === null) throw new ErroDaApi({ tipo: 'resposta_invalida', status: 422 })
      throw new ErroDaApi({ tipo: 'validacao', status: 422, erro })
    }

    if (resposta.status !== 200) {
      throw new ErroDaApi({ tipo: 'http', status: resposta.status })
    }

    const corpo = await lerJson(resposta, signal)
    if (!ehAnaliseTextoResponse(corpo)) {
      throw new ErroDaApi({ tipo: 'resposta_invalida', status: 200 })
    }
    return corpo
  }

  return { analisarTexto }
}

/** Cliente com a configuração do ambiente (`VITE_API_BASE_URL`) e o `fetch` global. */
export const analisarTexto: ReturnType<typeof criarClienteApi>['analisarTexto'] = (pedido, opcoes) =>
  criarClienteApi().analisarTexto(pedido, opcoes)
