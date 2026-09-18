"""Enumerações compartilhadas pelos schemas de reunião e análise.

Os valores seguem o contrato consolidado em C01, documentado em
docs/contratos/analise-texto.md.
"""

from enum import Enum


class Vinculo(str, Enum):
    """Relação comercial entre a empresa e quem participou da reunião."""

    CLIENTE = "cliente"
    PROSPECT = "prospect"
    NAO_INFORMADO = "nao_informado"


class Sentimento(str, Enum):
    """Sentimento geral identificado na transcrição."""

    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"
    INFORMACAO_INSUFICIENTE = "informacao_insuficiente"


class ChurnSituacao(str, Enum):
    """Situação de risco de cancelamento identificada na análise.

    `NAO_APLICAVEL` é obrigatório para `Vinculo.PROSPECT`: um prospect não
    tem contrato para cancelar. `INFORMACAO_INSUFICIENTE` é usado quando a
    transcrição não permite avaliar o risco; a ausência de sinal detectado
    (`SEM_SINAL_DETECTADO`) não deve ser lida como baixo risco confirmado.
    """

    SINAL_DETECTADO = "sinal_detectado"
    SEM_SINAL_DETECTADO = "sem_sinal_detectado"
    NAO_APLICAVEL = "nao_aplicavel"
    INFORMACAO_INSUFICIENTE = "informacao_insuficiente"
