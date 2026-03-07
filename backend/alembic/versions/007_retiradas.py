"""007 - Cria tabela retiradas.

Registra retiradas de lucro dos sócios.

Revision ID: 007
Revises: 006
Create Date: 2026-03-07
"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "retiradas",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("data", sa.Date, nullable=False, index=True),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("retiradas")
