"""Schema de resposta do endpoint de saúde."""

from typing import Literal

from pydantic import BaseModel


class RespostaSaude(BaseModel):
    status: Literal["ok"]
    ambiente: str
