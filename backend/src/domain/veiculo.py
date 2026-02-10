"""
Modelo Veículo - ShiftLab Pro.

Representa um veículo cadastrado no sistema.
Cada veículo pertence a um cliente e pode ter várias trocas de óleo.
"""

from enum import Enum

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class TipoCambio(str, Enum):
    """Tipos de câmbio suportados."""
    MANUAL = "manual"
    AUTOMATICO = "automatico"
    CVT = "cvt"
    AUTOMATIZADO = "automatizado"       # Ex: I-Motion, Dualogic
    DUPLA_EMBREAGEM = "dupla_embreagem" # Ex: DSG, PowerShift, DCT
    OUTRO = "outro"


class Veiculo(BaseModel):
    """
    Entidade Veículo.

    Attributes:
        cliente_id: ID do cliente proprietário
        placa: Placa do veículo (única)
        marca: Marca do veículo (ex: Toyota, Honda)
        modelo: Modelo do veículo (ex: Corolla, Civic)
        ano: Ano de fabricação
        tipo_cambio: Tipo de câmbio (manual, automático, CVT, etc)
        quilometragem_atual: Última quilometragem registrada
        cor: Cor do veículo (opcional)
        observacoes: Notas adicionais

    Relationships:
        cliente: Cliente proprietário
        trocas: Histórico de trocas de óleo
    """

    __tablename__ = "veiculos"

    # Relacionamento com cliente
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do cliente proprietário"
    )

    # Identificação do veículo
    placa: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        comment="Placa do veículo"
    )

    marca: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Marca do veículo"
    )

    modelo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Modelo do veículo"
    )

    ano: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Ano de fabricação"
    )

    # Características do câmbio
    tipo_cambio: Mapped[str] = mapped_column(
        String(20),
        default=TipoCambio.AUTOMATICO.value,
        nullable=False,
        comment="Tipo de câmbio"
    )

    # Quilometragem
    quilometragem_atual: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Última quilometragem registrada"
    )

    # Dados opcionais
    cor: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Cor do veículo"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se o veículo está ativo no sistema"
    )

    # Relacionamentos
    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="veiculos"
    )

    trocas: Mapped[list["TrocaOleo"]] = relationship(
        "TrocaOleo",
        back_populates="veiculo",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(TrocaOleo.data_troca)"
    )

    @property
    def nome_completo(self) -> str:
        """Retorna marca + modelo + ano."""
        return f"{self.marca} {self.modelo} {self.ano}"

    def __repr__(self) -> str:
        return f"<Veiculo(id={self.id}, placa='{self.placa}', modelo='{self.modelo}')>"
