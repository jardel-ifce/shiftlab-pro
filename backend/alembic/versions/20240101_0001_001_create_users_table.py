"""create users table

Revision ID: 001
Revises: None
Create Date: 2024-01-01 00:00:01

Esta é a primeira migration do sistema.
Cria a tabela de usuários para autenticação.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria a tabela users.

    Campos:
    - id: Chave primária auto-incrementada
    - email: Email único do usuário (usado para login)
    - hashed_password: Senha criptografada com bcrypt
    - nome: Nome completo do usuário
    - role: Papel no sistema (admin ou funcionario)
    - is_active: Se o usuário pode fazer login
    - created_at: Data de criação do registro
    - updated_at: Data da última atualização

    Índices:
    - ix_users_email: Índice único no email (busca rápida no login)
    - ix_users_role: Índice no role (filtrar por papel)
    """
    op.create_table(
        "users",
        # Chave primária
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        # Campos de identificação
        sa.Column("email", sa.String(length=255), nullable=False),
        # Campos de autenticação
        sa.Column("hashed_password", sa.Text(), nullable=False),
        # Campos de perfil
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="funcionario"
        ),
        # Campos de controle
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),
        # Campos de auditoria (herdados de BaseModel)
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # Índices para performance
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)


def downgrade() -> None:
    """
    Remove a tabela users.

    ATENÇÃO: Esta operação é destrutiva!
    Todos os dados de usuários serão perdidos.
    """
    # Remove índices
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")

    # Remove tabela
    op.drop_table("users")
