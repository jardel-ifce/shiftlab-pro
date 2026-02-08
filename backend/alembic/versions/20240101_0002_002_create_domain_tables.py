"""create domain tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:02

Esta migration cria as tabelas principais do sistema:
- clientes: Cadastro de clientes
- veiculos: Veículos dos clientes
- oleos: Tipos de óleo disponíveis
- trocas_oleo: Registro de trocas realizadas
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria as tabelas do domínio principal.
    """
    # ==========================================================================
    # TABELA CLIENTES
    # ==========================================================================
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("telefone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("cpf_cnpj", sa.String(length=18), nullable=False),
        sa.Column("endereco", sa.Text(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_clientes"),
        sa.UniqueConstraint("cpf_cnpj", name="uq_clientes_cpf_cnpj"),
    )
    op.create_index("ix_clientes_cpf_cnpj", "clientes", ["cpf_cnpj"], unique=True)
    op.create_index("ix_clientes_nome", "clientes", ["nome"], unique=False)

    # ==========================================================================
    # TABELA VEÍCULOS
    # ==========================================================================
    op.create_table(
        "veiculos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("placa", sa.String(length=10), nullable=False),
        sa.Column("marca", sa.String(length=50), nullable=False),
        sa.Column("modelo", sa.String(length=50), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column(
            "tipo_cambio",
            sa.String(length=20),
            server_default="automatico",
            nullable=False
        ),
        sa.Column("quilometragem_atual", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cor", sa.String(length=30), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_veiculos"),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name="fk_veiculos_cliente_id",
            ondelete="CASCADE"
        ),
        sa.UniqueConstraint("placa", name="uq_veiculos_placa"),
    )
    op.create_index("ix_veiculos_placa", "veiculos", ["placa"], unique=True)
    op.create_index("ix_veiculos_cliente_id", "veiculos", ["cliente_id"], unique=False)

    # ==========================================================================
    # TABELA ÓLEOS (PRODUTOS)
    # ==========================================================================
    op.create_table(
        "oleos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("marca", sa.String(length=50), nullable=False),
        sa.Column("tipo", sa.String(length=20), server_default="atf", nullable=False),
        sa.Column("viscosidade", sa.String(length=20), nullable=True),
        sa.Column("especificacao", sa.String(length=100), nullable=True),
        sa.Column("preco_litro", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque_litros", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(10, 2), server_default="5", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_oleos"),
    )
    op.create_index("ix_oleos_marca", "oleos", ["marca"], unique=False)
    op.create_index("ix_oleos_tipo", "oleos", ["tipo"], unique=False)

    # ==========================================================================
    # TABELA TROCAS DE ÓLEO
    # ==========================================================================
    op.create_table(
        "trocas_oleo",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("veiculo_id", sa.Integer(), nullable=False),
        sa.Column("oleo_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("data_troca", sa.Date(), nullable=False),
        sa.Column("quilometragem_troca", sa.Integer(), nullable=False),
        sa.Column("quantidade_litros", sa.Numeric(5, 2), nullable=False),
        sa.Column("valor_oleo", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("valor_servico", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("valor_total", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("proxima_troca_km", sa.Integer(), nullable=True),
        sa.Column("proxima_troca_data", sa.Date(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_trocas_oleo"),
        sa.ForeignKeyConstraint(
            ["veiculo_id"],
            ["veiculos.id"],
            name="fk_trocas_oleo_veiculo_id",
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["oleo_id"],
            ["oleos.id"],
            name="fk_trocas_oleo_oleo_id",
            ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_trocas_oleo_user_id",
            ondelete="SET NULL"
        ),
    )
    op.create_index("ix_trocas_oleo_veiculo_id", "trocas_oleo", ["veiculo_id"], unique=False)
    op.create_index("ix_trocas_oleo_oleo_id", "trocas_oleo", ["oleo_id"], unique=False)
    op.create_index("ix_trocas_oleo_user_id", "trocas_oleo", ["user_id"], unique=False)
    op.create_index("ix_trocas_oleo_data_troca", "trocas_oleo", ["data_troca"], unique=False)


def downgrade() -> None:
    """
    Remove as tabelas do domínio.

    ATENÇÃO: Esta operação é destrutiva!
    """
    # Remove na ordem inversa (por causa das foreign keys)
    op.drop_index("ix_trocas_oleo_data_troca", table_name="trocas_oleo")
    op.drop_index("ix_trocas_oleo_user_id", table_name="trocas_oleo")
    op.drop_index("ix_trocas_oleo_oleo_id", table_name="trocas_oleo")
    op.drop_index("ix_trocas_oleo_veiculo_id", table_name="trocas_oleo")
    op.drop_table("trocas_oleo")

    op.drop_index("ix_oleos_tipo", table_name="oleos")
    op.drop_index("ix_oleos_marca", table_name="oleos")
    op.drop_table("oleos")

    op.drop_index("ix_veiculos_cliente_id", table_name="veiculos")
    op.drop_index("ix_veiculos_placa", table_name="veiculos")
    op.drop_table("veiculos")

    op.drop_index("ix_clientes_nome", table_name="clientes")
    op.drop_index("ix_clientes_cpf_cnpj", table_name="clientes")
    op.drop_table("clientes")
