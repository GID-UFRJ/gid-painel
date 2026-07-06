import threading
import subprocess
import os
import requests
from decouple import config
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

from common.utils.dispatcher import Dispatcher
from .utils.export_helpers import DICIONARIOS_MAPEAMENTO, get_csv_response

from django.core.cache import cache


def download_csv_generic(request, plotter_name: str, **kwargs):
    mapeamento_alvo = DICIONARIOS_MAPEAMENTO.get(plotter_name)
    if not mapeamento_alvo:
        raise Http404(f"Mapeamento de exportação não encontrado para o app: {plotter_name}")

    nome_plot = kwargs.pop('nome_plot', None)
    plotter = Dispatcher(mapeamentos=mapeamento_alvo)
    
    filtros = request.GET.dict().copy()
    filtros.update(kwargs)

    df = plotter.get_dataframe_for_plot(nome_plot, filtros)

    if df.empty:
        return HttpResponse("Nenhum dado encontrado para os filtros informados.", status=404)

    return get_csv_response(df, f"{plotter_name}_{nome_plot}")


def tarefa_atualizacao_dados():
    url_do_dump = config('DUMP_URL')
    caminho_tmp = '/tmp/novo_banco.dump'
    
    db_user = config('POSTGRES_USER')
    db_pass = config('POSTGRES_PASSWORD')
    db_host = config('POSTGRES_HOST')
    db_port = config('POSTGRES_PORT', default='5432')
    db_name = config('POSTGRES_DB')
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    try:
        print(f"Processando URL: {url_do_dump}")
        
        # 1. Resolve redirecionamentos do Zenodo ou usa links diretos
        if "doi.org" in url_do_dump or "zenodo.org" in url_do_dump:
            resposta = requests.head(url_do_dump, allow_redirects=True)
            url_base = resposta.url.rstrip('/')
            link_download = f"{url_base}/files/gid_db.dump?download=1" if "/files/" not in url_base else url_base
        else:
            link_download = url_do_dump
            
        print(f"Baixando arquivo final de: {link_download}")
        
        # 2. Faz o download nativo em Python (seguro, sem dependência do curl)
        resposta_arquivo = requests.get(link_download, stream=True)
        resposta_arquivo.raise_for_status()
        
        with open(caminho_tmp, 'wb') as f:
            for chunk in resposta_arquivo.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print("Download concluído. Iniciando restauração do banco...")

        # 3. Restaura o banco de dados
        subprocess.run([
            'pg_restore', '--clean', '--if-exists', '--no-owner', 
            '--dbname', db_url, caminho_tmp
        ], check=True)
        
        print("Sincronização do banco concluída com sucesso!")

        # 4. Limpeza do cache
        print("Limpando os gráficos antigos do Redis...")
        cache.clear()
        print("Cache limpo! O painel já está exibindo os dados mais recentes.")

    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao baixar o banco de dados: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a restauração do banco (pg_restore): {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        # 5. Limpa a sujeira
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