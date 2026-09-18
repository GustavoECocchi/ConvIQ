"""Formato padronizado de erro da API, incluindo erros de validação do FastAPI."""

from pydantic import BaseModel


class ErroDetalhe(BaseModel):
    codigo: str
    mensagem: str


class ErroResposta(BaseModel):
    erro: ErroDetalhe
