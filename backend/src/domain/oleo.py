"""
Modelo Óleo - ShiftLab Pro.

Representa um tipo de óleo disponível para troca de câmbio.
Contém informações do produto e controle de estoque.
"""

from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class TipoOleo(str, Enum):
    """Tipos de óleo de câmbio."""
    ATF = "atf"              # Automatic Transmission Fluid
    CVT = "cvt"              # Para câmbios CVT
    MANUAL = "manual"        # Para câmbios manuais
    DUAL_CLUTCH = "dct"      # Para câmbios de dupla embreagem
    UNIVERSAL = "universal"  # Multiuso


class Oleo(BaseModel):
    """
    Entidade Óleo (Produto).

    Attributes:
        nome: Nome comercial do produto
        marca: Fabricante do óleo
        tipo: Tipo de óleo (ATF, CVT, Manual, etc)
        viscosidade: Especificação de viscosidade (ex: 75W-90)
        especificacao: Normas atendidas (ex: Dexron VI, ATF+4)
        preco_litro: Preço por litro
        estoque_litros: Quantidade em estoque (litros)
        estoque_minimo: Alerta quando estoque abaixo deste valor
        ativo: Se o produto está disponível para uso
        observacoes: Notas adicionais

    Relationships:
        trocas: Trocas realizadas com este óleo
    """

    __tablename__ = "oleos"

    # Identificação do produto
    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome comercial do produto"
    )

    marca: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Fabricante do óleo"
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        default=TipoOleo.ATF.value,
        nullable=False,
        index=True,
        comment="Tipo de óleo"
    )

    # Especificações técnicas
    viscosidade: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Especificação de viscosidade (ex: 75W-90)"
    )

    especificacao: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Normas atendidas (ex: Dexron VI)"
    )

    # Preço e estoque
    custo_litro: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Custo de aquisição por litro"
    )

    preco_litro: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Preço de venda por litro"
    )

    estoque_litros: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Quantidade em estoque (litros)"
    )

    estoque_minimo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=5,
        nullable=False,
        comment="Alerta quando abaixo deste valor"
    )

    # Controle
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

    # Relacionamentos
    trocas: Mapped[list["TrocaOleo"]] = relationship(
        "TrocaOleo",
        back_populates="oleo",
        lazy="selectin"
    )

    @property
    def estoque_baixo(self) -> bool:
        """Verifica se estoque está abaixo do mínimo."""
        return self.estoque_litros < self.estoque_minimo

    @property
    def margem_lucro(self) -> Decimal:
        """Calcula margem de lucro em percentual."""
        if self.custo_litro and self.custo_litro > 0:
            return ((self.preco_litro - self.custo_litro) / self.custo_litro) * 100
        return Decimal("0")

    @property
    def lucro_por_litro(self) -> Decimal:
        """Retorna o lucro bruto por litro."""
        return self.preco_litro - self.custo_litro

    @property
    def nome_completo(self) -> str:
        """Retorna nome formatado com marca."""
        return f"{self.marca} {self.nome}"

    def __repr__(self) -> str:
        return f"<Oleo(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
