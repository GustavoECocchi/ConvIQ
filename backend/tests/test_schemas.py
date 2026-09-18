import pytest
from pydantic import ValidationError

from app.schemas.analise import AnaliseTextoResponse, Churn, Evidencia
from app.schemas.comum import ChurnSituacao, Sentimento, Vinculo
from app.schemas.reuniao import AnaliseTextoRequest


def test_analise_texto_request_aceita_entrada_valida():
    pedido = AnaliseTextoRequest(
        titulo="Acompanhamento comercial",
        empresa="Empresa Exemplo",
        vinculo=Vinculo.CLIENTE,
        transcricao="Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.",
    )

    assert pedido.vinculo is Vinculo.CLIENTE


def test_analise_texto_request_rejeita_transcricao_vazia():
    with pytest.raises(ValidationError):
        AnaliseTextoRequest(
            titulo="Acompanhamento comercial",
            empresa="Empresa Exemplo",
            vinculo=Vinculo.CLIENTE,
            transcricao="",
        )


def test_analise_texto_request_rejeita_transcricao_so_com_espacos():
    """C01: espaço nas pontas não conta como conteúdo (achado da revisão de B01)."""

    with pytest.raises(ValidationError):
        AnaliseTextoRequest(
            titulo="Acompanhamento comercial",
            empresa="Empresa Exemplo",
            vinculo=Vinculo.CLIENTE,
            transcricao="   \n\t  ",
        )


@pytest.mark.parametrize(
    "campo, valor",
    [("titulo", 1), ("empresa", None), ("transcricao", ["a"]), ("titulo", {"a": 1})],
)
def test_analise_texto_request_rejeita_tipo_nao_textual_como_erro_de_validacao(campo, valor):
    """C01-R01: tipo errado deve virar ValidationError, não TypeError escapando."""

    dados = {"titulo": "x", "empresa": "x", "vinculo": "cliente", "transcricao": "x", campo: valor}

    with pytest.raises(ValidationError) as excecao:
        AnaliseTextoRequest(**dados)

    assert excecao.value.errors()[0]["type"] == "string_type"


def test_analise_texto_request_remove_espacos_nas_pontas_do_titulo_e_empresa():
    pedido = AnaliseTextoRequest(
        titulo="  Acompanhamento comercial  ",
        empresa="  Empresa Exemplo  ",
        vinculo=Vinculo.CLIENTE,
        transcricao="Texto qualquer.",
    )

    assert pedido.titulo == "Acompanhamento comercial"
    assert pedido.empresa == "Empresa Exemplo"


def test_analise_texto_request_rejeita_vinculo_fora_do_enum():
    with pytest.raises(ValidationError):
        AnaliseTextoRequest(
            titulo="Acompanhamento comercial",
            empresa="Empresa Exemplo",
            vinculo="parceiro",
            transcricao="Texto qualquer.",
        )


def test_evidencia_rejeita_fim_menor_ou_igual_a_inicio():
    with pytest.raises(ValidationError):
        Evidencia(id="e1", trecho="trecho", inicio=10, fim=10)


def test_evidencia_aceita_posicoes_validas():
    evidencia = Evidencia(id="e1", trecho="Estamos insatisfeitos com o suporte.", inicio=0, fim=36)

    assert evidencia.fim > evidencia.inicio


def _resposta_exemplo(**sobrescritas):
    base = dict(
        transcricao="Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.",
        sentimento=Sentimento.NEGATIVO,
        churn=Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=["e1"]),
        oportunidades=[],
        produtos=["Fluig"],
        concorrentes=[],
        evidencias=[
            Evidencia(id="e1", trecho="Estamos insatisfeitos com o suporte.", inicio=0, fim=36),
        ],
        recomendacoes=[],
        metodo="regras",
        versao_analise="0.1",
    )
    base.update(sobrescritas)
    return base


def test_analise_texto_response_aceita_exemplo_do_plano():
    resposta = AnaliseTextoResponse(**_resposta_exemplo())

    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert resposta.evidencias[0].id == "e1"


def test_analise_texto_response_rejeita_evidencia_referenciada_inexistente():
    dados = _resposta_exemplo(
        churn=Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=["e1", "e2-inexistente"])
    )

    with pytest.raises(ValidationError):
        AnaliseTextoResponse(**dados)


def test_analise_texto_response_rejeita_ids_de_evidencia_duplicados():
    """C01: `Evidencia.id` precisa ser único dentro da resposta (achado B01-R02/README)."""

    dados = _resposta_exemplo(
        evidencias=[
            Evidencia(id="e1", trecho="Estamos insatisfeitos com o suporte.", inicio=0, fim=36),
            Evidencia(id="e1", trecho="Queremos conhecer o Fluig.", inicio=37, fim=64),
        ],
    )

    with pytest.raises(ValidationError):
        AnaliseTextoResponse(**dados)


def test_analise_texto_response_prospect_pode_registrar_churn_nao_aplicavel():
    """Confirma que o schema aceita a combinação exigida pelo plano para
    prospect; a obrigatoriedade dessa combinação é aplicada pelo serviço de
    análise (B03), não pelo schema, que valida request e response em separado.
    """

    dados = _resposta_exemplo(
        churn=Churn(situacao=ChurnSituacao.NAO_APLICAVEL, evidencias=[]),
    )

    resposta = AnaliseTextoResponse(**dados)

    assert resposta.churn.situacao is ChurnSituacao.NAO_APLICAVEL
