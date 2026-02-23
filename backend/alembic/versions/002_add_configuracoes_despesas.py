"""002 - Adiciona tabelas configuracoes e despesas.

Revision ID: 002
Revises: 001
Create Date: 2026-02-23

Novas tabelas:
- configuracoes: Configurações do sistema (chave-valor)
- despesas: Despesas avulsas para cálculo do lucro líquido
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CONFIGURACOES
    op.create_table(
        "configuracoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chave", sa.String(50), nullable=False),
        sa.Column("valor", sa.Text(), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_configuracoes"),
        sa.UniqueConstraint("chave", name="uq_configuracoes_chave"),
    )
    op.create_index("ix_configuracoes_chave", "configuracoes", ["chave"])

    # Seed: imposto padrão 6% (MEI/Simples)
    op.execute(
        "INSERT INTO configuracoes (chave, valor, descricao, created_at, updated_at) "
        "VALUES ('imposto_percentual', '6.0', 'Percentual de imposto sobre faturamento bruto (MEI/Simples)', NOW(), NOW())"
    )

    # DESPESAS
    op.create_table(
        "despesas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_despesas"),
    )
    op.create_index("ix_despesas_data", "despesas", ["data"])
    op.create_index("ix_despesas_categoria", "despesas", ["categoria"])


def downgrade() -> None:
    op.drop_table("despesas")
    op.drop_table("configuracoes")
