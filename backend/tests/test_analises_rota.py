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
    assert corpo["versao_analise"] == "0.4"
    assert len(corpo["oportunidades"]) == 1
    assert len(corpo["recomendacoes"]) == 2
    ids_evidencia = {e["id"] for e in corpo["evidencias"]}
    assert set(corpo["churn"]["evidencias"]) <= ids_evidencia


def test_negacao_com_virgula_e_mas_chega_pela_rota_com_recortes_literais(configuracao_padrao):
    """B11/B11-R01 de ponta a ponta: elogio negado vira evidência com o marcador,
    o elogio depois de ", mas" fica intacto e cada recorte fecha com o eco da
    transcrição na resposta."""

    transcricao = "Não gostei do atendimento, mas adoramos o produto."
    payload = _payload_valido(transcricao=transcricao)

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["sentimento"] == "neutro"
    assert [e["trecho"] for e in corpo["evidencias"]] == ["Não gostei", "adoramos"]
    assert [e["id"] for e in corpo["evidencias"]] == ["e1", "e2"]
    for evidencia in corpo["evidencias"]:
        assert corpo["transcricao"][evidencia["inicio"]:evidencia["fim"]] == evidencia["trecho"]
    assert corpo["churn"]["situacao"] == "sem_sinal_detectado"
    assert corpo["versao_analise"] == "0.4"


def test_negacao_de_cancelar_pela_rota_gera_sem_sinal_nao_informacao_insuficiente(configuracao_padrao):
    """B12 de ponta a ponta: "Não vamos cancelar o contrato." não é risco
    (ação negada), mas "contrato" ainda é contexto comercial — avaliado,
    sem sinal, não confundido com informação insuficiente."""

    payload = _payload_valido(transcricao="Não vamos cancelar o contrato.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["churn"]["situacao"] == "sem_sinal_detectado"
    assert corpo["churn"]["evidencias"] == []
    assert corpo["evidencias"] == []
    assert corpo["versao_analise"] == "0.4"


def test_reuniao_sobre_o_contrato_pela_rota_nao_gera_risco(configuracao_padrao):
    """B12-R02 de ponta a ponta: cancelar a reunião não é cancelar o contrato
    que ela discute — sem sinal, sem evidência e sem recomendação."""

    payload = _payload_valido(transcricao="Vamos cancelar a reunião sobre o contrato.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["churn"] == {"situacao": "sem_sinal_detectado", "evidencias": []}
    assert corpo["evidencias"] == []
    assert corpo["recomendacoes"] == []


def test_evidencia_de_churn_pela_rota_traz_condicao_acao_e_objeto(configuracao_padrao):
    """B12-R03 de ponta a ponta: a evidência de risco recorta do eco da
    transcrição a condição, a ação e o objeto, e é a citada por churn e pela
    recomendação."""

    payload = _payload_valido(transcricao="Se o suporte continuar assim, vamos cancelar o contrato.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert [e["trecho"] for e in corpo["evidencias"]] == ["Se o suporte continuar assim, vamos cancelar o contrato"]
    evidencia = corpo["evidencias"][0]
    assert corpo["transcricao"][evidencia["inicio"]:evidencia["fim"]] == evidencia["trecho"]
    assert corpo["churn"]["evidencias"] == [evidencia["id"]]
    assert [r["evidencias"] for r in corpo["recomendacoes"]] == [[evidencia["id"]]]


def test_sujeito_de_outra_oracao_pela_rota_nao_gera_risco(configuracao_padrao):
    """B12-R06 de ponta a ponta: o contrato depois do "e" é sujeito de
    "continua", não objeto de "cancelar"."""

    payload = _payload_valido(transcricao="Vamos cancelar a reunião e o contrato continua vigente.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["churn"] == {"situacao": "sem_sinal_detectado", "evidencias": []}
    assert corpo["evidencias"] == []
    assert corpo["recomendacoes"] == []


def test_insatisfacao_com_tema_alheio_pela_rota_nao_gera_churn(configuracao_padrao):
    """B12-R04 de ponta a ponta: sentimento negativo com evidência literal,
    churn sem base para avaliação e nenhuma recomendação de retenção."""

    payload = _payload_valido(transcricao="Estamos insatisfeitos com o clima.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["sentimento"] == "negativo"
    assert corpo["churn"] == {"situacao": "informacao_insuficiente", "evidencias": []}
    assert [e["trecho"] for e in corpo["evidencias"]] == ["insatisfeitos"]
    evidencia = corpo["evidencias"][0]
    assert corpo["transcricao"][evidencia["inicio"]:evidencia["fim"]] == evidencia["trecho"]
    assert corpo["recomendacoes"] == []


def test_interesse_negado_pela_rota_nao_gera_oportunidade(configuracao_padrao):
    """B13 de ponta a ponta: o interesse negado deixa de gerar oportunidade,
    evidência e recomendação; o produto segue em `produtos`."""

    payload = _payload_valido(transcricao="Não temos interesse em conhecer o Fluig.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["oportunidades"] == []
    assert corpo["evidencias"] == []
    assert corpo["recomendacoes"] == []
    assert corpo["produtos"] == ["Fluig"]
    assert corpo["churn"] == {"situacao": "sem_sinal_detectado", "evidencias": []}
    assert corpo["versao_analise"] == "0.4"


def test_risco_e_intencao_coexistem_pela_rota_com_referencias_validas(configuracao_padrao):
    """B13 de ponta a ponta (critério 7): risco de B12 e oportunidade de B13
    na mesma transcrição, cada um com a sua evidência e recomendação."""

    payload = _payload_valido()  # "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    por_id = {e["id"]: e for e in corpo["evidencias"]}
    assert corpo["churn"]["situacao"] == "sinal_detectado"
    assert [por_id[i]["trecho"] for i in corpo["churn"]["evidencias"]] == ["insatisfeitos com o suporte"]
    assert [por_id[o["evidencias"][0]]["trecho"] for o in corpo["oportunidades"]] == ["Queremos conhecer o Fluig"]
    assert [r["evidencias"] for r in corpo["recomendacoes"]] == [
        corpo["churn"]["evidencias"],
        corpo["oportunidades"][0]["evidencias"],
    ]
    for evidencia in corpo["evidencias"]:
        assert corpo["transcricao"][evidencia["inicio"]:evidencia["fim"]] == evidencia["trecho"]


def test_intencao_preservada_com_acao_alheia_posterior_pela_rota(configuracao_padrao):
    """B13-R01 de ponta a ponta: a intenção sobre o módulo continua, com
    evidência literal e recomendação que a referencia."""

    payload = _payload_valido(transcricao="Precisamos de um módulo e conhecer a cidade.")

    resposta = _cliente(configuracao_padrao).post("/api/analises/texto", json=payload)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert [e["trecho"] for e in corpo["evidencias"]] == ["Precisamos de um módulo"]
    evidencia = corpo["evidencias"][0]
    assert corpo["transcricao"][evidencia["inicio"]:evidencia["fim"]] == evidencia["trecho"]
    assert [o["evidencias"] for o in corpo["oportunidades"]] == [[evidencia["id"]]]
    assert [r["evidencias"] for r in corpo["recomendacoes"]] == [[evidencia["id"]]]


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
