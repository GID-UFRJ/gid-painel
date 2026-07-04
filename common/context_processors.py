import os

def versoes_sistema(request):
    # Pega o commit da imagem (se não existir, é porque está rodando local)
    commit = os.environ.get('COMMIT_HASH', 'Local')
    
    # Encurta o hash do GitHub para 7 caracteres (padrão de exibição)
    if commit not in ['Local', 'Desenvolvimento']:
        commit = commit[:7]
        
    return {
        'APP_VERSAO_COMMIT': commit,
    }