FROM python:3.13-slim

# Configurando variaveis de ambiente 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Instalando dependências do sistema (imagem slim é bem enxuta)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Working directory da applicação
WORKDIR /app

# Instala dependências python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia repo do projeto
COPY . .

# Comando para rodar o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gid.wsgi:application"]