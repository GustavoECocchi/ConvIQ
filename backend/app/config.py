"""Configuração da API lida a partir de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração por ambiente do backend do ConvIQ.

    Os valores padrão cobrem o desenvolvimento local. Um arquivo `.env`
    na pasta `backend/` (não versionado) sobrescreve esses valores;
    `.env.example` documenta as chaves aceitas.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ambiente: str = "desenvolvimento"
    prefixo_api: str = "/api"
    origens_cors: list[str] = ["http://localhost:5173"]


@lru_cache
def obter_configuracao() -> Settings:
    """Retorna a configuração cacheada para reutilização entre requisições."""

    return Settings()
