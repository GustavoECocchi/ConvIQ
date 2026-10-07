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

Negação simples (B11): "não", "nem", "sem" e "nenhum(a)" invertem ou
suprimem um sinal léxico dentro da mesma expressão/oração — ver
`app/services/negacao.py` (extraído em B12 para reúso pelo risco de
cancelamento). Escopo maior de frase/ironia/negação dupla continua fora do
alcance; ver `backend/README.md`, seção "Serviço de sentimento (B02,
negação simples em B11)", limitações.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.analise import Evidencia
from app.schemas.comum import Sentimento
from app.services.negacao import escopos_de_negacao, inicio_da_negacao_mais_proxima
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


@dataclass(frozen=True)
class _Ocorrencia:
    """Um sinal já resolvido (negação aplicada ou não), pronto para contagem."""

    inicio: int
    fim: int
    sentimento: Sentimento


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

    Negação (B11): dentro do escopo de "não"/"nem"/"sem"/"nenhum(a)" (mesma
    expressão/oração, ver `app/services/negacao.py`), um sinal positivo vira negativo — "não
    gostei" é insatisfação, não elogio anulado — e sua evidência cobre o
    trecho negado inteiro, do marcador ao fim da palavra léxica, recortado
    literalmente da transcrição original. Um sinal negativo dentro do escopo
    é só suprimido, não vira positivo — negar um problema ("sem problemas",
    "não foi ruim") não é prova de elogio, então essa ocorrência não gera
    evidência. Sem outro sinal na oração, o resultado é
    `informacao_insuficiente`, não `neutro`.
    """

    normalizado = normalizar_preservando_posicoes(transcricao)
    escopos = escopos_de_negacao(normalizado, transcricao)

    ocorrencias: list[_Ocorrencia] = []

    for correspondencia in _REGEX_POSITIVO.finditer(normalizado):
        inicio_negacao = inicio_da_negacao_mais_proxima(escopos, correspondencia.start())
        if inicio_negacao is None:
            ocorrencias.append(_Ocorrencia(correspondencia.start(), correspondencia.end(), Sentimento.POSITIVO))
        else:
            ocorrencias.append(_Ocorrencia(inicio_negacao, correspondencia.end(), Sentimento.NEGATIVO))

    for correspondencia in _REGEX_NEGATIVO.finditer(normalizado):
        inicio_negacao = inicio_da_negacao_mais_proxima(escopos, correspondencia.start())
        if inicio_negacao is not None:
            continue
        ocorrencias.append(_Ocorrencia(correspondencia.start(), correspondencia.end(), Sentimento.NEGATIVO))

    negativos = [ocorrencia for ocorrencia in ocorrencias if ocorrencia.sentimento is Sentimento.NEGATIVO]
    positivos = [ocorrencia for ocorrencia in ocorrencias if ocorrencia.sentimento is Sentimento.POSITIVO]

    if not negativos and not positivos:
        return ResultadoSentimento(sentimento=Sentimento.INFORMACAO_INSUFICIENTE, evidencias=[])

    if len(negativos) > len(positivos):
        sentimento = Sentimento.NEGATIVO
        selecionadas = negativos
    elif len(positivos) > len(negativos):
        sentimento = Sentimento.POSITIVO
        selecionadas = positivos
    else:
        sentimento = Sentimento.NEUTRO
        selecionadas = negativos + positivos

    ocorrencias_ordenadas = sorted(selecionadas, key=lambda ocorrencia: ocorrencia.inicio)
    evidencias = [
        Evidencia(
            id=f"e{indice}",
            trecho=transcricao[ocorrencia.inicio:ocorrencia.fim],
            inicio=ocorrencia.inicio,
            fim=ocorrencia.fim,
        )
        for indice, ocorrencia in enumerate(ocorrencias_ordenadas, start=1)
    ]
    return ResultadoSentimento(sentimento=sentimento, evidencias=evidencias)
