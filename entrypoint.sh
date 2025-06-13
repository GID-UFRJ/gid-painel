#!/bin/bash
set -e # Sai imediatamente se um comando falhar

# Define GUNICORN_PORT com um valor padrão de 8000 se não estiver definido
GUNICORN_PORT=${GUNICORN_PORT:-8000}

# Define GUNICORN_WORKERS com um valor padrão de 2 se não estiver definido
GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}

# Verificar se algum argumento foi passado para o entrypoint.sh
# Se "$#" for maior que 0, significa que um comando (ou seus argumentos) foi fornecido
if [ "$#" -gt 0 ]; then
    echo "--- Executando comando customizado ---"
    echo "Comando: '$@'"
    # Executa o comando que foi passado para o entrypoint.sh
    # Isso é o que init-db precisa para rodar seus comandos de migração
    exec "$@"
else
    # Se nenhum argumento foi passado, executa o comando padrão (Gunicorn)
    # Isso é o que gid-painel fará por padrão
    echo "--- Iniciando Gunicorn (comando padrão) ---"
    echo "Porta: ${GUNICORN_PORT}, Workers: ${GUNICORN_WORKERS}"
    exec gunicorn --bind "0.0.0.0:${GUNICORN_PORT}" --workers "${GUNICORN_WORKERS}" gid.wsgi:application
fi
