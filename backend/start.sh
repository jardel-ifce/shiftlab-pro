#!/bin/bash
set -e

echo "=== Verificando estado do banco de dados ==="

# Verifica se a tabela alembic_version existe
# Se não existe, o banco foi criado por metadata.create_all() sem Alembic
HAS_ALEMBIC=$(python -c "
import asyncio
from sqlalchemy import text
from src.database import engine

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version')\"
        ))
        row = result.scalar()
        print('yes' if row else 'no')

asyncio.run(check())
" 2>/dev/null || echo "no")

if [ "$HAS_ALEMBIC" = "no" ]; then
    echo "📌 Tabela alembic_version não encontrada."
    echo "📌 Marcando banco existente na revisão 006 (pré-marketplace)..."
    alembic stamp 006
    echo "✅ Stamp 006 aplicado."
fi

echo "🔄 Executando migrations pendentes..."
alembic upgrade head
echo "✅ Migrations aplicadas com sucesso!"

echo "🚀 Iniciando servidor..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
