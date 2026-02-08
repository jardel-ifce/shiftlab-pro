"""
Modelo base para todas as entidades do domínio.

Fornece campos comuns que todas as tabelas devem ter:
- id: Chave primária auto-incrementada
- created_at: Data/hora de criação
- updated_at: Data/hora da última atualização

Uso:
    from src.domain.base import BaseModel

    class Cliente(BaseModel):
        __tablename__ = "clientes"
        nome: Mapped[str] = mapped_column(String(100))
        ...
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from src.database import Base


class BaseModel(Base):
    """
    Classe base abstrata para todos os models do domínio.

    Fornece:
    - id: Chave primária inteira auto-incrementada
    - created_at: Timestamp de criação (preenchido automaticamente)
    - updated_at: Timestamp de atualização (atualizado automaticamente)

    Exemplo:
        class User(BaseModel):
            __tablename__ = "users"

            email: Mapped[str] = mapped_column(String(255), unique=True)
            name: Mapped[str] = mapped_column(String(100))
    """

    # Marca como classe abstrata (não cria tabela para BaseModel)
    __abstract__ = True

    # ==========================================================================
    # CAMPOS COMUNS
    # ==========================================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Identificador único da entidade"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Data e hora de criação do registro"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Data e hora da última atualização"
    )

    # ==========================================================================
    # MÉTODOS UTILITÁRIOS
    # ==========================================================================

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """
        Gera nome da tabela automaticamente baseado no nome da classe.

        Converte CamelCase para snake_case e pluraliza.
        Exemplo: UserProfile -> user_profiles

        Pode ser sobrescrito definindo __tablename__ diretamente na classe.
        """
        import re
        # Converte CamelCase para snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Pluraliza (simplificado)
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return name + 'es'
        else:
            return name + 's'

    def to_dict(self) -> dict[str, Any]:
        """
        Converte o model para dicionário.

        Útil para serialização e debugging.

        Returns:
            dict: Dicionário com todos os campos do model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """
        Representação string do model para debugging.

        Exemplo: <User(id=1, email='admin@example.com')>
        """
        # Pega apenas os primeiros 3 campos para não ficar muito longo
        columns = list(self.__table__.columns)[:3]
        attrs = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in columns
        )
        return f"<{self.__class__.__name__}({attrs})>"


class SoftDeleteMixin:
    """
    Mixin para soft delete (exclusão lógica).

    Em vez de deletar fisicamente o registro, marca como deletado.
    Isso permite manter histórico e recuperar dados.

    Uso:
        class Cliente(BaseModel, SoftDeleteMixin):
            __tablename__ = "clientes"
            nome: Mapped[str] = mapped_column(String(100))

        # Para "deletar":
        cliente.deleted_at = datetime.now()

        # Para buscar apenas ativos:
        query = select(Cliente).where(Cliente.deleted_at.is_(None))
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Data de exclusão lógica (None = ativo)"
    )

    @property
    def is_deleted(self) -> bool:
        """Verifica se o registro foi deletado logicamente."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Marca o registro como deletado."""
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restaura um registro deletado logicamente."""
        self.deleted_at = None
