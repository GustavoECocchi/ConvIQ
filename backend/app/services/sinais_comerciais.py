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
ação só conta como risco quando um objeto da relação comercial
("contrato", "serviço", "fornecedor") é o núcleo do seu complemento
(revisão B12-R02: "cancelar a reunião sobre o contrato" não liga a ação ao
contrato), e é suprimida quando negada — reutilizando o escopo de negação
de B11 (`app/services/negacao.py`), não uma regra nova. Negar satisfação
atual ("não estamos satisfeitos") passa a contar como risco, do mesmo jeito
que "insatisfeitos" já contava; negar "insatisfeito" deixa de contar (a
mesma regra de B11: negar um problema não prova baixo risco, só suprime o
sinal). A evidência de risco inclui o contexto que a sustenta (revisão
B12-R03): ação e objeto, a condição que abre a frase e o complemento
"com ..." da insatisfação.
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
# "reavaliar"/"rescindir" precisam de um objeto da relação comercial
# (`_PADROES_OBJETO_RISCO`) como núcleo do seu complemento e são suprimidos
# quando negados; "satisfeit" (positivo) só é risco quando negado — o
# espelho de "insatisfeit".
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

# Ligação ação–objeto (revisão B12-R02): palavras que podem ficar entre a
# ação e o núcleo do seu complemento sem mudar de qual objeto se fala —
# artigos, preposições/contrações de regência ("cancelamento do contrato",
# "cancelar com o fornecedor"), possessivos, demonstrativos, quantificadores
# e uns poucos advérbios curtos. Qualquer outra palavra é o núcleo: se não
# for objeto da relação comercial ("a reunião", "a pauta"), a ação não se
# liga a um objeto que apareça depois dele ("a reunião sobre o contrato").
# Lista fechada de palavras funcionais, não vocabulário de domínio.
_PALAVRAS_ANTES_DO_OBJETO = frozenset(
    {
        "o", "a", "os", "as", "um", "uma", "uns", "umas",
        "de", "do", "da", "dos", "das", "com",
        "nosso", "nossa", "nossos", "nossas", "meu", "minha", "meus", "minhas",
        "seu", "sua", "seus", "suas",
        "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas",
        "aquele", "aquela", "aqueles", "aquelas",
        "todo", "toda", "todos", "todas",
        "atual", "atuais",
        "ja", "mesmo", "tambem", "logo", "agora", "imediatamente", "definitivamente",
    }
)
# Coordenação de objetos ("cancelar a reunião e o contrato"): depois de um
# núcleo, "e"/"ou" abrem um novo membro do mesmo complemento.
_CONJUNCOES_COORDENATIVAS = frozenset({"e", "ou"})
# Membro coordenado que é sintagma nominal (revisão B12-R06): depois do
# núcleo, só palavras de `_PALAVRAS_ANTES_DO_OBJETO` ou complementos
# preposicionados ("e o contrato de suporte", "e o contrato no fim do mês").
# Qualquer outra palavra — tipicamente o verbo de uma nova oração, como em
# "e o contrato continua vigente" — mostra que o substantivo depois do "e"
# é sujeito de outra oração, não membro do complemento.
_PREPOSICOES_DO_SINTAGMA = frozenset(
    {"de", "do", "da", "dos", "das", "com", "no", "na", "nos", "nas", "em", "ate"}
)

# Temas inequivocamente alheios à relação comercial (revisão B12-R04):
# clima, refeições, deslocamento e lazer. Quando o núcleo do complemento
# "com ..." de uma insatisfação é um destes temas e o complemento não cita
# nenhum termo da relação comercial (contexto comercial ou produto do
# catálogo), a insatisfação não é risco de churn — "Estamos insatisfeitos
# com o clima." — e, para "satisfeito", também não conta como contexto
# comercial. Lista pequena e fechada, de palavras sem sentido comercial
# plausível numa reunião com cliente; termos ambíguos ("tempo", "time",
# "viagem", "equipe") ficam de fora de propósito. Não é um classificador de
# assuntos: tema alheio fora da lista continua sendo risco, como em B03.
_PADROES_TEMA_ALHEIO = [
    r"clima",
    r"chuvas?",
    r"calor",
    r"frio",
    r"almocos?",
    r"jantar(es)?",
    r"cafes?",
    r"lanches?",
    r"comidas?",
    r"restaurantes?",
    r"transito",
    r"estacionamentos?",
    r"futebol",
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
_REGEX_PALAVRA = re.compile(r"\w+")
# Fim do complemento local de uma ação ou de uma insatisfação: pontuação de
# oração/separação e conjunções adversativas, os mesmos limites do escopo de
# negação de B11 (`app/services/negacao.py`). A conjunção "e" é tratada à
# parte por quem percorre o complemento (coordena objetos de uma ação, mas
# encerra o complemento de uma insatisfação).
_REGEX_FIM_DE_COMPLEMENTO = re.compile(r"[.!?;,\n]|\b(?:mas|porem|contudo|todavia|entretanto)\b")
# Início de frase para reconhecer uma condição que a abre ("Se ..., vamos
# cancelar o contrato"); dois-pontos incluídos para rótulos como "Cliente:".
_REGEX_INICIO_DE_FRASE = re.compile(r"[.!?;:\n]")
_REGEX_COMPLEMENTO_COM = re.compile(r"\s+com\b")
_REGEX_TEMA_ALHEIO = re.compile(r"(?:" + "|".join(_PADROES_TEMA_ALHEIO) + r")")
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


def _fim_do_complemento(normalizado: str, inicio: int) -> int:
    fronteira = _REGEX_FIM_DE_COMPLEMENTO.search(normalizado, inicio)
    return fronteira.start() if fronteira else len(normalizado)


def _e_conjuncao(palavra: re.Match[str], transcricao: str) -> bool:
    """"e"/"ou" como conjunção; o "é" do verbo também vira "e" na
    normalização, por isso o caractere original é consultado (como em
    `app/services/negacao.py`)."""

    return palavra.group() in _CONJUNCOES_COORDENATIVAS and transcricao[palavra.start()] not in "éÉ"


def _nucleo(membro: list[re.Match[str]]) -> re.Match[str] | None:
    """Primeira palavra do membro fora de `_PALAVRAS_ANTES_DO_OBJETO`."""

    return next((palavra for palavra in membro if palavra.group() not in _PALAVRAS_ANTES_DO_OBJETO), None)


def _e_sintagma_nominal(membro: list[re.Match[str]]) -> bool:
    """O membro é um núcleo com modificadores, sem verbo de outra oração (B12-R06).

    Depois do núcleo, aceita só palavras de `_PALAVRAS_ANTES_DO_OBJETO` e
    complementos preposicionados de `_PREPOSICOES_DO_SINTAGMA` seguidos do
    seu próprio núcleo: "o contrato", "o contrato atual", "o contrato de
    suporte", "o contrato no fim do mês". "o contrato continua vigente" e
    "o fornecedor será avisado" não são, porque "continua"/"será" não é
    modificador. Não reconhece verbos: qualquer palavra fora dessas listas
    encerra o sintagma, inclusive advérbios como "hoje" (limite documentado).
    """

    esperando_nucleo = True
    for palavra in membro:
        texto = palavra.group()
        if esperando_nucleo:
            if texto not in _PALAVRAS_ANTES_DO_OBJETO:
                esperando_nucleo = False
        elif texto in _PREPOSICOES_DO_SINTAGMA:
            esperando_nucleo = True
        elif texto not in _PALAVRAS_ANTES_DO_OBJETO:
            return False
    return not esperando_nucleo


def _membros_coordenados(palavras: list[re.Match[str]], transcricao: str) -> list[list[re.Match[str]]]:
    """Divide um complemento em membros coordenados por "e"/"ou".

    O primeiro membro é o complemento direto e vale como está. Cada membro
    depois de uma conjunção só entra se for sintagma nominal
    (`_e_sintagma_nominal`); o primeiro que não for indica que começou outra
    oração ("a reunião e o contrato continua vigente"), e ele e os seguintes
    ficam fora do complemento.
    """

    membros: list[list[re.Match[str]]] = [[]]
    for palavra in palavras:
        if _e_conjuncao(palavra, transcricao):
            membros.append([])
        else:
            membros[-1].append(palavra)
    incluidos = [membros[0]]
    for membro in membros[1:]:
        if not _e_sintagma_nominal(membro):
            break
        incluidos.append(membro)
    return incluidos


def _fim_do_objeto_da_acao(normalizado: str, transcricao: str, fim_acao: int) -> int | None:
    """Fim do objeto da relação comercial ligado à ação, ou `None` (B12-R02/R06).

    Percorre o complemento da ação até `_fim_do_complemento`, dividido em
    membros coordenados (`_membros_coordenados`). Em cada membro, as palavras
    de `_PALAVRAS_ANTES_DO_OBJETO` são puladas e a primeira outra palavra é
    o núcleo. Se um núcleo for objeto de `_PADROES_OBJETO_RISCO`, a ação está
    ligada a ele ("cancelar o contrato", "rescindir o nosso contrato",
    "cancelamento do contrato", "cancelar com o fornecedor", "cancelar a
    reunião e o contrato"). Se o núcleo for outro substantivo ("cancelar a
    reunião"), o que vem depois só o modifica ("a reunião sobre o contrato",
    "a pauta com o fornecedor") e não liga a ação a um contrato. "e não o
    contrato" e "e o contrato continua vigente" não são membros do
    complemento. Objeto antes da ação ou em outra oração nunca se liga.
    """

    palavras = list(_REGEX_PALAVRA.finditer(normalizado, fim_acao, _fim_do_complemento(normalizado, fim_acao)))
    for membro in _membros_coordenados(palavras, transcricao):
        nucleo = _nucleo(membro)
        if nucleo is not None and _REGEX_OBJETO_RISCO.fullmatch(nucleo.group()):
            return nucleo.end()
    return None


def _inicio_da_condicao(normalizado: str, inicio_acao: int) -> int | None:
    """Início do "Se" que abre a frase da ação, quando houver (B12-R03).

    "Se o suporte continuar assim, vamos cancelar o contrato." é uma ameaça
    condicional: continua sendo risco, mas a evidência mostra a condição
    para não parecer uma decisão já tomada. Só a condição no início da
    frase é reconhecida; "se" em outra posição pode ser pronome
    ("decidiu-se") e não estende a evidência.
    """

    fronteiras = [fronteira.end() for fronteira in _REGEX_INICIO_DE_FRASE.finditer(normalizado, 0, inicio_acao)]
    primeira_palavra = _REGEX_PALAVRA.search(normalizado, fronteiras[-1] if fronteiras else 0, inicio_acao)
    if primeira_palavra is not None and primeira_palavra.group() == "se":
        return primeira_palavra.start()
    return None


def _complemento_com(normalizado: str, transcricao: str, fim_palavra: int) -> list[list[re.Match[str]]]:
    """Membros do complemento "com ..." logo depois de uma palavra, ou `[]`.

    "insatisfeitos com o suporte" → `[["o", "suporte"]]`; "com o almoço e
    com o suporte" → dois membros; "com o suporte e vamos cancelar o
    contrato" → só o primeiro, porque "vamos cancelar o contrato" é outra
    oração (`_membros_coordenados`). O complemento termina em
    `_fim_do_complemento`. Sem "com" logo depois, ou sem palavra depois do
    "com", não há complemento.
    """

    preposicao = _REGEX_COMPLEMENTO_COM.match(normalizado, fim_palavra)
    if preposicao is None:
        return []
    limite = _fim_do_complemento(normalizado, preposicao.end())
    palavras = list(_REGEX_PALAVRA.finditer(normalizado, preposicao.end(), limite))
    membros = _membros_coordenados(palavras, transcricao)
    return membros if membros[0] else []


def _e_tema_alheio(normalizado: str, membros: list[list[re.Match[str]]]) -> bool:
    """O complemento trata só de tema alheio à relação comercial (B12-R04).

    Exige as duas condições, para só excluir casos inequívocos: o núcleo de
    cada membro está em `_PADROES_TEMA_ALHEIO` ("com o clima", "com o almoço
    e o café"), e nenhum termo de contexto comercial ou produto do catálogo
    aparece no complemento ("com o clima da parceria" continua risco).
    """

    if not membros:
        return False
    for membro in membros:
        nucleo = _nucleo(membro)
        if nucleo is None or not _REGEX_TEMA_ALHEIO.fullmatch(nucleo.group()):
            return False
    trecho = normalizado[membros[0][0].start():membros[-1][-1].end()]
    return not (_REGEX_CONTEXTO_COMERCIAL.search(trecho) or _REGEX_PRODUTOS.search(trecho))


def _ocorrencias_risco(
    normalizado: str, transcricao: str, escopos: list[tuple[int, int, int]]
) -> list[tuple[int, int]]:
    """Devolve `(inicio, fim)` de cada ocorrência de risco, já com a negação
    de B11 aplicada (ver `app/services/negacao.py`).

    Três fontes, cada uma com sua própria regra de negação:

    - `_PADROES_RISCO_PADRAO` ("insatisfeito", "frustrado"): risco por si só,
      suprimido quando negado — "não estamos insatisfeitos" deixa de ser
      risco, do mesmo jeito que B11 suprime "sem problemas" no sentimento —
      ou quando o complemento "com ..." é tema alheio à relação comercial
      (`_e_tema_alheio`, revisão B12-R04: "insatisfeitos com o clima").
    - `_PADROES_ACAO_RISCO` ("cancelar", "reavaliar", "rescindir"): só é
      risco quando um objeto da relação comercial (`_PADROES_OBJETO_RISCO`)
      é o núcleo do seu complemento (`_fim_do_objeto_da_acao`) — "cancelar
      a reunião" e "cancelar a reunião sobre o contrato" não bastam,
      "cancelar o contrato" basta — e é suprimido quando a própria ação
      está negada.
    - `_PADROES_SATISFACAO` ("satisfeito"): é o espelho de "insatisfeito" —
      só é risco quando **negado** ("não estamos satisfeitos"), com a mesma
      exceção de tema alheio ("não estamos satisfeitos com o almoço");
      satisfação afirmada nunca é risco. A evidência começa no marcador,
      como a evidência negada de B11.

    Evidência com o contexto que sustenta o risco (revisão B12-R03): a ação
    vai até o objeto ligado ("cancelar o contrato"), começando no "Se" de
    uma condição que abre a frase; a insatisfação inclui o complemento
    "com ..." quando houver ("insatisfeitos com o suporte"), com seus
    membros coordenados. Sempre um recorte literal e contínuo da transcrição.
    """

    spans: list[tuple[int, int]] = []

    def _insatisfacao(inicio: int, fim_palavra: int) -> None:
        membros = _complemento_com(normalizado, transcricao, fim_palavra)
        if _e_tema_alheio(normalizado, membros):
            return
        spans.append((inicio, membros[-1][-1].end() if membros else fim_palavra))

    for correspondencia in _REGEX_RISCO_PADRAO.finditer(normalizado):
        if inicio_da_negacao_mais_proxima(escopos, correspondencia.start()) is not None:
            continue
        _insatisfacao(correspondencia.start(), correspondencia.end())

    for acao in _REGEX_ACAO_RISCO.finditer(normalizado):
        if inicio_da_negacao_mais_proxima(escopos, acao.start()) is not None:
            continue
        fim_objeto = _fim_do_objeto_da_acao(normalizado, transcricao, acao.end())
        if fim_objeto is None:
            continue
        inicio_condicao = _inicio_da_condicao(normalizado, acao.start())
        spans.append((acao.start() if inicio_condicao is None else inicio_condicao, fim_objeto))

    for correspondencia in _REGEX_SATISFACAO.finditer(normalizado):
        inicio_negacao = inicio_da_negacao_mais_proxima(escopos, correspondencia.start())
        if inicio_negacao is not None:
            _insatisfacao(inicio_negacao, correspondencia.end())

    return sorted(set(spans))


def _ha_contexto_comercial(normalizado: str, transcricao: str) -> bool:
    """Algum termo de `_PADROES_CONTEXTO_COMERCIAL` fala da relação comercial.

    "satisfeito" com complemento de tema alheio ("satisfeitos com o
    almoço", afirmado ou negado) não conta (revisão B12-R04): sem outro
    termo, a conversa não dá base para avaliar churn.
    """

    for termo in _REGEX_CONTEXTO_COMERCIAL.finditer(normalizado):
        if _REGEX_SATISFACAO.fullmatch(termo.group()) and _e_tema_alheio(
            normalizado, _complemento_com(normalizado, transcricao, termo.end())
        ):
            continue
        return True
    return False


def _ha_conteudo_comercial(
    normalizado: str,
    transcricao: str,
    ocorrencias_oportunidade: list[re.Match[str]],
    produtos: list[str],
    concorrentes: list[str],
) -> bool:
    """Decide se a transcrição dá base para avaliar churn (B03-R01).

    Risco explícito já é tratado antes de chamar esta função. Aqui, qualquer
    oportunidade, produto, concorrente ou termo de contexto comercial basta
    para considerar a conversa avaliável (`_ha_contexto_comercial`).
    Limite: usa vocabulário fixo — uma conversa sobre a relação comercial
    que não use nenhum destes termos cai em `informacao_insuficiente`, e um
    termo genérico ("produto") usado fora do sentido comercial ainda conta
    como contexto ("sistema" foi removido em B12 por ser genérico demais;
    "produto" permanece, limite conhecido e não resolvido nesta entrega).
    """

    return bool(
        ocorrencias_oportunidade
        or produtos
        or concorrentes
        or _ha_contexto_comercial(normalizado, transcricao)
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
        ocorrencias_risco = _ocorrencias_risco(normalizado, transcricao, escopos)
        if ocorrencias_risco:
            ids_risco = [_nova_evidencia(inicio, fim).id for inicio, fim in ocorrencias_risco]
            churn = Churn(situacao=ChurnSituacao.SINAL_DETECTADO, evidencias=ids_risco)
        elif _ha_conteudo_comercial(normalizado, transcricao, ocorrencias_oportunidade, produtos, concorrentes):
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
