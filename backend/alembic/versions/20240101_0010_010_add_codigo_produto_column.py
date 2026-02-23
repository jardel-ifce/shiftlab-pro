"""010 - Adicionar coluna codigo_produto à tabela oleos.

Revision ID: 010
Revises: 009
Create Date: 2024-01-01 00:10:00.000000

Adiciona campo codigo_produto (código interno/fornecedor) à tabela oleos.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("oleos", sa.Column(
        "codigo_produto", sa.String(30), nullable=True,
        comment="Código do produto (fornecedor/interno)"
    ))
    op.create_index("ix_oleos_codigo_produto", "oleos", ["codigo_produto"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_oleos_codigo_produto", table_name="oleos")
    op.drop_column("oleos", "codigo_produto")
