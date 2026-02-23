"""011 - Criar tabela filtros_oleo.

Revision ID: 011
Revises: 010
Create Date: 2024-01-01 00:11:00.000000

Cria tabela para gerenciamento de filtros de óleo de câmbio.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "filtros_oleo",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_produto", sa.String(30), nullable=True, comment="Código do produto (fornecedor/interno)"),
        sa.Column("nome", sa.String(100), nullable=False, comment="Modelo do filtro (ex: WFC960)"),
        sa.Column("marca", sa.String(50), nullable=False, comment="Fabricante do filtro"),
        sa.Column("codigo_oem", sa.String(100), nullable=True, comment="Referência OEM (ex: OC.1604202)"),
        sa.Column("custo_unitario", sa.Numeric(10, 2), nullable=False, server_default="0", comment="Custo de aquisição unitário"),
        sa.Column("preco_unitario", sa.Numeric(10, 2), nullable=False, server_default="0", comment="Preço de venda unitário"),
        sa.Column("estoque", sa.Integer(), nullable=False, server_default="0", comment="Quantidade em estoque (unidades)"),
        sa.Column("estoque_minimo", sa.Integer(), nullable=False, server_default="2", comment="Alerta quando abaixo deste valor"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true", comment="Se está disponível para uso"),
        sa.Column("observacoes", sa.Text(), nullable=True, comment="Notas adicionais"),
        sa.Column("foto_url", sa.String(255), nullable=True, comment="Caminho da foto do produto"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_filtros_oleo"),
    )
    op.create_index("ix_filtros_oleo_id", "filtros_oleo", ["id"])
    op.create_index("ix_filtros_oleo_codigo_produto", "filtros_oleo", ["codigo_produto"])
    op.create_index("ix_filtros_oleo_marca", "filtros_oleo", ["marca"])


def downgrade() -> None:
    op.drop_index("ix_filtros_oleo_marca", table_name="filtros_oleo")
    op.drop_index("ix_filtros_oleo_codigo_produto", table_name="filtros_oleo")
    op.drop_index("ix_filtros_oleo_id", table_name="filtros_oleo")
    op.drop_table("filtros_oleo")
