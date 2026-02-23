"""013 - Adicionar snapshot de custos para cálculo de lucro.

Revision ID: 013
Revises: 012
Create Date: 2024-01-01 00:13:00.000000

Adiciona custo_oleo em trocas_oleo e custo_unitario em itens_troca.
Popula dados existentes com custos atuais dos produtos.
"""

from alembic import op
import sqlalchemy as sa


revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adicionar colunas nullable primeiro
    op.add_column(
        "trocas_oleo",
        sa.Column("custo_oleo", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "itens_troca",
        sa.Column("custo_unitario", sa.Numeric(10, 2), nullable=True),
    )

    # 2. Popular dados existentes com custos atuais
    op.execute("""
        UPDATE trocas_oleo
        SET custo_oleo = COALESCE(
            (SELECT oleos.custo_litro * trocas_oleo.quantidade_litros
             FROM oleos WHERE oleos.id = trocas_oleo.oleo_id),
            0
        )
    """)

    op.execute("""
        UPDATE itens_troca
        SET custo_unitario = COALESCE(
            (SELECT pecas.preco_custo
             FROM pecas WHERE pecas.id = itens_troca.peca_id),
            0
        )
    """)

    # 3. Tornar NOT NULL com default 0
    op.alter_column(
        "trocas_oleo",
        "custo_oleo",
        nullable=False,
        server_default="0",
    )
    op.alter_column(
        "itens_troca",
        "custo_unitario",
        nullable=False,
        server_default="0",
    )


def downgrade() -> None:
    op.drop_column("itens_troca", "custo_unitario")
    op.drop_column("trocas_oleo", "custo_oleo")
