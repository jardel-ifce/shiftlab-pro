"""
Modelo Item de Troca - ShiftLab Pro.

Representa uma peça/item adicional usado em uma troca de óleo.
Permite associar filtros, descarbonizantes e outros itens a uma troca.
"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class ItemTroca(BaseModel):
    """
    Entidade Item de Troca.

    Attributes:
        troca_id: ID da troca de óleo
        peca_id: ID da peça utilizada
        quantidade: Quantidade utilizada
        valor_unitario: Preço unitário no momento da venda
        valor_total: quantidade × valor_unitario
    """

    __tablename__ = "itens_troca"

    troca_id: Mapped[int] = mapped_column(
        ForeignKey("trocas_oleo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID da troca de óleo"
    )

    peca_id: Mapped[int] = mapped_column(
        ForeignKey("pecas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID da peça utilizada"
    )

    quantidade: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=1,
        comment="Quantidade utilizada"
    )

    valor_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Preço unitário no momento da venda"
    )

    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Total do item (qtd × valor_unitário)"
    )

    # Relacionamentos
    troca: Mapped["TrocaOleo"] = relationship(
        "TrocaOleo",
        back_populates="itens"
    )

    peca: Mapped["Peca"] = relationship(
        "Peca",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ItemTroca(id={self.id}, troca_id={self.troca_id}, peca_id={self.peca_id})>"
