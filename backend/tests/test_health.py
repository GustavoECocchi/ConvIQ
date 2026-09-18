from fastapi.testclient import TestClient

from app.config import Settings
from app.main import criar_app


def test_saude_responde_ok_na_configuracao_padrao(configuracao_padrao):
    cliente = TestClient(criar_app(configuracao_padrao))

    resposta = cliente.get("/api/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "ambiente": "desenvolvimento"}


def test_saude_nao_existe_fora_do_prefixo_api(configuracao_padrao):
    cliente = TestClient(criar_app(configuracao_padrao))

    resposta = cliente.get("/health")

    assert resposta.status_code == 404


def test_saude_respeita_ambiente_e_prefixo_configurados():
    configuracao = Settings(ambiente="homologacao", prefixo_api="/v1", _env_file=None)
    cliente = TestClient(criar_app(configuracao))

    resposta = cliente.get("/v1/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "ambiente": "homologacao"}
    assert cliente.get("/api/health").status_code == 404


def test_cors_libera_somente_origens_configuradas():
    configuracao = Settings(origens_cors=["http://exemplo.test"], _env_file=None)
    cliente = TestClient(criar_app(configuracao))

    permitida = cliente.get("/api/health", headers={"Origin": "http://exemplo.test"})
    bloqueada = cliente.get("/api/health", headers={"Origin": "http://outra.test"})

    assert permitida.headers.get("access-control-allow-origin") == "http://exemplo.test"
    assert "access-control-allow-origin" not in bloqueada.headers
