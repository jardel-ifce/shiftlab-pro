#!/bin/bash
set -e

echo "=== ShiftLab Pro - Inicializando ==="

echo "🔄 Executando migrations..."
alembic upgrade head
echo "✅ Migrations aplicadas com sucesso!"

echo "🚀 Iniciando servidor..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
