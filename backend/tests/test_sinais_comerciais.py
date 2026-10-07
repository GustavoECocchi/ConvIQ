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
