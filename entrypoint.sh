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
    # Se nenhum argumento foi passado, faz o setup automático e inicia o Gunicorn
    echo "--- 1. Aplicando migrações (se houver novas)... ---"
    python manage.py migrate --no-input

    echo "--- 2. Coletando arquivos estáticos... ---"
    python manage.py collectstatic --no-input

    echo "--- 3. Garantindo superusuário (ignora erro se já existir)... ---"
    python manage.py createsuperuser --noinput \
                     --username "$DJANGO_SUPERUSER_USERNAME" \
                     --email "$DJANGO_SUPERUSER_EMAIL" || true

    echo "--- Setup da Aplicação Concluído! ---"

    # Limpa o cache do Redis 
    echo "Limpando o cache antigo do Redis..."
    python manage.py shell -c "from django.core.cache import cache; cache.clear()"
    
    echo "--- Iniciando Gunicorn (comando padrão) ---"
    echo "Porta: ${DJANGO_PORT}, Workers: ${GUNICORN_WORKERS}"
    exec gunicorn --bind "0.0.0.0:${DJANGO_PORT}" --workers "${GUNICORN_WORKERS}" gid.wsgi:application
fi