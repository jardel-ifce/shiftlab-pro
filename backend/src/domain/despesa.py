"""
Modelo Despesa - ShiftLab Pro.

Despesas operacionais avulsas da oficina (manutenção, aluguel, etc.).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class Despesa(BaseModel):
    """Despesa avulsa da oficina."""

    __tablename__ = "despesas"

    data: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data da despesa"
    )

    descricao: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Descrição da despesa"
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Valor da despesa em R$"
    )

    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Categoria: manutencao, aluguel, energia, etc."
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    def __repr__(self) -> str:
        return f"<Despesa(id={self.id}, descricao='{self.descricao}', valor={self.valor})>"
