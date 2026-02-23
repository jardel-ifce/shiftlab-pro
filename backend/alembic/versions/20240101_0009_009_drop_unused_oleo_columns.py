"""009 - Remover colunas não utilizadas da tabela oleos.

Revision ID: 009
Revises: 008
Create Date: 2024-01-01 00:09:00.000000

Remove campos redundantes: modelo, tipo_veiculo, viscosidade,
volume_unidade, formato_venda, tipo_recipiente, desempenho.
Mantém: volume_liquido, tipo_oleo_transmissao, codigo_oem.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("oleos", "modelo")
    op.drop_column("oleos", "tipo_veiculo")
    op.drop_column("oleos", "viscosidade")
    op.drop_column("oleos", "volume_unidade")
    op.drop_column("oleos", "formato_venda")
    op.drop_column("oleos", "tipo_recipiente")
    op.drop_column("oleos", "desempenho")


def downgrade() -> None:
    op.add_column("oleos", sa.Column(
        "desempenho", sa.String(100), nullable=True,
        comment="Desempenho do óleo (ex: Full Synthetic Multi-Vehicle)"
    ))
    op.add_column("oleos", sa.Column(
        "tipo_recipiente", sa.String(50), nullable=True,
        comment="Tipo de recipiente (ex: Garrafa plástica, Lata)"
    ))
    op.add_column("oleos", sa.Column(
        "formato_venda", sa.String(30), nullable=True,
        comment="Formato de venda (ex: Unidade, Caixa, Galão)"
    ))
    op.add_column("oleos", sa.Column(
        "volume_unidade", sa.String(20), nullable=True,
        comment="Volume por unidade (ex: 1 L, 946 mL)"
    ))
    op.add_column("oleos", sa.Column(
        "viscosidade", sa.String(20), nullable=True,
        comment="Grau de viscosidade (ex: 75W-90)"
    ))
    op.add_column("oleos", sa.Column(
        "tipo_veiculo", sa.String(50), nullable=True,
        comment="Tipo de veículo (ex: Carro, Caminhonete)"
    ))
    op.add_column("oleos", sa.Column(
        "modelo", sa.String(100), nullable=True,
        comment="Linha/modelo do produto (ex: ATF, Multi ATF)"
    ))
