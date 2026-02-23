#!/bin/bash
# ==============================================================
# ShiftLab Pro - Script de Inicialização (Desenvolvimento)
# ==============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=============================================="
echo "  ShiftLab Pro - Iniciando ambiente local"
echo "=============================================="

# 1. Inicia Docker (PostgreSQL)
echo ""
echo "[1/3] Verificando Docker e PostgreSQL..."
if ! docker info > /dev/null 2>&1; then
    echo "  Docker não está rodando. Abrindo Docker Desktop..."
    open -a Docker
    echo "  Aguardando Docker iniciar..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
    done
    echo "  Docker iniciado!"
fi

if docker ps --format '{{.Names}}' | grep -q shiftlab_db; then
    echo "  PostgreSQL já está rodando."
else
    echo "  Iniciando PostgreSQL..."
    docker run -d \
        --name shiftlab_db \
        -e POSTGRES_USER=shiftlab \
        -e POSTGRES_PASSWORD=shiftlab123 \
        -e POSTGRES_DB=shiftlab_pro \
        -p 5434:5432 \
        --restart unless-stopped \
        postgres:15-alpine > /dev/null 2>&1 || \
    docker start shiftlab_db > /dev/null 2>&1
    echo "  PostgreSQL rodando na porta 5434."
fi

# 2. Inicia Backend
echo ""
echo "[2/3] Iniciando Backend (porta 8001)..."
cd "$DIR/backend"
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# 3. Inicia Frontend
echo ""
echo "[3/3] Iniciando Frontend (Vite)..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=============================================="
echo "  ShiftLab Pro rodando!"
echo "  Backend:  http://localhost:8001/docs"
echo "  Frontend: http://localhost:5174"
echo "  Banco:    localhost:5434"
echo ""
echo "  Pressione Ctrl+C para parar tudo."
echo "=============================================="

# Encerra tudo ao pressionar Ctrl+C
trap "echo ''; echo 'Encerrando...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Parado!'; exit 0" SIGINT SIGTERM

wait
