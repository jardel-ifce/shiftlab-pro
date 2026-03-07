"""006 - Adiciona campo taxa_valor em trocas_oleo.

Armazena o valor absoluto da taxa (cartão) para cada troca,
permitindo calcular imposto sobre o faturamento bruto (antes da taxa).

Revision ID: 006
Revises: 005
Create Date: 2026-03-07
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trocas_oleo",
        sa.Column("taxa_valor", sa.Numeric(10, 2), nullable=False,
                  server_default="0",
                  comment="Valor absoluto da taxa (R$)"),
    )

    # Preencher taxa_valor para trocas existentes que têm taxa_percentual > 0
    # subtotal_com_desconto = valor_total / (1 - taxa_percentual/100)
    # taxa_valor = subtotal_com_desconto - valor_total
    op.execute("""
        UPDATE trocas_oleo
        SET taxa_valor = ROUND(
            valor_total / (1 - taxa_percentual / 100) - valor_total, 2
        )
        WHERE taxa_percentual > 0
    """)


def downgrade() -> None:
    op.drop_column("trocas_oleo", "taxa_valor")
