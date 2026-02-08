"""
Schemas Pydantic para Item de Troca.

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.peca import PecaResponse


class ItemTrocaCreate(BaseModel):
    """Schema para criar item de troca (nested dentro de TrocaOleoCreate)."""
    peca_id: int = Field(..., description="ID da peça")
    quantidade: Decimal = Field(..., gt=0, le=999, description="Quantidade")
    valor_unitario: Decimal = Field(..., ge=0, description="Preço unitário")


class ItemTrocaResponse(BaseModel):
    """Schema de resposta para item de troca."""
    id: int
    peca_id: int
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    peca: PecaResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
