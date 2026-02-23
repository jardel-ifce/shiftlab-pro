"""Schemas Pydantic para Despesa."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DespesaBase(BaseModel):
    """Campos comuns para Despesa."""
    data: date = Field(..., description="Data da despesa")
    descricao: str = Field(..., min_length=2, max_length=200, description="Descrição")
    valor: Decimal = Field(..., gt=0, description="Valor em R$")
    categoria: str = Field(..., min_length=2, max_length=50, description="Categoria")
    observacoes: str | None = Field(None, description="Observações")


class DespesaCreate(DespesaBase):
    """Schema para criar despesa."""
    pass


class DespesaUpdate(BaseModel):
    """Schema para atualizar despesa (todos opcionais)."""
    data: date | None = None
    descricao: str | None = Field(None, min_length=2, max_length=200)
    valor: Decimal | None = Field(None, gt=0)
    categoria: str | None = Field(None, min_length=2, max_length=50)
    observacoes: str | None = None


class DespesaResponse(DespesaBase):
    """Schema de resposta."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DespesaListResponse(BaseModel):
    """Resposta paginada de despesas."""
    items: list[DespesaResponse]
    total: int
    page: int
    pages: int
