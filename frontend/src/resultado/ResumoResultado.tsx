import { BotoesEvidencia } from './BotoesEvidencia.tsx'
import type { AoVerEvidencia, FalhaEvidencia } from './BotoesEvidencia.tsx'
import type { AnaliseTextoRequest, AnaliseTextoResponse, ChurnSituacao, Sentimento, Vinculo } from '../types/analise.ts'

/**
 * Resumo do resultado (F04-A): identificação da reunião, sentimento e situação de churn.
 * Só apresenta o que o chamador entrega — não classifica texto, não consulta a API e não
 * lê fixture. As evidências de `churn` ficam para F05; `sentimento` não traz IDs em C01.
 */
export interface ResumoResultadoProps {
  entrada: Pick<AnaliseTextoRequest, 'titulo' | 'empresa' | 'vinculo'>
  resposta: Pick<AnaliseTextoResponse, 'sentimento'> & { churn: Pick<AnaliseTextoResponse['churn'], 'situacao'> & Partial<Pick<AnaliseTextoResponse['churn'], 'evidencias'>> }
  /** Se vier, o risco com `evidencias` ganha "Ver evidência" (F05-B); o sentimento nunca ganha, pois C01 não lhe dá IDs. */
  aoVerEvidencia?: AoVerEvidencia
  /** Último pedido de evidência não localizada; o aviso aparece junto do botão do sinal que pediu. */
  falhaEvidencia?: FalhaEvidencia
}

interface Mensagem {
  rotulo: string
  texto: string
}

const VINCULOS: Record<Vinculo, Mensagem> = {
  cliente: { rotulo: 'Cliente', texto: 'Vínculo declarado no envio.' },
  prospect: { rotulo: 'Prospect', texto: 'Vínculo declarado no envio.' },
  nao_informado: { rotulo: 'Não informado', texto: 'O vínculo não foi declarado e nada foi presumido.' },
}

const SENTIMENTOS: Record<Sentimento, Mensagem> = {
  positivo: { rotulo: 'Positivo', texto: 'Predominam trechos de satisfação ou elogio no texto.' },
  neutro: { rotulo: 'Neutro', texto: 'Há sinais positivos e negativos na mesma quantidade.' },
  negativo: { rotulo: 'Negativo', texto: 'Predominam trechos de insatisfação ou reclamação no texto.' },
  informacao_insuficiente: {
    rotulo: 'Informação insuficiente',
    texto: 'O texto não traz sinais de sentimento. Isso não quer dizer que a conversa foi neutra.',
  },
}

const CHURN: Record<ChurnSituacao, Mensagem> = {
  sinal_detectado: {
    rotulo: 'Sinal detectado',
    texto:
      'Há trechos que indicam risco de cancelamento. Vale investigar a relação; não é uma previsão de que o contrato será encerrado. Os trechos que sustentam os sinais aparecem destacados na transcrição.',
  },
  sem_sinal_detectado: {
    rotulo: 'Sem sinal detectado',
    texto:
      'A conversa tratou da relação comercial e nenhum sinal de cancelamento apareceu no texto. Isso não confirma que a relação está segura: a análise só vê o que está escrito.',
  },
  nao_aplicavel: {
    rotulo: 'Não aplicável',
    texto:
      'Usado quando a reunião é com um prospect, que ainda não tem contrato a cancelar. Não indica nem presença nem ausência de risco.',
  },
  informacao_insuficiente: {
    rotulo: 'Informação insuficiente',
    texto:
      'O texto não traz conteúdo comercial suficiente para avaliar o cancelamento. Não é o mesmo que ausência de risco.',
  },
}

export function ResumoResultado({ entrada, resposta, aoVerEvidencia, falhaEvidencia }: ResumoResultadoProps) {
  const vinculo = VINCULOS[entrada.vinculo]
  const sentimento = SENTIMENTOS[resposta.sentimento]
  const churn = CHURN[resposta.churn.situacao]

  return (
    <div className="resumo">
      <section className="panel resumo-reuniao" aria-labelledby="resumo-reuniao">
        <h2 id="resumo-reuniao">Reunião analisada</h2>
        <dl className="resumo-dados">
          <div><dt>Título</dt><dd>{entrada.titulo}</dd></div>
          <div><dt>Empresa</dt><dd>{entrada.empresa}</dd></div>
          <div>
            <dt>Vínculo</dt>
            <dd><strong>{vinculo.rotulo}</strong> <span className="resumo-nota">{vinculo.texto}</span></dd>
          </div>
        </dl>
      </section>

      <section className="resumo-sinais" aria-labelledby="resumo-sinais">
        <h2 id="resumo-sinais">Sinais da conversa</h2>
        <div className="resumo-cartoes">
          <article className="panel resumo-cartao" aria-labelledby="resumo-sentimento" data-sentimento={resposta.sentimento}>
            <h3 id="resumo-sentimento">Sentimento</h3>
            <p className="resumo-estado">{sentimento.rotulo}</p>
            <p>{sentimento.texto}</p>
          </article>
          <article className="panel resumo-cartao" aria-labelledby="resumo-churn" data-churn={resposta.churn.situacao}>
            <h3 id="resumo-churn">Risco de cancelamento</h3>
            <p className="resumo-estado">{churn.rotulo}</p>
            <p>{churn.texto}</p>
            {aoVerEvidencia && resposta.churn.situacao === 'sinal_detectado' ? (
              <BotoesEvidencia ids={resposta.churn.evidencias ?? []} sinal="risco de cancelamento" aoVerEvidencia={aoVerEvidencia} falha={falhaEvidencia} />
            ) : null}
          </article>
        </div>
      </section>
    </div>
  )
}
