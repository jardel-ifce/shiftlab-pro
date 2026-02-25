"""004 - Tabela fotos_filtro para múltiplas imagens por filtro.

Cria tabela fotos_filtro, migra dados existentes de foto_url
e remove a coluna foto_url de filtros_oleo.

Revision ID: 004
Revises: 003
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fotos_filtro",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("filtro_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
        sa.Column("ordem", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_fotos_filtro"),
        sa.ForeignKeyConstraint(
            ["filtro_id"], ["filtros_oleo.id"],
            name="fk_fotos_filtro_filtro_id",
            ondelete="CASCADE"
        ),
    )
    op.create_index("ix_fotos_filtro_filtro_id", "fotos_filtro", ["filtro_id"])

    # Migrar dados existentes de foto_url para a nova tabela
    op.execute("""
        INSERT INTO fotos_filtro (filtro_id, url, ordem, created_at, updated_at)
        SELECT id, foto_url, 0, NOW(), NOW()
        FROM filtros_oleo
        WHERE foto_url IS NOT NULL
    """)

    # Remover coluna antiga
    op.drop_column("filtros_oleo", "foto_url")


def downgrade() -> None:
    op.add_column(
        "filtros_oleo",
        sa.Column("foto_url", sa.String(255), nullable=True)
    )

    # Restaurar a primeira foto de cada filtro
    op.execute("""
        UPDATE filtros_oleo
        SET foto_url = (
            SELECT url FROM fotos_filtro
            WHERE fotos_filtro.filtro_id = filtros_oleo.id
            ORDER BY ordem ASC
            LIMIT 1
        )
    """)

    op.drop_table("fotos_filtro")
