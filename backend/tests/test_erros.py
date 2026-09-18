"""Testa o envelope de erro de validação (C01), via uma rota só do teste.

Nenhuma rota real ainda aceita `AnaliseTextoRequest` (isso é B04). Para
exercitar `app/erros.py` de ponta a ponta — não só a função pura —, este
teste monta uma rota descartável só na instância local de `FastAPI`, sem
alterar `app/main.py` nem `app/api/`.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import criar_app
from app.schemas.reuniao import AnaliseTextoRequest


def _cliente_com_rota_de_teste(configuracao_padrao, raise_server_exceptions: bool = True) -> TestClient:
    aplicacao = criar_app(configuracao_padrao)

    @aplicacao.post("/_teste/analise-texto")
    def _eco(corpo: AnaliseTextoRequest) -> AnaliseTextoRequest:
        return corpo

    # raise_server_exceptions=False deixa um 500 aparecer como resposta HTTP
    # no teste, em vez de estourar como exceção — é o que detecta C01-R01.
    return TestClient(aplicacao, raise_server_exceptions=raise_server_exceptions)


def _payload_valido() -> dict:
    return {
        "titulo": "Acompanhamento comercial",
        "empresa": "Empresa Exemplo",
        "vinculo": "cliente",
        "transcricao": "Estamos insatisfeitos com o suporte.",
    }


def test_entrada_valida_nao_aciona_o_manipulador_de_erro(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)

    resposta = cliente.post("/_teste/analise-texto", json=_payload_valido())

    assert resposta.status_code == 200


def test_transcricao_vazia_usa_o_codigo_do_contrato(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)
    payload = _payload_valido() | {"transcricao": ""}

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json() == {
        "erro": {"codigo": "TRANSCRICAO_VAZIA", "mensagem": "Informe a transcrição para continuar."}
    }


def test_transcricao_so_com_espacos_usa_o_mesmo_codigo(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)
    payload = _payload_valido() | {"transcricao": "   "}

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "TRANSCRICAO_VAZIA"


def test_titulo_ausente_usa_codigo_obrigatorio(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)
    payload = _payload_valido()
    del payload["titulo"]

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "TITULO_OBRIGATORIO"


def test_titulo_muito_longo_usa_codigo_invalido(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)
    payload = _payload_valido() | {"titulo": "x" * 201}

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "TITULO_INVALIDO"


def test_vinculo_invalido_usa_codigo_do_contrato(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)
    payload = _payload_valido() | {"vinculo": "parceiro"}

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "VINCULO_INVALIDO"


@pytest.mark.parametrize(
    "campo, valor",
    [("titulo", 1), ("empresa", None), ("transcricao", ["a"])],
)
def test_tipo_incorreto_responde_422_no_envelope(configuracao_padrao, campo, valor):
    """C01-R01: antes, str.strip em não-str levantava TypeError e a rota devolvia 500."""

    cliente = _cliente_com_rota_de_teste(configuracao_padrao, raise_server_exceptions=False)
    payload = _payload_valido() | {campo: valor}

    resposta = cliente.post("/_teste/analise-texto", json=payload)

    assert resposta.status_code == 422
    assert resposta.json() == {"erro": {"codigo": "DADOS_INVALIDOS", "mensagem": f"Campo inválido: {campo}."}}


def test_json_malformado_usa_codigo_e_mensagem_genericos(configuracao_padrao):
    """C01-R03: o `loc` aqui é a posição do byte, não um campo; a mensagem não pode citá-lo."""

    cliente = _cliente_com_rota_de_teste(configuracao_padrao)

    resposta = cliente.post("/_teste/analise-texto", content="não é json", headers={"content-type": "application/json"})

    assert resposta.status_code == 422
    assert resposta.json() == {
        "erro": {"codigo": "DADOS_INVALIDOS", "mensagem": "Confira os dados enviados e tente novamente."}
    }


def test_corpo_que_nao_e_objeto_usa_mensagem_generica(configuracao_padrao):
    cliente = _cliente_com_rota_de_teste(configuracao_padrao)

    resposta = cliente.post("/_teste/analise-texto", json=[1, 2])

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == {
        "codigo": "DADOS_INVALIDOS",
        "mensagem": "Confira os dados enviados e tente novamente.",
    }
