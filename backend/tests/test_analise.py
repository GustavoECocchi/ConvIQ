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
    assert resposta.versao_analise == "0.6"
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
    oportunidade apontam para o ID novo. B13: a evidência da oportunidade é
    a intenção inteira ("queremos conhecer o Fluig"), não só "conhecer"."""

    transcricao = "Não gostei do atendimento, mas queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [
        ("e1", "Não gostei"),
        ("e2", "queremos conhecer o Fluig"),
    ]
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho
    assert resposta.oportunidades[0].evidencias == ["e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"]]
    # "atendimento" é contexto comercial; nenhum padrão de risco → avaliado, sem sinal
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resposta.produtos == ["Fluig"]
    assert resposta.versao_analise == "0.6"


def test_negacao_fechada_na_virgula_nao_inverte_elogio_nem_apaga_oportunidade():
    """B11-R01 na composição: "sem problemas" só suprime "problemas"; o elogio
    após a vírgula e a oportunidade após o "e" seguem intactos."""

    transcricao = "Sem problemas com o suporte, estamos satisfeitos e queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.POSITIVO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [
        ("e1", "satisfeitos"),
        ("e2", "queremos conhecer o Fluig"),
    ]
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
        ("e3", "Queremos conhecer o Fluig"),
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
        ("e3", "Queremos conhecer o Fluig", 37, 62),
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
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [
        ("e1", "insatisfeitos"),
        ("e2", "Queremos conhecer o Fluig"),
    ]
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


def test_interesse_negado_nao_gera_oportunidade_nem_recomendacao_na_composicao():
    """B13 na composição: antes, "Não temos interesse em conhecer o Fluig."
    gerava duas oportunidades e duas recomendações. O produto continua no
    catálogo e o churn é avaliado, sem sinal."""

    resposta = compor_analise_texto(_pedido("Não temos interesse em conhecer o Fluig.", "cliente"))

    assert resposta.oportunidades == []
    assert resposta.recomendacoes == []
    assert resposta.evidencias == []
    assert resposta.produtos == ["Fluig"]
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO


def test_modulo_citado_sem_intencao_nao_gera_oportunidade():
    resposta = compor_analise_texto(_pedido("O módulo atual está instalado.", "cliente"))

    assert resposta.oportunidades == []
    assert resposta.recomendacoes == []
    assert resposta.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE


def test_so_a_intencao_afirmativa_depois_do_mas_gera_oportunidade_e_recomendacao():
    transcricao = "Não queremos o Fluig, mas temos interesse no Protheus."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "interesse no Protheus")]
    assert len(resposta.oportunidades) == 1
    assert resposta.oportunidades[0].evidencias == ["e1"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]
    assert resposta.produtos == ["Fluig", "Protheus"]
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_necessidade_comercial_gera_oportunidade_na_composicao():
    transcricao = "Precisamos automatizar o faturamento."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [
        ("e1", "Precisamos automatizar o faturamento", 0, 36)
    ]
    assert resposta.oportunidades[0].evidencias == ["e1"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO  # "faturamento" é contexto comercial


def test_acao_alheia_posterior_nao_apaga_oportunidade_nem_recomendacao():
    """B13-R01 na composição: antes, "Queremos o Fluig e conhecer a cidade."
    não tinha oportunidade nem recomendação, embora "Queremos o Fluig." tivesse."""

    transcricao = "Queremos o Fluig e conhecer a cidade."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [("e1", "Queremos o Fluig", 0, 16)]
    assert resposta.oportunidades[0].evidencias == ["e1"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]
    assert resposta.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO


def test_sistema_solar_nao_gera_oportunidade_nem_torna_churn_avaliavel():
    """B13-R02 na composição: sem oportunidade, evidência ou recomendação, e
    churn `informacao_insuficiente` (antes, sem_sinal_detectado por causa da
    oportunidade indevida)."""

    resposta = compor_analise_texto(_pedido("Queremos integrar o sistema solar.", "cliente"))

    assert resposta.oportunidades == []
    assert resposta.evidencias == []
    assert resposta.recomendacoes == []
    assert resposta.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE


# B14 — acento decomposto (NFD) na composição ----------------------------------


def _nfd(texto: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", texto)


@pytest.mark.parametrize(
    "transcricao",
    [
        "O suporte é péssimo. Queremos conhecer o Fluig.",
        "Não estamos satisfeitos com o suporte. Queremos conhecer o Fluig.",
        "Estamos insatisfeitos com o suporte, mas vamos cancelar o contrato.",
    ],
)
def test_nfc_e_nfd_geram_a_mesma_analise_completa(transcricao):
    """B14 na composição: sentimento, churn, oportunidades, recomendações e IDs
    iguais nas duas formas; só os recortes e índices mudam, e todo recorte NFD
    é literal sobre o eco devolvido."""

    nfc = compor_analise_texto(_pedido(transcricao, "cliente"))
    decomposto = _nfd(transcricao)
    nfd = compor_analise_texto(_pedido(decomposto, "cliente"))

    assert nfd.transcricao == decomposto
    assert nfd.sentimento is nfc.sentimento
    assert nfd.churn == nfc.churn
    assert [o.evidencias for o in nfd.oportunidades] == [o.evidencias for o in nfc.oportunidades]
    assert [r.evidencias for r in nfd.recomendacoes] == [r.evidencias for r in nfc.recomendacoes]
    assert [e.id for e in nfd.evidencias] == [e.id for e in nfc.evidencias]
    assert [_nfd(e.trecho) for e in nfc.evidencias] == [e.trecho for e in nfd.evidencias]
    for evidencia in nfd.evidencias:
        assert nfd.transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_ordem_das_evidencias_nfd_segue_a_posicao_na_transcricao():
    transcricao = _nfd("Não estamos satisfeitos com o suporte. Queremos conhecer o Fluig.")

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    posicoes = [e.inicio for e in resposta.evidencias]
    assert posicoes == sorted(posicoes)
    assert [e.id for e in resposta.evidencias] == ["e1", "e2", "e3"]
    assert resposta.evidencias[-1].trecho == "Queremos conhecer o Fluig"
    assert resposta.evidencias[-1].inicio == transcricao.index("Queremos")


def test_espaco_inicial_e_removido_do_eco_e_os_indices_valem_para_o_eco():
    """O contrato C01 remove espaços das pontas; os índices são relativos ao
    eco devolvido, não à entrada bruta."""

    bruta = "   " + _nfd("O suporte é péssimo.   ")

    resposta = compor_analise_texto(_pedido(bruta, "cliente"))

    assert resposta.transcricao == bruta.strip()
    evidencia = resposta.evidencias[0]
    assert evidencia.trecho == _nfd("péssimo")
    assert evidencia.inicio == resposta.transcricao.index(evidencia.trecho)
    assert bruta[evidencia.inicio:evidencia.fim] != evidencia.trecho
    assert resposta.transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_versao_da_analise_com_nfd_e_0_6():
    assert compor_analise_texto(_pedido(_nfd("O suporte é péssimo."), "cliente")).versao_analise == "0.6"


# B19 — evidência compartilhada por intervalo exato ------------------------


def _ids_validos(resposta) -> None:
    """Invariantes de B19: IDs consecutivos, referências existentes e sem
    repetição dentro de cada lista, recortes literais."""

    ids = [e.id for e in resposta.evidencias]
    assert ids == [f"e{n}" for n in range(1, len(ids) + 1)]
    listas = [resposta.churn.evidencias]
    listas += [o.evidencias for o in resposta.oportunidades]
    listas += [r.evidencias for r in resposta.recomendacoes]
    for lista in listas:
        assert len(lista) == len(set(lista))
        assert set(lista) <= set(ids)
    assert len({(e.inicio, e.fim, e.trecho) for e in resposta.evidencias}) == len(ids)
    for evidencia in resposta.evidencias:
        assert resposta.transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


@pytest.mark.parametrize(
    ("transcricao", "trecho", "inicio", "fim"),
    [
        ("Estamos insatisfeitos.", "insatisfeitos", 8, 21),
        ("Não estamos satisfeitos.", "Não estamos satisfeitos", 0, 23),
    ],
)
def test_sentimento_e_risco_no_mesmo_intervalo_compartilham_uma_evidencia(transcricao, trecho, inicio, fim):
    """B19: antes, o sentimento e o risco geravam duas evidências idênticas
    (e1 e e2) e churn/recomendação citavam só a segunda."""

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [("e1", trecho, inicio, fim)]
    assert resposta.churn.evidencias == ["e1"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"]]
    _ids_validos(resposta)


def test_intervalos_aninhados_continuam_duas_evidencias():
    """Contraprova obrigatória: "insatisfeitos" (8–21) e "insatisfeitos com o
    suporte" (8–35) não são unidos; churn e recomendação citam a mais longa."""

    resposta = compor_analise_texto(_pedido("Estamos insatisfeitos com o suporte.", "cliente"))

    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [
        ("e1", "insatisfeitos", 8, 21),
        ("e2", "insatisfeitos com o suporte", 8, 35),
    ]
    assert resposta.churn.evidencias == ["e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2"]]
    _ids_validos(resposta)


def test_frase_repetida_em_posicoes_diferentes_mantem_duas_evidencias():
    """Unir pelo texto apagaria uma ocorrência válida: cada posição tem a sua
    evidência, e churn e recomendação citam as duas, na ordem."""

    transcricao = "Estamos insatisfeitos. Depois, estamos insatisfeitos."

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho, e.inicio) for e in resposta.evidencias] == [
        ("e1", "insatisfeitos", 8),
        ("e2", "insatisfeitos", transcricao.rindex("insatisfeitos")),
    ]
    assert resposta.churn.evidencias == ["e1", "e2"]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1", "e2"]]
    _ids_validos(resposta)


def test_nfd_compartilha_a_evidencia_com_recorte_literal_mais_longo():
    import unicodedata

    transcricao = unicodedata.normalize("NFD", "Não estamos satisfeitos.")

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.inicio, e.fim) for e in resposta.evidencias] == [("e1", 0, 24)]
    assert resposta.evidencias[0].trecho == transcricao[:24]
    assert resposta.churn.evidencias == ["e1"]
    _ids_validos(resposta)


def test_emoji_e_espacos_antes_do_sinal_nao_deslocam_os_indices_compartilhados():
    resposta = compor_analise_texto(_pedido("   😀 Estamos insatisfeitos.", "cliente"))

    assert resposta.transcricao == "😀 Estamos insatisfeitos."
    assert [(e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [("insatisfeitos", 10, 23)]
    assert resposta.churn.evidencias == ["e1"]
    _ids_validos(resposta)


def test_risco_compartilhado_e_oportunidade_vizinha_coexistem_e_sao_recomendados():
    resposta = compor_analise_texto(_pedido("Estamos insatisfeitos. Queremos conhecer o Fluig.", "cliente"))

    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "insatisfeitos"), ("e2", "Queremos conhecer o Fluig")]
    assert resposta.churn.evidencias == ["e1"]
    assert [o.evidencias for o in resposta.oportunidades] == [["e2"]]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e1"], ["e2"]]
    assert resposta.produtos == ["Fluig"]
    _ids_validos(resposta)


def test_prospect_mantem_churn_nao_aplicavel_e_so_a_evidencia_de_sentimento():
    resposta = compor_analise_texto(_pedido("Estamos insatisfeitos.", "prospect"))

    assert resposta.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert resposta.churn.evidencias == []
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "insatisfeitos")]
    assert resposta.recomendacoes == []
    _ids_validos(resposta)


@pytest.mark.parametrize("transcricao", ["Hoje usamos o Protheus e o RM.", "Bom dia a todos.", "Ouvimos falar da Oracle."])
def test_catalogo_e_texto_sem_sinal_nao_ganham_evidencia(transcricao):
    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert resposta.evidencias == []
    assert resposta.churn.evidencias == []
    _ids_validos(resposta)


def test_duplicata_exata_nao_adjacente_e_unida_sem_lacunas_nos_ids(monkeypatch):
    """Sintético: sentimento (8–21), comercial aninhada (8–35), comercial
    idêntica ao sentimento (8–21) e uma posterior. A duplicata exata não fica
    ao lado da original depois de ordenar por início, mas ainda é unida; os
    IDs finais não têm lacuna e a lista de churn não repete."""

    from app.schemas.analise import Churn, Evidencia, Oportunidade
    from app.services import analise as modulo
    from app.services.sentimento import ResultadoSentimento
    from app.services.sinais_comerciais import ResultadoSinaisComerciais

    transcricao = "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."
    sentimento = ResultadoSentimento(
        sentimento=Sentimento.NEGATIVO, evidencias=[Evidencia(id="e1", trecho="insatisfeitos", inicio=8, fim=21)]
    )
    comercial = ResultadoSinaisComerciais(
        churn=Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=["e1", "e2", "e1"]),
        oportunidades=[Oportunidade(descricao="Interesse.", evidencias=["e3"])],
        evidencias=[
            Evidencia(id="e1", trecho="insatisfeitos com o suporte", inicio=8, fim=35),
            Evidencia(id="e2", trecho="insatisfeitos", inicio=8, fim=21),
            Evidencia(id="e3", trecho="Queremos conhecer o Fluig", inicio=37, fim=62),
        ],
    )
    monkeypatch.setattr(modulo, "analisar_sentimento", lambda _t: sentimento)
    monkeypatch.setattr(modulo, "analisar_sinais_comerciais", lambda _t, _v: comercial)

    resposta = compor_analise_texto(_pedido(transcricao, "cliente"))

    assert [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias] == [
        ("e1", "insatisfeitos", 8, 21),
        ("e2", "insatisfeitos com o suporte", 8, 35),
        ("e3", "Queremos conhecer o Fluig", 37, 62),
    ]
    assert resposta.churn.evidencias == ["e2", "e1"]
    assert [o.evidencias for o in resposta.oportunidades] == [["e3"]]
    assert [r.evidencias for r in resposta.recomendacoes] == [["e2", "e1"], ["e3"]]
    _ids_validos(resposta)


def test_versao_da_analise_com_evidencia_compartilhada_e_0_6():
    assert compor_analise_texto(_pedido("Estamos insatisfeitos.", "cliente")).versao_analise == "0.6"
