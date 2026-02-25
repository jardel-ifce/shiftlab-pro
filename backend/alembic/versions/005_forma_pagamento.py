"""005 - Adiciona campo forma_pagamento em trocas_oleo.

Revision ID: 005
Revises: 004
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trocas_oleo",
        sa.Column("forma_pagamento", sa.String(100), nullable=True,
                  comment="Forma(s) de pagamento (ex: PIX, Dinheiro, Cartão Crédito)"),
    )


def downgrade() -> None:
    op.drop_column("trocas_oleo", "forma_pagamento")
