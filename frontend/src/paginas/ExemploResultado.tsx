import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'
import { ResultadoAnalise } from '../resultado/ResultadoAnalise.tsx'
import { exemplos } from '../services/mocks/exemplos.ts'

function carregarExemplo() {
  const encontrado = exemplos.find((item) => item.chave === 'cliente-risco-e-oportunidade')
  if (!encontrado) throw new Error('Fixture "cliente-risco-e-oportunidade" ausente em exemplos.ts')
  return encontrado
}

const exemplo = carregarExemplo()

/** Rota didática, aberta pelo guia: injeta uma fixture rotulada no resultado completo (resumo, detalhe e transcrição com Ver evidência). Não é resultado de análise enviada. */
export function ExemploResultado() {
  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">EXEMPLO DIDÁTICO</p>
          <h1 id="page-title" tabIndex={-1}>Exemplo de resultado</h1>
          <p>Como o resultado de uma reunião aparece depois da análise, do resumo à transcrição, com cada sinal ligado ao seu trecho.</p>
        </div>
        <Link className="intro-tag guide-back" to={PAGINAS.comoLer.caminho}>← Voltar ao guia</Link>
      </section>

      <div className="exemplo-aviso" role="note">
        <p className="exemplo-rotulo">{exemplo.rotulo}</p>
        <p>Isto não é uma análise enviada: os dados abaixo são fictícios e não vêm de nenhuma transcrição sua.</p>
      </div>

      <ResultadoAnalise entrada={exemplo.entrada} resposta={exemplo.resposta} />

      <p className="guide-footer"><Link className="action-link" to={PAGINAS.comoLer.caminho}>Voltar ao guia: Como ler os sinais</Link></p>
    </>
  )
}
