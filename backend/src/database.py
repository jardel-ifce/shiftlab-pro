"""
Configuração do banco de dados SQLAlchemy.

Este módulo configura a conexão assíncrona com o banco de dados
e fornece a sessão para uso em toda a aplicação.

Uso:
    from src.database import get_db, Base

    # Em endpoints FastAPI:
    @router.get("/")
    async def list_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()

    # Em models:
    class MyModel(Base):
        __tablename__ = "my_table"
        ...
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

# =============================================================================
# CONFIGURAÇÃO DO ENGINE
# =============================================================================

# Convenção de nomes para constraints (facilita migrations)
# Isso garante nomes consistentes para índices, foreign keys, etc.
convention = {
    "ix": "ix_%(column_0_label)s",           # Índice
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign Key
    "pk": "pk_%(table_name)s",               # Primary Key
}

# Metadados com convenção de nomes
metadata = MetaData(naming_convention=convention)


# Configurações específicas por tipo de banco
def get_engine_args() -> dict:
    """
    Retorna argumentos específicos para o engine baseado no tipo de banco.

    SQLite: Requer check_same_thread=False para async
    PostgreSQL: Usa pool de conexões otimizado
    """
    args = {
        "echo": settings.DATABASE_ECHO,  # Log de queries SQL
    }

    if settings.is_sqlite:
        # SQLite não suporta pool de conexões
        args["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL: configurações de pool
        args["pool_size"] = settings.DATABASE_POOL_SIZE
        args["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        args["pool_pre_ping"] = True  # Verifica conexão antes de usar

    return args


# Engine assíncrono - gerencia conexões com o banco
engine = create_async_engine(
    settings.DATABASE_URL,
    **get_engine_args()
)

# Session factory - cria sessões para operações no banco
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Objetos permanecem acessíveis após commit
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# CLASSE BASE PARA MODELS
# =============================================================================

class Base(DeclarativeBase):
    """
    Classe base para todos os models SQLAlchemy.

    Todos os models devem herdar desta classe:

        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            ...
    """
    metadata = metadata


# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão do banco de dados.

    Uso em endpoints FastAPI:

        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()

    A sessão é automaticamente fechada após o request,
    mesmo em caso de exceção.

    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias para injeção de dependência (mais limpo)
DbSession = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

async def create_all_tables() -> None:
    """
    Cria todas as tabelas no banco de dados.

    ATENÇÃO: Use apenas em desenvolvimento ou testes.
    Em produção, sempre use migrations (Alembic).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """
    Remove todas as tabelas do banco de dados.

    ATENÇÃO: Esta operação é DESTRUTIVA e irreversível!
    Use apenas em desenvolvimento ou testes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def check_connection() -> bool:
    """
    Verifica se a conexão com o banco está funcionando.

    Returns:
        bool: True se conectou com sucesso, False caso contrário
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
