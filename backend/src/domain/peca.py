"""
Modelo Peça/Item - ShiftLab Pro.

Representa peças e itens auxiliares usados nas trocas
(filtros, descarbonizantes, estopas, aditivos, etc.).
"""

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class Peca(BaseModel):
    """
    Entidade Peça/Item.

    Attributes:
        nome: Nome do item
        marca: Fabricante
        unidade: Unidade de medida (texto livre)
        preco_custo: Preço de aquisição
        preco_venda: Preço de venda ao cliente
        estoque: Quantidade em estoque
        estoque_minimo: Alerta quando abaixo deste valor
        ativo: Se o item está disponível
        comentarios: Comentários sobre o item
        observacoes: Notas adicionais
    """

    __tablename__ = "pecas"

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome do item"
    )

    marca: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Fabricante"
    )

    unidade: Mapped[str] = mapped_column(
        String(20),
        default="unidade",
        nullable=False,
        comment="Unidade de medida"
    )

    preco_custo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Preço de aquisição"
    )

    preco_venda: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Preço de venda ao cliente"
    )

    estoque: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Quantidade em estoque"
    )

    estoque_minimo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=5,
        nullable=False,
        comment="Alerta quando abaixo deste valor"
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se está disponível para uso"
    )

    comentarios: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Comentários sobre o item"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    @property
    def estoque_baixo(self) -> bool:
        """Verifica se estoque está abaixo do mínimo."""
        return self.estoque < self.estoque_minimo

    @property
    def margem_lucro(self) -> Decimal:
        """Calcula margem de lucro em percentual."""
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return Decimal("0")

    def __repr__(self) -> str:
        return f"<Peca(id={self.id}, nome='{self.nome}')>"
