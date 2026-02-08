"""add custo_litro to oleos

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:03

Adiciona campo de custo de aquisição para controle de margem de lucro.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona coluna custo_litro à tabela oleos."""
    op.add_column(
        "oleos",
        sa.Column(
            "custo_litro",
            sa.Numeric(10, 2),
            server_default="0",
            nullable=False,
            comment="Custo de aquisição por litro"
        )
    )


def downgrade() -> None:
    """Remove coluna custo_litro."""
    op.drop_column("oleos", "custo_litro")
