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
    "transcricao, sentimento_esperado",
    [
        ("Estamos satisfeitos.", Sentimento.POSITIVO),
        ("Não estamos satisfeitos.", Sentimento.NEGATIVO),
        ("Gostei do atendimento.", Sentimento.POSITIVO),
        ("Não gostei do atendimento.", Sentimento.NEGATIVO),
    ],
)
def test_negacao_simples_inverte_par_afirmativo_negado(transcricao, sentimento_esperado):
    """B11: negar satisfação/agrado explícito conta como insatisfação."""

    assert analisar_sentimento(transcricao).sentimento is sentimento_esperado


@pytest.mark.parametrize(
    "transcricao, sentimento_esperado",
    [
        ("Estamos insatisfeitos.", Sentimento.NEGATIVO),
        ("Não estamos insatisfeitos.", Sentimento.INFORMACAO_INSUFICIENTE),
        ("Sem problemas.", Sentimento.INFORMACAO_INSUFICIENTE),
        ("Nenhum problema até agora.", Sentimento.INFORMACAO_INSUFICIENTE),
        ("Não foi ruim.", Sentimento.INFORMACAO_INSUFICIENTE),
    ],
)
def test_negacao_de_termo_negativo_nao_vira_elogio_fica_insuficiente(transcricao, sentimento_esperado):
    """Política conservadora do cartão B11: negar um problema não é prova de
    elogio. Sem outro sinal na oração, o resultado é informação insuficiente,
    nunca positivo nem neutro (que exigiria sinal positivo e negativo reais)."""

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is sentimento_esperado
    if sentimento_esperado is Sentimento.INFORMACAO_INSUFICIENTE:
        assert resultado.evidencias == []


def test_negacao_nao_vaza_para_oracao_independente():
    """Duas orações: a negação de uma não apaga o sinal independente da outra."""

    resultado = analisar_sentimento("Não houve atraso. Estamos satisfeitos.")

    assert resultado.sentimento is Sentimento.POSITIVO
    assert [e.trecho for e in resultado.evidencias] == ["satisfeitos"]


def test_negacao_nao_vaza_quando_ambas_as_oracoes_tem_sinal_lexico():
    """Se o escopo vazasse para a 2ª oração, "adoramos" viraria negativo também
    (2 negativos, 0 positivos → negativo). O resultado correto é empate."""

    resultado = analisar_sentimento("Não gostamos do atendimento. Adoramos o produto.")

    assert resultado.sentimento is Sentimento.NEUTRO
    trechos = {e.trecho for e in resultado.evidencias}
    assert trechos == {"Não gostamos", "Adoramos"}


@pytest.mark.parametrize(
    "transcricao, sentimento_esperado, trechos_esperados",
    [
        ("Sem problemas, estamos satisfeitos.", Sentimento.POSITIVO, ["satisfeitos"]),
        ("Nenhum problema e estamos satisfeitos.", Sentimento.POSITIVO, ["satisfeitos"]),
        ("Não gostei do atendimento, mas adoramos o produto.", Sentimento.NEUTRO, ["Não gostei", "adoramos"]),
        ("Não é ruim, é ótimo.", Sentimento.POSITIVO, ["ótimo"]),
    ],
)
def test_negacao_fecha_na_virgula_ou_conjuncao_e_nao_inverte_elogio_independente(
    transcricao, sentimento_esperado, trechos_esperados
):
    """B11-R01: o escopo da negação termina na vírgula, em "mas"/"porém"/...
    ou na conjunção "e" — o elogio da outra expressão/oração fica intacto."""

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is sentimento_esperado
    assert [e.trecho for e in resultado.evidencias] == trechos_esperados
    for evidencia in resultado.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


@pytest.mark.parametrize(
    "transcricao, trechos_esperados",
    [
        # "e" liga objetos, não orações: a negação pertinente ("gostei") continua
        ("Não gostei do suporte e do produto.", ["Não gostei"]),
        # "nem" é marcador próprio, então o segundo adjetivo também é negado
        ("Não estamos satisfeitos nem contentes.", ["Não estamos satisfeitos", "nem contentes"]),
        ("Não estamos satisfeitos, nem contentes.", ["Não estamos satisfeitos", "nem contentes"]),
        ("Nem gostei.", ["Nem gostei"]),
    ],
)
def test_conjuncao_nao_corta_negacao_pertinente_e_nem_e_marcador(transcricao, trechos_esperados):
    """Contraexemplos de B11-R01: fechar escopo em vírgula/conjunção não pode
    apagar a negação que de fato alcança a palavra."""

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert [e.trecho for e in resultado.evidencias] == trechos_esperados


@pytest.mark.parametrize("transcricao", ["Não é ruim.", "NÃO É RUIM."])
def test_e_com_acento_e_verbo_e_nao_fecha_o_escopo(transcricao):
    """"é" normaliza para "e"; só a conjunção sem acento fecha escopo. Se o
    verbo fechasse, "ruim" ficaria fora da negação e o resultado seria negativo."""

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
    assert resultado.evidencias == []


def test_nao_so_e_excecao_afirma_os_dois_lados():
    """"Não só X, como Y" afirma X e Y — não é negação de X."""

    resultado = analisar_sentimento("Não só estamos satisfeitos, como adoramos o atendimento.")

    assert resultado.sentimento is Sentimento.POSITIVO
    trechos = [e.trecho for e in resultado.evidencias]
    assert trechos == ["satisfeitos", "adoramos"]
    # a exceção não deixa "não" grudado em nenhuma evidência
    assert all("não" not in trecho.lower() for trecho in trechos)


def test_evidencia_negada_inclui_o_marcador_e_e_recorte_literal():
    """A evidência de um sinal negado cobre o trecho negado inteiro, incluindo
    "não", recortado literalmente da transcrição original (sem paráfrase)."""

    transcricao = "Não estamos satisfeitos."

    resultado = analisar_sentimento(transcricao)

    assert len(resultado.evidencias) == 1
    evidencia = resultado.evidencias[0]
    assert evidencia.trecho == "Não estamos satisfeitos"
    assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho
    assert evidencia.trecho.lower().startswith("não")


def test_negacao_repetida_gera_evidencias_em_posicoes_distintas():
    transcricao = "Não gostei do produto. Não gostei do suporte."

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEGATIVO
    assert len(resultado.evidencias) == 2
    primeira, segunda = resultado.evidencias
    assert primeira.trecho == segunda.trecho == "Não gostei"
    assert primeira.inicio < segunda.inicio
    assert transcricao[primeira.inicio:primeira.fim] == "Não gostei"
    assert transcricao[segunda.inicio:segunda.fim] == "Não gostei"
    assert [e.id for e in resultado.evidencias] == ["e1", "e2"]


@pytest.mark.parametrize(
    "transcricao, sentimento_atual",
    [
        # Ironia não é detectada: "ótimo" continua contando como sinal positivo
        # genuíno mesmo em uso sarcástico. Fora do escopo de B11 (prompt).
        ("Ótimo, mais um problema.", Sentimento.NEUTRO),
        # "O problema foi resolvido" não é reconhecido como neutralização do
        # problema — comportamento já documentado desde B02, inalterado por B11.
        ("O problema foi resolvido, ficamos satisfeitos.", Sentimento.NEUTRO),
        # Negação dupla geral não é corrigida: cada "não" tenta negar o sinal
        # mais próximo, sem compor as duas negações numa afirmação.
        ("Não é verdade que não gostamos do produto.", Sentimento.NEGATIVO),
        # Vírgula parentética dentro da mesma expressão fecha o escopo cedo
        # demais (B11-R01 fecha em toda vírgula; não há análise sintática).
        ("Não estamos, hoje, satisfeitos.", Sentimento.POSITIVO),
        # Adjetivos coordenados por "e" sob uma só negação: o segundo fica
        # sem negação. A forma natural em português é "nem", que é marcador.
        ("Não estamos satisfeitos e contentes.", Sentimento.NEUTRO),
    ],
)
def test_construcoes_fora_do_escopo_de_b11_permanecem_limitacao(transcricao, sentimento_atual):
    """Pina construções que o cartão B11 explicitamente não cobre (ironia,
    "problema resolvido", negação dupla geral) e os limites da regra de
    escopo de B11-R01. Se este teste falhar, uma dessas limitações foi
    resolvida e o README precisa ser atualizado junto.
    """

    assert analisar_sentimento(transcricao).sentimento is sentimento_atual


def test_texto_vazio_ou_so_espacos_e_informacao_insuficiente():
    for transcricao in ("", "   \n\t "):
        resultado = analisar_sentimento(transcricao)
        assert resultado.sentimento is Sentimento.INFORMACAO_INSUFICIENTE
        assert resultado.evidencias == []


# B14 — acento decomposto (NFD) ----------------------------------------------


def _nfd(texto: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFD", texto)


@pytest.mark.parametrize(
    ("transcricao", "sentimento", "trecho"),
    [
        ("O suporte é péssimo.", Sentimento.NEGATIVO, "péssimo"),
        ("O atendimento é ótimo.", Sentimento.POSITIVO, "ótimo"),
    ],
)
def test_nfc_e_nfd_classificam_igual_e_o_recorte_nfd_inclui_o_combinante(transcricao, sentimento, trecho):
    """B14: com NFD o combinante ficava entre as letras e o sinal sumia
    ("péssimo" → informação insuficiente). O recorte devolvido é literal e
    contém o código combinante."""

    nfc = analisar_sentimento(transcricao)
    decomposto = _nfd(transcricao)
    nfd = analisar_sentimento(decomposto)

    assert nfc.sentimento is nfd.sentimento is sentimento
    assert [e.trecho for e in nfc.evidencias] == [trecho]
    assert [e.trecho for e in nfd.evidencias] == [_nfd(trecho)]
    assert len(nfd.evidencias[0].trecho) > len(trecho)
    evidencia = nfd.evidencias[0]
    assert decomposto[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_negacao_nfd_inverte_o_elogio_como_na_forma_nfc():
    """`Não` precisa ser reconhecido como marcador: antes, "não estamos
    satisfeitos" em NFD virava sentimento positivo."""

    transcricao = "Não estamos satisfeitos com o suporte."

    nfc = analisar_sentimento(transcricao)
    nfd = analisar_sentimento(_nfd(transcricao))

    assert nfd.sentimento is nfc.sentimento is Sentimento.NEGATIVO
    assert [_nfd(e.trecho) for e in nfc.evidencias] == [e.trecho for e in nfd.evidencias]
    assert nfd.evidencias[0].trecho == _nfd("Não estamos satisfeitos")


@pytest.mark.parametrize(
    ("transcricao", "sentimento", "trechos"),
    [
        (
            "Não só estamos satisfeitos, como adoramos o atendimento.",
            Sentimento.POSITIVO,
            ["satisfeitos", "adoramos"],
        ),
        ("Não é ruim, é ótimo.", Sentimento.POSITIVO, ["ótimo"]),
        ("Sem problemas, estamos satisfeitos.", Sentimento.POSITIVO, ["satisfeitos"]),
        ("Não gostei do atendimento, mas adoramos o produto.", Sentimento.NEUTRO, ["Não gostei", "adoramos"]),
    ],
)
def test_excecoes_e_limites_de_escopo_da_negacao_valem_em_nfd(transcricao, sentimento, trechos):
    """`não só` não abre negação; o `é` do verbo (`é`) não fecha o escopo
    como a conjunção `e`; vírgula e `mas` fecham — tudo igual à forma NFC."""

    decomposto = _nfd(transcricao)
    resultado = analisar_sentimento(decomposto)

    assert resultado.sentimento is sentimento
    assert [e.trecho for e in resultado.evidencias] == [_nfd(t) for t in trechos]
    for evidencia in resultado.evidencias:
        assert decomposto[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_acento_decomposto_antes_nao_desloca_a_evidencia_do_sinal_posterior():
    """Antes, os índices eram do texto normalizado; cada combinante antes do
    sinal deslocava o recorte. Agora a evidência aponta a posição da transcrição."""

    transcricao = _nfd("Ontem, às três da tarde, a reunião começou. O suporte é péssimo e o atendimento é ótimo.")

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.NEUTRO
    esperado = [_nfd("péssimo"), _nfd("ótimo")]
    assert [e.trecho for e in resultado.evidencias] == esperado
    for evidencia, trecho in zip(resultado.evidencias, esperado):
        assert evidencia.inicio == transcricao.index(trecho)
        assert transcricao[evidencia.inicio:evidencia.fim] == trecho


def test_sinal_valido_sobrevive_a_palavra_nfd_alheia_e_a_trecho_negado():
    transcricao = _nfd("Não houve atraso. Estamos satisfeitos com a negociação, não é ruim.")

    resultado = analisar_sentimento(transcricao)

    assert resultado.sentimento is Sentimento.POSITIVO
    assert [e.trecho for e in resultado.evidencias] == ["satisfeitos"]
    evidencia = resultado.evidencias[0]
    assert transcricao[evidencia.inicio:evidencia.fim] == "satisfeitos"


def test_repeticoes_emoji_e_quebra_de_linha_em_nfd_mantem_indices_distintos():
    transcricao = _nfd("😀 O suporte é péssimo.\nDe novo: péssimo!\n")

    resultado = analisar_sentimento(transcricao)

    assert [e.trecho for e in resultado.evidencias] == [_nfd("péssimo")] * 2
    posicoes = [(e.inicio, e.fim) for e in resultado.evidencias]
    assert posicoes[0] != posicoes[1]
    assert posicoes[0][0] < posicoes[1][0]
    for evidencia in resultado.evidencias:
        assert transcricao[evidencia.inicio:evidencia.fim] == evidencia.trecho


def test_sinal_no_inicio_e_no_fim_do_texto_nfd():
    inicio = analisar_sentimento(_nfd("Ótimo atendimento"))
    fim = analisar_sentimento(_nfd("O suporte é péssimo"))

    assert (inicio.evidencias[0].inicio, inicio.evidencias[0].trecho) == (0, _nfd("Ótimo"))
    ultima = fim.evidencias[0]
    assert ultima.fim == len(_nfd("O suporte é péssimo"))
    assert ultima.trecho == _nfd("péssimo")
