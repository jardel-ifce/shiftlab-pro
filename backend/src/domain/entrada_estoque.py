"""
Modelo Entrada de Estoque - ShiftLab Pro.

Registra cada compra/aquisição de produto (óleo, filtro ou peça),
mantendo histórico de custos e fornecedores.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class EntradaEstoque(BaseModel):
    """Entidade Entrada de Estoque (multi-produto)."""

    __tablename__ = "entradas_estoque"

    # Produto genérico
    tipo_produto: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="Tipo: oleo, filtro, peca"
    )

    produto_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID do produto (genérico)"
    )

    produto_nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome do produto (desnormalizado)"
    )

    produto_marca: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Marca do produto (desnormalizada)"
    )

    # FK legado (nullable para entradas de filtro/peça)
    oleo_id: Mapped[int | None] = mapped_column(
        ForeignKey("oleos.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID do óleo (legado, nullable)"
    )

    quantidade_litros: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Quantidade comprada"
    )

    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Custo unitário na compra"
    )

    custo_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total da compra (qtd × custo)"
    )

    fornecedor: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Nome do fornecedor"
    )

    nota_fiscal: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Número da nota fiscal"
    )

    data_compra: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data da compra"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    # Relacionamentos
    oleo: Mapped["Oleo"] = relationship(
        "Oleo",
        back_populates="entradas_estoque"
    )

    def __repr__(self) -> str:
        return f"<EntradaEstoque(id={self.id}, tipo={self.tipo_produto}, produto_id={self.produto_id})>"
