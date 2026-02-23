"""014 — add taxa_percentual to trocas_oleo

Revision ID: 014
Revises: 013
Create Date: 2024-01-01 00:14:00
"""

from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trocas_oleo",
        sa.Column(
            "taxa_percentual",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="0",
            comment="Percentual de taxa (ex: taxa cartão)",
        ),
    )


def downgrade() -> None:
    op.drop_column("trocas_oleo", "taxa_percentual")
