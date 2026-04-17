# common/views.py
from django.http import HttpResponse, Http404
from common.utils.dispatcher import Dispatcher
from .utils.export_helpers import DICIONARIOS_MAPEAMENTO, get_csv_response

def download_csv_generic(request, plotter_name: str, **kwargs):
    # 1. Busca o dicionário mestre do app (ex: 'openalex')
    mapeamento_alvo = DICIONARIOS_MAPEAMENTO.get(plotter_name)
    if not mapeamento_alvo:
        raise Http404(f"Mapeamento de exportação não encontrado para o app: {plotter_name}")

    nome_plot = kwargs.pop('nome_plot', None)
    
    # 2. Instancia o motor BASE passando o dicionário alvo
    plotter = Dispatcher(mapeamentos=mapeamento_alvo, **kwargs)
    
    filtros = request.GET.dict().copy()
    filtros.update(kwargs)

    # 3. O motor gera o dataframe genérico
    df = plotter.get_dataframe_for_plot(nome_plot, filtros)

    if df.empty:
        return HttpResponse("Nenhum dado encontrado para os filtros informados.", status=404)

    # 4. Transforma em CSV
    return get_csv_response(df, f"{plotter_name}_{nome_plot}")