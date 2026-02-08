"""
Schemas Pydantic para Serviço.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
    """Campos comuns para Serviço."""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do serviço")
    descricao: str | None = Field(None, description="Descrição detalhada")
    preco: Decimal = Field(Decimal("0"), ge=0, description="Preço padrão")
    observacoes: str | None = Field(None, description="Notas adicionais")


class ServicoCreate(ServicoBase):
    """Schema para criar serviço."""
    pass


class ServicoUpdate(BaseModel):
    """Schema para atualizar serviço (todos opcionais)."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    descricao: str | None = Field(None)
    preco: Decimal | None = Field(None, ge=0)
    ativo: bool | None = Field(None)
    observacoes: str | None = Field(None)


class ServicoResponse(ServicoBase):
    """Schema de resposta com dados do banco."""
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServicoListResponse(BaseModel):
    """Resposta paginada de serviços."""
    items: list[ServicoResponse]
    total: int
    page: int
    pages: int
