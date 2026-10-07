"""Composição da análise completa de uma transcrição em texto.

Escopo de B04: junta o sentimento de B02 (`analisar_sentimento`) com os
sinais comerciais de B03 (`analisar_sinais_comerciais`) numa única
`AnaliseTextoResponse` (contrato de C01), deriva `recomendacoes` a partir
dos sinais e renumera os IDs de evidência — pendência registrada desde B02
("B04 precisa recompor a numeração ao juntar com as evidências de B03").
A rota HTTP (`POST /api/analises/texto`) está em `app/api/analises.py`,
que só chama `compor_analise_texto`; este módulo não depende de rota.
"""

from __future__ import annotations

from app.schemas.analise import AnaliseTextoResponse, Churn, Evidencia, Oportunidade, Recomendacao
from app.schemas.comum import ChurnSituacao
from app.schemas.reuniao import AnaliseTextoRequest
from app.services.sentimento import analisar_sentimento
from app.services.sinais_comerciais import analisar_sinais_comerciais

_METODO = "regras"
_VERSAO_ANALISE = "0.4"


def compor_analise_texto(pedido: AnaliseTextoRequest) -> AnaliseTextoResponse:
    """Executa B02 e B03 sobre a transcrição do pedido e compõe a resposta.

    B02 e B03 numeram suas evidências de forma independente, cada um a
    partir de `e1` — misturados sem ajuste, os IDs colidiriam e deixariam
    de identificar uma evidência específica. Aqui, as evidências das duas
    origens são reunidas, ordenadas pela posição na transcrição (`inicio`)
    e renumeradas em sequência única; as referências em `churn.evidencias`
    e em cada `oportunidades[].evidencias` são atualizadas para os novos IDs.
    """

    resultado_sentimento = analisar_sentimento(pedido.transcricao)
    resultado_comercial = analisar_sinais_comerciais(pedido.transcricao, pedido.vinculo)

    origens = [("sentimento", evidencia) for evidencia in resultado_sentimento.evidencias]
    origens += [("comercial", evidencia) for evidencia in resultado_comercial.evidencias]
    origens.sort(key=lambda par: par[1].inicio)

    mapa_ids: dict[tuple[str, str], str] = {}
    evidencias_finais: list[Evidencia] = []
    for indice, (origem, evidencia) in enumerate(origens, start=1):
        novo_id = f"e{indice}"
        mapa_ids[(origem, evidencia.id)] = novo_id
        evidencias_finais.append(evidencia.model_copy(update={"id": novo_id}))

    def _remapear(ids_antigos: list[str]) -> list[str]:
        return [mapa_ids[("comercial", id_antigo)] for id_antigo in ids_antigos]

    churn = resultado_comercial.churn.model_copy(
        update={"evidencias": _remapear(resultado_comercial.churn.evidencias)}
    )
    oportunidades = [
        oportunidade.model_copy(update={"evidencias": _remapear(oportunidade.evidencias)})
        for oportunidade in resultado_comercial.oportunidades
    ]

    return AnaliseTextoResponse(
        transcricao=pedido.transcricao,
        sentimento=resultado_sentimento.sentimento,
        churn=churn,
        oportunidades=oportunidades,
        produtos=resultado_comercial.produtos,
        concorrentes=resultado_comercial.concorrentes,
        evidencias=evidencias_finais,
        recomendacoes=_gerar_recomendacoes(churn, oportunidades),
        metodo=_METODO,
        versao_analise=_VERSAO_ANALISE,
    )


def _gerar_recomendacoes(churn: Churn, oportunidades: list[Oportunidade]) -> list[Recomendacao]:
    """Deriva recomendações dos sinais já calculados, cada uma evidenciada.

    Recomendações são sugestões sustentadas pelo conteúdo: uma por sinal
    encontrado (risco de churn, cada oportunidade), citando as evidências
    que a sustentam. Sem risco nem oportunidade, a lista fica vazia — nada
    é sugerido sem uma evidência que a justifique.
    """

    recomendacoes: list[Recomendacao] = []

    if churn.situacao is ChurnSituacao.SINAL_DETECTADO:
        recomendacoes.append(
            Recomendacao(
                texto="Investigar o risco de cancelamento identificado na conversa.",
                evidencias=list(churn.evidencias),
            )
        )

    for oportunidade in oportunidades:
        recomendacoes.append(
            Recomendacao(
                texto="Dar seguimento ao interesse comercial identificado nesta oportunidade.",
                evidencias=list(oportunidade.evidencias),
            )
        )

    return recomendacoes
