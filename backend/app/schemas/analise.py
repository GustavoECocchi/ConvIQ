"""Schemas do resultado da análise de uma reunião.

Contrato consolidado em C01 para o corpo de resposta de
`POST /api/analises/texto` (rota implementada em B04, sobre os serviços de
B02/B03). Campos, exemplos e o que o schema não impõe estão documentados em
docs/contratos/analise-texto.md.
"""

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.comum import ChurnSituacao, Sentimento


class Evidencia(BaseModel):
    """Trecho literal da transcrição original que sustenta um sinal.

    `inicio`/`fim` são posições em caracteres na transcrição de entrada
    (`fim` exclusivo), para localizar o trecho mesmo quando o texto se
    repete. Timestamps de áudio não fazem parte deste schema porque só
    existem quando fornecidos pelo transcritor, a partir da etapa 4.
    """

    id: str = Field(min_length=1, description="Identificador da evidência, único dentro da resposta.")
    trecho: str = Field(min_length=1, description="Trecho literal copiado da transcrição original.")
    inicio: int = Field(ge=0, description="Posição, em caracteres, onde o trecho começa na transcrição.")
    fim: int = Field(gt=0, description="Posição, em caracteres, onde o trecho termina na transcrição (exclusiva).")

    @field_validator("fim")
    @classmethod
    def fim_maior_que_inicio(cls, fim: int, info) -> int:
        inicio = info.data.get("inicio")
        if inicio is not None and fim <= inicio:
            raise ValueError("'fim' deve ser maior que 'inicio'.")
        return fim


class Churn(BaseModel):
    """Situação de risco de cancelamento.

    A regra de produto que obriga `nao_aplicavel` para reunião com
    `vinculo=prospect` não é validável neste schema, pois envolve o
    schema de entrada (`AnaliseTextoRequest`); cabe ao serviço de análise
    (B03) aplicá-la antes de compor esta resposta.
    """

    situacao: ChurnSituacao
    evidencias: list[str] = Field(default_factory=list, description="IDs de evidências que sustentam esta situação.")


class Oportunidade(BaseModel):
    descricao: str = Field(min_length=1)
    evidencias: list[str] = Field(default_factory=list)


class Recomendacao(BaseModel):
    texto: str = Field(min_length=1)
    evidencias: list[str] = Field(default_factory=list)


class AnaliseTextoResponse(BaseModel):
    transcricao: str = Field(min_length=1, description="Transcrição recebida, ecoada para referência da interface.")
    sentimento: Sentimento
    churn: Churn
    oportunidades: list[Oportunidade] = Field(default_factory=list)
    produtos: list[str] = Field(default_factory=list, description="Produtos citados; lista vazia quando nenhum foi identificado.")
    concorrentes: list[str] = Field(default_factory=list, description="Concorrentes citados; menção isolada não implica intenção de troca.")
    evidencias: list[Evidencia] = Field(default_factory=list)
    recomendacoes: list[Recomendacao] = Field(default_factory=list)
    metodo: str = Field(min_length=1, description="Método usado na análise, ex.: 'regras'.")
    versao_analise: str = Field(min_length=1, description="Versão do método de análise usado.")

    @model_validator(mode="after")
    def evidencias_tem_ids_unicos(self) -> "AnaliseTextoResponse":
        ids = [evidencia.id for evidencia in self.evidencias]
        duplicados = {id_ for id_ in ids if ids.count(id_) > 1}
        if duplicados:
            raise ValueError(f"IDs de evidência duplicados em 'evidencias': {sorted(duplicados)}")
        return self

    @model_validator(mode="after")
    def evidencias_referenciadas_existem(self) -> "AnaliseTextoResponse":
        ids_existentes = {evidencia.id for evidencia in self.evidencias}
        referenciados: set[str] = set(self.churn.evidencias)
        for oportunidade in self.oportunidades:
            referenciados.update(oportunidade.evidencias)
        for recomendacao in self.recomendacoes:
            referenciados.update(recomendacao.evidencias)
        faltantes = referenciados - ids_existentes
        if faltantes:
            raise ValueError(
                f"IDs de evidência referenciados e ausentes em 'evidencias': {sorted(faltantes)}"
            )
        return self
