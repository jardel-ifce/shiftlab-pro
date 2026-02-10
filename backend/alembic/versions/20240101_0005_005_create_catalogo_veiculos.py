"""create catalogo veiculos

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 00:00:05

Cria tabelas montadoras e modelos_referencia para catálogo de veículos.
Amplia veiculos.modelo de VARCHAR(50) para VARCHAR(200).
Insere seed data com montadoras e modelos do mercado brasileiro.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Criar tabela montadoras ===
    op.create_table(
        "montadoras",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(50), nullable=False),
        sa.Column("pais_origem", sa.String(50), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_index("ix_montadoras_nome", "montadoras", ["nome"])

    # === Criar tabela modelos_referencia ===
    op.create_table(
        "modelos_referencia",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("montadora_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("tipo_cambio", sa.String(20), nullable=True),
        sa.Column("ano_inicio", sa.Integer(), nullable=True),
        sa.Column("ano_fim", sa.Integer(), nullable=True),
        sa.Column("motor", sa.String(50), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["montadora_id"], ["montadoras.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_modelos_referencia_montadora_id", "modelos_referencia", ["montadora_id"])

    # === Ampliar veiculos.modelo de VARCHAR(50) para VARCHAR(200) ===
    op.alter_column(
        "veiculos",
        "modelo",
        existing_type=sa.String(50),
        type_=sa.String(200),
        existing_nullable=False,
    )

    # === Seed data ===
    _insert_seed_data()


def downgrade() -> None:
    op.alter_column(
        "veiculos",
        "modelo",
        existing_type=sa.String(200),
        type_=sa.String(50),
        existing_nullable=False,
    )
    op.drop_table("modelos_referencia")
    op.drop_table("montadoras")


def _insert_seed_data() -> None:
    """Insere montadoras e modelos de referência."""
    montadoras_table = sa.table(
        "montadoras",
        sa.column("id", sa.Integer),
        sa.column("nome", sa.String),
        sa.column("pais_origem", sa.String),
    )

    modelos_table = sa.table(
        "modelos_referencia",
        sa.column("montadora_id", sa.Integer),
        sa.column("nome", sa.String),
        sa.column("descricao", sa.String),
        sa.column("tipo_cambio", sa.String),
        sa.column("ano_inicio", sa.Integer),
        sa.column("ano_fim", sa.Integer),
        sa.column("motor", sa.String),
    )

    # --- Montadoras ---
    montadoras = [
        {"id": 1, "nome": "TOYOTA", "pais_origem": "Japão"},
        {"id": 2, "nome": "HONDA", "pais_origem": "Japão"},
        {"id": 3, "nome": "VOLKSWAGEN", "pais_origem": "Alemanha"},
        {"id": 4, "nome": "HYUNDAI", "pais_origem": "Coreia do Sul"},
        {"id": 5, "nome": "CHEVROLET", "pais_origem": "Estados Unidos"},
        {"id": 6, "nome": "FIAT", "pais_origem": "Itália"},
        {"id": 7, "nome": "FORD", "pais_origem": "Estados Unidos"},
        {"id": 8, "nome": "JEEP", "pais_origem": "Estados Unidos"},
        {"id": 9, "nome": "NISSAN", "pais_origem": "Japão"},
        {"id": 10, "nome": "KIA", "pais_origem": "Coreia do Sul"},
        {"id": 11, "nome": "MITSUBISHI", "pais_origem": "Japão"},
        {"id": 12, "nome": "RENAULT", "pais_origem": "França"},
        {"id": 13, "nome": "PEUGEOT", "pais_origem": "França"},
        {"id": 14, "nome": "CITROEN", "pais_origem": "França"},
        {"id": 15, "nome": "BMW", "pais_origem": "Alemanha"},
        {"id": 16, "nome": "MERCEDES-BENZ", "pais_origem": "Alemanha"},
        {"id": 17, "nome": "AUDI", "pais_origem": "Alemanha"},
        {"id": 18, "nome": "VOLVO", "pais_origem": "Suécia"},
        {"id": 19, "nome": "SUBARU", "pais_origem": "Japão"},
        {"id": 20, "nome": "SUZUKI", "pais_origem": "Japão"},
        {"id": 21, "nome": "CAOA CHERY", "pais_origem": "China"},
        {"id": 22, "nome": "RAM", "pais_origem": "Estados Unidos"},
        {"id": 23, "nome": "DODGE", "pais_origem": "Estados Unidos"},
        {"id": 24, "nome": "LAND ROVER", "pais_origem": "Reino Unido"},
        {"id": 25, "nome": "PORSCHE", "pais_origem": "Alemanha"},
        {"id": 26, "nome": "MINI", "pais_origem": "Reino Unido"},
        {"id": 27, "nome": "JAC", "pais_origem": "China"},
    ]

    op.bulk_insert(montadoras_table, montadoras)

    # --- Modelos de Referência ---
    modelos = [
        # TOYOTA (1)
        {"montadora_id": 1, "nome": "COROLLA", "descricao": "COROLLA 1.8L FLEX AT 2009-2014", "tipo_cambio": "automatico", "ano_inicio": 2009, "ano_fim": 2014, "motor": "1.8L FLEX"},
        {"montadora_id": 1, "nome": "COROLLA", "descricao": "COROLLA 2.0L FLEX AT 2015-2019", "tipo_cambio": "automatico", "ano_inicio": 2015, "ano_fim": 2019, "motor": "2.0L FLEX"},
        {"montadora_id": 1, "nome": "COROLLA", "descricao": "COROLLA 2.0L FLEX CVT 2020-", "tipo_cambio": "cvt", "ano_inicio": 2020, "ano_fim": None, "motor": "2.0L FLEX"},
        {"montadora_id": 1, "nome": "COROLLA CROSS", "descricao": "COROLLA CROSS 2.0L FLEX CVT 2021-", "tipo_cambio": "cvt", "ano_inicio": 2021, "ano_fim": None, "motor": "2.0L FLEX"},
        {"montadora_id": 1, "nome": "HILUX SW4", "descricao": "HILUX SW4 3.0 DIESEL AT 2005-2015", "tipo_cambio": "automatico", "ano_inicio": 2005, "ano_fim": 2015, "motor": "3.0 DIESEL"},
        {"montadora_id": 1, "nome": "HILUX SW4", "descricao": "HILUX SW4 2.8 DIESEL AT 2016-", "tipo_cambio": "automatico", "ano_inicio": 2016, "ano_fim": None, "motor": "2.8 DIESEL"},
        {"montadora_id": 1, "nome": "HILUX", "descricao": "HILUX 2.8 DIESEL AT 2016-", "tipo_cambio": "automatico", "ano_inicio": 2016, "ano_fim": None, "motor": "2.8 DIESEL"},
        {"montadora_id": 1, "nome": "RAV4", "descricao": "RAV4 2.0L AT 2013-2019", "tipo_cambio": "automatico", "ano_inicio": 2013, "ano_fim": 2019, "motor": "2.0L"},
        {"montadora_id": 1, "nome": "YARIS", "descricao": "YARIS 1.5L AT 2018-2023", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": 2023, "motor": "1.5L"},
        {"montadora_id": 1, "nome": "ETIOS", "descricao": "ETIOS 1.5L AT 2016-2023", "tipo_cambio": "automatico", "ano_inicio": 2016, "ano_fim": 2023, "motor": "1.5L"},
        {"montadora_id": 1, "nome": "CAMRY", "descricao": "CAMRY 3.5 V6 AT 2007-2011", "tipo_cambio": "automatico", "ano_inicio": 2007, "ano_fim": 2011, "motor": "3.5 V6"},

        # HONDA (2)
        {"montadora_id": 2, "nome": "CIVIC", "descricao": "CIVIC 2.0L FLEX AT 2017-2021", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": 2021, "motor": "2.0L FLEX"},
        {"montadora_id": 2, "nome": "CIVIC", "descricao": "CIVIC 1.5 TURBO CVT 2017-2021", "tipo_cambio": "cvt", "ano_inicio": 2017, "ano_fim": 2021, "motor": "1.5 TURBO"},
        {"montadora_id": 2, "nome": "HR-V", "descricao": "HR-V 1.8L FLEX CVT 2015-2022", "tipo_cambio": "cvt", "ano_inicio": 2015, "ano_fim": 2022, "motor": "1.8L FLEX"},
        {"montadora_id": 2, "nome": "HR-V", "descricao": "HR-V 1.5 TURBO CVT 2023-", "tipo_cambio": "cvt", "ano_inicio": 2023, "ano_fim": None, "motor": "1.5 TURBO"},
        {"montadora_id": 2, "nome": "FIT", "descricao": "FIT 1.5L FLEX CVT 2015-2021", "tipo_cambio": "cvt", "ano_inicio": 2015, "ano_fim": 2021, "motor": "1.5L FLEX"},
        {"montadora_id": 2, "nome": "CR-V", "descricao": "CR-V 2.0L AT 2012-2017", "tipo_cambio": "automatico", "ano_inicio": 2012, "ano_fim": 2017, "motor": "2.0L"},
        {"montadora_id": 2, "nome": "CITY", "descricao": "CITY 1.5L FLEX CVT 2015-2023", "tipo_cambio": "cvt", "ano_inicio": 2015, "ano_fim": 2023, "motor": "1.5L FLEX"},
        {"montadora_id": 2, "nome": "WR-V", "descricao": "WR-V 1.5L FLEX CVT 2017-2023", "tipo_cambio": "cvt", "ano_inicio": 2017, "ano_fim": 2023, "motor": "1.5L FLEX"},

        # VOLKSWAGEN (3)
        {"montadora_id": 3, "nome": "GOL", "descricao": "GOL 1.6L I-MOTION 2009-2016", "tipo_cambio": "automatizado", "ano_inicio": 2009, "ano_fim": 2016, "motor": "1.6L"},
        {"montadora_id": 3, "nome": "POLO", "descricao": "POLO 1.0 TSI AT 2018-", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": None, "motor": "1.0 TSI"},
        {"montadora_id": 3, "nome": "VIRTUS", "descricao": "VIRTUS 1.0 TSI AT 2018-", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": None, "motor": "1.0 TSI"},
        {"montadora_id": 3, "nome": "T-CROSS", "descricao": "T-CROSS 1.0 TSI AT 2019-", "tipo_cambio": "automatico", "ano_inicio": 2019, "ano_fim": None, "motor": "1.0 TSI"},
        {"montadora_id": 3, "nome": "TIGUAN", "descricao": "TIGUAN 1.4 TSI DSG 2017-", "tipo_cambio": "dupla_embreagem", "ano_inicio": 2017, "ano_fim": None, "motor": "1.4 TSI"},
        {"montadora_id": 3, "nome": "JETTA", "descricao": "JETTA 2.0 TSI DSG 2011-2018", "tipo_cambio": "dupla_embreagem", "ano_inicio": 2011, "ano_fim": 2018, "motor": "2.0 TSI"},
        {"montadora_id": 3, "nome": "AMAROK", "descricao": "AMAROK 2.0 TDI AT 2011-2022", "tipo_cambio": "automatico", "ano_inicio": 2011, "ano_fim": 2022, "motor": "2.0 TDI"},
        {"montadora_id": 3, "nome": "TAOS", "descricao": "TAOS 1.4 TSI AT 2021-", "tipo_cambio": "automatico", "ano_inicio": 2021, "ano_fim": None, "motor": "1.4 TSI"},
        {"montadora_id": 3, "nome": "NIVUS", "descricao": "NIVUS 1.0 TSI AT 2020-", "tipo_cambio": "automatico", "ano_inicio": 2020, "ano_fim": None, "motor": "1.0 TSI"},

        # HYUNDAI (4)
        {"montadora_id": 4, "nome": "HB20", "descricao": "HB20 1.6L AT 2012-2019", "tipo_cambio": "automatico", "ano_inicio": 2012, "ano_fim": 2019, "motor": "1.6L"},
        {"montadora_id": 4, "nome": "HB20", "descricao": "HB20 1.0 TURBO AT 2020-", "tipo_cambio": "automatico", "ano_inicio": 2020, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 4, "nome": "CRETA", "descricao": "CRETA 2.0L AT 2017-2021", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": 2021, "motor": "2.0L"},
        {"montadora_id": 4, "nome": "CRETA", "descricao": "CRETA 1.0 TURBO AT 2022-", "tipo_cambio": "automatico", "ano_inicio": 2022, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 4, "nome": "TUCSON", "descricao": "TUCSON 2.0L AT 2006-2016", "tipo_cambio": "automatico", "ano_inicio": 2006, "ano_fim": 2016, "motor": "2.0L"},
        {"montadora_id": 4, "nome": "IX35", "descricao": "IX35 2.0L AT 2010-2019", "tipo_cambio": "automatico", "ano_inicio": 2010, "ano_fim": 2019, "motor": "2.0L"},
        {"montadora_id": 4, "nome": "SANTA FE", "descricao": "SANTA FE 3.3 V6 AT 2014-2019", "tipo_cambio": "automatico", "ano_inicio": 2014, "ano_fim": 2019, "motor": "3.3 V6"},

        # CHEVROLET (5)
        {"montadora_id": 5, "nome": "ONIX", "descricao": "ONIX 1.0 TURBO AT 2020-", "tipo_cambio": "automatico", "ano_inicio": 2020, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 5, "nome": "TRACKER", "descricao": "TRACKER 1.0 TURBO AT 2021-", "tipo_cambio": "automatico", "ano_inicio": 2021, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 5, "nome": "CRUZE", "descricao": "CRUZE 1.4 TURBO AT 2017-", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": None, "motor": "1.4 TURBO"},
        {"montadora_id": 5, "nome": "S10", "descricao": "S10 2.8 DIESEL AT 2012-", "tipo_cambio": "automatico", "ano_inicio": 2012, "ano_fim": None, "motor": "2.8 DIESEL"},
        {"montadora_id": 5, "nome": "EQUINOX", "descricao": "EQUINOX 1.5 TURBO AT 2018-2022", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": 2022, "motor": "1.5 TURBO"},
        {"montadora_id": 5, "nome": "SPIN", "descricao": "SPIN 1.8L AT 2013-2024", "tipo_cambio": "automatico", "ano_inicio": 2013, "ano_fim": 2024, "motor": "1.8L"},
        {"montadora_id": 5, "nome": "TRAILBLAZER", "descricao": "TRAILBLAZER 2.8 DIESEL AT 2013-", "tipo_cambio": "automatico", "ano_inicio": 2013, "ano_fim": None, "motor": "2.8 DIESEL"},

        # FIAT (6)
        {"montadora_id": 6, "nome": "TORO", "descricao": "TORO 1.8L AT 2016-2022", "tipo_cambio": "automatico", "ano_inicio": 2016, "ano_fim": 2022, "motor": "1.8L"},
        {"montadora_id": 6, "nome": "TORO", "descricao": "TORO 1.3 TURBO AT 2022-", "tipo_cambio": "automatico", "ano_inicio": 2022, "ano_fim": None, "motor": "1.3 TURBO"},
        {"montadora_id": 6, "nome": "PULSE", "descricao": "PULSE 1.0 TURBO AT 2021-", "tipo_cambio": "automatico", "ano_inicio": 2021, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 6, "nome": "FASTBACK", "descricao": "FASTBACK 1.0 TURBO AT 2022-", "tipo_cambio": "automatico", "ano_inicio": 2022, "ano_fim": None, "motor": "1.0 TURBO"},
        {"montadora_id": 6, "nome": "ARGO", "descricao": "ARGO 1.8L AT 2018-", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": None, "motor": "1.8L"},
        {"montadora_id": 6, "nome": "CRONOS", "descricao": "CRONOS 1.8L AT 2018-", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": None, "motor": "1.8L"},

        # FORD (7)
        {"montadora_id": 7, "nome": "RANGER", "descricao": "RANGER 3.2 DIESEL AT 2012-2024", "tipo_cambio": "automatico", "ano_inicio": 2012, "ano_fim": 2024, "motor": "3.2 DIESEL"},
        {"montadora_id": 7, "nome": "ECOSPORT", "descricao": "ECOSPORT 2.0L POWERSHIFT 2013-2017", "tipo_cambio": "dupla_embreagem", "ano_inicio": 2013, "ano_fim": 2017, "motor": "2.0L"},
        {"montadora_id": 7, "nome": "ECOSPORT", "descricao": "ECOSPORT 1.5L AT 2018-2022", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": 2022, "motor": "1.5L"},
        {"montadora_id": 7, "nome": "FOCUS", "descricao": "FOCUS 2.0L POWERSHIFT 2014-2019", "tipo_cambio": "dupla_embreagem", "ano_inicio": 2014, "ano_fim": 2019, "motor": "2.0L"},
        {"montadora_id": 7, "nome": "KA", "descricao": "KA 1.5L AT 2019-2023", "tipo_cambio": "automatico", "ano_inicio": 2019, "ano_fim": 2023, "motor": "1.5L"},
        {"montadora_id": 7, "nome": "TERRITORY", "descricao": "TERRITORY 1.5 TURBO AT 2020-", "tipo_cambio": "automatico", "ano_inicio": 2020, "ano_fim": None, "motor": "1.5 TURBO"},

        # JEEP (8)
        {"montadora_id": 8, "nome": "COMPASS", "descricao": "COMPASS 2.0 FLEX AT 2017-", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": None, "motor": "2.0 FLEX"},
        {"montadora_id": 8, "nome": "COMPASS", "descricao": "COMPASS 2.0 DIESEL AT 2017-", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": None, "motor": "2.0 DIESEL"},
        {"montadora_id": 8, "nome": "RENEGADE", "descricao": "RENEGADE 1.8L AT 2015-2022", "tipo_cambio": "automatico", "ano_inicio": 2015, "ano_fim": 2022, "motor": "1.8L"},
        {"montadora_id": 8, "nome": "RENEGADE", "descricao": "RENEGADE 1.3 TURBO AT 2022-", "tipo_cambio": "automatico", "ano_inicio": 2022, "ano_fim": None, "motor": "1.3 TURBO"},
        {"montadora_id": 8, "nome": "COMMANDER", "descricao": "COMMANDER 2.0 TURBO DIESEL AT 2022-", "tipo_cambio": "automatico", "ano_inicio": 2022, "ano_fim": None, "motor": "2.0 TURBO DIESEL"},

        # NISSAN (9)
        {"montadora_id": 9, "nome": "KICKS", "descricao": "KICKS 1.6L CVT 2017-", "tipo_cambio": "cvt", "ano_inicio": 2017, "ano_fim": None, "motor": "1.6L"},
        {"montadora_id": 9, "nome": "SENTRA", "descricao": "SENTRA 2.0L CVT 2014-2022", "tipo_cambio": "cvt", "ano_inicio": 2014, "ano_fim": 2022, "motor": "2.0L"},
        {"montadora_id": 9, "nome": "FRONTIER", "descricao": "FRONTIER 2.3 DIESEL AT 2017-", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": None, "motor": "2.3 DIESEL"},
        {"montadora_id": 9, "nome": "VERSA", "descricao": "VERSA 1.6L CVT 2020-", "tipo_cambio": "cvt", "ano_inicio": 2020, "ano_fim": None, "motor": "1.6L"},
        {"montadora_id": 9, "nome": "MARCH", "descricao": "MARCH 1.6L CVT 2012-2021", "tipo_cambio": "cvt", "ano_inicio": 2012, "ano_fim": 2021, "motor": "1.6L"},

        # KIA (10)
        {"montadora_id": 10, "nome": "SPORTAGE", "descricao": "SPORTAGE 2.0L AT 2011-2022", "tipo_cambio": "automatico", "ano_inicio": 2011, "ano_fim": 2022, "motor": "2.0L"},
        {"montadora_id": 10, "nome": "CERATO", "descricao": "CERATO 2.0L AT 2014-2022", "tipo_cambio": "automatico", "ano_inicio": 2014, "ano_fim": 2022, "motor": "2.0L"},
        {"montadora_id": 10, "nome": "SELTOS", "descricao": "SELTOS 2.0L AT 2021-", "tipo_cambio": "automatico", "ano_inicio": 2021, "ano_fim": None, "motor": "2.0L"},
        {"montadora_id": 10, "nome": "SORENTO", "descricao": "SORENTO 3.5 V6 AT 2010-2020", "tipo_cambio": "automatico", "ano_inicio": 2010, "ano_fim": 2020, "motor": "3.5 V6"},

        # MITSUBISHI (11)
        {"montadora_id": 11, "nome": "OUTLANDER", "descricao": "OUTLANDER 2.0L CVT 2014-2022", "tipo_cambio": "cvt", "ano_inicio": 2014, "ano_fim": 2022, "motor": "2.0L"},
        {"montadora_id": 11, "nome": "ASX", "descricao": "ASX 2.0L CVT 2011-2023", "tipo_cambio": "cvt", "ano_inicio": 2011, "ano_fim": 2023, "motor": "2.0L"},
        {"montadora_id": 11, "nome": "L200 TRITON", "descricao": "L200 TRITON 2.4 DIESEL AT 2017-", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": None, "motor": "2.4 DIESEL"},
        {"montadora_id": 11, "nome": "PAJERO SPORT", "descricao": "PAJERO SPORT 2.4 DIESEL AT 2016-", "tipo_cambio": "automatico", "ano_inicio": 2016, "ano_fim": None, "motor": "2.4 DIESEL"},
        {"montadora_id": 11, "nome": "ECLIPSE CROSS", "descricao": "ECLIPSE CROSS 1.5 TURBO CVT 2018-", "tipo_cambio": "cvt", "ano_inicio": 2018, "ano_fim": None, "motor": "1.5 TURBO"},

        # RENAULT (12)
        {"montadora_id": 12, "nome": "DUSTER", "descricao": "DUSTER 1.6L CVT 2020-", "tipo_cambio": "cvt", "ano_inicio": 2020, "ano_fim": None, "motor": "1.6L"},
        {"montadora_id": 12, "nome": "CAPTUR", "descricao": "CAPTUR 1.6L CVT 2017-2022", "tipo_cambio": "cvt", "ano_inicio": 2017, "ano_fim": 2022, "motor": "1.6L"},
        {"montadora_id": 12, "nome": "KWID", "descricao": "KWID 1.0L AT 2021-", "tipo_cambio": "automatico", "ano_inicio": 2021, "ano_fim": None, "motor": "1.0L"},

        # PEUGEOT (13)
        {"montadora_id": 13, "nome": "208", "descricao": "208 1.6L AT 2017-2023", "tipo_cambio": "automatico", "ano_inicio": 2017, "ano_fim": 2023, "motor": "1.6L"},
        {"montadora_id": 13, "nome": "2008", "descricao": "2008 1.6L AT 2019-", "tipo_cambio": "automatico", "ano_inicio": 2019, "ano_fim": None, "motor": "1.6L"},
        {"montadora_id": 13, "nome": "3008", "descricao": "3008 1.6 TURBO AT 2018-", "tipo_cambio": "automatico", "ano_inicio": 2018, "ano_fim": None, "motor": "1.6 TURBO"},
    ]

    op.bulk_insert(modelos_table, modelos)
