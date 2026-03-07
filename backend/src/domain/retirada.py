"""Modelo Retirada - ShiftLab Pro.

Retiradas de lucro dos sócios.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class Retirada(BaseModel):
    """Retirada de lucro dos sócios."""

    __tablename__ = "retiradas"

    data: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data da retirada"
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Valor total retirado (soma dos sócios)"
    )

    descricao: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Descrição da retirada"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )
