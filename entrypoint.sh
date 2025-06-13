#!/bin/bash
set -e # Sai imediatamente se um comando falhar

# Assegure-se de que as variáveis obrigatórias estejam definidas.
# Se não estiverem, o script falhará com a mensagem de erro.
# O valor virá do 'ENV' do Dockerfile, ou de um override do 'compose.yaml',
# ou de 'docker run -e'.
: "${DJANGO_PORT?Missing DJANGO_PORT environment variable}"
: "${GUNICORN_WORKERS?Missing GUNICORN_WORKERS environment variable}"

echo "Starting with DJANGO_PORT=${DJANGO_PORT} and GUNICORN_WORKERS=${GUNICORN_WORKERS}"

# Verificar se algum argumento foi passado para o entrypoint.sh 
# Se "$#" for maior que 0, significa que um comando (ou seus argumentos) foi fornecido
if [ "$#" -gt 0 ]; then
    echo "--- Executando comando customizado ---"
    echo "Comando: '$@'"
    # Executa o comando que foi passado para o entrypoint.sh
    # Isso é o que init-db precisa para rodar seus comandos de migração
    exec "$@"
else
    # Se nenhum argumento foi passado (assume CMD vazio no Dockerfile), executa o comando padrão (Gunicorn)
    # Isso é o que gid-painel fará por padrão
    echo "--- Iniciando Gunicorn (comando padrão) ---"
    echo "Porta: ${GUNICORN_PORT}, Workers: ${GUNICORN_WORKERS}"
    exec gunicorn --bind "0.0.0.0:${GUNICORN_PORT}" --workers "${GUNICORN_WORKERS}" gid.wsgi:application
fi
