"""Utilitário de texto compartilhado entre os serviços de análise.

Extraído de B02 (`sentimento.py`) para reúso em B03, como já previsto no
README do backend. Nenhuma regra de sentimento ou de sinal comercial mora
aqui — só a normalização de texto que os serviços de detecção usam.
"""

from __future__ import annotations

import unicodedata


def normalizar_preservando_posicoes(texto: str) -> str:
    """Minúsculas e sem acento, um caractere de saída por caractere de entrada.

    Preserva o índice de cada caractere: a posição de um casamento de regex
    no texto normalizado vale também na transcrição original, sem precisar
    remapear índices entre as duas versões. Ao contrário de uma limpeza que
    remove pontuação/stopwords (como em `limpar_texto` do experimento), aqui
    nada é removido — só minúsculas e substituição do caractere acentuado
    pela sua base, caractere a caractere.

    Limitação conhecida: texto em forma NFD (acento como código combinante
    separado) não é fundido em um único caractere base — fundir quebraria a
    correspondência 1:1 de posições. Transcrições em NFC (padrão de editores
    e APIs) não são afetadas.
    """

    resultado = []
    for caractere in texto:
        decomposto = unicodedata.normalize("NFKD", caractere)
        base = next((c for c in decomposto if not unicodedata.combining(c)), caractere)
        resultado.append(base.lower())
    return "".join(resultado)
