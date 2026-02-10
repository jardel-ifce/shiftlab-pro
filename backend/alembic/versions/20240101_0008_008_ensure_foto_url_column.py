"""008 - Garantir que foto_url existe na tabela oleos.

Revision ID: 008
Revises: 007
Create Date: 2024-01-01 00:08:00.000000

Corrige caso onde o banco foi criado por create_all() sem a coluna
foto_url, e o stamp do Alembic pulou a migration 006.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("oleos")]

    if "foto_url" not in columns:
        op.add_column(
            "oleos",
            sa.Column("foto_url", sa.String(255), nullable=True),
        )


def downgrade() -> None:
    pass
