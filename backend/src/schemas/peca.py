"""
Schemas Pydantic para Peça/Item.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PecaBase(BaseModel):
    """Campos comuns para Peça."""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do item")
    marca: str | None = Field(None, max_length=50, description="Fabricante")
    unidade: str = Field("unidade", max_length=20, description="Unidade de medida")
    preco_custo: Decimal = Field(Decimal("0"), ge=0, description="Preço de aquisição")
    preco_venda: Decimal = Field(Decimal("0"), ge=0, description="Preço de venda")
    estoque: Decimal = Field(Decimal("0"), ge=0, description="Quantidade em estoque")
    estoque_minimo: Decimal = Field(Decimal("5"), ge=0, description="Estoque mínimo")
    comentarios: str | None = Field(None, description="Comentários")
    observacoes: str | None = Field(None, description="Notas adicionais")


class PecaCreate(PecaBase):
    """Schema para criar peça."""
    pass


class PecaUpdate(BaseModel):
    """Schema para atualizar peça (todos opcionais)."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    marca: str | None = Field(None, max_length=50)
    unidade: str | None = Field(None, max_length=20)
    preco_custo: Decimal | None = Field(None, ge=0)
    preco_venda: Decimal | None = Field(None, ge=0)
    estoque: Decimal | None = Field(None, ge=0)
    estoque_minimo: Decimal | None = Field(None, ge=0)
    ativo: bool | None = Field(None)
    comentarios: str | None = Field(None)
    observacoes: str | None = Field(None)


class PecaResponse(PecaBase):
    """Schema de resposta com dados do banco."""
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime
    estoque_baixo: bool = Field(description="Se estoque está abaixo do mínimo")
    margem_lucro: Decimal = Field(description="Margem de lucro em %")

    model_config = ConfigDict(from_attributes=True)


class PecaListResponse(BaseModel):
    """Resposta paginada de peças."""
    items: list[PecaResponse]
    total: int
    page: int
    pages: int
