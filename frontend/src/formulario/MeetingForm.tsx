import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent, FormEvent, MouseEvent } from 'react'
import type { AnaliseTextoRequest } from '../types/analise.ts'
import { CAMPOS, VALORES_INICIAIS, montarPedido, validar, validarCampo } from './validacao.ts'
import type { CampoDoFormulario, ErrosDoFormulario, ValoresDoFormulario } from './validacao.ts'

interface MeetingFormProps {
  /** Chamado uma vez por envio válido, com os textos já aparados. */
  onSubmit: (pedido: AnaliseTextoRequest) => void
  /** Chamado a cada edição de campo, para a página retirar avisos que já não valem para o texto digitado. */
  onEdit?: () => void
  /** Valores com que o formulário começa (ao voltar para editar); sem eles, começa vazio. */
  valoresIniciais?: ValoresDoFormulario
  /** Recebe todos os valores a cada edição, para a página guardá-los em memória. */
  onValores?: (valores: ValoresDoFormulario) => void
  /** Envio em andamento: o botão fica indisponível sem perder o foco, e os campos não mudam até a resposta. */
  enviando?: boolean
}

const ROTULOS: Record<CampoDoFormulario, string> = {
  titulo: 'Título da reunião',
  empresa: 'Empresa',
  vinculo: 'Vínculo com a empresa',
  transcricao: 'Transcrição da reunião',
}

const AJUDAS: Record<CampoDoFormulario, string> = {
  titulo: 'Um nome para reconhecer a reunião. Até 200 caracteres.',
  empresa: 'Empresa com quem a conversa aconteceu. Até 200 caracteres.',
  vinculo: 'Escolha “Não informado” se não souber a relação com a empresa.',
  transcricao: 'Cole o texto completo da conversa.',
}

const idDoCampo = (campo: CampoDoFormulario) => `campo-${campo}`

export function MeetingForm({ onSubmit, onEdit, valoresIniciais = VALORES_INICIAIS, onValores, enviando = false }: MeetingFormProps) {
  const [valores, setValores] = useState<ValoresDoFormulario>(valoresIniciais)
  const [erros, setErros] = useState<ErrosDoFormulario>({})
  // Conta envios inválidos: cada um leva o foco ao resumo, mesmo que o conteúdo seja igual.
  const [falhas, setFalhas] = useState(0)
  const resumo = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (falhas > 0) resumo.current?.focus()
  }, [falhas])

  const camposComErro = CAMPOS.filter((campo) => erros[campo])

  function editar(campo: CampoDoFormulario) {
    return (evento: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      // Durante o envio os campos ficam como foram enviados: o resultado volta para esse pedido, não para outro texto.
      if (enviando) return
      const proximos = { ...valores, [campo]: evento.target.value } as ValoresDoFormulario
      setValores(proximos)
      onValores?.(proximos)
      // Depois de um envio inválido, só o erro do campo editado é recalculado.
      if (falhas > 0) {
        setErros((atuais) => {
          const demais = { ...atuais }
          delete demais[campo]
          const novo = validarCampo(campo, proximos)
          return novo ? { ...demais, [campo]: novo } : demais
        })
      }
      onEdit?.()
    }
  }

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (enviando) return
    const encontrados = validar(valores)
    setErros(encontrados)
    if (Object.keys(encontrados).length > 0) {
      setFalhas((n) => n + 1)
      return
    }
    onSubmit(montarPedido(valores))
  }

  function irParaCampo(campo: CampoDoFormulario) {
    return (evento: MouseEvent<HTMLAnchorElement>) => {
      evento.preventDefault()
      document.getElementById(idDoCampo(campo))?.focus()
    }
  }

  function propriedades(campo: CampoDoFormulario) {
    const erro = erros[campo]
    return {
      id: idDoCampo(campo),
      name: campo,
      value: valores[campo],
      onChange: editar(campo),
      'aria-invalid': erro ? (true as const) : undefined,
      'aria-describedby': erro ? `ajuda-${campo} erro-${campo}` : `ajuda-${campo}`,
    }
  }

  function mensagens(campo: CampoDoFormulario) {
    return (
      <>
        <p className="field-hint" id={`ajuda-${campo}`}>{AJUDAS[campo]}</p>
        {erros[campo] && <p className="field-error" id={`erro-${campo}`}>{erros[campo]}</p>}
      </>
    )
  }

  return (
    <form className="panel meeting-form" onSubmit={enviar} noValidate aria-labelledby="form-titulo" aria-busy={enviando || undefined}>
      <h2 id="form-titulo">Dados da reunião</h2>

      {camposComErro.length > 0 && (
        <div className="error-summary" ref={resumo} tabIndex={-1} role="group" aria-labelledby="resumo-titulo">
          <h3 id="resumo-titulo">Confira os dados</h3>
          <ul>
            {camposComErro.map((campo) => (
              <li key={campo}>
                <a href={`#${idDoCampo(campo)}`} onClick={irParaCampo(campo)}>{erros[campo]}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className={`field${erros.titulo ? ' has-error' : ''}`}>
        <label htmlFor={idDoCampo('titulo')}>{ROTULOS.titulo}</label>
        {mensagens('titulo')}
        <input type="text" autoComplete="off" {...propriedades('titulo')} />
      </div>

      <div className={`field${erros.empresa ? ' has-error' : ''}`}>
        <label htmlFor={idDoCampo('empresa')}>{ROTULOS.empresa}</label>
        {mensagens('empresa')}
        <input type="text" autoComplete="organization" {...propriedades('empresa')} />
      </div>

      <div className={`field${erros.vinculo ? ' has-error' : ''}`}>
        <label htmlFor={idDoCampo('vinculo')}>{ROTULOS.vinculo}</label>
        {mensagens('vinculo')}
        <select {...propriedades('vinculo')}>
          <option value="">Selecione o vínculo</option>
          <option value="cliente">Cliente</option>
          <option value="prospect">Prospect</option>
          <option value="nao_informado">Não informado</option>
        </select>
      </div>

      <div className={`field${erros.transcricao ? ' has-error' : ''}`}>
        <label htmlFor={idDoCampo('transcricao')}>{ROTULOS.transcricao}</label>
        {mensagens('transcricao')}
        <textarea rows={10} {...propriedades('transcricao')} />
      </div>

      {/* aria-disabled, não disabled: o botão continua focável e o foco não se perde ao enviar com Enter. */}
      <button className="action-button" type="submit" aria-disabled={enviando || undefined}>
        {enviando ? 'Enviando…' : 'Analisar reunião'}
      </button>
    </form>
  )
}
