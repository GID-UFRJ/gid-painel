import os
from django.core.cache import cache

def versoes_sistema(request):
    # Pega o commit da imagem (se não existir, é porque está rodando local)
    commit = os.environ.get('COMMIT_HASH', 'Local')
    
    # Encurta o hash do GitHub para 7 caracteres
    if commit not in ['Local', 'Desenvolvimento']:
        commit = commit[:7]
        
    # Tenta pegar a versão no Redis, protegendo contra quedas ou ausência do serviço
    try:
        db_versao = cache.get('DB_VERSAO_ZENODO', 'Aguardando atualização')
    except Exception:
        # Se o Redis não estiver rodando (típico do ambiente local), ignora o erro
        db_versao = 'Desconhecida (Cache offline)'
    
    return {
        'APP_VERSAO_COMMIT': commit,
        'APP_VERSAO_DB': db_versao
    }