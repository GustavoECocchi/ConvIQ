import { Link } from 'react-router'
import { PAGINAS } from '../destinos.ts'
import { DetalheResultado } from '../resultado/DetalheResultado.tsx'
import { ResumoResultado } from '../resultado/ResumoResultado.tsx'
import { exemplos } from '../services/mocks/exemplos.ts'

function carregarExemplo() {
  const encontrado = exemplos.find((item) => item.chave === 'cliente-risco-e-oportunidade')
  if (!encontrado) throw new Error('Fixture "cliente-risco-e-oportunidade" ausente em exemplos.ts')
  return encontrado
}

const exemplo = carregarExemplo()

/** Rota didática, aberta pelo guia: injeta uma fixture rotulada no resumo e no detalhe. Não é resultado de análise enviada. */
export function ExemploResultado() {
  return (
    <>
      <section className="page-intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">EXEMPLO DIDÁTICO</p>
          <h1 id="page-title" tabIndex={-1}>Exemplo de resultado</h1>
          <p>Como o resultado de uma reunião aparece depois da análise, do resumo às recomendações.</p>
        </div>
        <Link className="intro-tag guide-back" to={PAGINAS.comoLer.caminho}>← Voltar ao guia</Link>
      </section>

      <div className="exemplo-aviso" role="note">
        <p className="exemplo-rotulo">{exemplo.rotulo}</p>
        <p>Isto não é uma análise enviada: os dados abaixo são fictícios e não vêm de nenhuma transcrição sua.</p>
      </div>

      <ResumoResultado entrada={exemplo.entrada} resposta={exemplo.resposta} />
      <DetalheResultado resposta={exemplo.resposta} />

      <p className="guide-footer"><Link className="action-link" to={PAGINAS.comoLer.caminho}>Voltar ao guia: Como ler os sinais</Link></p>
    </>
  )
}
