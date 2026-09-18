import pytest

from app.schemas.comum import Sentimento
from app.services.sentimento import analisar_sentimento


def test_insatisfeito_gera_sentimento_negativo_com_evidencia():
    transcricao = "Estamos insatisfeitos com o suporte."

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert len(resultado.evidencias) == 1
    evidencia = resultado.evidencias[0]
    assert evidencia.trecho == "insatisfeitos"
    assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_ausencia_de_sinal_e_informacao_insuficiente_sem_evidencias():
    resultado = analisar_sentimento("Bom dia a todos. Vamos seguir a pauta de hoje.")

    assert resultado.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []


def test_trechos_repetidos_geram_evidencias_em_posicoes_distintas():
    transcricao = "Ficamos frustrados com o atraso. No fim, ficamos frustrados de novo."

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert len(resultado.evidencias) == 2
    primeira, segunda = resultado.evidencias
    assert primeira.inicio < segunda.inicio
    assert primeira.trecho == segunda.trecho == "frustrados"
    # cada evidência aponta para a ocorrência real naquela posição, não para a primeira sempre
    assert transcricao[primeira.inicio:primeira.fim] == "frustrados"
    assert transcricao[segunda.inicio:segunda.fim] == "frustrados"
    assert primeira.inicio != segunda.inicio


def test_satisfeito_nao_e_confundido_com_insatisfeito():
    """Regra de produto: evitar a colisão entre "satisfeito" e "insatisfeito"."""

    resultado = analisar_sentimento("Estamos muito satisfeitos com o Datasul.")

    assert resultado.sentimento is Sentimento.POSITIVO
    assert len(resultado.evidencias) == 1
    assert resultado.evidencias[0].trecho == "satisfeitos"


def test_insatisfeito_nao_soma_ponto_positivo_para_satisfeito():
    """A palavra "insatisfeito" não deve contar como sinal positivo de "satisfeito"."""

    resultado = analisar_sentimento("Estou insatisfeito com o atendimento.")

    assert resultado.sentimento is Sentimento.NEGATIVO
    trechos = [evidencia.trecho for evidencia in resultado.evidencias]
    assert trechos == ["insatisfeito"]
    assert "satisfeito" not in trechos


def test_sinais_positivos_e_negativos_empatados_geram_neutro_com_ambas_evidencias():
    transcricao = "O suporte foi excelente, mas tivemos um problema com o faturamento."

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEUTRO
    trechos = {evidencia.trecho for evidencia in resultado.evidencias}
    assert trechos == {"excelente", "problema"}


def test_evidencias_preservam_acentuacao_e_maiusculas_do_trecho_original():
    transcricao = "Ficamos muito Satisfeitos com a implantação."

    resultado = analisar_sentimento(transcricao)

    assert resultado.evidencias[0].trecho == "Satisfeitos"


def test_evidencias_tem_ids_unicos_e_sequenciais():
    transcricao = "Excelente atendimento, ótimo suporte, adorei o resultado."

    resultado = analisar_sentimento(transcricao)

    assert [evidencia.id for evidencia in resultado.evidencias] == [
        f"e{n}" for n in range(1, len(resultado.evidencias) + 1)
    ]


@pytest.mark.parametrize(
    "transcricao, inicio, fim",
    [
        ("Excelente reunião com o time.", 0, 9),
        ("A reunião foi excelente para todos.", 14, 23),
        ("A reunião de hoje foi excelente", 22, 31),
        ("Excelente", 0, 9),
    ],
)
def test_ocorrencia_no_inicio_meio_e_fim_tem_posicao_exata(transcricao, inicio, fim):
    resultado = analisar_sentimento(transcricao)

    assert len(resultado.evidencias) == 1
    evidencia = resultado.evidencias[0]
    assert (evidencia.inicio, evidencia.fim) == (inicio, fim)
    assert transcricao[inicio:fim] == evidencia.trecho


@pytest.mark.parametrize(
    "transcricao",
    [
        "A otimização ficou pronta.",  # "otim" dentro de outra palavra
        "Ele é otimista.",
        "O conteúdo foi entregue.",  # não é "contente"
        "Eu gostaria de ver.",  # "gosta" + "ria"
        "Desgosto total.",  # "gosto" sem fronteira antes
        "Adorador de futebol.",
        "A problemática é antiga.",
        "Dificilmente veremos.",
    ],
)
def test_radical_dentro_de_outra_palavra_nao_e_sinal(transcricao):
    """Fronteira de palavra: parte de palavra maior não conta como sinal."""

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []


@pytest.mark.parametrize("transcricao, trecho", [("O suporte foi ruim.", "ruim"), ("Os resultados foram ruins.", "ruins")])
def test_ruim_e_reconhecido_no_singular_e_no_plural(transcricao, trecho):
    """B02-R01: `ruim` era o único padrão sem plural; o plural troca "m" por "n",
    então `ruins?` não serve — precisa de `ruim|ruins` para manter o singular.
    """

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert resultado.evidencias[0].trecho == trecho


def test_tres_repeticoes_geram_tres_evidencias_com_posicoes_crescentes():
    transcricao = "Problema aqui, problema ali, problema acolá."

    resultado = analisar_sentimento(transcricao)

    posicoes = [(e.inicio, e.fim) for e in resultado.evidencias]
    assert posicoes == [(0, 8), (15, 23), (29, 37)]
    assert [e.id for e in resultado.evidencias] == ["e1", "e2", "e3"]


def test_maioria_negativa_com_um_positivo_e_negativo_so_com_evidencias_negativas():
    transcricao = "Excelente ideia, mas problema e mais problema."

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert [e.trecho for e in resultado.evidencias] == ["problema", "problema"]


@pytest.mark.parametrize(
    "transcricao, sentimento_atual",
    [
        ("Não estamos satisfeitos.", Sentimento.POSITIVO),
        ("Sem problemas, tudo certo.", Sentimento.NEGATIVO),
        ("Não foi ruim.", Sentimento.NEGATIVO),
    ],
)
def test_negacao_de_frase_nao_e_tratada_limitacao_documentada(transcricao, sentimento_atual):
    """Pina a limitação registrada no README: negação inverte o sentido, mas o
    serviço só conta a palavra. Se este teste falhar, a limitação foi resolvida
    e o README precisa ser atualizado junto.
    """

    assert analisar_sentimento(transcricao).sentimento is sentimento_atual


def test_texto_vazio_ou_so_espacos_e_informacao_insuficiente():
    for transcricao in ("", "   \n\t "):
        resultado = analisar_sentimento(transcricao)
        assert resultado.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
        assert resultado.evidencias == []
