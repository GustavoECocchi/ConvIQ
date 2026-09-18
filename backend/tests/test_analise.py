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
    assert resposta.versao_analise == "0.1"
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
