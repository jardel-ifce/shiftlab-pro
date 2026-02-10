"""006 - Adicionar foto_url na tabela oleos.

Revision ID: 006
Revises: 005
Create Date: 2024-01-01 00:06:00.000000

Permite armazenar caminho da imagem do produto (embalagem do óleo).
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "oleos",
        sa.Column("foto_url", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("oleos", "foto_url")
