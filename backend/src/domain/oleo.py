"""
Modelo Óleo - ShiftLab Pro.

Representa um tipo de óleo disponível para troca de câmbio.
Contém informações do produto e controle de estoque.
"""

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class Oleo(BaseModel):
    """
    Entidade Óleo (Produto).

    Attributes:
        nome: Nome comercial do produto
        marca: Fabricante do óleo
        modelo: Linha/modelo do produto (ex: ATF, Multi ATF)
        tipo_veiculo: Tipo de veículo (ex: Carro, Caminhonete)
        viscosidade: Grau de viscosidade (ex: 75W-90)
        volume_unidade: Volume por unidade (ex: 1 L)
        volume_liquido: Volume líquido (ex: 1 L)
        formato_venda: Formato de venda (ex: Unidade, Caixa)
        tipo_recipiente: Tipo de recipiente (ex: Garrafa plástica)
        tipo_oleo_transmissao: Tipo de óleo de transmissão (ex: ATF Dexron VI)
        desempenho: Desempenho do óleo (ex: Full Synthetic Multi-Vehicle)
        codigo_oem: Código OEM (ex: GM General Motors)
        custo_litro: Custo de aquisição por litro
        preco_litro: Preço de venda por litro
        estoque_litros: Quantidade em estoque (litros)
        estoque_minimo: Alerta quando estoque abaixo deste valor
        ativo: Se o produto está disponível para uso
        observacoes: Notas adicionais
        foto_url: Caminho da foto do produto

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

    # Atributos de marketplace
    modelo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Linha/modelo do produto (ex: ATF, Multi ATF)"
    )

    tipo_veiculo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de veículo (ex: Carro, Caminhonete)"
    )

    viscosidade: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Grau de viscosidade (ex: 75W-90)"
    )

    volume_unidade: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Volume por unidade (ex: 1 L, 946 mL)"
    )

    volume_liquido: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Volume líquido (ex: 1 L)"
    )

    formato_venda: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Formato de venda (ex: Unidade, Caixa, Galão)"
    )

    tipo_recipiente: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de recipiente (ex: Garrafa plástica, Lata)"
    )

    tipo_oleo_transmissao: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Tipo de óleo de transmissão (ex: ATF Dexron VI)"
    )

    desempenho: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Desempenho do óleo (ex: Full Synthetic Multi-Vehicle)"
    )

    codigo_oem: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Código OEM (ex: GM General Motors)"
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

    foto_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Caminho da foto do produto"
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
        return f"<Oleo(id={self.id}, nome='{self.nome}', tipo='{self.tipo_oleo_transmissao}')>"
