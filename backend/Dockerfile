FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY . .

# Porta configurável pelo Railway
ENV PORT=8000

# Comando de execução
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
