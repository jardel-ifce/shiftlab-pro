"""
Schemas Pydantic para Troca de Óleo.

Define validação de entrada e formato de saída da API.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.schemas.item_troca import ItemTrocaCreate, ItemTrocaResponse
from src.schemas.oleo import OleoResponse
from src.schemas.veiculo import VeiculoResponse
from src.auth.schemas import UserResponse


class TrocaOleoBase(BaseModel):
    """Campos comuns para Troca de Óleo."""
    data_troca: date = Field(..., description="Data da troca")
    quilometragem_troca: int = Field(..., ge=0, description="KM no momento da troca")
    quantidade_litros: Decimal = Field(..., gt=0, le=50, description="Litros utilizados")
    valor_oleo: Decimal = Field(Decimal("0"), ge=0, description="Valor cobrado pelo óleo")
    valor_servico: Decimal = Field(Decimal("0"), ge=0, description="Valor do serviço")
    desconto_percentual: Decimal = Field(Decimal("0"), ge=0, le=100, description="% de desconto")
    desconto_valor: Decimal = Field(Decimal("0"), ge=0, description="Desconto fixo em R$")
    motivo_desconto: str | None = Field(None, max_length=200, description="Justificativa do desconto")
    proxima_troca_km: int | None = Field(None, ge=0, description="KM próxima troca")
    proxima_troca_data: date | None = Field(None, description="Data próxima troca")
    observacoes: str | None = Field(None, description="Observações")


class TrocaOleoCreate(TrocaOleoBase):
    """Schema para criar troca de óleo."""
    veiculo_id: int = Field(..., description="ID do veículo")
    oleo_id: int = Field(..., description="ID do óleo utilizado")
    itens: list[ItemTrocaCreate] = Field(
        default_factory=list,
        description="Peças adicionais (filtros, etc.)"
    )

    @field_validator("data_troca")
    @classmethod
    def validar_data(cls, v: date) -> date:
        """Não permite data futura."""
        if v > date.today():
            raise ValueError("Data da troca não pode ser futura")
        return v


class TrocaOleoUpdate(BaseModel):
    """Schema para atualizar troca (todos opcionais)."""
    data_troca: date | None = Field(None)
    quilometragem_troca: int | None = Field(None, ge=0)
    quantidade_litros: Decimal | None = Field(None, gt=0, le=50)
    oleo_id: int | None = Field(None)
    valor_oleo: Decimal | None = Field(None, ge=0)
    valor_servico: Decimal | None = Field(None, ge=0)
    desconto_percentual: Decimal | None = Field(None, ge=0, le=100)
    desconto_valor: Decimal | None = Field(None, ge=0)
    motivo_desconto: str | None = Field(None, max_length=200)
    proxima_troca_km: int | None = Field(None, ge=0)
    proxima_troca_data: date | None = Field(None)
    observacoes: str | None = Field(None)
    itens: list[ItemTrocaCreate] | None = Field(
        None, description="Peças adicionais — se enviado, substitui todos os itens"
    )


class TrocaOleoResponse(TrocaOleoBase):
    """Schema de resposta com dados do banco."""
    id: int
    veiculo_id: int
    oleo_id: int
    user_id: int | None
    valor_total: Decimal
    itens: list[ItemTrocaResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrocaOleoDetailResponse(TrocaOleoResponse):
    """Schema de resposta com relacionamentos e cálculos."""
    veiculo: VeiculoResponse
    oleo: OleoResponse
    user: UserResponse | None = None
    valor_sugerido_oleo: Decimal = Field(description="Preço sugerido: preço_litro × quantidade")
    economia_cliente: Decimal = Field(description="Quanto o cliente economizou")


class TrocaOleoListResponse(BaseModel):
    """Resposta paginada de trocas."""
    items: list[TrocaOleoResponse]
    total: int
    page: int
    pages: int


class ProximasTrocasResponse(BaseModel):
    """Veículos que precisam de troca."""
    veiculo_id: int
    placa: str
    modelo: str
    cliente_nome: str
    ultima_troca: date
    proxima_troca_km: int | None
    proxima_troca_data: date | None
    km_atual: int
    dias_restantes: int | None
    km_restantes: int | None
    urgente: bool = Field(description="Se está vencido ou próximo de vencer")
