import { VINCULOS } from '../types/analise.ts'
import type { AnaliseTextoRequest, Vinculo } from '../types/analise.ts'

/** Valores digitados. `vinculo` é '' até a pessoa escolher uma opção. */
export interface ValoresDoFormulario {
  titulo: string
  empresa: string
  vinculo: Vinculo | ''
  transcricao: string
}

export type CampoDoFormulario = keyof ValoresDoFormulario
export type ErrosDoFormulario = Partial<Record<CampoDoFormulario, string>>

export const CAMPOS: readonly CampoDoFormulario[] = ['titulo', 'empresa', 'vinculo', 'transcricao']

/** Limite de C01 para título e empresa, em pontos de código Unicode (não em unidades UTF-16). */
export const LIMITE_TEXTO_CURTO = 200

export const VALORES_INICIAIS: ValoresDoFormulario = { titulo: '', empresa: '', vinculo: '', transcricao: '' }

const ehVinculo = (valor: string): valor is Vinculo => (VINCULOS as readonly string[]).includes(valor)

/** Mesma contagem do backend: pontos de código depois de remover espaços das pontas. */
export const contarPontosDeCodigo = (valor: string) => Array.from(valor.trim()).length

function validarTextoCurto(valor: string, vazio: string, longo: string) {
  const tamanho = contarPontosDeCodigo(valor)
  if (tamanho === 0) return vazio
  if (tamanho > LIMITE_TEXTO_CURTO) return longo
  return undefined
}

/** Mensagem de erro de um campo ou `undefined` se ele está válido. */
export function validarCampo(campo: CampoDoFormulario, valores: ValoresDoFormulario): string | undefined {
  switch (campo) {
    case 'titulo':
      return validarTextoCurto(valores.titulo, 'Informe o título da reunião.', 'Use até 200 caracteres no título.')
    case 'empresa':
      return validarTextoCurto(valores.empresa, 'Informe a empresa.', 'Use até 200 caracteres no nome da empresa.')
    case 'vinculo':
      return ehVinculo(valores.vinculo) ? undefined : 'Selecione o vínculo com a empresa.'
    case 'transcricao':
      // Sem teto local: a API continua sendo a autoridade para o tamanho da transcrição.
      return valores.transcricao.trim().length === 0 ? 'Cole a transcrição da reunião.' : undefined
  }
}

export function validar(valores: ValoresDoFormulario): ErrosDoFormulario {
  const erros: ErrosDoFormulario = {}
  for (const campo of CAMPOS) {
    const erro = validarCampo(campo, valores)
    if (erro) erros[campo] = erro
  }
  return erros
}

/** Pedido C01 com os três textos aparados. Só deve ser chamado com valores já validados. */
export function montarPedido(valores: ValoresDoFormulario): AnaliseTextoRequest {
  if (!ehVinculo(valores.vinculo)) throw new Error('vínculo não selecionado')
  return {
    titulo: valores.titulo.trim(),
    empresa: valores.empresa.trim(),
    vinculo: valores.vinculo,
    transcricao: valores.transcricao.trim(),
  }
}
