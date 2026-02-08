"""add desconto to trocas

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:04

Adiciona campos de desconto à tabela trocas_oleo.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona colunas de desconto à tabela trocas_oleo."""
    op.add_column(
        "trocas_oleo",
        sa.Column(
            "desconto_percentual",
            sa.Numeric(5, 2),
            server_default="0",
            nullable=False,
            comment="Percentual de desconto aplicado"
        )
    )

    op.add_column(
        "trocas_oleo",
        sa.Column(
            "desconto_valor",
            sa.Numeric(10, 2),
            server_default="0",
            nullable=False,
            comment="Valor fixo de desconto em R$"
        )
    )

    op.add_column(
        "trocas_oleo",
        sa.Column(
            "motivo_desconto",
            sa.Text(),
            nullable=True,
            comment="Justificativa do desconto"
        )
    )


def downgrade() -> None:
    """Remove colunas de desconto."""
    op.drop_column("trocas_oleo", "motivo_desconto")
    op.drop_column("trocas_oleo", "desconto_valor")
    op.drop_column("trocas_oleo", "desconto_percentual")
