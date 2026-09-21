"""Serviço de sinais comerciais: churn, oportunidades, produtos e concorrentes.

Escopo de B03, sobre o contrato de C01 e a convenção de posição de B02:
`analisar_sinais_comerciais(transcricao, vinculo)` extrai esses quatro
sinais da transcrição, com evidências de churn/oportunidades localizadas
por posição de caractere (mesma convenção de `app/services/sentimento.py`,
via `app/services/texto.py`). Sentimento geral fica em B02; compor a
resposta completa (`AnaliseTextoResponse`) e a rota HTTP ficam para B04.
Este módulo não depende de rota nem do serviço de sentimento.

Três regras de produto guiam este serviço, e cada uma corrige um padrão
específico do experimento de referência (`conviq_datascience.py`,
`analisar_reuniao`):

1. **Prospect recebe `churn.situacao = nao_aplicavel`.** O experimento não
   distingue cliente de prospect ao calcular churn — usa só sinais de texto.
   Aqui, `vinculo` decide isso antes de qualquer análise de texto.
2. **Concorrente isolado não implica troca.** O experimento calcula
   `churn = bool(concorrente) or (neg >= 2 and neg > pos)` — citar um
   concorrente, sozinho, já classifica risco `ALTO`. Aqui, concorrentes são
   detectados à parte, sem influenciar `churn` nem `oportunidades`.
3. **Risco e oportunidade podem coexistir.** O experimento calcula
   `upsell = (not churn) and contar(t, SINAIS_UPSELL) >= 1` — uma
   oportunidade só é registrada quando não há churn. Aqui, `churn` e
   `oportunidades` vêm de padrões independentes, sem um suprimir o outro.

Risco de cancelamento com contexto local (B12): "cancelar"/"reavaliar"/
"rescindir" sozinhos geravam risco com qualquer objeto ("cancelar a
reunião" tanto quanto "cancelar o contrato") e sem checar negação ("não
vamos cancelar o contrato" gerava risco igual a "vamos cancelar"). Aqui a
ação só conta como risco quando tem um objeto da relação comercial
("contrato", "serviço", "fornecedor") na mesma oração, e é suprimida
quando negada — reutilizando o escopo de negação de B11
(`app/services/negacao.py`), não uma regra nova. Negar satisfação atual
("não estamos satisfeitos") passa a contar como risco, do mesmo jeito que
"insatisfeitos" já contava; negar "insatisfeito" deixa de contar (a mesma
regra de B11: negar um problema não prova baixo risco, só suprime o sinal).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.analise import Churn, Evidencia, Oportunidade
from app.schemas.comum import ChurnSituacao, Vinculo
from app.services.negacao import escopos_de_negacao, inicio_da_negacao_mais_proxima
from app.services.texto import normalizar_preservando_posicoes

# Risco de cancelamento: linguagem que indica avaliação ou intenção de
# encerrar a relação comercial, não qualquer sentimento negativo genérico
# (esse é o escopo de B02). Sobreposição com o léxico negativo de B02
# ("insatisfeit", "frustrad") é proposital — os dois serviços respondem
# perguntas diferentes (sentimento geral vs. risco de cancelamento) e podem
# gerar evidências próprias para o mesmo trecho; B04 renumera os IDs ao
# juntar os resultados numa `AnaliseTextoResponse` só.
#
# B12: "insatisfeit"/"frustrad" continuam risco por si só (independem de
# objeto), mas agora são suprimidos quando negados — "cancelar"/
# "reavaliar"/"rescindir" precisam de um objeto da relação comercial na
# mesma oração (`_PADROES_OBJETO_RISCO`) e são suprimidos quando negados;
# "satisfeit" (positivo) só é risco quando negado — o espelho de
# "insatisfeit".
_PADROES_RISCO_PADRAO = [
    r"insatisfeit[oa]s?",
    r"frustrad[oa]s?",
]
_PADROES_ACAO_RISCO = [
    r"cancelar",
    r"cancelamento",
    r"reavaliar",
    r"rescindir",
]
_PADROES_OBJETO_RISCO = [
    r"contratos?",
    r"servicos?",
    r"fornecedor(es)?",
]
_PADROES_SATISFACAO = [
    r"satisfeit[oa]s?",
]

# Interesse comercial: linguagem que sugere abertura a um novo módulo,
# produto ou expansão — não confirma venda, só sinaliza a evidência.
_PADROES_OPORTUNIDADE = [
    r"interessad[oa]s?",
    r"interesse",
    r"conhecer",
    r"expandir",
    r"integrar",
    r"automatizar",
    r"modulo|modulos",
]

# Contexto comercial (B03-R01): vocabulário que mostra que a conversa trata
# da relação comercial — contrato, serviço, produto, cobrança, satisfação.
# Serve só para decidir se há o que avaliar para churn: sem nenhum destes
# termos, e sem risco, oportunidade, produto ou concorrente, a transcrição
# não fornece informação para avaliar (`informacao_insuficiente`), o que é
# diferente de ter sido avaliada e não apresentar risco
# (`sem_sinal_detectado`). Não gera evidência.
#
# B12: removido "sistema"/"sistemas" — termo genérico demais ("o sistema
# solar é extenso" virava conteúdo comercial avaliável). "produto" continua
# na lista com a mesma ambiguidade conhecida; só o caso de "sistema" citado
# no cartão B12 foi corrigido, sem prometer resolver todo termo genérico.
_PADROES_CONTEXTO_COMERCIAL = [
    r"contratos?",
    r"renova(r|cao|coes|mos)",
    r"suporte",
    r"atendimento",
    r"servicos?",
    r"produtos?",
    r"implantacao",
    r"licencas?",
    r"precos?",
    r"custos?",
    r"propostas?",
    r"parceria",
    r"fornecedor(es)?",
    r"plataforma",
    r"pagamentos?",
    r"faturamento",
    r"mensalidades?",
    r"satisfeit[oa]s?",
]

_REGEX_RISCO_PADRAO = re.compile(r"\b(?:" + "|".join(_PADROES_RISCO_PADRAO) + r")\b")
_REGEX_ACAO_RISCO = re.compile(r"\b(?:" + "|".join(_PADROES_ACAO_RISCO) + r")\b")
_REGEX_OBJETO_RISCO = re.compile(r"\b(?:" + "|".join(_PADROES_OBJETO_RISCO) + r")\b")
_REGEX_SATISFACAO = re.compile(r"\b(?:" + "|".join(_PADROES_SATISFACAO) + r")\b")
_REGEX_FIM_DE_ORACAO = re.compile(r"[.!?;\n]")
_REGEX_OPORTUNIDADE = re.compile(r"\b(?:" + "|".join(_PADROES_OPORTUNIDADE) + r")\b")
_REGEX_CONTEXTO_COMERCIAL = re.compile(r"\b(?:" + "|".join(_PADROES_CONTEXTO_COMERCIAL) + r")\b")

# Nome canônico por radical normalizado (minúsculo, sem acento). Reaproveita
# os catálogos de `conviq_datascience.py` (dados factuais de produto/mercado,
# não a lógica de contagem com bug que este módulo evita).
_PRODUTOS = {
    "protheus": "Protheus",
    "datasul": "Datasul",
    "fluig": "Fluig",
    "analytics": "Analytics",
    "rm": "RM",
}
_CONCORRENTES = {
    "senior": "Senior",
    "sap": "SAP",
    "oracle": "Oracle",
    "sankhya": "Sankhya",
}

_REGEX_PRODUTOS = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _PRODUTOS) + r")\b")
_REGEX_CONCORRENTES = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _CONCORRENTES) + r")\b")


@dataclass(frozen=True)
class ResultadoSinaisComerciais:
    churn: Churn
    oportunidades: list[Oportunidade]
    produtos: list[str] = field(default_factory=list)
    concorrentes: list[str] = field(default_factory=list)
    evidencias: list[Evidencia] = field(default_factory=list)


def _nomes_unicos_em_ordem(normalizado: str, regex: re.Pattern[str], catalogo: dict[str, str]) -> list[str]:
    encontrados: list[str] = []
    for correspondencia in regex.finditer(normalizado):
        nome = catalogo[correspondencia.group()]
        if nome not in encontrados:
            encontrados.append(nome)
    return encontrados


def _ocorrencias_risco(normalizado: str, escopos: list[tuple[int, int, int]]) -> list[tuple[int, int]]:
    """Devolve `(inicio, fim)` de cada ocorrência de risco, já com a negação
    de B11 aplicada (ver `app/services/negacao.py`).

    Três fontes, cada uma com sua própria regra de negação:

    - `_PADROES_RISCO_PADRAO` ("insatisfeito", "frustrado"): risco por si só,
      suprimido quando negado — "não estamos insatisfeitos" deixa de ser
      risco, do mesmo jeito que B11 suprime "sem problemas" no sentimento.
    - `_PADROES_ACAO_RISCO` ("cancelar", "reavaliar", "rescindir"): só é
      risco quando há um objeto da relação comercial
      (`_PADROES_OBJETO_RISCO`) na mesma oração — "cancelar a reunião" não
      basta, "cancelar o contrato" basta — e é suprimido quando a própria
      ação está negada. O objeto em si não vira evidência; a evidência é a
      ação, como já era antes de B12 (`test_evidencia_de_churn_...`).
    - `_PADROES_SATISFACAO` ("satisfeito"): é o espelho de "insatisfeito" —
      só é risco quando **negado** ("não estamos satisfeitos"); satisfação
      afirmada nunca é risco. A evidência cobre o trecho negado inteiro, do
      marcador ao fim da palavra léxica, como a evidência negada de B11.

    "Mesma oração" aqui é delimitada só por pontuação de fim de frase
    (`. ! ? ;`/quebra de linha), não por vírgula/conjunção como o escopo de
    negação — o objeto da ameaça pode estar em qualquer parte da mesma
    frase ("Se o suporte continuar assim, vamos cancelar o contrato.").
    """

    fins_de_oracao = [correspondencia.start() for correspondencia in _REGEX_FIM_DE_ORACAO.finditer(normalizado)]

    def _mesma_oracao(posicao_a: int, posicao_b: int) -> bool:
        inicio, fim = sorted((posicao_a, posicao_b))
        return not any(inicio <= fronteira < fim for fronteira in fins_de_oracao)

    spans: list[tuple[int, int]] = []

    for correspondencia in _REGEX_RISCO_PADRAO.finditer(normalizado):
        if inicio_da_negacao_mais_proxima(escopos, correspondencia.start()) is not None:
            continue
        spans.append((correspondencia.start(), correspondencia.end()))

    objetos_risco = list(_REGEX_OBJETO_RISCO.finditer(normalizado))
    for acao in _REGEX_ACAO_RISCO.finditer(normalizado):
        if inicio_da_negacao_mais_proxima(escopos, acao.start()) is not None:
            continue
        if any(_mesma_oracao(acao.start(), objeto.start()) for objeto in objetos_risco):
            spans.append((acao.start(), acao.end()))

    for correspondencia in _REGEX_SATISFACAO.finditer(normalizado):
        inicio_negacao = inicio_da_negacao_mais_proxima(escopos, correspondencia.start())
        if inicio_negacao is not None:
            spans.append((inicio_negacao, correspondencia.end()))

    return sorted(set(spans), key=lambda span: span[0])


def _ha_conteudo_comercial(
    normalizado: str,
    ocorrencias_oportunidade: list[re.Match[str]],
    produtos: list[str],
    concorrentes: list[str],
) -> bool:
    """Decide se a transcrição dá base para avaliar churn (B03-R01).

    Risco explícito já é tratado antes de chamar esta função. Aqui, qualquer
    oportunidade, produto, concorrente ou termo de contexto comercial basta
    para considerar a conversa avaliável. Limite: usa vocabulário fixo —
    uma conversa sobre a relação comercial que não use nenhum destes termos
    cai em `informacao_insuficiente`, e um termo genérico ("produto") usado
    fora do sentido comercial ainda conta como contexto ("sistema" foi
    removido em B12 por ser genérico demais; "produto" permanece, limite
    conhecido e não resolvido nesta entrega).
    """

    return bool(
        ocorrencias_oportunidade
        or produtos
        or concorrentes
        or _REGEX_CONTEXTO_COMERCIAL.search(normalizado)
    )


def analisar_sinais_comerciais(transcricao: str, vinculo: Vinculo) -> ResultadoSinaisComerciais:
    """Extrai churn, oportunidades, produtos e concorrentes da transcrição.

    `churn.situacao`:
    - `vinculo == prospect`: sempre `nao_aplicavel`, sem evidências — não
      avalia o texto, porque um prospect não tem contrato para cancelar.
    - algum padrão de risco encontrado (ver `_ocorrencias_risco`, com a
      negação de B11 já aplicada): `sinal_detectado`, evidenciado pelas
      ocorrências.
    - sem risco, mas com **conteúdo comercial avaliável** — oportunidade,
      produto, concorrente ou vocabulário da relação comercial
      (`_PADROES_CONTEXTO_COMERCIAL`): `sem_sinal_detectado` — avaliado, sem
      sinal, o que não é o mesmo que confirmar baixo risco.
    - sem risco e sem nenhum conteúdo comercial (ex.: saudação, pauta,
      texto vazio): `informacao_insuficiente` — não há o que avaliar.
      `vinculo == nao_informado` segue a mesma regra que `cliente`: não é
      presumido como baixo risco nem como prospect.

    `oportunidades` vem de `_REGEX_OPORTUNIDADE`, cada ocorrência gerando uma
    entrada própria, **independente** do resultado de `churn` — os dois
    podem coexistir. `produtos` e `concorrentes` são listas de nomes únicos,
    na ordem em que aparecem, sem evidência associada (o contrato de C01 não
    prevê evidência para esses dois campos) e sem influenciar `churn` ou
    `oportunidades`.
    """

    normalizado = normalizar_preservando_posicoes(transcricao)

    produtos = _nomes_unicos_em_ordem(normalizado, _REGEX_PRODUTOS, _PRODUTOS)
    concorrentes = _nomes_unicos_em_ordem(normalizado, _REGEX_CONCORRENTES, _CONCORRENTES)

    evidencias: list[Evidencia] = []

    def _nova_evidencia(inicio: int, fim: int) -> Evidencia:
        evidencia = Evidencia(
            id=f"e{len(evidencias) + 1}",
            trecho=transcricao[inicio:fim],
            inicio=inicio,
            fim=fim,
        )
        evidencias.append(evidencia)
        return evidencia

    ocorrencias_oportunidade = sorted(_REGEX_OPORTUNIDADE.finditer(normalizado), key=lambda m: m.start())

    if vinculo is Vinculo.PROSPECT:
        churn = Churn(situacao=ChurnSituacao.NAO_APLICAVEL, evidencias=[])
    else:
        escopos = escopos_de_negacao(normalizado, transcricao)
        ocorrencias_risco = _ocorrencias_risco(normalizado, escopos)
        if ocorrencias_risco:
            ids_risco = [_nova_evidencia(inicio, fim).id for inicio, fim in ocorrencias_risco]
            churn = Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=ids_risco)
        elif _ha_conteudo_comercial(normalizado, ocorrencias_oportunidade, produtos, concorrentes):
            churn = Churn(situacao=ChurnSituacao.SEM_SINAL_DETECTADO, evidencias=[])
        else:
            churn = Churn(situacao=ChurnSituacao.INFORMACAO_INSUFICIENTE, evidencias=[])

    oportunidades = []
    for correspondencia in ocorrencias_oportunidade:
        evidencia = _nova_evidencia(correspondencia.start(), correspondencia.end())
        oportunidades.append(
            Oportunidade(
                descricao=f'Interesse comercial sinalizado por "{evidencia.trecho}".',
                evidencias=[evidencia.id],
            )
        )

    return ResultadoSinaisComerciais(
        churn=churn,
        oportunidades=oportunidades,
        produtos=produtos,
        concorrentes=concorrentes,
        evidencias=evidencias,
    )
