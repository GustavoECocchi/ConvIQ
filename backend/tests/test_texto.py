import unicodedata

import pytest

from app.services.texto import normalizar_com_mapa


def _nfd(texto: str) -> str:
    return unicodedata.normalize("NFD", texto)


@pytest.mark.parametrize(
    "texto",
    [
        "O suporte é péssimo.",
        "Não só estamos satisfeitos; também adoramos o atendimento!",
        "Ação, órgão, ÓTIMO, Ç, ü, ñ",
    ],
)
def test_nfc_e_nfd_geram_o_mesmo_texto_normalizado(texto):
    """B14: antes, o combinante da forma NFD ficava entre as letras e impedia o
    casamento; agora é absorvido e o texto de busca é igual ao da forma NFC."""

    assert normalizar_com_mapa(_nfd(texto)).texto == normalizar_com_mapa(texto).texto


def test_texto_normalizado_e_minusculo_sem_acento_e_sem_remover_pontuacao():
    resultado = normalizar_com_mapa("Não, Ótimo!\nÇA va? 😀")

    assert resultado.texto == "nao, otimo!\nca va? 😀"


def test_intervalo_original_inclui_o_combinante_apos_a_letra():
    """`péssimo` tem 8 caracteres na transcrição e 7 no texto normalizado;
    o intervalo normalizado da palavra volta com o acento (fim exclusivo)."""

    original = "O suporte é péssimo."
    resultado = normalizar_com_mapa(original)
    inicio = resultado.texto.index("pessimo")

    inicio_original, fim_original = resultado.intervalo_original(inicio, inicio + len("pessimo"))

    assert original[inicio_original:fim_original] == "péssimo"
    assert fim_original - inicio_original == 8
    assert len(resultado.texto) < len(original)


def test_intervalo_original_nao_inclui_o_combinante_do_caractere_seguinte():
    """O fim exclusivo é o do último caractere do intervalo: `"e"` de `"pé"`
    leva o acento, mas o `"p"` sozinho não leva nada."""

    resultado = normalizar_com_mapa("péssimo")

    assert resultado.intervalo_original(0, 1) == (0, 1)
    assert resultado.intervalo_original(1, 2) == (1, 3)
    assert resultado.intervalo_original(0, 2) == (0, 3)


def test_intervalo_do_texto_inteiro_e_posicao_do_fim():
    original = "Não"
    resultado = normalizar_com_mapa(original)

    assert resultado.texto == "nao"
    assert resultado.intervalo_original(0, 3) == (0, 4)
    assert resultado.posicao_original(3) == len(original)
    assert resultado.intervalo_original(3, 3) == (4, 4)


def test_caractere_que_expande_na_normalizacao_mantem_o_intervalo_do_original():
    """`"ﬁ"` vira `"fi"`: os dois caracteres normalizados apontam para o mesmo
    caractere original, e cobrir só um deles devolve o caractere inteiro."""

    resultado = normalizar_com_mapa("aﬁx")

    assert resultado.texto == "afix"
    assert resultado.intervalo_original(1, 2) == (1, 2)
    assert resultado.intervalo_original(2, 3) == (1, 2)
    assert resultado.intervalo_original(1, 3) == (1, 2)


def test_combinante_orfao_no_inicio_fica_fora_de_qualquer_intervalo():
    resultado = normalizar_com_mapa("́abc")

    assert resultado.texto == "abc"
    assert resultado.intervalo_original(0, 3) == (1, 4)


def test_emoji_e_quebra_de_linha_ocupam_uma_posicao_cada():
    original = "😀\nNão"
    resultado = normalizar_com_mapa(original)

    assert resultado.texto == "😀\nnao"
    inicio = resultado.texto.index("nao")
    assert resultado.intervalo_original(inicio, inicio + 3) == (2, 6)
    assert original[2:6] == "Não"


@pytest.mark.parametrize("texto", ["É assim, e depois", "é assim", "É assim"])
def test_caractere_original_distingue_e_de_acento_em_nfc_e_nfd(texto):
    """A conjunção "e" e o verbo "é" viram o mesmo "e" no texto normalizado; o
    caractere original (composto) permite separá-los em qualquer forma."""

    resultado = normalizar_com_mapa(texto)

    assert resultado.texto.startswith("e")
    assert resultado.caractere_original(0) in ("é", "É")


def test_caractere_original_da_conjuncao_e_o_e_simples():
    resultado = normalizar_com_mapa("Uma e outra")

    assert resultado.caractere_original(resultado.texto.index(" e ") + 1) == "e"


@pytest.mark.parametrize(
    "texto",
    ["", "abc", "Não é ótimo", "́̂x́", "😀 aﬁ́ ", "ÇÃO ç̧ão"],
)
def test_mapa_e_monotonico_e_cobre_so_trechos_validos(texto):
    resultado = normalizar_com_mapa(texto)

    assert len(resultado.inicios) == len(resultado.fins) == len(resultado.texto)
    for i in range(len(resultado.texto)):
        assert 0 <= resultado.inicios[i] < resultado.fins[i] <= len(texto)
        if i:
            assert resultado.inicios[i] >= resultado.inicios[i - 1]
            assert resultado.fins[i] >= resultado.fins[i - 1]
