import pytest

from app.schemas.comum import ChurnSituacao, Vinculo
from app.schemas.reuniao import AnaliseTextoRequest
from app.services.sinais_comerciais import analisar_sinais_comerciais


def _analisar_via_contrato(transcricao: str, vinculo: str):
    """Passa pelo schema de C01 antes do serviço, como B04 fará — assim os
    testes não exercitam só entradas (vazio, só espaço) que o contrato rejeita."""

    pedido = AnaliseTextoRequest(
        titulo="Reunião de alinhamento",
        empresa="Empresa Exemplo",
        vinculo=vinculo,
        transcricao=transcricao,
    )
    return analisar_sinais_comerciais(pedido.transcricao, pedido.vinculo)


SAUDACAO_DO_CONTRATO = "Bom dia a todos. Vamos seguir a pauta de hoje."  # exemplo 3 de C01


@pytest.mark.parametrize("vinculo", ["cliente", "nao_informado"])
def test_entrada_valida_sem_conteudo_comercial_e_informacao_insuficiente(vinculo):
    """B03-R01: antes, `informacao_insuficiente` só saía para texto vazio, que
    C01 rejeita — o estado era inalcançável para entradas válidas."""

    resultado = _analisar_via_contrato(SAUDACAO_DO_CONTRATO, vinculo)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.churn.evidencias == []
    assert resultado.evidencias == []


@pytest.mark.parametrize(
    "transcricao",
    [
        "Obrigado pela presença, até a próxima semana.",
        "Vamos marcar a próxima conversa para quinta-feira.",
    ],
)
def test_outras_entradas_validas_sem_conteudo_comercial_tambem_sao_insuficientes(transcricao):
    """A regra não decora a frase do contrato: vale para qualquer texto sem
    vocabulário comercial, risco, oportunidade, produto ou concorrente."""

    resultado = _analisar_via_contrato(transcricao, "cliente")

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE


@pytest.mark.parametrize(
    "transcricao",
    [
        "O suporte foi excelente e o contrato segue normal.",  # vocabulário da relação
        "Estamos muito satisfeitos com a implantação.",  # satisfação declarada
        "Ouvimos falar bem da Oracle numa conferência.",  # concorrente = conteúdo avaliável
        "Queremos conhecer o Fluig.",  # oportunidade + produto = conteúdo avaliável
    ],
)
def test_conteudo_comercial_sem_risco_e_avaliado_como_sem_sinal(transcricao):
    resultado = _analisar_via_contrato(transcricao, "cliente")

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []


def test_prospect_com_saudacao_continua_nao_aplicavel():
    resultado = _analisar_via_contrato(SAUDACAO_DO_CONTRATO, "prospect")

    assert resultado.churn.situacao is ChurnSituacao.NAO_APLICAVEL


def test_vinculo_nao_informado_diferencia_insuficiente_de_risco_explicito():
    """Vínculo desconhecido não presume prospect nem baixo risco: sem conteúdo
    é insuficiente; com risco explícito é sinal detectado."""

    insuficiente = _analisar_via_contrato(SAUDACAO_DO_CONTRATO, "nao_informado")
    com_risco = _analisar_via_contrato("Vamos cancelar o contrato no fim do mês.", "nao_informado")

    assert insuficiente.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert com_risco.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(com_risco.churn.evidencias) == 1


def test_prospect_sempre_recebe_churn_nao_aplicavel_mesmo_com_linguagem_de_risco():
    """Regra de produto: prospect recebe churn não aplicável."""

    resultado = analisar_sinais_comerciais(
        "Estamos pensando em cancelar e reavaliar tudo.", Vinculo.PROSPECT
    )

    assert resultado.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert resultado.churn.evidencias == []


def test_prospect_ainda_recebe_oportunidades_e_produtos():
    """`nao_aplicavel` é só sobre churn; o resto da análise continua."""

    resultado = analisar_sinais_comerciais(
        "Temos interesse em conhecer o Fluig.", Vinculo.PROSPECT
    )

    assert resultado.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert len(resultado.oportunidades) == 2  # "interesse" e "conhecer"
    assert resultado.produtos == ["Fluig"]


def test_concorrente_isolado_nao_implica_churn():
    """Regra de produto: menção isolada a concorrente não comprova intenção de troca."""

    resultado = analisar_sinais_comerciais(
        "Ouvimos falar bem da Oracle numa conferência.", Vinculo.CLIENTE
    )

    assert resultado.concorrentes == ["Oracle"]
    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []
    assert resultado.oportunidades == []


def test_risco_e_oportunidade_podem_coexistir():
    """Regra de produto: risco e oportunidade podem coexistir. Mesmo texto do
    exemplo do contrato C01 (docs/contratos/analise-texto.md)."""

    resultado = analisar_sinais_comerciais(
        "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.", Vinculo.CLIENTE
    )

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resultado.churn.evidencias) == 1
    assert len(resultado.oportunidades) == 1
    assert resultado.produtos == ["Fluig"]
    # evidências de churn e de oportunidade não colidem de ID
    assert resultado.churn.evidencias[0] != resultado.oportunidades[0].evidencias[0]


def test_conteudo_comercial_sem_risco_e_sem_sinal_detectado():
    """Conversa sobre a relação comercial (contrato, suporte), sem linguagem
    de risco: avaliada, sem sinal — o que não é o mesmo que baixo risco."""

    resultado = analisar_sinais_comerciais(
        "O suporte foi excelente e o contrato segue normal.", Vinculo.CLIENTE
    )

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []


def test_transcricao_vazia_e_informacao_insuficiente_para_churn():
    for transcricao in ("", "   \n\t "):
        resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)
        assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
        assert resultado.churn.evidencias == []
        assert resultado.oportunidades == []
        assert resultado.produtos == []
        assert resultado.concorrentes == []


def test_vinculo_nao_informado_e_avaliado_normalmente_nao_presume_baixo_risco():
    """Vínculo desconhecido não é tratado como prospect nem como baixo risco
    automático — é avaliado como qualquer outro texto."""

    resultado = analisar_sinais_comerciais(
        "Vamos cancelar o contrato no fim do mês.", Vinculo.NAO_INFORMADO
    )

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO


def test_produtos_detectados_com_nomes_canonicos():
    resultado = analisar_sinais_comerciais(
        "Hoje usamos o protheus e o RM, e temos interesse no fluig.", Vinculo.CLIENTE
    )

    assert resultado.produtos == ["Protheus", "RM", "Fluig"]


def test_concorrentes_detectados_sem_duplicar():
    resultado = analisar_sinais_comerciais(
        "Comparamos com SAP e também com sap novamente, além da Oracle.", Vinculo.CLIENTE
    )

    assert resultado.concorrentes == ["SAP", "Oracle"]


def test_evidencia_de_churn_aponta_para_trecho_real():
    transcricao = "No mês passado, decidimos cancelar dois módulos."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    evidencia = resultado.churn.evidencias
    assert len(evidencia) == 1
    ev = next(e for e in resultado.evidencias if e.id == evidencia[0])
    assert ev.trecho == "cancelar"
    assert transcricao[ev.inicio:ev.fim] == "cancelar"


def test_multiplas_oportunidades_geram_evidencias_distintas():
    transcricao = "Queremos integrar o sistema e depois expandir para outra filial."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert len(resultado.oportunidades) == 2
    ids = [o.evidencias[0] for o in resultado.oportunidades]
    assert len(set(ids)) == 2
    for oportunidade in resultado.oportunidades:
        ev = next(e for e in resultado.evidencias if e.id == oportunidade.evidencias[0])
        assert transcricao[ev.inicio:ev.fim] == ev.trecho


@pytest.mark.parametrize(
    "transcricao",
    [
        "Eles cancelaram a visita de amanhã.",  # "cancelar" + "am", sem fronteira
        "A diretoria reavaliaria a decisão, mas ainda não decidiu.",  # "reavaliar" + "ia"
    ],
)
def test_radical_dentro_de_outra_palavra_nao_e_sinal_de_risco(transcricao):
    """Fronteira de palavra: "cancelaram"/"reavaliaria" não são a palavra
    inteira "cancelar"/"reavaliar", mesmo contendo o radical como prefixo.
    O que importa aqui é não virar risco; sem conteúdo comercial no resto da
    frase, a situação correta é `informacao_insuficiente`."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is not ChurnSituacao.SINAL_DETECTADO
    assert resultado.churn.evidencias == []
    assert resultado.evidencias == []
