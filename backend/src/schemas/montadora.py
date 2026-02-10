"""
Schemas Pydantic para Montadora.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MontadoraBase(BaseModel):
    """Campos comuns para Montadora."""
    nome: str = Field(..., min_length=1, max_length=50, description="Nome da montadora")
    pais_origem: str | None = Field(None, max_length=50, description="País de origem")


class MontadoraCreate(MontadoraBase):
    """Schema para criar montadora."""
    pass


class MontadoraUpdate(BaseModel):
    """Schema para atualizar montadora (todos opcionais)."""
    nome: str | None = Field(None, min_length=1, max_length=50)
    pais_origem: str | None = Field(None, max_length=50)
    ativo: bool | None = None


class MontadoraResponse(MontadoraBase):
    """Schema de resposta com dados do banco."""
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MontadoraComModelosResponse(MontadoraResponse):
    """Schema de resposta incluindo modelos da montadora."""
    modelos: list["ModeloReferenciaResponse"] = []


class MontadoraListResponse(BaseModel):
    """Resposta de lista de montadoras."""
    items: list[MontadoraResponse]
    total: int


# Importação tardia para evitar referência circular
from src.schemas.modelo_referencia import ModeloReferenciaResponse  # noqa: E402

MontadoraComModelosResponse.model_rebuild()
