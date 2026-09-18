from fastapi.testclient import TestClient

from app.main import criar_app


def _cliente(configuracao_padrao) -> TestClient:
    return TestClient(criar_app(configuracao_padrao))


def _payload_valido(**sobrescritas) -> dict:
    base = {
        "titulo": "Acompanhamento comercial",
        "empresa": "Empresa Exemplo",
        "vinculo": "cliente",
        "transcricao": "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.",
    }
    base.update(sobrescritas)
    return base


def test_entrada_valida_responde_200_conforme_o_contrato(configuracao_padrao):
    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=_payload_valido())

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["sentimento"] == "negativo"
    assert corpo["churn"]["situacao"] == "sinal_detectado"
    assert corpo["produtos"] == ["Fluig"]
    assert corpo["metodo"] == "regras"
    assert corpo["versao_analise"] == "0.1"
    assert len(corpo["oportunidades"]) == 1
    assert len(corpo["recomendacoes"]) == 2
    ids_evidencia = {e["id"] for e in corpo["evidencias"]}
    assert set(corpo["churn"]["evidencias"]) <= ids_evidencia


def test_prospect_recebe_churn_nao_aplicavel_pela_rota(configuracao_padrao):
    payload = _payload_valido(vinculo="prospect", transcricao="Vamos cancelar tudo imediatamente.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    assert resposta.json()["churn"] == {"situacao": "nao_aplicavel", "evidencias": []}


def test_transcricao_vazia_responde_422_no_envelope_do_contrato(configuracao_padrao):
    payload = _payload_valido(transcricao="")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json() == {
        "erro": {"codigo": "TRANSCRICAO_VAZIA", "mensagem": "Informe a transcrição para continuar."}
    }


def test_vinculo_invalido_responde_422_no_envelope_do_contrato(configuracao_padrao):
    payload = _payload_valido(vinculo="parceiro")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "VINCULO_INVALIDO"


def test_titulo_com_tipo_invalido_responde_422_dados_invalidos(configuracao_padrao):
    payload = _payload_valido(titulo=123)

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "DADOS_INVALIDOS"


def test_campo_ausente_responde_422(configuracao_padrao):
    payload = _payload_valido()
    del payload["empresa"]

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "EMPRESA_OBRIGATORIA"


def test_informacao_insuficiente_devolve_listas_vazias_sem_inventar_sinal(configuracao_padrao):
    payload = _payload_valido(transcricao="Bom dia a todos. Vamos seguir a pauta de hoje.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["sentimento"] == "informacao_insuficiente"
    assert corpo["churn"]["situacao"] == "informacao_insuficiente"
    assert corpo["evidencias"] == []
    assert corpo["oportunidades"] == []
    assert corpo["recomendacoes"] == []


def test_rota_de_analise_aparece_no_openapi_junto_da_saude(configuracao_padrao):
    resposta = _cliente(configuracao_padrao).get("/openapi.json")

    assert resposta.status_code == 200
    caminhos = resposta.json()["paths"]
    assert set(caminhos) == {"/api/health", "/api/analises/texto"}


def test_openapi_anuncia_o_envelope_de_erro_do_contrato_para_422(configuracao_padrao):
    """B04-R01: sem `responses={422: ...}` o FastAPI anunciava
    `HTTPValidationError` (campo `detail`), que não é o que a rota devolve."""

    cliente = _cliente(configuracao_padrao)
    especificacao = cliente.get("/openapi.json").json()
    respostas = especificacao["paths"]["/api/analises/texto"]["post"]["responses"]

    assert respostas["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/AnaliseTextoResponse"
    }
    assert respostas["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErroResposta"
    }
    assert "HTTPValidationError" not in especificacao["components"]["schemas"]
    assert list(especificacao["components"]["schemas"]["ErroResposta"]["properties"]) == ["erro"]

    # o envelope real tem exatamente o formato anunciado
    real = cliente.post("/api/analises/texto", json=_payload_valido(transcricao=""))
    assert real.status_code == 422
    assert set(real.json()) == {"erro"}
    assert set(real.json()["erro"]) == {"codigo", "mensagem"}
