import pytest

from app.config import Settings

CHAVES_DE_AMBIENTE = ("AMBIENTE", "PREFIXO_API", "ORIGENS_CORS")


@pytest.fixture
def ambiente_limpo(monkeypatch):
    """Remove as variáveis da API do ambiente do processo durante o teste."""

    for chave in CHAVES_DE_AMBIENTE:
        monkeypatch.delenv(chave, raising=False)


@pytest.fixture
def configuracao_padrao(ambiente_limpo) -> Settings:
    """Configuração com os valores padrão, ignorando variáveis de ambiente e `.env`."""

    return Settings(_env_file=None)
