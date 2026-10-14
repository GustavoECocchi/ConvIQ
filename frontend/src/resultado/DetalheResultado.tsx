import type { AnaliseTextoResponse } from '../types/analise.ts'
import { BotoesEvidencia } from './BotoesEvidencia.tsx'
import type { AoVerEvidencia, FalhaEvidencia } from './BotoesEvidencia.tsx'

/**
 * Detalhe do resultado (F04-B): oportunidades, menções a produtos e concorrentes,
 * recomendações e método. Mostra as listas como chegam de C01 — sem classificar,
 * filtrar, deduplicar ou consultar a API — e diz com clareza quando uma lista vem
 * vazia. Os IDs de evidência dos itens ficam para F05; aqui não aparecem.
 */
export interface DetalheResultadoProps {
  resposta: Pick<AnaliseTextoResponse, 'oportunidades' | 'produtos' | 'concorrentes' | 'recomendacoes' | 'metodo' | 'versao_analise'>
  /** Se vier, cada oportunidade e recomendação com `evidencias` ganha "Ver evidência" (F05-B). */
  aoVerEvidencia?: AoVerEvidencia
  /** Último pedido de evidência não localizada; o aviso aparece junto do botão do sinal que pediu. */
  falhaEvidencia?: FalhaEvidencia
}

function Nomes({ nomes, vazio }: { nomes: string[]; vazio: string }) {
  if (nomes.length === 0) return <p className="detalhe-vazio">{vazio}</p>
  return (
    <ul className="detalhe-nomes">
      {nomes.map((nome, indice) => <li key={indice}>{nome}</li>)}
    </ul>
  )
}

export function DetalheResultado({ resposta, aoVerEvidencia, falhaEvidencia }: DetalheResultadoProps) {
  const { oportunidades, produtos, concorrentes, recomendacoes } = resposta

  return (
    <div className="detalhe">
      <section className="panel detalhe-bloco detalhe-oportunidades" aria-labelledby="detalhe-oportunidades">
        <h2 id="detalhe-oportunidades">Oportunidades</h2>
        {oportunidades.length > 0 ? (
          <>
            <ul className="detalhe-lista">
              {oportunidades.map((oportunidade, indice) => (
                <li key={indice}>
                  {oportunidade.descricao}
                  {aoVerEvidencia ? <BotoesEvidencia ids={oportunidade.evidencias} sinal={`oportunidade ${indice + 1}`} aoVerEvidencia={aoVerEvidencia} falha={falhaEvidencia} /> : null}
                </li>
              ))}
            </ul>
            <p className="detalhe-nota">Cada oportunidade é um indício para dar seguimento, não uma venda confirmada.</p>
          </>
        ) : (
          <p className="detalhe-vazio">
            Nenhuma oportunidade identificada no texto. A análise só reconhece intenções comerciais explícitas, como
            querer conhecer ou contratar uma solução; isso não quer dizer que não haja interesse.
          </p>
        )}
      </section>

      <section className="panel detalhe-bloco" aria-labelledby="detalhe-mencoes">
        <h2 id="detalhe-mencoes">Menções na conversa</h2>
        <p className="detalhe-nota detalhe-nota-topo">
          Nomes reconhecidos no texto a partir de uma lista fixa. Citar um produto não é o mesmo que querer
          contratá-lo, e citar um concorrente não indica, sozinho, intenção de troca.
        </p>
        <h3>Produtos</h3>
        <Nomes nomes={produtos} vazio="Nenhum produto da lista conhecida foi citado." />
        <h3>Concorrentes</h3>
        <Nomes nomes={concorrentes} vazio="Nenhum concorrente da lista conhecida foi citado." />
      </section>

      <section className="panel detalhe-bloco detalhe-recomendacoes" aria-labelledby="detalhe-recomendacoes">
        <h2 id="detalhe-recomendacoes">Recomendações</h2>
        {recomendacoes.length > 0 ? (
          <>
            <ul className="detalhe-lista">
              {recomendacoes.map((recomendacao, indice) => (
                <li key={indice}>
                  {recomendacao.texto}
                  {aoVerEvidencia ? <BotoesEvidencia ids={recomendacao.evidencias} sinal={`recomendação ${indice + 1}`} aoVerEvidencia={aoVerEvidencia} falha={falhaEvidencia} /> : null}
                </li>
              ))}
            </ul>
            <p className="detalhe-nota">
              {aoVerEvidencia
                ? 'Cada sugestão vem de um risco ou de uma oportunidade encontrada no texto. Use Ver evidência para ir ao trecho que a sustenta.'
                : 'Cada sugestão vem de um risco ou de uma oportunidade encontrada no texto. Os trechos que sustentam os sinais aparecem destacados na transcrição, ainda sem indicar qual sugestão cada um sustenta.'}
            </p>
          </>
        ) : (
          <p className="detalhe-vazio">
            Nenhuma recomendação. A análise só sugere um próximo passo quando encontra um risco ou uma oportunidade
            que o sustente.
          </p>
        )}
      </section>

      <p className="detalhe-metodo">
        Método da análise: <strong>{resposta.metodo}</strong>, versão <strong>{resposta.versao_analise}</strong>.
      </p>
    </div>
  )
}
