"""Rota de verificação de disponibilidade da API."""

from fastapi import APIRouter, Request

from app.config import Settings
from app.schemas.saude import RespostaSaude

roteador = APIRouter(tags=["saude"])


@roteador.get("/health", response_model=RespostaSaude)
def consultar_saude(request: Request) -> RespostaSaude:
    """Confirma que a API está no ar e informa o ambiente configurado."""

    configuracao: Settings = request.app.state.configuracao
    return RespostaSaude(status="ok", ambiente=configuracao.ambiente)
