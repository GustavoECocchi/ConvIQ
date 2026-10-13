import { useState } from 'react'
import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'
import { MeetingForm } from '../formulario/MeetingForm.tsx'

export function NovaAnalise() {
  const [conferido, setConferido] = useState(false)

  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">ANÁLISE POR TEXTO</p>
          <h1 id="page-title" tabIndex={-1}>Nova análise por texto</h1>
          <p>Organize os dados da reunião antes de conferir os sinais.</p>
        </div>
        <Link className="intro-tag guide-back" to={PAGINAS.visaoGeral.caminho}>← Voltar à visão geral</Link>
      </section>

      <div className="form-layout">
        <div className="form-main">
          <MeetingForm onSubmit={() => setConferido(true)} onEdit={() => setConferido(false)} />
          <div className="form-status" role="status">
            {conferido && <p>Dados prontos. A transcrição ainda não foi enviada.</p>}
          </div>
        </div>

        <aside className="panel form-help" aria-labelledby="ajuda-lateral">
          <h2 id="ajuda-lateral">Antes de começar</h2>
          <p>Cole a transcrição completa em texto. Os trechos dela sustentam os sinais apresentados depois.</p>
          <p>Nesta etapa nada é enviado: o botão apenas confere se os dados estão completos.</p>
        </aside>
      </div>
    </>
  )
}
