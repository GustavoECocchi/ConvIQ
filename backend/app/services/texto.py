"""Utilitário de texto compartilhado entre os serviços de análise.

Extraído de B02 (`sentimento.py`) para reúso em B03, como já previsto no
README do backend. Nenhuma regra de sentimento ou de sinal comercial mora
aqui — só a normalização de texto que os serviços de detecção usam e o mapa
que devolve cada posição normalizada à transcrição original (B14).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TextoNormalizado:
    """Texto para busca (`texto`) e o mapa de volta à transcrição (`original`).

    `texto` está em minúsculas e sem acentos: cada caractere vem de um caractere
    da transcrição, e os códigos combinantes (acento decomposto, forma NFD)
    são absorvidos pelo caractere anterior, em vez de ficarem entre as letras
    e impedirem o casamento. Por isso `len(texto)` pode ser menor que
    `len(original)`; os índices dos dois **não** coincidem em geral, e toda
    posição que sai para o cliente precisa passar por `intervalo_original`.

    Cada caractere normalizado `i` corresponde ao intervalo `[inicios[i],
    fins[i])` da transcrição: o caractere de origem mais os combinantes que o
    seguem. Um caractere que expande na normalização (`"ﬁ"` → `"fi"`) gera
    vários caracteres normalizados com o mesmo intervalo.
    """

    original: str
    texto: str
    inicios: tuple[int, ...]
    fins: tuple[int, ...]

    def posicao_original(self, posicao: int) -> int:
        """Índice da transcrição em que começa o caractere normalizado `posicao`.

        `posicao == len(texto)` (fim do texto) devolve `len(original)`.
        """

        return self.inicios[posicao] if posicao < len(self.texto) else len(self.original)

    def intervalo_original(self, inicio: int, fim: int) -> tuple[int, int]:
        """Converte `[inicio, fim)` normalizado em `[inicio, fim)` da transcrição.

        O início é o do primeiro caractere de origem e o fim (exclusivo) é o
        do último, **incluindo os combinantes que o seguem**: o recorte de
        `"pe\\u0301ssimo"` contém o acento. Se o intervalo normalizado cobrir só
        parte de um caractere que expandiu, o intervalo original cobre o
        caractere inteiro. Um intervalo vazio devolve o ponto da posição.
        """

        if fim <= inicio:
            ponto = self.posicao_original(inicio)
            return ponto, ponto
        return self.inicios[inicio], self.fins[fim - 1]

    def caractere_original(self, posicao: int) -> str:
        """Trecho original do caractere normalizado `posicao`, composto (NFC).

        Serve para distinguir o que a normalização funde: o `"e"` da conjunção
        e o `"é"` do verbo viram o mesmo `"e"` em `texto`, tenham a transcrição
        em NFC ou em NFD.
        """

        return unicodedata.normalize("NFC", self.original[self.inicios[posicao]:self.fins[posicao]])


def normalizar_com_mapa(texto: str) -> TextoNormalizado:
    """Minúsculas e sem acento, com o mapa de volta à transcrição (B14).

    Substitui `normalizar_preservando_posicoes` (B02), cujo texto de saída
    tinha um caractere por caractere de entrada e por isso não funcionava
    com acento decomposto (NFD): o código combinante ficava entre as letras.
    Regras:

    - Cada caractere é decomposto (NFKD); os combinantes resultantes e os
      combinantes soltos que seguem um caractere são descartados do texto e
      passam a fazer parte do intervalo do caractere anterior.
    - O restante vira minúsculas. Caracteres que expandem geram vários
      caracteres normalizados com o mesmo intervalo original.
    - Um combinante sem caractere anterior (início do texto ou depois de
      outro combinante órfão) não gera caractere normalizado e fica fora de
      qualquer intervalo.
    - Nada mais é removido: pontuação, espaços, emoji e quebras de linha
      continuam no texto, cada um com seu intervalo de um caractere.
    """

    caracteres: list[str] = []
    inicios: list[int] = []
    fins: list[int] = []
    ultimo_grupo: list[int] = []  # índices normalizados gerados pelo último caractere-base

    for posicao, caractere in enumerate(texto):
        if unicodedata.combining(caractere) and ultimo_grupo:
            for indice in ultimo_grupo:
                fins[indice] = posicao + 1
            continue
        grupo: list[int] = []
        for decomposto in unicodedata.normalize("NFKD", caractere):
            if unicodedata.combining(decomposto):
                continue
            for minusculo in decomposto.lower():
                grupo.append(len(caracteres))
                caracteres.append(minusculo)
                inicios.append(posicao)
                fins.append(posicao + 1)
        if grupo:
            ultimo_grupo = grupo

    return TextoNormalizado(
        original=texto,
        texto="".join(caracteres),
        inicios=tuple(inicios),
        fins=tuple(fins),
    )
