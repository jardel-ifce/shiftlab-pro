"""Schemas Pydantic para Retirada."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RetiradaBase(BaseModel):
    """Campos comuns para Retirada."""
    data: date = Field(..., description="Data da retirada")
    valor: Decimal = Field(..., gt=0, description="Valor total retirado (R$)")
    descricao: str = Field(..., min_length=2, max_length=200, description="Descrição")
    observacoes: str | None = Field(None, description="Observações")


class RetiradaCreate(RetiradaBase):
    """Schema para criar retirada."""
    pass


class RetiradaUpdate(BaseModel):
    """Schema para atualizar retirada (todos opcionais)."""
    data: date | None = None
    valor: Decimal | None = Field(None, gt=0)
    descricao: str | None = Field(None, min_length=2, max_length=200)
    observacoes: str | None = None


class RetiradaResponse(RetiradaBase):
    """Schema de resposta."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetiradaListResponse(BaseModel):
    """Resposta paginada de retiradas."""
    items: list[RetiradaResponse]
    total: int
    page: int
    pages: int
