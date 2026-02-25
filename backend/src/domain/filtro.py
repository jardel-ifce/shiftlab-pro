"""
Modelo Filtro de Óleo - ShiftLab Pro.

Representa um filtro de óleo de câmbio disponível para uso em trocas.
"""

from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class FiltroOleo(BaseModel):
    """Entidade Filtro de Óleo."""

    __tablename__ = "filtros_oleo"

    codigo_produto: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True,
        comment="Código do produto (fornecedor/interno)"
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Modelo do filtro (ex: WFC960)"
    )

    marca: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Fabricante do filtro"
    )

    codigo_oem: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Referência OEM (ex: OC.1604202)"
    )

    custo_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Custo de aquisição unitário"
    )

    preco_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Preço de venda unitário"
    )

    estoque: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Quantidade em estoque (unidades)"
    )

    estoque_minimo: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
        comment="Alerta quando abaixo deste valor"
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se está disponível para uso"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    fotos: Mapped[list["FotoFiltro"]] = relationship(
        "FotoFiltro",
        back_populates="filtro",
        cascade="all, delete-orphan",
        order_by="FotoFiltro.ordem",
        lazy="selectin"
    )

    @property
    def foto_url(self) -> str | None:
        """Backward-compat: URL da foto principal."""
        return self.fotos[0].url if self.fotos else None

    @property
    def estoque_baixo(self) -> bool:
        return self.estoque < self.estoque_minimo

    @property
    def margem_lucro(self) -> Decimal:
        if self.custo_unitario and self.custo_unitario > 0:
            return ((self.preco_unitario - self.custo_unitario) / self.custo_unitario) * 100
        return Decimal("0")

    @property
    def lucro_unitario(self) -> Decimal:
        return self.preco_unitario - self.custo_unitario

    def __repr__(self) -> str:
        return f"<FiltroOleo(id={self.id}, nome='{self.nome}', marca='{self.marca}')>"
