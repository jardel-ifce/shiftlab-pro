"""
Schemas Pydantic para Item de Troca.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.schemas.filtro import FiltroResponse
from src.schemas.peca import PecaResponse


class ItemTrocaCreate(BaseModel):
    """Schema para criar item de troca (nested dentro de TrocaOleoCreate)."""
    peca_id: int | None = Field(None, description="ID da peça (se for peça)")
    filtro_id: int | None = Field(None, description="ID do filtro (se for filtro)")
    quantidade: Decimal = Field(..., gt=0, le=999, description="Quantidade")
    valor_unitario: Decimal = Field(..., ge=0, description="Preço unitário")

    @model_validator(mode="after")
    def check_peca_or_filtro(self) -> "ItemTrocaCreate":
        if not self.peca_id and not self.filtro_id:
            raise ValueError("Informe peca_id ou filtro_id")
        if self.peca_id and self.filtro_id:
            raise ValueError("Informe apenas peca_id ou filtro_id, não ambos")
        return self


class ItemTrocaResponse(BaseModel):
    """Schema de resposta para item de troca."""
    id: int
    peca_id: int | None = None
    filtro_id: int | None = None
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    custo_unitario: Decimal = Field(default=Decimal("0"))
    peca: PecaResponse | None = None
    filtro: FiltroResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
