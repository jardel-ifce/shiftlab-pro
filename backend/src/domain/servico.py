"""
Modelo Serviço - ShiftLab Pro.

Representa tipos de serviço oferecidos pela oficina
(troca simples, troca motor transversal, SUV/pickup, etc.).
"""

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class Servico(BaseModel):
    """
    Entidade Serviço.

    Attributes:
        nome: Nome do serviço
        descricao: Descrição detalhada
        preco: Preço padrão do serviço
        ativo: Se está disponível para seleção
        observacoes: Notas adicionais
    """

    __tablename__ = "servicos"

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome do serviço"
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição detalhada"
    )

    preco: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Preço padrão do serviço"
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se está disponível para seleção"
    )

    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    def __repr__(self) -> str:
        return f"<Servico(id={self.id}, nome='{self.nome}')>"
