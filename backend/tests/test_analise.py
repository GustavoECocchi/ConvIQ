import pytest

from app.schemas.comum import ChurnSituacao, Sentimento, Vinculo
from app.schemas.reuniao import AnaliseTextoRequest
from app.services.analise import compor_analise_texto


def _pedido(transcricao: str, vinculo: str = "cliente", **sobrescritas) -> AnaliseTextoRequest:
    base = dict(titulo="Reunião", empresa="Empresa Exemplo", vinculo=vinculo, transcricao=transcricao)
    base.update(sobrescritas)
    return AnaliseTextoRequest(**base)


def test_exemplo_do_contrato_c01_risco_e_oportunidade_coexistindo():
    """Mesmo texto do exemplo 1 de docs/contratos/analise-texto.md."""

    pedido = _pedido("Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.", "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.transcricao == pedido.transcricao
    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resposta.oportunidades) == 1
    assert resposta.produtos == ["Fluig"]
    assert resposta.concorrentes == []
    assert resposta.metodo == "regras"
    assert resposta.versao_analise == "0.3"
    # uma recomendação para o risco, uma para a oportunidade
    assert len(resposta.recomendacoes) == 2


def test_prospect_com_saudacao_e_informacao_insuficiente_em_tudo():
    pedido = _pedido("Bom dia a todos. Vamos seguir a pauta de hoje.", "prospect")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resposta.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert resposta.oportunidades == []
    assert resposta.evidencias == []
    assert resposta.recomendacoes == []


def test_prospect_com_oportunidade_gera_recomendacao_sem_recomendacao_de_churn():
    pedido = _pedido("Temos interesse em conhecer o Fluig.", "prospect")

    resposta = compor_analise_texto(pedido)

    assert resposta.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert len(resposta.oportunidades) == 2  # "interesse" e "conhecer"
    assert len(resposta.recomendacoes) == 2
    assert all("cancelamento" not in r.texto for r in resposta.recomendacoes)


def test_cliente_sem_nenhum_sinal_nao_gera_recomendacao():
    pedido = _pedido("O suporte foi excelente e o contrato segue normal.", "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resposta.oportunidades == []
    assert resposta.recomendacoes == []


def test_evidencias_sao_renumeradas_unicas_e_ordenadas_por_posicao():
    """B02 e B03 numeram evidências a partir de e1 cada um; a composição
    precisa renumerar para não colidir, na ordem em que aparecem no texto."""

    transcricao = "Vamos cancelar. Mais tarde, ficamos frustrados com o atraso."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    ids = [e.id for e in resposta.evidencias]
    assert ids == [f"e{n}" for n in range(1, len(ids) + 1)]
    assert len(ids) == len(set(ids))
    posicoes = [e.inicio for e in resposta.evidencias]
    assert posicoes == sorted(posicoes)
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_referencias_de_churn_e_oportunidade_apontam_para_ids_renumerados():
    pedido = _pedido("Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.", "cliente")

    resposta = compor_analise_texto(pedido)

    ids_existentes = {e.id for e in resposta.evidencias}
    assert set(resposta.churn.evidencias) <= ids_existentes
    for oportunidade in resposta.oportunidades:
        assert set(oportunidade.evidencias) <= ids_existentes
    # a validação de referências de AnaliseTextoResponse já teria rejeitado
    # IDs inexistentes; chegar aqui sem erro já comprova a consistência.


def test_vinculo_nao_informado_mantem_regra_de_churn_de_b03():
    pedido = _pedido("Vamos cancelar o contrato no fim do mês.", "nao_informado")

    resposta = compor_analise_texto(pedido)

    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resposta.recomendacoes) == 1


def test_elogio_negado_entra_na_composicao_com_recorte_literal_e_ids_renumerados():
    """B11 na composição: a evidência do elogio negado (com o marcador) convive
    com a evidência comercial, renumerada por posição, e as referências de
    oportunidade apontam para o ID novo."""

    transcricao = "Não gostei do atendimento, mas queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "Não gostei"), ("e2", "conhecer")]
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho
    assert resposta.oportunidades[0].evidencias == ["e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"]]
    # "atendimento" é contexto comercial; nenhum padrão de risco → avaliado, sem sinal
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resposta.produtos == ["Fluig"]
    assert resposta.versao_analise == "0.3"


def test_negacao_fechada_na_virgula_nao_inverte_elogio_nem_apaga_oportunidade():
    """B11-R01 na composição: "sem problemas" só suprime "problemas"; o elogio
    após a vírgula e a oportunidade após o "e" seguem intactos."""

    transcricao = "Sem problemas com o suporte, estamos satisfeitos e queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.POSITIVO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "satisfeitos"), ("e2", "conhecer")]
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho
    assert resposta.oportunidades[0].evidencias == ["e2"]
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO


def test_satisfacao_negada_gera_risco_com_evidencia_propria_que_inclui_o_complemento():
    """B12 na composição: "Não estamos satisfeitos" é evidência do sentimento
    (B11) e, com o complemento, do risco (B12) — "Não estamos satisfeitos
    com o suporte" (revisão B12-R03). Antes da revisão, as duas evidências
    tinham o mesmo intervalo; agora a de churn contém a de sentimento. As
    duas começam na mesma posição e mantêm IDs distintos, ordem estável."""

    transcricao = "Não estamos satisfeitos com o suporte. Queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [
        ("e1", "Não estamos satisfeitos"),
        ("e2", "Não estamos satisfeitos com o suporte"),
        ("e3", "conhecer"),
    ]
    assert resposta.churn.evidencias == ["e2"]
    assert resposta.oportunidades[0].evidencias == ["e3"]
    assert resposta.produtos == ["Fluig"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"], ["e3"]]
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_acao_de_risco_com_objeto_distante_na_mesma_frase_gera_recomendacao():
    """B12: a condição antes da vírgula não impede a ligação ação–objeto,
    mesmo sem nenhum outro sinal de sentimento na transcrição. Revisão
    B12-R03: a evidência mostra a condição, a ação e o objeto."""

    transcricao = "Se o suporte continuar assim, vamos cancelar o contrato."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [
        ("e1", "Se o suporte continuar assim, vamos cancelar o contrato")
    ]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]


def test_exemplo_c01_evidencia_de_churn_inclui_o_complemento():
    """B12-R03 no texto do exemplo 1 de C01: o sentimento evidencia
    "insatisfeitos"; o churn evidencia "insatisfeitos com o suporte". O
    formato do contrato não muda, só o recorte de churn (ver nota B12 em
    docs/contratos/analise-texto.md)."""

    transcricao = "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [
        ("e1", "insatisfeitos", 8, 21),
        ("e2", "insatisfeitos com o suporte", 8, 35),
        ("e3", "conhecer", 46, 54),
    ]
    assert resposta.churn.evidencias == ["e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"], ["e3"]]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a reunião sobre o contrato.",
        "Vamos reavaliar a pauta com o fornecedor.",
        "O contrato continua vigente, vamos cancelar a reunião.",
        "Vamos cancelar a reunião, mas não o contrato.",
    ],
)
def test_reuniao_ou_pauta_com_contrato_por_perto_nao_gera_recomendacao_de_retencao(transcricao):
    """B12-R02 na composição: antes, cada caso gerava sinal de churn e uma
    recomendação de retenção; agora, sem sinal e sem recomendação."""

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resposta.churn.evidencias == []
    assert resposta.evidencias == []
    assert resposta.recomendacoes == []


@pytest.mark.parametrize(
    "transcricao",
    [
        "Estamos insatisfeitos com o clima.",
        "Não estamos satisfeitos com o almoço.",
    ],
)
def test_insatisfacao_com_tema_alheio_mantem_sentimento_sem_churn_nem_retencao(transcricao):
    """B12-R04 na composição: antes, cada frase gerava churn e uma
    recomendação de retenção. O sentimento negativo continua, com sua
    evidência; churn não tem base para avaliação."""

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resposta.churn.evidencias == []
    assert resposta.recomendacoes == []
    assert len(resposta.evidencias) == 1  # só a do sentimento
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_tema_alheio_com_oportunidade_mantem_so_a_recomendacao_da_oportunidade():
    transcricao = "Estamos insatisfeitos com o almoço. Queremos conhecer o Fluig."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "insatisfeitos"), ("e2", "conhecer")]
    assert resposta.oportunidades[0].evidencias == ["e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"]]
    assert resposta.produtos == ["Fluig"]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a reunião e o contrato continua vigente.",
        "Vamos cancelar a reunião e o fornecedor será avisado.",
    ],
)
def test_sujeito_de_outra_oracao_nao_gera_recomendacao_de_retencao(transcricao):
    """B12-R06 na composição: antes, sinal de churn, evidência "cancelar a
    reunião e o contrato/fornecedor" e recomendação de retenção."""

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resposta.evidencias == []
    assert resposta.recomendacoes == []


def test_objeto_coordenado_gera_risco_com_evidencia_e_recomendacao():
    transcricao = "Vamos cancelar a reunião e o contrato."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [
        ("e1", "cancelar a reunião e o contrato", 6, 37)
    ]
    assert resposta.churn.evidencias == ["e1"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]
