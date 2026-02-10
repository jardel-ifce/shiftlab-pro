"""
Schemas Pydantic para Veículo.

Define validação de entrada e formato de saída da API.
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.veiculo import TipoCambio
from src.schemas.cliente import ClienteResponse


class VeiculoBase(BaseModel):
    """Campos comuns para Veículo."""
    placa: str = Field(..., min_length=7, max_length=10, description="Placa do veículo")
    marca: str = Field(..., min_length=2, max_length=50, description="Marca")
    modelo: str = Field(..., min_length=1, max_length=200, description="Modelo")
    ano: int = Field(..., ge=1900, le=2100, description="Ano de fabricação")
    tipo_cambio: str = Field(TipoCambio.AUTOMATICO.value, description="Tipo de câmbio")
    quilometragem_atual: int = Field(0, ge=0, description="Quilometragem atual")
    cor: str | None = Field(None, max_length=30, description="Cor do veículo")
    observacoes: str | None = Field(None, description="Observações")

    @field_validator("placa")
    @classmethod
    def formatar_placa(cls, v: str) -> str:
        """Normaliza a placa para maiúsculo sem espaços."""
        placa = re.sub(r"[^A-Za-z0-9]", "", v).upper()
        # Formato antigo: ABC1234 ou Mercosul: ABC1D23
        if not re.match(r"^[A-Z]{3}\d[A-Z0-9]\d{2}$", placa):
            raise ValueError("Placa inválida. Use formato ABC1234 ou ABC1D23")
        return placa

    @field_validator("tipo_cambio")
    @classmethod
    def validar_tipo_cambio(cls, v: str) -> str:
        """Valida se é um tipo de câmbio válido."""
        tipos_validos = [t.value for t in TipoCambio]
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de câmbio inválido. Use: {', '.join(tipos_validos)}")
        return v.lower()


class VeiculoCreate(VeiculoBase):
    """Schema para criar veículo."""
    cliente_id: int = Field(..., description="ID do cliente proprietário")


class VeiculoUpdate(BaseModel):
    """Schema para atualizar veículo (todos opcionais)."""
    marca: str | None = Field(None, min_length=2, max_length=50)
    modelo: str | None = Field(None, min_length=1, max_length=200)
    ano: int | None = Field(None, ge=1900, le=2100)
    tipo_cambio: str | None = Field(None)
    quilometragem_atual: int | None = Field(None, ge=0)
    cor: str | None = Field(None, max_length=30)
    observacoes: str | None = Field(None)
    cliente_id: int | None = Field(None, description="Transferir para outro cliente")


class VeiculoResponse(VeiculoBase):
    """Schema de resposta com dados do banco."""
    id: int
    cliente_id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VeiculoComClienteResponse(VeiculoResponse):
    """Schema de resposta incluindo dados do cliente."""
    cliente: ClienteResponse


class VeiculoListResponse(BaseModel):
    """Resposta paginada de veículos."""
    items: list[VeiculoResponse]
    total: int
    page: int
    pages: int
