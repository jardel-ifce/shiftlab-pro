"""003 - Adiciona filtro_id em itens_troca.

Permite que itens de uma troca referenciem filtros de óleo
além de peças. peca_id passa a ser nullable; um dos dois
(peca_id ou filtro_id) deve estar preenchido.

Revision ID: 003
Revises: 002
Create Date: 2026-02-23
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Torna peca_id nullable
    op.alter_column(
        "itens_troca",
        "peca_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # Adiciona filtro_id (nullable, FK para filtros_oleo)
    op.add_column(
        "itens_troca",
        sa.Column("filtro_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_itens_troca_filtro_id",
        "itens_troca",
        "filtros_oleo",
        ["filtro_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_itens_troca_filtro_id", "itens_troca", ["filtro_id"])

    # CHECK: pelo menos um dos dois deve estar preenchido
    op.create_check_constraint(
        "ck_itens_troca_peca_or_filtro",
        "itens_troca",
        "peca_id IS NOT NULL OR filtro_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_constraint("ck_itens_troca_peca_or_filtro", "itens_troca", type_="check")
    op.drop_index("ix_itens_troca_filtro_id", table_name="itens_troca")
    op.drop_constraint("fk_itens_troca_filtro_id", "itens_troca", type_="foreignkey")
    op.drop_column("itens_troca", "filtro_id")
    op.alter_column(
        "itens_troca",
        "peca_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
