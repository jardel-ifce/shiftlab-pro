"""
Modelo Item de Troca - ShiftLab Pro.

Representa uma peça ou filtro usado em uma troca de óleo.
Permite associar filtros de óleo, peças e outros itens a uma troca.
"""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class ItemTroca(BaseModel):
    """
    Entidade Item de Troca.

    Attributes:
        troca_id: ID da troca de óleo
        peca_id: ID da peça utilizada (nullable se filtro)
        filtro_id: ID do filtro utilizado (nullable se peça)
        quantidade: Quantidade utilizada
        valor_unitario: Preço unitário no momento da venda
        valor_total: quantidade × valor_unitario
    """

    __tablename__ = "itens_troca"
    __table_args__ = (
        CheckConstraint(
            "peca_id IS NOT NULL OR filtro_id IS NOT NULL",
            name="ck_itens_troca_peca_or_filtro",
        ),
    )

    troca_id: Mapped[int] = mapped_column(
        ForeignKey("trocas_oleo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID da troca de óleo"
    )

    peca_id: Mapped[int | None] = mapped_column(
        ForeignKey("pecas.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="ID da peça utilizada"
    )

    filtro_id: Mapped[int | None] = mapped_column(
        ForeignKey("filtros_oleo.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="ID do filtro de óleo utilizado"
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

    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="Custo de aquisição no momento da troca"
    )

    @property
    def lucro_item(self) -> Decimal:
        """Lucro bruto do item."""
        return self.valor_total - (self.custo_unitario * self.quantidade)

    # Relacionamentos
    troca: Mapped["TrocaOleo"] = relationship(
        "TrocaOleo",
        back_populates="itens"
    )

    peca: Mapped["Peca | None"] = relationship(
        "Peca",
        lazy="selectin"
    )

    filtro: Mapped["FiltroOleo | None"] = relationship(
        "FiltroOleo",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        ref = f"peca_id={self.peca_id}" if self.peca_id else f"filtro_id={self.filtro_id}"
        return f"<ItemTroca(id={self.id}, troca_id={self.troca_id}, {ref})>"
