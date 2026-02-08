"""
Model de Usuário para autenticação.

Este módulo define a entidade User que é armazenada no banco de dados
e utilizada para autenticação e autorização.

Campos:
- id: Identificador único (herdado de BaseModel)
- email: Email único do usuário (usado para login)
- hashed_password: Senha criptografada com bcrypt
- nome: Nome completo do usuário
- role: Papel do usuário (admin ou funcionario)
- is_active: Se o usuário está ativo no sistema
- created_at: Data de criação (herdado de BaseModel)
- updated_at: Data de atualização (herdado de BaseModel)
"""

from enum import Enum

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import BaseModel


class UserRole(str, Enum):
    """
    Papéis (roles) disponíveis para usuários.

    Attributes:
        ADMIN: Administrador - acesso total ao sistema
        FUNCIONARIO: Funcionário - acesso operacional
    """
    ADMIN = "admin"
    FUNCIONARIO = "funcionario"


class User(BaseModel):
    """
    Modelo de usuário do sistema.

    Representa um usuário que pode fazer login e realizar
    operações no sistema de acordo com seu papel (role).

    Attributes:
        email: Email único usado para login
        hashed_password: Senha criptografada (nunca armazena texto plano)
        nome: Nome completo para exibição
        role: Papel do usuário (admin ou funcionario)
        is_active: Se pode fazer login (False = bloqueado)

    Example:
        user = User(
            email="joao@oficina.com",
            hashed_password=hash_password("senha123"),
            nome="João Silva",
            role=UserRole.FUNCIONARIO
        )
    """

    __tablename__ = "users"

    # =========================================================================
    # CAMPOS DE IDENTIFICAÇÃO
    # =========================================================================

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Email único do usuário (usado para login)"
    )

    # =========================================================================
    # CAMPOS DE AUTENTICAÇÃO
    # =========================================================================

    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Senha criptografada com bcrypt (NUNCA armazena texto plano)"
    )

    # =========================================================================
    # CAMPOS DE PERFIL
    # =========================================================================

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nome completo do usuário"
    )

    role: Mapped[UserRole] = mapped_column(
        String(20),
        default=UserRole.FUNCIONARIO,
        nullable=False,
        doc="Papel do usuário no sistema (admin ou funcionario)"
    )

    # =========================================================================
    # CAMPOS DE CONTROLE
    # =========================================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Se o usuário está ativo (False = não pode fazer login)"
    )

    # =========================================================================
    # MÉTODOS
    # =========================================================================

    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário é administrador."""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
