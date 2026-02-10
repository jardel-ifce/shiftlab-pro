"""
Modelo de Referência - ShiftLab Pro.

Representa modelos de veículos no catálogo de referência.
Cada modelo pertence a uma montadora e contém informações
detalhadas como motor, tipo de câmbio e faixa de anos.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class ModeloReferencia(BaseModel):
    """
    Entidade Modelo de Referência.

    Attributes:
        montadora_id: ID da montadora
        nome: Nome curto do modelo (ex: COROLLA)
        descricao: Descrição completa (ex: COROLLA 1.8L FLEX AT 2009-2019)
        tipo_cambio: Tipo de câmbio padrão deste modelo
        ano_inicio: Ano inicial de produção
        ano_fim: Ano final de produção (NULL = produção atual)
        motor: Motorização (ex: 1.8L FLEX)
        observacoes: Notas adicionais
        ativo: Se está disponível para seleção
    """

    __tablename__ = "modelos_referencia"

    montadora_id: Mapped[int] = mapped_column(
        ForeignKey("montadoras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID da montadora"
    )

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome curto do modelo"
    )

    descricao: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Descrição completa do modelo"
    )

    tipo_cambio: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Tipo de câmbio padrão"
    )

    ano_inicio: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ano inicial de produção"
    )

    ano_fim: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ano final de produção"
    )

    motor: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Motorização"
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
        comment="Se está disponível para seleção"
    )

    # Relacionamentos
    montadora: Mapped["Montadora"] = relationship(
        "Montadora",
        back_populates="modelos"
    )

    def __repr__(self) -> str:
        return f"<ModeloReferencia(id={self.id}, descricao='{self.descricao}')>"
