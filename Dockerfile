# ---- Estágio 1: Builder ----
FROM python:3.13-slim AS builder

# Dependências de compilação 
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \                   
    postgresql-server-dev-all \    
    && rm -rf /var/lib/apt/lists/*

# Ambiente virtual e instalação de dependências
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Estágio 2: Runtime ----
FROM python:3.13-slim

# Variáveis críticas para produção:

# Logs em tempo real (Docker/K8s)
ENV PYTHONUNBUFFERED=1         
# Evita lixo no container
ENV PYTHONDONTWRITEBYTECODE=1  

# Copia apenas o ambiente virtual (sem as dependências de compilação)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configuração da aplicação
WORKDIR /app
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gid.wsgi:application"]