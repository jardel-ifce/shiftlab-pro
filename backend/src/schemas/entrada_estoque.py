"""
Schemas Pydantic para Entrada de Estoque (multi-produto).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntradaEstoqueCreate(BaseModel):
    """Schema para criar entrada."""
    tipo_produto: str = Field(..., description="Tipo: oleo, filtro, peca")
    produto_id: int = Field(..., description="ID do produto")
    quantidade_litros: Decimal = Field(..., gt=0, description="Quantidade")
    custo_unitario: Decimal = Field(..., ge=0, description="Custo unitário")
    fornecedor: str | None = Field(None, max_length=100, description="Fornecedor")
    nota_fiscal: str | None = Field(None, max_length=50, description="Número da NF")
    data_compra: date = Field(..., description="Data da compra")
    observacoes: str | None = Field(None, description="Observações")

    @field_validator("tipo_produto")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in ("oleo", "filtro", "peca"):
            raise ValueError("Tipo deve ser 'oleo', 'filtro' ou 'peca'")
        return v


class EntradaEstoqueResponse(BaseModel):
    """Schema de resposta."""
    id: int
    tipo_produto: str
    produto_id: int
    produto_nome: str
    produto_marca: str
    quantidade_litros: Decimal
    custo_unitario: Decimal
    custo_total: Decimal
    fornecedor: str | None
    nota_fiscal: str | None
    data_compra: date
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EntradaEstoqueListResponse(BaseModel):
    """Resposta paginada."""
    items: list[EntradaEstoqueResponse]
    total: int
    page: int
    pages: int


class ProdutoBuscaResponse(BaseModel):
    """Resultado de busca de produto."""
    tipo: str = Field(description="oleo, filtro, peca")
    id: int
    codigo_produto: str | None = None
    nome: str
    marca: str
    label: str = Field(description="Texto formatado para exibição")
