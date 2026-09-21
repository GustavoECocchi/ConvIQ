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


def test_satisfacao_negada_gera_risco_e_evidencia_duplicada_do_mesmo_trecho():
    """B12 na composição: "Não estamos satisfeitos" é evidência tanto do
    sentimento (B11) quanto do risco (B12) — o mesmo trecho, duas evidências
    com IDs distintos, como o README já documenta para "insatisfeito"."""

    transcricao = "Não estamos satisfeitos com o suporte. Queremos conhecer o Fluig."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.NEGATIVO
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    trechos_negados = [e for e in resposta.evidencias if e.trecho == "Não estamos satisfeitos"]
    assert len(trechos_negados) == 2
    assert trechos_negados[0].id != trechos_negados[1].id
    assert resposta.churn.evidencias[0] in {e.id for e in trechos_negados}
    assert len(resposta.oportunidades) == 1
    assert resposta.produtos == ["Fluig"]
    assert len(resposta.recomendacoes) == 2
    for evidencia in resposta.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_acao_de_risco_com_objeto_distante_na_mesma_frase_gera_recomendacao():
    """B12: ação e objeto continuam ligados numa frase mais longa, mesmo sem
    nenhum outro sinal de sentimento na transcrição."""

    transcricao = "Se o suporte continuar assim, vamos cancelar o contrato."
    pedido = _pedido(transcricao, "cliente")

    resposta = compor_analise_texto(pedido)

    assert resposta.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resposta.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [(e.id, e.trecho) for e in resposta.evidencias] == [("e1", "cancelar")]
    assert len(resposta.recomendacoes) == 1
