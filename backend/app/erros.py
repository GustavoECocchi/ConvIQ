"""Tradução dos erros de validação do FastAPI para o envelope padronizado.

Contrato consolidado em C01 (`docs/contratos/analise-texto.md`): toda
resposta de erro tem o formato `{"erro": {"codigo", "mensagem"}}`. Este
módulo cobre os erros de validação do corpo da requisição (422); nenhuma
rota usa `AnaliseTextoRequest` ainda — a tradução é registrada aqui para que
B04 não precise reformular o formato de erro ao implementar a rota.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.erro import ErroDetalhe, ErroResposta

_CODIGO_PADRAO = "DADOS_INVALIDOS"
_MENSAGEM_PADRAO = "Confira os dados enviados e tente novamente."

_ERROS_CONHECIDOS: dict[tuple[str, str], tuple[str, str]] = {
    ("titulo", "missing"): ("TITULO_OBRIGATORIO", "Informe o título da reunião."),
    ("titulo", "string_too_short"): ("TITULO_OBRIGATORIO", "Informe o título da reunião."),
    ("titulo", "string_too_long"): ("TITULO_INVALIDO", "O título deve ter no máximo 200 caracteres."),
    ("empresa", "missing"): ("EMPRESA_OBRIGATORIA", "Informe a empresa envolvida na reunião."),
    ("empresa", "string_too_short"): ("EMPRESA_OBRIGATORIA", "Informe a empresa envolvida na reunião."),
    ("empresa", "string_too_long"): ("EMPRESA_INVALIDA", "O nome da empresa deve ter no máximo 200 caracteres."),
    ("transcricao", "missing"): ("TRANSCRICAO_VAZIA", "Informe a transcrição para continuar."),
    ("transcricao", "string_too_short"): ("TRANSCRICAO_VAZIA", "Informe a transcrição para continuar."),
    ("vinculo", "missing"): ("VINCULO_INVALIDO", "Informe o vínculo: cliente, prospect ou nao_informado."),
    ("vinculo", "enum"): ("VINCULO_INVALIDO", "Informe um vínculo válido: cliente, prospect ou nao_informado."),
}
"""Mapa (campo, tipo do erro pydantic) -> (código, mensagem) da API.

Cobre só os campos de `AnaliseTextoRequest` (C01/B01). Uma combinação fora
do mapa cai no código genérico `DADOS_INVALIDOS`, sem quebrar a resposta.
"""


def montar_erro_resposta(excecao: RequestValidationError) -> ErroResposta:
    """Converte o primeiro erro de validação relatado no envelope padronizado.

    A API devolve um único erro por resposta; usamos o primeiro item de
    `excecao.errors()`, na ordem dos campos do schema. Combinações não
    mapeadas em `_ERROS_CONHECIDOS` usam o código genérico `DADOS_INVALIDOS`,
    citando o campo quando disponível.
    """

    erros = excecao.errors()
    if not erros:
        return ErroResposta(erro=ErroDetalhe(codigo=_CODIGO_PADRAO, mensagem=_MENSAGEM_PADRAO))

    primeiro = erros[0]
    campo = _nome_do_campo(primeiro["loc"])
    codigo, mensagem = _ERROS_CONHECIDOS.get(
        (campo, primeiro["type"]),
        (_CODIGO_PADRAO, f"Campo inválido: {campo}." if campo else _MENSAGEM_PADRAO),
    )
    return ErroResposta(erro=ErroDetalhe(codigo=codigo, mensagem=mensagem))


def _nome_do_campo(loc: tuple) -> str | None:
    # JSON malformado chega como ('body', <posição do byte>) e corpo que não é
    # objeto como ('body',): nenhum dos dois nomeia um campo do schema.
    if not loc:
        return None
    ultimo = loc[-1]
    if not isinstance(ultimo, str) or ultimo == "body":
        return None
    return ultimo


async def _manipular_erro_validacao(request: Request, excecao: RequestValidationError) -> JSONResponse:
    resposta = montar_erro_resposta(excecao)
    return JSONResponse(status_code=422, content=resposta.model_dump())


def registrar_manipuladores_erro(app: FastAPI) -> None:
    """Liga o envelope padronizado de erro à aplicação, em `criar_app`."""

    app.add_exception_handler(RequestValidationError, _manipular_erro_validacao)
