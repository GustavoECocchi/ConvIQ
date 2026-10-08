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
    """B12: "cancelar" só é risco com um objeto da relação comercial como
    complemento (aqui, "contrato"); a versão anterior deste teste usava
    "cancelar dois módulos", que deixou de ser risco (ver
    test_acao_de_risco_sem_objeto_comercial_e_insuficiente_isolada) porque
    "módulo" não é objeto da relação comercial no cartão B12. Revisão
    B12-R03: a evidência era só "cancelar", que não mostra por que é risco
    comercial e não cancelamento de reunião; agora inclui o objeto."""

    transcricao = "No mês passado, decidimos cancelar o contrato."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    evidencia = resultado.churn.evidencias
    assert len(evidencia) == 1
    ev = next(e for e in resultado.evidencias if e.id == evidencia[0])
    assert ev.trecho == "cancelar o contrato"
    assert (ev.inicio, ev.fim) == (26, 45)
    assert transcricao[ev.inicio:ev.fim] == ev.trecho


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


# B12 — risco de cancelamento com contexto local (aceite do cartão) --------


def test_acao_de_risco_negada_nao_gera_sinal_mas_contrato_ainda_e_contexto():
    """"Não vamos cancelar o contrato." não é risco (ação negada), mas
    "contrato" ainda é vocabulário da relação comercial: avaliado, sem sinal
    — não confirma baixo risco."""

    resultado = analisar_sinais_comerciais("Não vamos cancelar o contrato.", Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []


def test_acao_de_risco_sem_objeto_comercial_e_insuficiente_isolada():
    """"Cancelar" sozinho, sem contrato/serviço/fornecedor por perto, não é
    risco nem vira conteúdo comercial por si só."""

    resultado = analisar_sinais_comerciais("Vamos cancelar a reunião.", Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []


def test_acao_de_risco_com_objeto_comercial_gera_sinal():
    """Revisão B12-R03: a evidência inclui ação e objeto, não só "cancelar"."""

    resultado = analisar_sinais_comerciais("Vamos cancelar o contrato.", Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resultado.churn.evidencias) == 1
    ev = next(e for e in resultado.evidencias if e.id == resultado.churn.evidencias[0])
    assert ev.trecho == "cancelar o contrato"


def test_ameaca_condicional_real_preserva_o_sinal():
    """A condição antes da vírgula não impede a ligação ação–objeto, que é
    local ao complemento da ação. Revisão B12-R03: a evidência começa no
    "Se" que abre a frase, para a ameaça não parecer decisão tomada."""

    transcricao = "Se o suporte continuar assim, vamos cancelar o contrato."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resultado.churn.evidencias) == 1
    ev = next(e for e in resultado.evidencias if e.id == resultado.churn.evidencias[0])
    assert ev.trecho == "Se o suporte continuar assim, vamos cancelar o contrato"
    assert (ev.inicio, ev.fim) == (0, len(transcricao) - 1)


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos reavaliar a pauta.",  # "reavaliar" sem objeto comercial
        "O sistema solar é extenso.",  # "sistema" fora do sentido comercial
    ],
)
def test_acao_ou_termo_generico_sem_objeto_nao_torna_conversa_comercial(transcricao):
    """B12: nem toda ocorrência de um radical de risco ou de um termo antes
    genérico basta para tornar a conversa avaliável."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []


def test_satisfacao_negada_sinaliza_risco_como_insatisfeito():
    """"Não estamos satisfeitos" continua sinalizando risco, sem exigir
    sempre a palavra "cancelar" — o espelho de "insatisfeitos". Revisão
    B12-R03: a evidência inclui o complemento "com o suporte"; antes era só
    "Não estamos satisfeitos", sem dizer com o que."""

    transcricao = "Não estamos satisfeitos com o suporte."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resultado.churn.evidencias) == 1
    ev = next(e for e in resultado.evidencias if e.id == resultado.churn.evidencias[0])
    assert ev.trecho == "Não estamos satisfeitos com o suporte"
    assert transcricao[ev.inicio:ev.fim] == ev.trecho


def test_satisfacao_afirmada_nunca_e_risco():
    resultado = analisar_sinais_comerciais("Estamos muito satisfeitos com a implantação.", Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []


def test_insatisfeito_negado_deixa_de_ser_risco():
    """B12 aplica a mesma regra de negação a "insatisfeito": negar um
    problema não prova baixo risco, só suprime o sinal (não vira elogio)."""

    resultado = analisar_sinais_comerciais("Não estamos insatisfeitos.", Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.churn.evidencias == []


def test_risco_por_negacao_de_satisfacao_coexiste_com_oportunidade():
    """Risco e oportunidade continuam podendo coexistir, agora também
    quando o risco vem da negação de satisfação, não só de "cancelar"."""

    transcricao = "Não estamos satisfeitos com o suporte. Queremos conhecer o Fluig."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert len(resultado.oportunidades) == 1
    assert resultado.churn.evidencias[0] != resultado.oportunidades[0].evidencias[0]


def test_prospect_com_negacao_de_satisfacao_continua_nao_aplicavel():
    """Regra de produto preservada com a nova fonte de risco: prospect
    continua `nao_aplicavel`, mesmo com "não satisfeitos" no texto."""

    resultado = analisar_sinais_comerciais("Não estamos satisfeitos com o atendimento.", Vinculo.PROSPECT)

    assert resultado.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert resultado.churn.evidencias == []


# Revisão B12 (Opus) — ligação ação–objeto, evidência com contexto ----------


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a reunião sobre o contrato.",
        "Vamos reavaliar a pauta com o fornecedor.",
        "O contrato continua vigente, vamos cancelar a reunião.",
        "Vamos cancelar a reunião, mas não o contrato.",
        "Vamos cancelar a reunião e não o contrato.",
        "Vamos cancelar a reunião e falar do contrato.",
    ],
)
def test_objeto_comercial_fora_do_complemento_da_acao_nao_gera_risco(transcricao):
    """B12-R02: antes, qualquer "contrato"/"fornecedor" na mesma frase ligava
    a ação a ele — a reunião cancelada virava risco de churn. O objeto da
    ação é o núcleo do seu complemento ("a reunião", "a pauta"); um contrato
    que só modifica esse núcleo, vem antes da ação ou aparece negado não é
    o que se cancela. Com "contrato"/"fornecedor" no texto, a conversa é
    avaliável: sem sinal, não informação insuficiente."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []
    assert resultado.evidencias == []


@pytest.mark.parametrize(
    ("transcricao", "trecho"),
    [
        ("Vamos reavaliar o fornecedor.", "reavaliar o fornecedor"),
        ("Decidimos rescindir o contrato.", "rescindir o contrato"),
        ("Vamos rescindir o nosso contrato.", "rescindir o nosso contrato"),
        ("Vamos cancelar todos os contratos.", "cancelar todos os contratos"),
        ("Pedimos o cancelamento do contrato.", "cancelamento do contrato"),
        ("Vamos cancelar com o fornecedor.", "cancelar com o fornecedor"),
        ("Vamos cancelar imediatamente o serviço.", "cancelar imediatamente o serviço"),
        ("Vamos cancelar a reunião e o contrato.", "cancelar a reunião e o contrato"),
    ],
)
def test_objeto_comercial_no_complemento_da_acao_gera_risco_com_evidencia_completa(transcricao, trecho):
    """Contraprova de B12-R02 e evidência de B12-R03: a ligação não exige
    palavras adjacentes — artigos, preposições, possessivos, quantificadores
    e advérbios curtos podem ficar entre ação e objeto, e "e" coordena um
    segundo objeto. A evidência vai da ação até o objeto, recorte literal."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [e.trecho for e in resultado.evidencias] == [trecho]
    ev = resultado.evidencias[0]
    assert resultado.churn.evidencias == [ev.id]
    assert transcricao[ev.inicio:ev.fim] == trecho


def test_condicao_com_negacao_propria_nao_suprime_a_ameaca():
    """A negação da condição ("não melhorar") fecha na vírgula e não alcança
    "cancelar"; a evidência mostra a condição inteira."""

    transcricao = "Se o suporte não melhorar, vamos cancelar o contrato."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [e.trecho for e in resultado.evidencias] == ["Se o suporte não melhorar, vamos cancelar o contrato"]


def test_se_fora_do_inicio_da_frase_nao_estende_a_evidencia():
    """Só o "Se" que abre a frase é condição; "decidiu-se" é pronome."""

    resultado = analisar_sinais_comerciais("Decidiu-se cancelar o contrato.", Vinculo.CLIENTE)

    assert [e.trecho for e in resultado.evidencias] == ["cancelar o contrato"]


def test_acao_repetida_gera_evidencias_distintas_nas_posicoes_reais():
    transcricao = "Vamos cancelar o contrato. Depois, vamos cancelar o contrato."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert [e.trecho for e in resultado.evidencias] == ["cancelar o contrato", "cancelar o contrato"]
    assert [(e.inicio, e.fim) for e in resultado.evidencias] == [(6, 25), (41, 60)]
    for ev in resultado.evidencias:
        assert transcricao[ev.inicio:ev.fim] == ev.trecho
    assert resultado.churn.evidencias == ["e1", "e2"]


@pytest.mark.parametrize(
    ("transcricao", "trechos"),
    [
        ("Estamos insatisfeitos com o suporte.", ["insatisfeitos com o suporte"]),
        ("Estamos frustrados com o atendimento.", ["frustrados com o atendimento"]),
        ("Estamos insatisfeitos.", ["insatisfeitos"]),
        (
            "Estamos insatisfeitos com o suporte e vamos cancelar o contrato.",
            ["insatisfeitos com o suporte", "cancelar o contrato"],
        ),
        ("Estamos insatisfeitos com o suporte, mas o contrato segue.", ["insatisfeitos com o suporte"]),
    ],
)
def test_evidencia_de_insatisfacao_inclui_o_complemento_com(transcricao, trechos):
    """B12-R03: o complemento "com ..." mostra com o que é a insatisfação;
    termina em vírgula, adversativa ou "e". Sem complemento, a evidência
    continua sendo a palavra."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [e.trecho for e in resultado.evidencias] == trechos
    for ev in resultado.evidencias:
        assert transcricao[ev.inicio:ev.fim] == ev.trecho


@pytest.mark.parametrize(
    "transcricao",
    [
        "Estamos insatisfeitos com o clima.",
        "Não estamos satisfeitos com o almoço.",
        "Estamos frustrados com o trânsito.",
        "Não estamos satisfeitos com o café.",
        "Estamos insatisfeitos com o almoço e o café.",
        "Estamos satisfeitos com o almoço.",  # afirmado: também não é contexto comercial
    ],
)
def test_insatisfacao_com_tema_alheio_isolada_e_informacao_insuficiente(transcricao):
    """B12-R04: antes, insatisfação com qualquer complemento era risco (regra
    de B03 para "insatisfeito", espelhada em B12 para "não satisfeito") e
    estas frases geravam churn e recomendação de retenção. Com o núcleo do
    complemento em `_PADROES_TEMA_ALHEIO` e nenhum termo da relação, não há
    risco; sem outro contexto comercial, não há base para avaliar churn."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.churn.evidencias == []
    assert resultado.evidencias == []


@pytest.mark.parametrize(
    "transcricao",
    [
        "Estamos insatisfeitos com o clima, mas o contrato segue normal.",
        "Não estamos satisfeitos com o almoço. O suporte foi excelente.",
        "Estamos insatisfeitos com o clima e o contrato segue normal.",  # "e" abre outra oração
    ],
)
def test_insatisfacao_com_tema_alheio_e_contexto_comercial_independente_e_sem_sinal(transcricao):
    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.evidencias == []


def test_tema_alheio_nao_apaga_outro_sinal_real_de_risco():
    """A insatisfação com o clima não sustenta o risco; o cancelamento do
    contrato, sim — e só ele vira evidência de churn."""

    transcricao = "Estamos insatisfeitos com o clima e vamos cancelar o contrato."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [e.trecho for e in resultado.evidencias] == ["cancelar o contrato"]


@pytest.mark.parametrize(
    ("transcricao", "trecho"),
    [
        ("Estamos insatisfeitos com o suporte.", "insatisfeitos com o suporte"),
        ("Estamos frustrados com o atendimento.", "frustrados com o atendimento"),
        ("Não estamos satisfeitos com o serviço.", "Não estamos satisfeitos com o serviço"),
        ("Estamos frustrados com o atraso.", "frustrados com o atraso"),
        ("Estamos insatisfeitos com a demora.", "insatisfeitos com a demora"),
        ("Estamos insatisfeitos com o clima da parceria.", "insatisfeitos com o clima da parceria"),
        ("Estamos insatisfeitos com o almoço e com o suporte.", "insatisfeitos com o almoço e com o suporte"),
    ],
)
def test_insatisfacao_que_nao_e_inequivocamente_alheia_continua_risco(transcricao, trecho):
    """Contraprova de B12-R04: só tema da lista, sem termo da relação, deixa
    de ser risco. Complemento fora da lista ("o atraso", "a demora") segue a
    regra de B03; tema alheio com termo da relação no complemento ("da
    parceria", "e com o suporte") não é inequívoco e continua risco."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert [e.trecho for e in resultado.evidencias] == [trecho]
    ev = resultado.evidencias[0]
    assert transcricao[ev.inicio:ev.fim] == trecho


@pytest.mark.parametrize(
    "transcricao",
    [
        "Estamos insatisfeitos com o hotel.",  # tema alheio fora da lista
        "O almoço nos deixou insatisfeitos.",  # tema antes da palavra, sem "com"
    ],
)
def test_limite_b12_r04_tema_alheio_fora_da_regra_ainda_e_risco(transcricao):
    """Limites documentados da regra de B12-R04: lista fechada de temas e
    só o complemento "com ..." depois da palavra."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a reunião e o contrato continua vigente.",
        "Vamos cancelar a reunião e o fornecedor será avisado.",
        "Vamos cancelar a reunião e o contrato do fornecedor continua vigente.",
    ],
)
def test_sujeito_de_outra_oracao_depois_do_e_nao_e_objeto_cancelado(transcricao):
    """B12-R06: antes, o substantivo depois do "e" era tratado como segundo
    objeto da ação mesmo quando sujeito de outra oração ("o contrato
    continua vigente"). Um membro coordenado só conta se termina como
    sintagma nominal."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.churn.evidencias == []
    assert resultado.evidencias == []


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a reunião e o contrato.",
        "Vamos cancelar a reunião ou o contrato.",
        "Vamos cancelar a reunião e o contrato de suporte.",
        "Vamos cancelar a reunião e o contrato atual.",
        "Vamos cancelar a reunião e o contrato no fim do mês.",
    ],
)
def test_objeto_coordenado_que_termina_como_sintagma_nominal_gera_risco(transcricao):
    """Contraprova de B12-R06: o contrato coordenado também é objeto da ação,
    com ou sem modificador preposicionado; a evidência vai até o objeto."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    ev = resultado.evidencias[0]
    assert len(resultado.evidencias) == 1
    assert ev.trecho in {"cancelar a reunião e o contrato", "cancelar a reunião ou o contrato"}
    assert transcricao[ev.inicio:ev.fim] == ev.trecho


def test_objeto_direto_seguido_de_outra_oracao_continua_risco():
    """O objeto direto não precisa terminar a oração: "o suporte continua"
    depois do "e" só fica fora do complemento."""

    resultado = analisar_sinais_comerciais("Vamos cancelar o contrato e o suporte continua.", Vinculo.CLIENTE)

    assert [e.trecho for e in resultado.evidencias] == ["cancelar o contrato"]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Vamos cancelar a renovação do contrato.",  # núcleo "renovação" não é objeto de risco
        "Vamos cancelar, infelizmente, o contrato.",  # vírgula encerra o complemento
        "O contrato, vamos cancelar.",  # objeto antes da ação
        "Vamos cancelar a reunião e o contrato hoje.",  # "hoje" encerra o sintagma (B12-R06)
    ],
)
def test_limites_da_ligacao_acao_objeto(transcricao):
    """Limites documentados da ligação local de B12-R02/R06: o objeto
    precisa ser o núcleo do complemento, depois da ação e antes de vírgula;
    um objeto coordenado precisa terminar como sintagma nominal."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado.evidencias == []


# B13 — oportunidade somente com intenção comercial -------------------------


def _trechos_das_oportunidades(resultado) -> list[str]:
    por_id = {e.id: e for e in resultado.evidencias}
    return [por_id[o.evidencias[0]].trecho for o in resultado.oportunidades]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Não temos interesse em conhecer o Fluig.",
        "Não queremos conhecer o Fluig.",
        "Sem interesse no Protheus.",
        "O módulo atual está instalado.",
        "Quero conhecer a cidade.",
        "Quero conhecer o novo diretor.",
        "Interessante o módulo atual.",
        "Queremos conhecer o hotel e o suporte técnico.",
    ],
)
def test_sem_intencao_afirmativa_com_objeto_comercial_nao_gera_oportunidade(transcricao):
    """B13: antes, "interesse", "conhecer" e "módulo" geravam oportunidade
    em qualquer contexto (negados, sem objeto comercial ou só como menção
    nominal). Agora o gatilho precisa estar fora de uma negação e ter um
    objeto comercial como núcleo do seu complemento."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.oportunidades == []
    assert resultado.evidencias == []


@pytest.mark.parametrize(
    ("transcricao", "trecho"),
    [
        ("Queremos conhecer o Fluig.", "Queremos conhecer o Fluig"),
        ("Precisamos automatizar o faturamento.", "Precisamos automatizar o faturamento"),
        ("Estamos interessados no Datasul.", "interessados no Datasul"),
        ("Queremos contratar um serviço de suporte.", "Queremos contratar um serviço"),
        ("Gostaríamos de avaliar a plataforma.", "Gostaríamos de avaliar a plataforma"),
        ("Precisamos de um módulo de faturamento.", "Precisamos de um módulo"),
        ("Queremos o Fluig.", "Queremos o Fluig"),
        ("Queremos muito conhecer o Fluig.", "Queremos muito conhecer o Fluig"),
    ],
)
def test_intencao_afirmativa_com_objeto_comercial_gera_oportunidade_com_evidencia_literal(transcricao, trecho):
    """Critérios 3 e 4 do cartão B13 e variantes: a evidência vai do início da
    intenção ao fim do objeto, recorte literal e contínuo da transcrição."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == [trecho]
    ev = resultado.evidencias[0]
    assert transcricao[ev.inicio:ev.fim] == trecho
    assert resultado.oportunidades[0].evidencias == [ev.id]


def test_negacao_nao_alcanca_a_oracao_depois_do_mas():
    """Critério 6: "Não queremos o Fluig" não gera oportunidade; "temos
    interesse no Protheus" depois da vírgula e do "mas" gera. O catálogo
    ainda lista as duas marcas citadas."""

    transcricao = "Não queremos o Fluig, mas temos interesse no Protheus."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["interesse no Protheus"]
    assert resultado.produtos == ["Fluig", "Protheus"]


def test_negacao_nao_alcanca_a_frase_seguinte():
    resultado = analisar_sinais_comerciais("Não temos interesse. Queremos conhecer o Fluig.", Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["Queremos conhecer o Fluig"]


def test_interesse_negado_mantem_o_produto_no_catalogo_e_o_churn_avaliavel():
    """A menção a Fluig continua em `produtos` (B13 muda a lista de
    oportunidades, não apaga nomes citados), e produto é conteúdo comercial
    independente: o churn é avaliado, sem sinal."""

    resultado = analisar_sinais_comerciais("Não temos interesse em conhecer o Fluig.", Vinculo.CLIENTE)

    assert resultado.oportunidades == []
    assert resultado.produtos == ["Fluig"]
    assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO


@pytest.mark.parametrize(
    "transcricao",
    [
        "O módulo atual está instalado.",
        "Quero conhecer a cidade.",
        "Quero conhecer o novo diretor.",
    ],
)
def test_ocorrencia_rejeitada_como_oportunidade_nao_torna_o_churn_avaliavel(transcricao):
    """B13: uma palavra rejeitada como oportunidade ("módulo", "conhecer")
    não conta, por si só, como conteúdo comercial: sem outro contexto, o
    churn é `informacao_insuficiente`, como em B03-R01."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE


def test_intencao_repetida_gera_oportunidades_em_posicoes_distintas():
    transcricao = "Queremos conhecer o Fluig. Queremos conhecer o Fluig."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert [(e.inicio, e.fim) for e in resultado.evidencias] == [(0, 25), (27, 52)]
    assert len({o.evidencias[0] for o in resultado.oportunidades}) == 2


def test_duas_acoes_na_mesma_frase_mantem_duas_oportunidades_com_seus_objetos():
    transcricao = "Queremos conhecer o Fluig e expandir as licenças do Protheus."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["Queremos conhecer o Fluig", "expandir as licenças"]


def test_gatilhos_encadeados_da_mesma_intencao_nao_sao_agrupados_aqui():
    """Fora do escopo de B13: agrupar "interesse em conhecer o Fluig" numa
    só oportunidade é B17. Cada gatilho continua gerando a sua, agora com
    recortes distintos que mostram a intenção e o objeto."""

    resultado = analisar_sinais_comerciais("Temos interesse em conhecer o Fluig.", Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["interesse em conhecer o Fluig", "conhecer o Fluig"]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Eles conheceram o Fluig.",  # outra flexão, sem fronteira
        "Foi uma reunião interessante sobre o Fluig.",
        "O sistema está integrado ao Protheus.",
        "A automação do faturamento já existe.",
    ],
)
def test_palavras_parecidas_nao_sao_gatilho(transcricao):
    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.oportunidades == []


def test_risco_e_oportunidade_coexistem_na_mesma_frase_com_evidencias_proprias():
    transcricao = "Queremos cancelar o contrato e conhecer o Fluig."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert _trechos_das_oportunidades(resultado) == ["conhecer o Fluig"]
    assert resultado.churn.evidencias[0] != resultado.oportunidades[0].evidencias[0]


def test_prospect_continua_recebendo_oportunidade_so_com_intencao():
    com_intencao = analisar_sinais_comerciais("Queremos conhecer o Fluig.", Vinculo.PROSPECT)
    sem_intencao = analisar_sinais_comerciais("Não temos interesse em conhecer o Fluig.", Vinculo.PROSPECT)

    assert com_intencao.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert len(com_intencao.oportunidades) == 1
    assert sem_intencao.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert sem_intencao.oportunidades == []


def test_concorrente_isolado_nao_vira_oportunidade_nem_risco():
    for transcricao in ("Ouvimos falar bem da Oracle numa conferência.", "Queremos conhecer a SAP."):
        resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

        assert resultado.oportunidades == []
        assert resultado.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO


def test_limite_b13_autoria_da_intencao_nao_e_identificada():
    """Limite da regra local, pinado para não parecer acerto: a regra não
    sabe quem quer ("O analista vai conhecer o Fluig." vira oportunidade).
    Atribuição de fala está fora do escopo (README, seção de oportunidades)."""

    resultado = analisar_sinais_comerciais("O analista vai conhecer o Fluig.", Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["conhecer o Fluig"]


def test_intencao_sobre_objeto_coordenado_comercial_e_oportunidade():
    """Revisão B13 (Opus): "Queremos conhecer a cidade e o Fluig." declara
    intenção de conhecer o Fluig, coordenado à cidade — não é falso positivo.
    O recorte vai até o objeto comercial e mostra a coordenação."""

    transcricao = "Queremos conhecer a cidade e o Fluig."

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["Queremos conhecer a cidade e o Fluig"]


@pytest.mark.parametrize(
    ("curta", "com_acao_alheia", "trecho"),
    [
        ("Queremos o Fluig.", "Queremos o Fluig e conhecer a cidade.", "Queremos o Fluig"),
        ("Precisamos de um módulo.", "Precisamos de um módulo e conhecer a cidade.", "Precisamos de um módulo"),
        ("Queremos o Fluig.", "Queremos o Fluig e não conhecer o Protheus.", "Queremos o Fluig"),
    ],
)
def test_gatilho_posterior_rejeitado_nao_apaga_a_intencao_anterior(curta, com_acao_alheia, trecho):
    """B13-R01: antes, uma forma de querer/precisar era descartada quando havia
    qualquer gatilho depois na oração, mesmo sem objeto comercial ou negado —
    acrescentar "e conhecer a cidade" apagava "Queremos o Fluig". Agora a
    intenção afirmativa é mantida e o gatilho alheio ou negado não gera outra."""

    antes = analisar_sinais_comerciais(curta, Vinculo.CLIENTE)
    depois = analisar_sinais_comerciais(com_acao_alheia, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(antes) == [trecho]
    assert _trechos_das_oportunidades(depois) == [trecho]
    ev = depois.evidencias[0]
    assert com_acao_alheia[ev.inicio:ev.fim] == trecho
    assert depois.oportunidades[0].evidencias == [ev.id]


def test_querer_e_gatilho_com_objetos_proprios_geram_duas_intencoes():
    """B13-R01: "Precisamos de um módulo" e "conhecer o Fluig" são duas
    intenções comerciais; antes, só a segunda sobrevivia. Não são agrupadas
    (B17)."""

    resultado = analisar_sinais_comerciais("Precisamos de um módulo e conhecer o Fluig.", Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["Precisamos de um módulo", "conhecer o Fluig"]
    assert len({o.evidencias[0] for o in resultado.oportunidades}) == 2


@pytest.mark.parametrize(
    "transcricao",
    [
        "Queremos conhecer o Fluig.",
        "Gostaríamos de avaliar a plataforma.",
        "Queremos e precisamos conhecer o Fluig.",
    ],
)
def test_querer_que_so_introduz_o_gatilho_conta_uma_vez(transcricao):
    """Contraprova de B13-R01: avaliado como intenção própria, o querer que
    só introduz o gatilho seguinte chega ao mesmo objeto e ao mesmo recorte;
    a oportunidade não é duplicada."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert len(resultado.oportunidades) == 1


@pytest.mark.parametrize(
    "transcricao",
    [
        "Queremos integrar o sistema solar.",
        "Queremos conhecer o sistema nervoso.",
        "Precisamos de um sistema imunológico forte.",
    ],
)
def test_sistema_com_modificador_alheio_nao_e_objeto_comercial(transcricao):
    """B13-R02: antes, "Queremos integrar o sistema solar." gerava oportunidade
    "Queremos integrar o sistema" e recomendação. Um modificador astronômico
    ou biológico logo depois de "sistema" o torna alheio à relação comercial;
    isolada, a frase não dá base para avaliar churn."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.oportunidades == []
    assert resultado.evidencias == []
    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE


@pytest.mark.parametrize(
    ("transcricao", "trecho"),
    [
        ("Queremos integrar o sistema ERP.", "Queremos integrar o sistema"),
        ("Queremos integrar o sistema de faturamento.", "Queremos integrar o sistema"),
        ("Queremos integrar o sistema.", "Queremos integrar o sistema"),
        ("Queremos integrar o sistema solar e o Fluig.", "Queremos integrar o sistema solar e o Fluig"),
    ],
)
def test_sistema_comercial_continua_objeto_de_oportunidade(transcricao, trecho):
    """Contraprova de B13-R02: "sistema" sem modificador alheio continua
    objeto comercial; um membro coordenado comercial depois do rejeitado
    ainda liga a intenção."""

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == [trecho]


@pytest.mark.parametrize(
    "transcricao",
    [
        "Queremos muito conhecer, no mês que vem, o Fluig.",  # vírgula intercalada
        "Queremos conhecer o suporte técnico.",  # "suporte" não é objeto de oportunidade
    ],
)
def test_limites_b13_falsos_negativos_documentados(transcricao):
    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.oportunidades == []


# B14 — acento decomposto (NFD) ----------------------------------------------


def _nfd(texto: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", texto)


def _evidencias_de(resultado) -> list[str]:
    return [e.trecho for e in resultado.evidencias]


def _confere_recortes(transcricao: str, resultado) -> None:
    for evidencia in resultado.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


@pytest.mark.parametrize(
    "transcricao",
    [
        "Não estamos satisfeitos com o suporte.",
        "Não vamos cancelar o contrato.",
        "Vamos cancelar o contrato.",
        "Se o suporte continuar assim, vamos cancelar o contrato.",
        "Estamos insatisfeitos com o suporte.",
        "Não temos interesse em conhecer o Fluig.",
        "Queremos conhecer o Fluig.",
        "Precisamos automatizar o faturamento.",
        "Não queremos o Fluig, mas temos interesse no Protheus.",
        "Vamos cancelar a reunião e o contrato continua vigente.",
    ],
)
def test_nfc_e_nfd_geram_o_mesmo_churn_e_as_mesmas_oportunidades(transcricao):
    """B14: negação, risco e oportunidade dão o mesmo resultado nas duas formas
    de Unicode; os recortes NFD são o equivalente decomposto dos NFC."""

    decomposto = _nfd(transcricao)
    nfc = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)
    nfd = analisar_sinais_comerciais(decomposto, Vinculo.CLIENTE)

    assert nfd.churn.situacao is nfc.churn.situacao
    assert [_nfd(t) for t in _evidencias_de(nfc)] == _evidencias_de(nfd)
    assert nfd.produtos == nfc.produtos
    assert nfd.concorrentes == nfc.concorrentes
    assert [o.evidencias for o in nfd.oportunidades] == [o.evidencias for o in nfc.oportunidades]
    _confere_recortes(decomposto, nfd)


def test_negacao_nfd_de_nao_estamos_satisfeitos_gera_risco_com_o_recorte_completo():
    transcricao = _nfd("Não estamos satisfeitos com o suporte.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert _evidencias_de(resultado) == [transcricao[:-1]]


def test_nao_so_e_e_verbo_em_nfd_respeitam_a_excecao_e_o_limite_de_escopo():
    """`Não só` não é negação; o `é` do verbo não fecha o escopo da
    negação (`não é bom` mantém o objeto negado), a conjunção `e` coordena."""

    nao_so = _nfd("Não só queremos conhecer o Fluig, como o Protheus.")
    verbo = _nfd("Não é bom cancelar o contrato.")

    resultado_nao_so = analisar_sinais_comerciais(nao_so, Vinculo.CLIENTE)
    resultado_verbo = analisar_sinais_comerciais(verbo, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado_nao_so) == [_nfd("queremos conhecer o Fluig")]
    assert resultado_verbo.churn.situacao is ChurnSituacao.SEM_SINAL_DETECTADO
    assert resultado_verbo.evidencias == []


def test_coordenacao_com_e_em_nfd_ainda_liga_o_segundo_objeto():
    transcricao = _nfd("Vamos cancelar a reunião e o contrato.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _evidencias_de(resultado) == [_nfd("cancelar a reunião e o contrato")]
    _confere_recortes(transcricao, resultado)


def test_churn_seguido_de_outra_acao_valida_nao_desloca_a_segunda_evidencia():
    """Cada combinante antes do sinal deslocava o recorte (índices do texto
    normalizado). Agora a segunda ação é localizada na transcrição."""

    transcricao = _nfd("Vamos cancelar o contrato. Também, até amanhã, vamos reavaliar o fornecedor.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    esperado = [_nfd("cancelar o contrato"), _nfd("reavaliar o fornecedor")]
    assert _evidencias_de(resultado) == esperado
    for evidencia, trecho in zip(resultado.evidencias, esperado):
        assert evidencia.inicio == transcricao.index(trecho)
    _confere_recortes(transcricao, resultado)


def test_oportunidade_depois_de_palavras_nfd_aponta_a_posicao_certa():
    transcricao = _nfd("Atenção: após a conversão, a negociação é nossa prioridade. Queremos conhecer o Fluig.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["Queremos conhecer o Fluig"]
    evidencia = resultado.evidencias[0]
    assert evidencia.inicio == transcricao.index("Queremos")
    assert resultado.produtos == ["Fluig"]
    _confere_recortes(transcricao, resultado)


def test_sinal_vizinho_valido_sobrevive_a_palavra_nfd_alheia_e_a_trecho_negado():
    transcricao = _nfd("Não queremos o Fluig, mas após a negociação temos interesse no Protheus.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _trechos_das_oportunidades(resultado) == ["interesse no Protheus"]
    assert resultado.produtos == ["Fluig", "Protheus"]
    _confere_recortes(transcricao, resultado)


def test_duas_ocorrencias_iguais_com_emoji_quebra_de_linha_e_pontuacao_em_nfd():
    transcricao = _nfd("😀 Vamos cancelar o contrato!\nEm março: vamos cancelar o contrato; é isso.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert _evidencias_de(resultado) == ["cancelar o contrato"] * 2
    posicoes = [(e.inicio, e.fim) for e in resultado.evidencias]
    assert posicoes[0][0] < posicoes[1][0]
    assert posicoes[1][0] == transcricao.rindex("cancelar")
    assert len(set(resultado.churn.evidencias)) == 2
    _confere_recortes(transcricao, resultado)


def test_catalogo_nfd_e_prospect_continuam_corretos():
    transcricao = _nfd("Hoje usamos o Protheus e o RM; após a avaliação, vamos cancelar o contrato.")

    cliente = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)
    prospect = analisar_sinais_comerciais(transcricao, Vinculo.PROSPECT)

    assert cliente.produtos == prospect.produtos == ["Protheus", "RM"]
    assert cliente.churn.situacao is ChurnSituacao.SINAL_DETECTADO
    assert prospect.churn.situacao is ChurnSituacao.NAO_APLICAVEL
    assert prospect.churn.evidencias == []


def test_tema_alheio_em_nfd_continua_sem_risco_de_churn():
    """B12-R04 na forma NFD: o complemento `com o almoço` (com cedilha/til
    decompostos) segue sendo tema alheio."""

    transcricao = _nfd("Não estamos satisfeitos com o almoço.")

    resultado = analisar_sinais_comerciais(transcricao, Vinculo.CLIENTE)

    assert resultado.churn.situacao is ChurnSituacao.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []
