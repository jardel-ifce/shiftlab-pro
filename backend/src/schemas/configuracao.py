"""Schemas Pydantic para Configuracao."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConfiguracaoUpdate(BaseModel):
    """Schema para atualizar uma configuração."""
    valor: str = Field(..., min_length=1, description="Novo valor da configuração")


class ConfiguracaoResponse(BaseModel):
    """Schema de resposta."""
    id: int
    chave: str
    valor: str
    descricao: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImpostoResponse(BaseModel):
    """Resposta simplificada do imposto."""
    percentual: float = Field(description="Percentual de imposto atual")
