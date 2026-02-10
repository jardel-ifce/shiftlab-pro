"""
Modelo Montadora - ShiftLab Pro.

Representa as marcas/fabricantes de veículos (catálogo de referência).
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class Montadora(BaseModel):
    """
    Entidade Montadora.

    Attributes:
        nome: Nome da montadora (ex: TOYOTA, HONDA)
        pais_origem: País de origem (ex: Japão)
        ativo: Se está disponível para seleção
    """

    __tablename__ = "montadoras"

    nome: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome da montadora"
    )

    pais_origem: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="País de origem"
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se está disponível para seleção"
    )

    # Relacionamentos
    modelos: Mapped[list["ModeloReferencia"]] = relationship(
        "ModeloReferencia",
        back_populates="montadora",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ModeloReferencia.nome"
    )

    def __repr__(self) -> str:
        return f"<Montadora(id={self.id}, nome='{self.nome}')>"
