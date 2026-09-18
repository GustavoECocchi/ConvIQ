"""Ponto de entrada da API do ConvIQ."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analises import roteador as roteador_analises
from app.api.health import roteador as roteador_saude
from app.config import Settings, obter_configuracao
from app.erros import registrar_manipuladores_erro


def criar_app(configuracao: Settings | None = None) -> FastAPI:
    """Monta a aplicação a partir de uma configuração explícita.

    Sem argumento, usa a configuração lida do ambiente. Os testes passam
    um `Settings` próprio para não depender de variáveis de ambiente,
    de `.env` nem do cache de `obter_configuracao`.
    """

    if configuracao is None:
        configuracao = obter_configuracao()

    aplicacao = FastAPI(title="ConvIQ API")
    aplicacao.state.configuracao = configuracao
    registrar_manipuladores_erro(aplicacao)

    aplicacao.add_middleware(
        CORSMiddleware,
        allow_origins=configuracao.origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    aplicacao.include_router(roteador_saude, prefix=configuracao.prefixo_api)
    aplicacao.include_router(roteador_analises, prefix=configuracao.prefixo_api)
    return aplicacao


app = criar_app()
