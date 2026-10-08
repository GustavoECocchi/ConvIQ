"""Negação simples, compartilhada entre sentimento (B02/B11) e sinais
comerciais (B12).

Extraído de `sentimento.py` em B12 porque o risco de cancelamento também
precisa distinguir "cancelar o contrato" de "não cancelar o contrato" e
"insatisfeitos" de "não insatisfeitos" — a mesma regra de escopo de B11,
não uma nova. Nenhuma regra de sentimento ou de sinal comercial mora aqui,
só a negação: quem chama decide o que fazer com o escopo (inverter sinal,
suprimir, ou os dois).
"""

from __future__ import annotations

import re

from app.services.texto import TextoNormalizado

# Marcadores de negação e a exceção "não só" (afirmação dupla, não negação:
# "não só X, como/mas também Y" afirma X e Y). "nem" é marcador próprio
# (revisão B11-R01) porque, com a vírgula fechando escopo, "não estamos
# satisfeitos, nem contentes" precisa de um marcador para "contentes".
_REGEX_MARCADOR_NEGACAO = re.compile(r"\b(?:nao|nem|sem|nenhum[a]?)\b")
_REGEX_NAO_SO = re.compile(r"\bnao\s+so\b")
# Fim do escopo de uma negação (B11-R01): pontuação de oração ou de
# separação, conjunção adversativa, ou a conjunção "e" isolada por espaços
# (o "é" do verbo também vira "e" na normalização; `escopos_de_negacao`
# descarta esse caso olhando o caractere original).
_REGEX_FIM_DE_ESCOPO = re.compile(r"[.!?;,\n]|\b(?:mas|porem|contudo|todavia|entretanto)\b|(?<=\s)e(?=\s)")


def escopos_de_negacao(texto: TextoNormalizado) -> list[tuple[int, int, int]]:
    """Devolve `(inicio_marcador, fim_marcador, fim_escopo)` de cada negação válida.

    As posições são do **texto normalizado** (`texto.texto`), o mesmo em que
    os serviços rodam suas regex; só convertem para a transcrição, com
    `texto.intervalo_original`, na hora de montar uma `Evidencia` (B14).

    O escopo de cada marcador ("não", "nem", "sem", "nenhum"/"nenhuma") vai do
    fim do marcador até o primeiro fim de escopo depois dele, ou o fim do
    texto. Fecham o escopo (revisão B11-R01): pontuação `. ! ? ; ,` e quebra
    de linha; as conjunções adversativas "mas", "porém", "contudo",
    "todavia", "entretanto"; e a conjunção "e" isolada por espaços. Assim
    "sem problemas, estamos satisfeitos" alcança "problemas" (antes da
    vírgula) e não "satisfeitos" (depois dela), e "não gostei do
    atendimento, mas adoramos o produto" não inverte "adoramos". A negação
    nunca é estendida até a próxima ocorrência de sinal — não se presume
    onde a expressão termina.

    O "é" do verbo também vira "e" na normalização; por isso o caractere
    original (`texto.caractere_original`, composto, válido para NFC e NFD) é
    consultado e "é"/"É" não fecha escopo ("não é ruim, é ótimo" mantém
    "ruim" negado). "Não só" é a exceção de
    marcador: não inicia negação, porque introduz uma afirmação dupla
    ("não só X, como/mas também Y" afirma X e Y), não a nega.

    Limites documentados no README: vírgula parentética dentro da mesma
    expressão ("não estamos, hoje, satisfeitos") fecha o escopo cedo demais,
    e adjetivos coordenados por "e" sob uma só negação ("não estamos
    satisfeitos e contentes") deixam o segundo sem negação — em português a
    forma natural é "nem", que é marcador.
    """

    normalizado = texto.texto
    posicoes_nao_so = {correspondencia.start() for correspondencia in _REGEX_NAO_SO.finditer(normalizado)}
    fins_de_escopo = [
        correspondencia.start()
        for correspondencia in _REGEX_FIM_DE_ESCOPO.finditer(normalizado)
        if not (correspondencia.group() == "e" and texto.caractere_original(correspondencia.start()) in ("é", "É"))
    ]

    escopos: list[tuple[int, int, int]] = []
    for marcador in _REGEX_MARCADOR_NEGACAO.finditer(normalizado):
        if marcador.group() == "nao" and marcador.start() in posicoes_nao_so:
            continue
        fim_escopo = next((posicao for posicao in fins_de_escopo if posicao >= marcador.end()), len(normalizado))
        escopos.append((marcador.start(), marcador.end(), fim_escopo))
    return escopos


def inicio_da_negacao_mais_proxima(escopos: list[tuple[int, int, int]], posicao: int) -> int | None:
    """Início do marcador de negação mais próximo (o último) que cobre `posicao`."""

    candidatos = [
        inicio_marcador
        for inicio_marcador, fim_marcador, fim_escopo in escopos
        if fim_marcador <= posicao < fim_escopo
    ]
    return max(candidatos) if candidatos else None
