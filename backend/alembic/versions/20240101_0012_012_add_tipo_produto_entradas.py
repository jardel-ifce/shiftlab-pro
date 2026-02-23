"""012 - Adicionar suporte multi-produto em entradas_estoque.

Revision ID: 012
Revises: 011
Create Date: 2024-01-01 00:12:00.000000

Adiciona tipo_produto, produto_id, produto_nome, produto_marca.
Migra dados existentes (oleo_id -> produto_id, tipo_produto='oleo').
Torna oleo_id nullable.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar novas colunas
    op.add_column("entradas_estoque", sa.Column(
        "tipo_produto", sa.String(10), nullable=True,
        comment="Tipo: oleo, filtro, peca"
    ))
    op.add_column("entradas_estoque", sa.Column(
        "produto_id", sa.Integer(), nullable=True,
        comment="ID do produto (genérico)"
    ))
    op.add_column("entradas_estoque", sa.Column(
        "produto_nome", sa.String(100), nullable=True,
        comment="Nome do produto (desnormalizado)"
    ))
    op.add_column("entradas_estoque", sa.Column(
        "produto_marca", sa.String(50), nullable=True,
        comment="Marca do produto (desnormalizada)"
    ))

    # Migrar dados existentes
    op.execute("""
        UPDATE entradas_estoque
        SET tipo_produto = 'oleo',
            produto_id = oleo_id,
            produto_nome = (SELECT nome FROM oleos WHERE oleos.id = entradas_estoque.oleo_id),
            produto_marca = (SELECT marca FROM oleos WHERE oleos.id = entradas_estoque.oleo_id)
    """)

    # Tornar colunas NOT NULL após popular
    op.alter_column("entradas_estoque", "tipo_produto", nullable=False)
    op.alter_column("entradas_estoque", "produto_id", nullable=False)
    op.alter_column("entradas_estoque", "produto_nome", nullable=False)
    op.alter_column("entradas_estoque", "produto_marca", nullable=False)

    # Tornar oleo_id nullable
    op.alter_column("entradas_estoque", "oleo_id", nullable=True)

    # Índices
    op.create_index("ix_entradas_estoque_tipo_produto", "entradas_estoque", ["tipo_produto"])
    op.create_index("ix_entradas_estoque_produto_id", "entradas_estoque", ["produto_id"])


def downgrade() -> None:
    op.drop_index("ix_entradas_estoque_produto_id", table_name="entradas_estoque")
    op.drop_index("ix_entradas_estoque_tipo_produto", table_name="entradas_estoque")
    op.alter_column("entradas_estoque", "oleo_id", nullable=False)
    op.drop_column("entradas_estoque", "produto_marca")
    op.drop_column("entradas_estoque", "produto_nome")
    op.drop_column("entradas_estoque", "produto_id")
    op.drop_column("entradas_estoque", "tipo_produto")
