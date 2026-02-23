"""001 - Schema inicial completo do ShiftLab Pro.

Revision ID: 001
Revises: None
Create Date: 2026-02-23

Cria todas as tabelas do sistema:
- users: Autenticação e autorização
- clientes: Cadastro de clientes
- veiculos: Veículos dos clientes
- oleos: Produtos de óleo disponíveis
- pecas: Peças e itens auxiliares
- servicos: Tipos de serviço
- filtros_oleo: Filtros de óleo de câmbio
- montadoras: Catálogo de montadoras
- modelos_referencia: Catálogo de modelos de veículo
- trocas_oleo: Registro de trocas realizadas
- itens_troca: Peças utilizadas em cada troca
- entradas_estoque: Histórico de compras/aquisições
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ======================================================================
    # 1. USERS
    # ======================================================================
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), server_default="funcionario", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ======================================================================
    # 2. CLIENTES
    # ======================================================================
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("cpf_cnpj", sa.String(18), nullable=False),
        sa.Column("endereco", sa.Text(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_clientes"),
        sa.UniqueConstraint("cpf_cnpj", name="uq_clientes_cpf_cnpj"),
    )
    op.create_index("ix_clientes_cpf_cnpj", "clientes", ["cpf_cnpj"], unique=True)
    op.create_index("ix_clientes_nome", "clientes", ["nome"])

    # ======================================================================
    # 3. VEICULOS
    # ======================================================================
    op.create_table(
        "veiculos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("placa", sa.String(10), nullable=False),
        sa.Column("marca", sa.String(50), nullable=False),
        sa.Column("modelo", sa.String(200), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("tipo_cambio", sa.String(20), server_default="automatico", nullable=False),
        sa.Column("quilometragem_atual", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cor", sa.String(30), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_veiculos"),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"], name="fk_veiculos_cliente_id", ondelete="CASCADE"),
        sa.UniqueConstraint("placa", name="uq_veiculos_placa"),
    )
    op.create_index("ix_veiculos_placa", "veiculos", ["placa"], unique=True)
    op.create_index("ix_veiculos_cliente_id", "veiculos", ["cliente_id"])

    # ======================================================================
    # 4. OLEOS
    # ======================================================================
    op.create_table(
        "oleos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_produto", sa.String(30), nullable=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("marca", sa.String(50), nullable=False),
        sa.Column("volume_liquido", sa.String(20), nullable=True),
        sa.Column("tipo_oleo_transmissao", sa.String(100), nullable=True),
        sa.Column("codigo_oem", sa.String(100), nullable=True),
        sa.Column("custo_litro", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("preco_litro", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque_litros", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(10, 2), server_default="5", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("foto_url", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_oleos"),
    )
    op.create_index("ix_oleos_codigo_produto", "oleos", ["codigo_produto"])
    op.create_index("ix_oleos_marca", "oleos", ["marca"])
    op.create_index("ix_oleos_tipo_oleo_transmissao", "oleos", ["tipo_oleo_transmissao"])

    # ======================================================================
    # 5. PECAS
    # ======================================================================
    op.create_table(
        "pecas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("marca", sa.String(50), nullable=True),
        sa.Column("unidade", sa.String(20), server_default="unidade", nullable=False),
        sa.Column("preco_custo", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("preco_venda", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(10, 2), server_default="5", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("comentarios", sa.Text(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_pecas"),
    )
    op.create_index("ix_pecas_marca", "pecas", ["marca"])

    # ======================================================================
    # 6. SERVICOS
    # ======================================================================
    op.create_table(
        "servicos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("preco", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_servicos"),
    )

    # ======================================================================
    # 7. FILTROS_OLEO
    # ======================================================================
    op.create_table(
        "filtros_oleo",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo_produto", sa.String(30), nullable=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("marca", sa.String(50), nullable=False),
        sa.Column("codigo_oem", sa.String(100), nullable=True),
        sa.Column("custo_unitario", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("preco_unitario", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("estoque", sa.Integer(), server_default="0", nullable=False),
        sa.Column("estoque_minimo", sa.Integer(), server_default="2", nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("foto_url", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_filtros_oleo"),
    )
    op.create_index("ix_filtros_oleo_codigo_produto", "filtros_oleo", ["codigo_produto"])
    op.create_index("ix_filtros_oleo_marca", "filtros_oleo", ["marca"])

    # ======================================================================
    # 8. MONTADORAS
    # ======================================================================
    op.create_table(
        "montadoras",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(50), nullable=False),
        sa.Column("pais_origem", sa.String(50), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_montadoras"),
        sa.UniqueConstraint("nome", name="uq_montadoras_nome"),
    )
    op.create_index("ix_montadoras_nome", "montadoras", ["nome"], unique=True)

    # ======================================================================
    # 9. MODELOS_REFERENCIA
    # ======================================================================
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
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_modelos_referencia"),
        sa.ForeignKeyConstraint(["montadora_id"], ["montadoras.id"], name="fk_modelos_referencia_montadora_id", ondelete="CASCADE"),
    )
    op.create_index("ix_modelos_referencia_montadora_id", "modelos_referencia", ["montadora_id"])

    # ======================================================================
    # 10. TROCAS_OLEO
    # ======================================================================
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
        sa.Column("desconto_percentual", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("desconto_valor", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("motivo_desconto", sa.Text(), nullable=True),
        sa.Column("taxa_percentual", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("custo_oleo", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("proxima_troca_km", sa.Integer(), nullable=True),
        sa.Column("proxima_troca_data", sa.Date(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_trocas_oleo"),
        sa.ForeignKeyConstraint(["veiculo_id"], ["veiculos.id"], name="fk_trocas_oleo_veiculo_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["oleo_id"], ["oleos.id"], name="fk_trocas_oleo_oleo_id", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_trocas_oleo_user_id", ondelete="SET NULL"),
    )
    op.create_index("ix_trocas_oleo_veiculo_id", "trocas_oleo", ["veiculo_id"])
    op.create_index("ix_trocas_oleo_oleo_id", "trocas_oleo", ["oleo_id"])
    op.create_index("ix_trocas_oleo_user_id", "trocas_oleo", ["user_id"])
    op.create_index("ix_trocas_oleo_data_troca", "trocas_oleo", ["data_troca"])

    # ======================================================================
    # 11. ITENS_TROCA
    # ======================================================================
    op.create_table(
        "itens_troca",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("troca_id", sa.Integer(), nullable=False),
        sa.Column("peca_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Numeric(10, 2), server_default="1", nullable=False),
        sa.Column("valor_unitario", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("valor_total", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("custo_unitario", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_itens_troca"),
        sa.ForeignKeyConstraint(["troca_id"], ["trocas_oleo.id"], name="fk_itens_troca_troca_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["peca_id"], ["pecas.id"], name="fk_itens_troca_peca_id", ondelete="RESTRICT"),
    )
    op.create_index("ix_itens_troca_troca_id", "itens_troca", ["troca_id"])
    op.create_index("ix_itens_troca_peca_id", "itens_troca", ["peca_id"])

    # ======================================================================
    # 12. ENTRADAS_ESTOQUE
    # ======================================================================
    op.create_table(
        "entradas_estoque",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tipo_produto", sa.String(10), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("produto_nome", sa.String(100), nullable=False),
        sa.Column("produto_marca", sa.String(50), nullable=False),
        sa.Column("oleo_id", sa.Integer(), nullable=True),
        sa.Column("quantidade_litros", sa.Numeric(10, 2), nullable=False),
        sa.Column("custo_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("custo_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("fornecedor", sa.String(100), nullable=True),
        sa.Column("nota_fiscal", sa.String(50), nullable=True),
        sa.Column("data_compra", sa.Date(), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_entradas_estoque"),
        sa.ForeignKeyConstraint(["oleo_id"], ["oleos.id"], name="fk_entradas_estoque_oleo_id", ondelete="CASCADE"),
    )
    op.create_index("ix_entradas_estoque_tipo_produto", "entradas_estoque", ["tipo_produto"])
    op.create_index("ix_entradas_estoque_produto_id", "entradas_estoque", ["produto_id"])
    op.create_index("ix_entradas_estoque_oleo_id", "entradas_estoque", ["oleo_id"])
    op.create_index("ix_entradas_estoque_data_compra", "entradas_estoque", ["data_compra"])


def downgrade() -> None:
    # Drop na ordem inversa (respeitar FKs)
    op.drop_table("entradas_estoque")
    op.drop_table("itens_troca")
    op.drop_table("trocas_oleo")
    op.drop_table("modelos_referencia")
    op.drop_table("montadoras")
    op.drop_table("filtros_oleo")
    op.drop_table("servicos")
    op.drop_table("pecas")
    op.drop_table("oleos")
    op.drop_table("veiculos")
    op.drop_table("clientes")
    op.drop_table("users")
