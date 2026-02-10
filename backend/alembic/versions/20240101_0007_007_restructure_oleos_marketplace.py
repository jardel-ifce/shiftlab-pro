"""007 - Reestruturar tabela oleos com atributos de marketplace.

Revision ID: 007
Revises: 006
Create Date: 2024-01-01 00:07:00.000000

Remove campos tipo e especificacao, adiciona 9 novos campos descritivos
no estilo marketplace. Wipe autorizado pelo usuário.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- DATA WIPE (autorizado pelo usuário) ---
    op.execute("DELETE FROM trocas_oleo")
    op.execute("DELETE FROM oleos")

    # --- REMOVER COLUNAS ANTIGAS ---
    op.drop_index("ix_oleos_tipo", table_name="oleos")
    op.drop_column("oleos", "tipo")
    op.drop_column("oleos", "especificacao")

    # --- ADICIONAR NOVAS COLUNAS ---
    op.add_column("oleos", sa.Column(
        "modelo", sa.String(100), nullable=True,
        comment="Linha/modelo do produto (ex: ATF, Multi ATF)"
    ))
    op.add_column("oleos", sa.Column(
        "tipo_veiculo", sa.String(50), nullable=True,
        comment="Tipo de veículo (ex: Carro, Caminhonete)"
    ))
    op.add_column("oleos", sa.Column(
        "volume_unidade", sa.String(20), nullable=True,
        comment="Volume por unidade (ex: 1 L, 946 mL)"
    ))
    op.add_column("oleos", sa.Column(
        "volume_liquido", sa.String(20), nullable=True,
        comment="Volume líquido (ex: 1 L)"
    ))
    op.add_column("oleos", sa.Column(
        "formato_venda", sa.String(30), nullable=True,
        comment="Formato de venda (ex: Unidade, Caixa, Galão)"
    ))
    op.add_column("oleos", sa.Column(
        "tipo_recipiente", sa.String(50), nullable=True,
        comment="Tipo de recipiente (ex: Garrafa plástica, Lata)"
    ))
    op.add_column("oleos", sa.Column(
        "tipo_oleo_transmissao", sa.String(100), nullable=True,
        comment="Tipo de óleo de transmissão (ex: ATF Dexron VI)"
    ))
    op.add_column("oleos", sa.Column(
        "desempenho", sa.String(100), nullable=True,
        comment="Desempenho do óleo (ex: Full Synthetic Multi-Vehicle)"
    ))
    op.add_column("oleos", sa.Column(
        "codigo_oem", sa.String(100), nullable=True,
        comment="Código OEM (ex: GM General Motors)"
    ))

    # --- NOVOS ÍNDICES ---
    op.create_index(
        "ix_oleos_tipo_oleo_transmissao", "oleos",
        ["tipo_oleo_transmissao"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_oleos_tipo_oleo_transmissao", table_name="oleos")

    op.drop_column("oleos", "codigo_oem")
    op.drop_column("oleos", "desempenho")
    op.drop_column("oleos", "tipo_oleo_transmissao")
    op.drop_column("oleos", "tipo_recipiente")
    op.drop_column("oleos", "formato_venda")
    op.drop_column("oleos", "volume_liquido")
    op.drop_column("oleos", "volume_unidade")
    op.drop_column("oleos", "tipo_veiculo")
    op.drop_column("oleos", "modelo")

    op.add_column("oleos", sa.Column(
        "tipo", sa.String(20), server_default="atf", nullable=False
    ))
    op.add_column("oleos", sa.Column(
        "especificacao", sa.String(100), nullable=True
    ))
    op.create_index("ix_oleos_tipo", "oleos", ["tipo"], unique=False)
