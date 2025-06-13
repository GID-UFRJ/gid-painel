# ---- Estágio 1: Builder ----
FROM python:3.13-slim AS builder

# Dependências de compilação 
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
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

# Instalando dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*


# Copia apenas o ambiente virtual (sem as dependências de compilação)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configuração da aplicação
WORKDIR /app
COPY . .

# Copiando o script entrypoint para dentro do contêiner
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Tornando-o executável (prática defensiva)
RUN chmod +x /usr/local/bin/entrypoint.sh

# Definindo o ENTRYPOINT como o script copiado
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Este CMD será executado por padrão se nenhum 'command' for especificado no compose.yaml.
# Entretanto, entrypoint.sh não precisa de nenhum argumento adicional, logo CMD será vazio aqui.
CMD []
