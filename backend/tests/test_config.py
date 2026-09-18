from app.config import Settings


def test_valores_padrao(configuracao_padrao):
    assert configuracao_padrao.ambiente == "desenvolvimento"
    assert configuracao_padrao.prefixo_api == "/api"
    assert configuracao_padrao.origens_cors == ["http://localhost:5173"]


def test_variaveis_de_ambiente_sobrescrevem_os_padroes(ambiente_limpo, monkeypatch):
    monkeypatch.setenv("AMBIENTE", "homologacao")
    monkeypatch.setenv("PREFIXO_API", "/v1")
    monkeypatch.setenv("ORIGENS_CORS", '["http://a.test", "http://b.test"]')

    configuracao = Settings(_env_file=None)

    assert configuracao.ambiente == "homologacao"
    assert configuracao.prefixo_api == "/v1"
    assert configuracao.origens_cors == ["http://a.test", "http://b.test"]


def test_arquivo_env_e_lido_quando_indicado(ambiente_limpo, tmp_path):
    arquivo_env = tmp_path / ".env"
    arquivo_env.write_text("AMBIENTE=homologacao\n", encoding="utf-8")

    configuracao = Settings(_env_file=arquivo_env)

    assert configuracao.ambiente == "homologacao"
    assert configuracao.prefixo_api == "/api"
