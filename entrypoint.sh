#!/bin/bash
# entrypoint.sh

# Definir um valor padrão para DJANGO_PORT e GUNICORN_WORKERS se não estiverem definidos
DJANGO_PORT=${DJANGO_PORT:-8000}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-1} 

echo "Iniciando Gunicorn na porta ${DJANGO_PORT} com ${GUNICORN_WORKERS} workers..."

# Executar o Gunicorn.
exec gunicorn --bind 0.0.0.0:${DJANGO_PORT} --workers ${GUNICORN_WORKERS} gid.wsgi:application
