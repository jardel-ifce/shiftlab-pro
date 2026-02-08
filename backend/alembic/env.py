"""
Alembic Environment Configuration.

Este arquivo configura o ambiente de execução das migrations.
É executado sempre que um comando alembic é chamado.

Principais responsabilidades:
- Carregar configurações do banco de dados
- Importar todos os models para detecção de mudanças
- Configurar modo online/offline de migrations
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Importa configurações do projeto
from src.config import settings

# Importa Base e metadata para autogenerate
from src.database import Base

# =============================================================================
# IMPORTAR TODOS OS MODELS AQUI
# =============================================================================
# O Alembic precisa conhecer todos os models para detectar mudanças.
# Adicione imports conforme criar novos models.

# Auth
from src.auth.models import User  # noqa: F401

# Domain (descomente conforme criar)
# from src.domain.cliente import Cliente  # noqa: F401
# from src.domain.veiculo import Veiculo  # noqa: F401
# from src.domain.troca_oleo import TrocaOleo  # noqa: F401
# from src.domain.produto import Produto  # noqa: F401

# =============================================================================
# CONFIGURAÇÃO DO ALEMBIC
# =============================================================================

# Objeto de configuração do Alembic (lê alembic.ini)
config = context.config

# Configura logging do Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos models para autogenerate
target_metadata = Base.metadata

# Sobrescreve a URL do banco com a do settings (que lê do .env)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# =============================================================================
# FUNÇÕES DE MIGRATION
# =============================================================================

def run_migrations_offline() -> None:
    """
    Executa migrations em modo 'offline'.

    Neste modo, não é necessária conexão com o banco.
    O Alembic gera o SQL que seria executado.

    Útil para:
    - Gerar scripts SQL para DBA revisar
    - Ambientes sem acesso direto ao banco
    - Debugging

    Uso:
        alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Compara tipos de colunas (detecta mudanças de VARCHAR(50) para VARCHAR(100))
        compare_type=True,
        # Compara server defaults
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Função auxiliar que executa as migrations com uma conexão.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Compara tipos de colunas
        compare_type=True,
        # Compara server defaults
        compare_server_default=True,
        # Renderiza item como batch para SQLite (permite ALTER TABLE)
        render_as_batch=settings.is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Executa migrations de forma assíncrona.

    Cria uma engine assíncrona e executa as migrations
    dentro de uma conexão.
    """
    # Configuração específica para async
    configuration = config.get_section(config.config_ini_section) or {}

    # Ajusta URL para driver assíncrono se necessário
    url = configuration.get("sqlalchemy.url", "")
    if "postgresql://" in url and "asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://")
        configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Executa migrations em modo 'online'.

    Neste modo, conecta diretamente ao banco de dados
    e executa as migrations em tempo real.

    Este é o modo padrão para:
        alembic upgrade head
        alembic downgrade -1
    """
    asyncio.run(run_async_migrations())


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
