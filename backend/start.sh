#!/bin/bash
set -e

echo "=== Verificando estado do banco de dados ==="

# Verifica se a tabela alembic_version existe e tem conteúdo
ALEMBIC_STATE=$(python -c "
import asyncio
from sqlalchemy import text
from src.database import engine

async def check():
    async with engine.connect() as conn:
        # Verifica se alembic_version existe
        result = await conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version')\"
        ))
        has_table = result.scalar()
        if not has_table:
            print('none')
            return

        # Verifica se tem algum registro
        result = await conn.execute(text('SELECT version_num FROM alembic_version LIMIT 1'))
        row = result.scalar()
        print(row if row else 'empty')

asyncio.run(check())
" 2>/dev/null || echo "none")

echo "📌 Estado Alembic: $ALEMBIC_STATE"

if [ "$ALEMBIC_STATE" = "none" ] || [ "$ALEMBIC_STATE" = "empty" ]; then
    echo "📌 Alembic não inicializado. Detectando estado do banco..."

    # Verifica quais colunas existem na tabela oleos para determinar revisão correta
    STAMP_REV=$(python -c "
import asyncio
from sqlalchemy import text
from src.database import engine

async def check():
    async with engine.connect() as conn:
        # Verifica se a tabela oleos existe
        result = await conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'oleos')\"
        ))
        if not result.scalar():
            print('none')
            return

        # Verifica se foto_url existe (migration 006)
        result = await conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'oleos' AND column_name = 'foto_url')\"
        ))
        has_foto = result.scalar()

        # Verifica se custo_litro existe (migration 003)
        result = await conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'oleos' AND column_name = 'custo_litro')\"
        ))
        has_custo = result.scalar()

        if has_foto:
            print('006')
        elif has_custo:
            # Tem custo_litro mas não foto_url: stamp em 005 para rodar 006+007
            print('005')
        else:
            # Tabela base sem colunas adicionais: stamp em 002
            print('002')

asyncio.run(check())
" 2>/dev/null || echo "none")

    if [ "$STAMP_REV" = "none" ]; then
        echo "📌 Banco vazio, migrations rodarão do zero."
    else
        echo "📌 Detectado estado compatível com revisão $STAMP_REV"
        alembic stamp "$STAMP_REV"
        echo "✅ Stamp $STAMP_REV aplicado."
    fi
fi

echo "🔄 Executando migrations pendentes..."
alembic upgrade head
echo "✅ Migrations aplicadas com sucesso!"

echo "🚀 Iniciando servidor..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
