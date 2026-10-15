import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAnaliseEmMemoria } from '../analise/useAnaliseEmMemoria.ts'
import { PAGINAS } from '../destinos.ts'
import { MeetingForm } from '../formulario/MeetingForm.tsx'
import { ErroDaApi, analisarTexto, mensagemDaFalha } from '../services/api.ts'
import type { AnaliseTextoRequest } from '../types/analise.ts'

type Envio = { situacao: 'inicial' | 'enviando' } | { situacao: 'erro'; mensagem: string }

/**
 * Envio real de uma reunião (F06-A): `POST /api/analises/texto` pelo cliente de F02-B. Estados: inicial,
 * enviando, erro e sucesso (que leva ao resultado). Um só envio por vez; o que foi digitado fica em
 * memória e volta se houver erro, ao editar ou ao retornar a esta página. Se a página sair de cena ou
 * o pedido mudar, a resposta pendente é cancelada e, se chegar mesmo assim, ignorada.
 */
export function NovaAnalise() {
  const { receber, esquecerAnalise, lerRascunho, guardarRascunho } = useAnaliseEmMemoria()
  const navegar = useNavigate()
  const [envio, setEnvio] = useState<Envio>({ situacao: 'inicial' })
  // O controlador do pedido em andamento; ausente quando nada está sendo enviado.
  const pendente = useRef<AbortController | null>(null)

  // Ao abrir o formulário a análise anterior sai da memória: nem "Editar dados" nem um erro a ressuscitam depois.
  useEffect(() => {
    esquecerAnalise()
  }, [esquecerAnalise])

  useEffect(
    () => () => {
      pendente.current?.abort()
      pendente.current = null
    },
    [],
  )

  async function enviar(pedido: AnaliseTextoRequest) {
    if (pendente.current) return
    const controlador = new AbortController()
    pendente.current = controlador
    setEnvio({ situacao: 'enviando' })
    // Cancelar só acontece aqui, ao sair da página; então um pedido que não é mais o atual é sempre ignorado, inclusive o `cancelado`.
    const atual = () => pendente.current === controlador && !controlador.signal.aborted

    try {
      const resposta = await analisarTexto(pedido, { signal: controlador.signal })
      if (!atual()) return
      pendente.current = null
      receber(pedido, resposta)
      void navegar(PAGINAS.resultado.caminho)
    } catch (erro) {
      if (!atual()) return
      pendente.current = null
      const falha = erro instanceof ErroDaApi ? erro.falha : ({ tipo: 'rede' } as const)
      setEnvio({ situacao: 'erro', mensagem: mensagemDaFalha(falha) })
    }
  }

  const enviando = envio.situacao === 'enviando'

  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">ANÁLISE POR TEXTO</p>
          <h1 id="page-title" tabIndex={-1}>Nova análise por texto</h1>
          <p>Cole a transcrição da reunião e envie para ver os sinais, cada um ligado ao trecho que o sustenta.</p>
        </div>
        <Link className="intro-tag guide-back" to={PAGINAS.visaoGeral.caminho}>← Voltar à visão geral</Link>
      </section>

      <div className="form-layout">
        <div className="form-main">
          <MeetingForm
            onSubmit={(pedido) => void enviar(pedido)}
            onEdit={() => setEnvio((atual) => (atual.situacao === 'erro' ? { situacao: 'inicial' } : atual))}
            valoresIniciais={lerRascunho()}
            onValores={guardarRascunho}
            enviando={enviando}
          />
          <div className="form-status" role="status">
            {enviando && <p>Enviando a transcrição para análise… os campos ficam somente leitura até a resposta; aguarde, isso pode levar alguns segundos.</p>}
          </div>
          {envio.situacao === 'erro' && (
            <div className="form-erro" role="alert">
              <p className="form-erro-titulo">Não foi possível concluir a análise.</p>
              <p>{envio.mensagem}</p>
              <p>Seus dados continuam no formulário: corrija o que for preciso e envie de novo.</p>
            </div>
          )}
        </div>

        <aside className="panel form-help" aria-labelledby="ajuda-lateral">
          <h2 id="ajuda-lateral">Antes de começar</h2>
          <p>Cole a transcrição completa em texto. Os trechos dela sustentam os sinais apresentados depois.</p>
          <p>Ao enviar, o texto vai para a API do ConvIQ e o resultado aparece em seguida. Nada é salvo: o resultado fica só na memória desta página e some ao recarregá-la.</p>
        </aside>
      </div>
    </>
  )
}
