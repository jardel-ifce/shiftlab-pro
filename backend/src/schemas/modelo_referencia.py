"""
Schemas Pydantic para Modelo de Referência.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ModeloReferenciaBase(BaseModel):
    """Campos comuns para ModeloReferencia."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome curto do modelo")
    descricao: str = Field(..., min_length=1, max_length=200, description="Descrição completa")
    tipo_cambio: str | None = Field(None, max_length=20, description="Tipo de câmbio padrão")
    ano_inicio: int | None = Field(None, ge=1900, le=2100, description="Ano inicial")
    ano_fim: int | None = Field(None, ge=1900, le=2100, description="Ano final")
    motor: str | None = Field(None, max_length=50, description="Motorização")
    observacoes: str | None = Field(None, description="Notas adicionais")


class ModeloReferenciaCreate(ModeloReferenciaBase):
    """Schema para criar modelo de referência."""
    montadora_id: int = Field(..., description="ID da montadora")


class ModeloReferenciaUpdate(BaseModel):
    """Schema para atualizar modelo de referência (todos opcionais)."""
    nome: str | None = Field(None, min_length=1, max_length=100)
    descricao: str | None = Field(None, min_length=1, max_length=200)
    tipo_cambio: str | None = None
    ano_inicio: int | None = None
    ano_fim: int | None = None
    motor: str | None = None
    observacoes: str | None = None
    ativo: bool | None = None


class ModeloReferenciaResponse(ModeloReferenciaBase):
    """Schema de resposta com dados do banco."""
    id: int
    montadora_id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModeloReferenciaListResponse(BaseModel):
    """Resposta de lista de modelos de referência."""
    items: list[ModeloReferenciaResponse]
    total: int
