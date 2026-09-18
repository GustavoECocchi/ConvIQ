"""Serviço de sentimento e evidências sobre uma transcrição em texto.

Escopo de B02, sobre o contrato consolidado em C01
(`docs/contratos/analise-texto.md`): extrai sinais de sentimento
(positivo/negativo) da transcrição original, com evidências localizadas por
posição de caractere. Sinais comerciais — churn, oportunidades, produtos e
concorrentes — ficam para B03; compor a resposta completa e a rota HTTP
ficam para B04. Este módulo não depende de rota nem de outro serviço.

Corrige a colisão entre "satisfeito" e "insatisfeito" citada nas regras de
produto da governança. No experimento de referência
(`conviq_datascience.py`), `LEX_POSITIVO` inclui o radical "satisfeit" e é
contado por substring (`texto.count(...)`), o que também conta a ocorrência
de "satisfeit" dentro de "insatisfeito" — as duas listas pontuam a mesma
palavra. Aqui, cada padrão é ancorado por fronteira de palavra (`\\b`), e
"insatisfeito" não tem fronteira de palavra antes de "satisfeito" (o "in"
está colado, sem separador), então o padrão positivo não casa dentro dele.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.analise import Evidencia
from app.schemas.comum import Sentimento
from app.services.texto import normalizar_preservando_posicoes

_PADROES_NEGATIVOS = [
    r"insatisfeit[oa]s?",
    r"frustrad[oa]s?",
    r"pessim[oa]s?",
    r"ruim|ruins",
    r"dificil|dificeis",
    r"problemas?",
    r"reclama(cao|coes|r|mos|ndo)?",
]

_PADROES_POSITIVOS = [
    r"satisfeit[oa]s?",
    r"excelente[s]?",
    r"otim[oa]s?",
    r"ador(a|amos|aram|ei|ou)",
    r"gost(ei|amos|aram|a|o)",
    r"content[ea]s?",
]

_REGEX_NEGATIVO = re.compile(r"\b(?:" + "|".join(_PADROES_NEGATIVOS) + r")\b")
_REGEX_POSITIVO = re.compile(r"\b(?:" + "|".join(_PADROES_POSITIVOS) + r")\b")


@dataclass(frozen=True)
class ResultadoSentimento:
    sentimento: Sentimento
    evidencias: list[Evidencia]


def analisar_sentimento(transcricao: str) -> ResultadoSentimento:
    """Classifica o sentimento geral da transcrição, com evidências localizadas.

    - Nenhum sinal (positivo ou negativo) encontrado: `informacao_insuficiente`,
      sem evidências. Não é presumido como `neutro` — ausência de sinal e
      neutralidade de fato são situações distintas (mesmo princípio que o
      contrato aplica a `churn`).
    - Mais sinais negativos que positivos: `negativo`, evidenciado pelas
      ocorrências negativas.
    - Mais sinais positivos que negativos: `positivo`, evidenciado pelas
      ocorrências positivas.
    - Mesma contagem, maior que zero: `neutro` (sinais mistos), evidenciado
      por todas as ocorrências encontradas, positivas e negativas.

    Cada ocorrência da regex vira uma evidência própria — inclusive quando a
    mesma palavra aparece mais de uma vez na transcrição, cada aparição fica
    em uma posição distinta, sem confundir uma repetição com outra.
    """

    normalizado = normalizar_preservando_posicoes(transcricao)

    negativos = list(_REGEX_NEGATIVO.finditer(normalizado))
    positivos = list(_REGEX_POSITIVO.finditer(normalizado))

    if not negativos and not positivos:
        return ResultadoSentimento(sentimento=Sentimento.INFORMACAO_INSUFICIENTE, evidencias=[])

    if len(negativos) > len(positivos):
        sentimento = Sentimento.NEGATIVO
        ocorrencias = negativos
    elif len(positivos) > len(negativos):
        sentimento = Sentimento.POSITIVO
        ocorrencias = positivos
    else:
        sentimento = Sentimento.NEUTRO
        ocorrencias = negativos + positivos

    ocorrencias_ordenadas = sorted(ocorrencias, key=lambda correspondencia: correspondencia.start())
    evidencias = [
        Evidencia(
            id=f"e{indice}",
            trecho=transcricao[correspondencia.start():correspondencia.end()],
            inicio=correspondencia.start(),
            fim=correspondencia.end(),
        )
        for indice, correspondencia in enumerate(ocorrencias_ordenadas, start=1)
    ]
    return ResultadoSentimento(sentimento=sentimento, evidencias=evidencias)
