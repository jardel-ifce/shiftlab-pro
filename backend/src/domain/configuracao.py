"""
Modelo Configuracao - ShiftLab Pro.

Armazena configurações do sistema em formato chave-valor.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class Configuracao(BaseModel):
    """Configuração do sistema (chave-valor)."""

    __tablename__ = "configuracoes"

    chave: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Chave da configuração (ex: imposto_percentual)"
    )

    valor: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Valor da configuração"
    )

    descricao: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Descrição legível da configuração"
    )

    def __repr__(self) -> str:
        return f"<Configuracao(chave='{self.chave}', valor='{self.valor}')>"
