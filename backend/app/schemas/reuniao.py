"""Schema de entrada para a análise de uma transcrição em texto.

Corresponde ao corpo previsto para `POST /api/analises/texto` (etapa 2).
B01 definiu o rascunho inicial; C01 consolida os limites e a normalização
dos campos de texto, documentados em `docs/contratos/analise-texto.md`.
A rota em si é implementada em B04.
"""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from app.schemas.comum import Vinculo

def _remover_espacos_nas_pontas(valor: object) -> object:
    # Só toca em str: outro tipo segue intacto para o Pydantic rejeitar com
    # `string_type` (ValidationError), em vez de um TypeError fora da validação.
    return valor.strip() if isinstance(valor, str) else valor


TextoSemEspacosNasPontas = Annotated[str, BeforeValidator(_remover_espacos_nas_pontas)]
"""Remove espaços nas pontas antes da validação de tamanho.

Sem isso, uma string só com espaços (`"   "`) passaria em `min_length=1`.
Com o `BeforeValidator`, ela vira `""` antes da checagem e cai no mesmo erro
`string_too_short` de um campo vazio — um único código de erro cobre os dois
casos (ver `app/erros.py`). Números, `null`, listas e objetos não são
convertidos para texto: caem em `string_type` e no envelope `DADOS_INVALIDOS`.
"""


class AnaliseTextoRequest(BaseModel):
    titulo: TextoSemEspacosNasPontas = Field(
        min_length=1, max_length=200, description="Título ou assunto da reunião."
    )
    empresa: TextoSemEspacosNasPontas = Field(
        min_length=1, max_length=200, description="Nome da empresa envolvida na reunião."
    )
    vinculo: Vinculo = Field(description="Relação comercial declarada para esta reunião.")
    transcricao: TextoSemEspacosNasPontas = Field(
        min_length=1, description="Transcrição completa da reunião, em texto."
    )
