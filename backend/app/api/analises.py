"""Rota de análise de uma transcrição em texto."""

from fastapi import APIRouter

from app.schemas.analise import AnaliseTextoResponse
from app.schemas.erro import ErroResposta
from app.schemas.reuniao import AnaliseTextoRequest
from app.services.analise import compor_analise_texto

roteador = APIRouter(tags=["analises"])


@roteador.post(
    "/analises/texto",
    response_model=AnaliseTextoResponse,
    responses={422: {"model": ErroResposta, "description": "Entrada inválida (contrato C01)."}},
)
def analisar_texto(pedido: AnaliseTextoRequest) -> AnaliseTextoResponse:
    """Analisa uma transcrição em texto e devolve sentimento e sinais comerciais.

    Validação do corpo (campos, limites, enum de vínculo) fica a cargo de
    `AnaliseTextoRequest`; erros de validação são traduzidos pelo
    manipulador registrado em `criar_app` (`app/erros.py`), no envelope do
    contrato de C01. `responses={422: ...}` só corrige o que o OpenAPI
    anuncia — sem isso o FastAPI documenta o `HTTPValidationError` padrão,
    que não é o formato devolvido (revisão B04-R01). A análise em si é só
    leitura: `compor_analise_texto` não persiste nada — persistência é B05.
    """

    return compor_analise_texto(pedido)
