#!/bin/bash
set -e # Sai imediatamente se um comando falhar

# --- Lógica de setup de ambiente que SEMPRE deve rodar antes do comando principal ---
# Ex: Definir variáveis de ambiente padrão, esperar pelo banco de dados (se não usar depends_on)
DJANGO_PORT=${DJANGO_PORT:-8000}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}

# Exemplo de log para depuração:
echo "--- Running Entrypoint Script ---"
echo "DJANGO_PORT: ${DJANGO_PORT}"
echo "GUNICORN_WORKERS: ${GUNICORN_WORKERS}"
echo "Command to execute: $@" # Mostra o comando que será executado (CMD ou command do compose)
echo "---------------------------------"

# --- EXECUTAR O COMANDO PASSADO COMO ARGUMENTO ---
# Isso é CRUCIAL. "$@" expande para todos os argumentos passados para o script.
# Se nenhum argumento for passado (como no init-db), ele não faz nada aqui, mas o CMD do compose.yaml
# será o argumento.
# Se o Dockerfile tiver um CMD, ele será o argumento.
exec "$@"
