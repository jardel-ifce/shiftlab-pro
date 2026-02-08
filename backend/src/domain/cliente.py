"""
Modelo Cliente - ShiftLab Pro.

Representa um cliente da oficina (pessoa física ou jurídica).
Um cliente pode ter vários veículos cadastrados.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class Cliente(BaseModel):
    """
    Entidade Cliente.

    Attributes:
        nome: Nome completo ou razão social
        telefone: Telefone principal para contato
        email: Email para comunicação (opcional)
        cpf_cnpj: CPF ou CNPJ (único)
        endereco: Endereço completo (opcional)
        observacoes: Notas adicionais sobre o cliente

    Relationships:
        veiculos: Lista de veículos do cliente
    """

    __tablename__ = "clientes"

    # Dados de identificação
    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Nome completo ou razão social"
    )

    telefone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Telefone principal"
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email para contato"
    )

    cpf_cnpj: Mapped[str] = mapped_column(
        String(18),
        unique=True,
        nullable=False,
        index=True,
        comment="CPF (11 dígitos) ou CNPJ (14 dígitos)"
    )

    # Endereço (texto livre)
    endereco: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Endereço completo"
    )

    # Observações
    observacoes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionais"
    )

    # Relacionamentos
    veiculos: Mapped[list["Veiculo"]] = relationship(
        "Veiculo",
        back_populates="cliente",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id}, nome='{self.nome}', cpf_cnpj='{self.cpf_cnpj}')>"
