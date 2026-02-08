"""
Schemas Pydantic para Cliente.

Define validação de entrada e formato de saída da API.
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClienteBase(BaseModel):
    """Campos comuns para Cliente."""
    nome: str = Field(..., min_length=2, max_length=150, description="Nome completo")
    telefone: str = Field(..., min_length=8, max_length=20, description="Telefone")
    email: str | None = Field(None, max_length=255, description="Email")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    endereco: str | None = Field(None, description="Endereço completo")
    observacoes: str | None = Field(None, description="Observações")

    @field_validator("cpf_cnpj")
    @classmethod
    def validar_cpf_cnpj(cls, v: str) -> str:
        """Remove formatação e valida tamanho."""
        # Remove caracteres não numéricos
        numeros = re.sub(r"\D", "", v)
        if len(numeros) == 11:
            # CPF - formata
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) == 14:
            # CNPJ - formata
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        else:
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")

    @field_validator("telefone")
    @classmethod
    def formatar_telefone(cls, v: str) -> str:
        """Remove formatação extra."""
        return re.sub(r"[^\d\+\-\(\)\s]", "", v).strip()


class ClienteCreate(ClienteBase):
    """Schema para criar cliente."""
    pass


class ClienteUpdate(BaseModel):
    """Schema para atualizar cliente (todos opcionais)."""
    nome: str | None = Field(None, min_length=2, max_length=150)
    telefone: str | None = Field(None, min_length=8, max_length=20)
    email: str | None = Field(None, max_length=255)
    endereco: str | None = Field(None)
    observacoes: str | None = Field(None)


class ClienteResponse(ClienteBase):
    """Schema de resposta com dados do banco."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClienteListResponse(BaseModel):
    """Resposta paginada de clientes."""
    items: list[ClienteResponse]
    total: int
    page: int
    pages: int
