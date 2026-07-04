# common/views.py
from django.http import HttpResponse, Http404
from common.utils.dispatcher import Dispatcher
from .utils.export_helpers import DICIONARIOS_MAPEAMENTO, get_csv_response

import re
import requests
from django.core.cache import cache
import threading
import subprocess
import os
from decouple import config
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

def download_csv_generic(request, plotter_name: str, **kwargs):
    # 1. Busca o dicionário mestre do app (ex: 'openalex')
    mapeamento_alvo = DICIONARIOS_MAPEAMENTO.get(plotter_name)
    if not mapeamento_alvo:
        raise Http404(f"Mapeamento de exportação não encontrado para o app: {plotter_name}")

    nome_plot = kwargs.pop('nome_plot', None)
    
    # 2. Instancia o motor BASE passando o dicionário alvo
    plotter = Dispatcher(mapeamentos=mapeamento_alvo)
    
    filtros = request.GET.dict().copy()
    filtros.update(kwargs)

    # 3. O motor gera o dataframe genérico
    df = plotter.get_dataframe_for_plot(nome_plot, filtros)

    if df.empty:
        return HttpResponse("Nenhum dado encontrado para os filtros informados.", status=404)

    # 4. Transforma em CSV
    return get_csv_response(df, f"{plotter_name}_{nome_plot}")



def tarefa_atualizacao_dados():
    # 1. Busca a URL genérica definida na infraestrutura
    url_do_dump = config('DUMP_URL')
    
    # Caminho temporário no contêiner
    caminho_tmp = '/tmp/novo_banco.dump'
    
    # 2. Busca as credenciais com decouple
    db_user = config('POSTGRES_USER')
    db_pass = config('POSTGRES_PASSWORD')
    db_host = config('POSTGRES_HOST')
    db_port = config('POSTGRES_PORT', default='5432')
    db_name = config('POSTGRES_DB')
    
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    try:
        print(f"Processando URL original: {url_do_dump}")
        
        # === INÍCIO DA LÓGICA DE DETECÇÃO (ZENODO VS CLOUDFLARE) ===
        # Se for um link de preservação científica (zenodo), seguimos o redirecionamento
        if "doi.org" in url_do_dump or "zenodo.org" in url_do_dump:
            print("Link Zenodo/DOI detectado. Buscando a versão mais recente...")
            # Pede ao servidor para onde a URL redireciona, pegando o link final
            resposta = requests.head(url_do_dump, allow_redirects=True)
            url_base = resposta.url.rstrip('/')
            
            # Se a URL não tiver os parâmetros de download anexados, nós montamos
            if "/files/" not in url_base:
                link_download = f"{url_base}/files/gid_db.dump?download=1"
            else:
                link_download = url_base
        else:
            # Se for link direto (como bucket Cloudflare, AWS), usa ele mesmo
            link_download = url_do_dump
            
        print(f"Iniciando download da fonte final: {link_download}")
        # === FIM DA LÓGICA ===

        # === NOVO: EXTRAÇÃO DA VERSÃO ===
        # Procura o padrão "records/NUMEROS" no link final do download
        match_zenodo = re.search(r'records/(\d+)', link_download)
        zenodo_id = match_zenodo.group(1) if match_zenodo else "Fonte Externa"
        # ================================

        # O curl agora recebe o link_download mastigado e exato!
        subprocess.run(['curl', '-L', '-o', caminho_tmp, link_download], check=True)

        print("Restaurando as tabelas científicas no banco...")
        comando_restore = [
            'pg_restore', 
            '--clean',      
            '--if-exists',  
            '--no-owner',   
            '--dbname', db_url, 
            caminho_tmp
        ]
        subprocess.run(comando_restore, check=True)
        print("Sincronização concluída com sucesso!")
        
        # === NOVO: SALVANDO A VERSÃO NO CACHE ===
        # Registra no Redis para que o Context Processor possa exibir no Admin
        cache.set('DB_VERSAO_ZENODO', zenodo_id, timeout=None)
        print(f"Versão do banco ({zenodo_id}) salva no cache com sucesso.")
        # ========================================

    except subprocess.CalledProcessError as e:
        print(f"Erro durante a execução do comando de sistema: {e}")
    except Exception as e:
        # Pega erros de rede do requests (Zenodo fora do ar, por exemplo)
        print(f"Erro inesperado ao processar atualização: {e}")
        
    finally:
        # Garante que o contêiner não fique com lixo acumulado
        if os.path.exists(caminho_tmp):
            os.remove(caminho_tmp)


@staff_member_required
def sincronizar_view(request):
    """
    View acionada pelo botão no painel admin.
    """
    thread = threading.Thread(target=tarefa_atualizacao_dados)
    thread.start()
    
    messages.success(
        request, 
        "A sincronização com a base de dados remota foi iniciada em segundo plano. Os dados do painel estarão atualizados em breve!"
    )
    
    return HttpResponseRedirect(reverse('admin:index'))