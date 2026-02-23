"""
Schemas Pydantic para Filtro de Óleo.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FiltroBase(BaseModel):
    """Campos comuns para Filtro de Óleo."""
    codigo_produto: str | None = Field(None, max_length=30, description="Código do produto (fornecedor/interno)")
    nome: str = Field(..., min_length=2, max_length=100, description="Modelo do filtro")
    marca: str = Field(..., min_length=2, max_length=50, description="Fabricante")
    codigo_oem: str | None = Field(None, max_length=100, description="Referência OEM")
    custo_unitario: Decimal = Field(Decimal("0"), ge=0, description="Custo de aquisição unitário")
    preco_unitario: Decimal = Field(Decimal("0"), ge=0, description="Preço de venda unitário")
    estoque: int = Field(0, ge=0, description="Estoque atual (unidades)")
    estoque_minimo: int = Field(2, ge=0, description="Estoque mínimo")
    observacoes: str | None = Field(None, description="Observações")


class FiltroCreate(FiltroBase):
    """Schema para criar filtro."""
    pass


class FiltroUpdate(BaseModel):
    """Schema para atualizar filtro (todos opcionais)."""
    codigo_produto: str | None = Field(None, max_length=30)
    nome: str | None = Field(None, min_length=2, max_length=100)
    marca: str | None = Field(None, min_length=2, max_length=50)
    codigo_oem: str | None = Field(None, max_length=100)
    custo_unitario: Decimal | None = Field(None, ge=0)
    preco_unitario: Decimal | None = Field(None, ge=0)
    estoque: int | None = Field(None, ge=0)
    estoque_minimo: int | None = Field(None, ge=0)
    ativo: bool | None = Field(None)
    observacoes: str | None = Field(None)
    foto_url: str | None = Field(None)


class FiltroResponse(FiltroBase):
    """Schema de resposta."""
    id: int
    ativo: bool
    foto_url: str | None = Field(None)
    created_at: datetime
    updated_at: datetime
    estoque_baixo: bool = Field(description="Se estoque está abaixo do mínimo")
    margem_lucro: Decimal = Field(description="Margem de lucro em %")
    lucro_unitario: Decimal = Field(description="Lucro bruto unitário")

    model_config = ConfigDict(from_attributes=True)


class FiltroListResponse(BaseModel):
    """Resposta paginada de filtros."""
    items: list[FiltroResponse]
    total: int
    page: int
    pages: int
