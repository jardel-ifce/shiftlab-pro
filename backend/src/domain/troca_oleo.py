"""
Modelo Troca de Óleo - ShiftLab Pro.

Representa o registro de uma troca de óleo de câmbio.
É o coração do sistema - armazena todo o histórico de serviços.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class TrocaOleo(BaseModel):
    """
    Entidade Troca de Óleo.

    Registra cada troca de óleo realizada, incluindo:
    - Qual veículo
    - Qual óleo foi usado
    - Quem realizou o serviço
    - Valores cobrados
    - Próxima troca prevista

    Attributes:
        veiculo_id: Veículo que recebeu a troca
        oleo_id: Tipo de óleo utilizado
        user_id: Funcionário que realizou a troca
        data_troca: Data em que a troca foi realizada
        quilometragem_troca: KM do veículo no momento da troca
        quantidade_litros: Quantidade de óleo utilizada
        valor_oleo: Valor cobrado pelo óleo
        valor_servico: Valor da mão de obra
        valor_total: Soma de óleo + serviço
        proxima_troca_km: KM previsto para próxima troca
        proxima_troca_data: Data prevista para próxima troca
        observacoes: Notas sobre o serviço

    Relationships:
        veiculo: Veículo relacionado
        oleo: Óleo utilizado
        user: Funcionário que realizou
    """

    __tablename__ = "trocas_oleo"

    # Relacionamentos obrigatórios
    veiculo_id: Mapped[int] = mapped_column(
        ForeignKey("veiculos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do veículo"
    )

    oleo_id: Mapped[int] = mapped_column(
        ForeignKey("oleos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID do óleo utilizado"
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID do funcionário que realizou"
    )

    # Dados da troca
    data_troca: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Data da troca"
    )

    quilometragem_troca: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="KM no momento da troca"
    )

    quantidade_litros: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Litros de óleo utilizados"
    )

    # Valores
    valor_oleo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Valor cobrado pelo óleo"
    )

    valor_servico: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Valor da mão de obra"
    )

    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Valor total (óleo + serviço - desconto)"
    )

    # Desconto
    desconto_percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
        comment="Percentual de desconto aplicado"
    )

    desconto_valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Valor fixo de desconto em R$"
    )

    motivo_desconto: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Justificativa do desconto"
    )

    # Próxima troca
    proxima_troca_km: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="KM previsto para próxima troca"
    )

    proxima_troca_data: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Data prevista para próxima troca"
    )

    # Observações
    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas sobre o serviço"
    )

    # Relacionamentos
    veiculo: Mapped["Veiculo"] = relationship(
        "Veiculo",
        back_populates="trocas"
    )

    oleo: Mapped["Oleo"] = relationship(
        "Oleo",
        back_populates="trocas"
    )

    user: Mapped["User | None"] = relationship(
        "User",
        lazy="selectin"
    )

    itens: Mapped[list["ItemTroca"]] = relationship(
        "ItemTroca",
        back_populates="troca",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def valor_sugerido_oleo(self) -> Decimal:
        """Calcula valor sugerido baseado no preço do óleo * quantidade."""
        if self.oleo and self.quantidade_litros:
            return self.oleo.preco_litro * self.quantidade_litros
        return Decimal("0")

    @property
    def economia_cliente(self) -> Decimal:
        """Retorna quanto o cliente economizou com o desconto."""
        return self.desconto_valor + (
            (self.valor_sugerido_oleo + self.valor_servico) * self.desconto_percentual / 100
        )

    @property
    def precisa_troca(self) -> bool:
        """Verifica se está na hora de fazer nova troca."""
        hoje = date.today()
        if self.proxima_troca_data and self.proxima_troca_data <= hoje:
            return True
        if self.proxima_troca_km and self.veiculo:
            if self.veiculo.quilometragem_atual >= self.proxima_troca_km:
                return True
        return False

    def __repr__(self) -> str:
        return f"<TrocaOleo(id={self.id}, veiculo_id={self.veiculo_id}, data='{self.data_troca}')>"
