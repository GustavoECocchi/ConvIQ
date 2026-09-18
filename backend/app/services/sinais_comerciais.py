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
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.analise import Churn, Evidencia, Oportunidade
from app.schemas.comum import ChurnSituacao, Vinculo
from app.services.texto import normalizar_preservando_posicoes

# Risco de cancelamento: linguagem que indica avaliação ou intenção de
# encerrar a relação comercial, não qualquer sentimento negativo genérico
# (esse é o escopo de B02). Sobreposição com o léxico negativo de B02
# ("insatisfeit", "frustrad") é proposital — os dois serviços respondem
# perguntas diferentes (sentimento geral vs. risco de cancelamento) e podem
# gerar evidências próprias para o mesmo trecho; B04 renumera os IDs ao
# juntar os resultados numa `AnaliseTextoResponse` só.
_PADROES_RISCO = [
    r"cancelar",
    r"cancelamento",
    r"reavaliar",
    r"rescindir",
    r"insatisfeit[oa]s?",
    r"frustrad[oa]s?",
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
_PADROES_CONTEXTO_COMERCIAL = [
    r"contratos?",
    r"renova(r|cao|coes|mos)",
    r"suporte",
    r"atendimento",
    r"servicos?",
    r"sistemas?",
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

_REGEX_RISCO = re.compile(r"\b(?:" + "|".join(_PADROES_RISCO) + r")\b")
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
    cai em `informacao_insuficiente`, e um termo genérico ("sistema",
    "produto") usado fora do sentido comercial conta como contexto.
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
    - algum padrão de risco encontrado: `sinal_detectado`, evidenciado pelas
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

    def _nova_evidencia(correspondencia: re.Match[str]) -> Evidencia:
        evidencia = Evidencia(
            id=f"e{len(evidencias) + 1}",
            trecho=transcricao[correspondencia.start():correspondencia.end()],
            inicio=correspondencia.start(),
            fim=correspondencia.end(),
        )
        evidencias.append(evidencia)
        return evidencia

    ocorrencias_oportunidade = sorted(_REGEX_OPORTUNIDADE.finditer(normalizado), key=lambda m: m.start())

    if vinculo is Vinculo.PROSPECT:
        churn = Churn(situacao=ChurnSituacao.NAO_APLICAVEL, evidencias=[])
    else:
        ocorrencias_risco = sorted(_REGEX_RISCO.finditer(normalizado), key=lambda m: m.start())
        if ocorrencias_risco:
            ids_risco = [_nova_evidencia(m).id for m in ocorrencias_risco]
            churn = Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=ids_risco)
        elif _ha_conteudo_comercial(normalizado, ocorrencias_oportunidade, produtos, concorrentes):
            churn = Churn(situacao=ChurnSituacao.SEM_SINAL_DETECTADO, evidencias=[])
        else:
            churn = Churn(situacao=ChurnSituacao.INFORMACAO_INSUFICIENTE, evidencias=[])

    oportunidades = []
    for correspondencia in ocorrencias_oportunidade:
        evidencia = _nova_evidencia(correspondencia)
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
