"""
Modelo Foto de Filtro - ShiftLab Pro.

Representa uma imagem associada a um filtro de óleo.
Suporta múltiplas fotos com ordenação.
"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import BaseModel


class FotoFiltro(BaseModel):
    """Entidade Foto de Filtro."""

    __tablename__ = "fotos_filtro"

    filtro_id: Mapped[int] = mapped_column(
        ForeignKey("filtros_oleo.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do filtro de óleo"
    )

    url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Caminho da foto (relativo a /uploads)"
    )

    ordem: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Ordem de exibição (0 = principal)"
    )

    filtro: Mapped["FiltroOleo"] = relationship(
        "FiltroOleo",
        back_populates="fotos"
    )

    def __repr__(self) -> str:
        return f"<FotoFiltro(id={self.id}, filtro_id={self.filtro_id}, ordem={self.ordem})>"
