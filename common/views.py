from django.http import HttpResponse, Http404
import pandas as pd

# Importe TODAS as suas classes de plotagem de todos os apps
from sucupira.utils.plots import PlotsPessoal, PlotsPpgDetalhe, PlotsPpgUfrj
# from rankings.utils.plots import PlotsRankings # Exemplo de como adicionar no futuro

# --- O MAPA QUE CONECTA O MUNDO EXTERNO (URL) ÀS SUAS CLASSES ---
PLOTTER_MAPPING = {
    'pessoal': PlotsPessoal,
    'ppg_detalhe': PlotsPpgDetalhe,
    'posgrad_ufrj': PlotsPpgUfrj,
    # 'rankings': PlotsRankings, # Exemplo de como registrar um novo app no futuro
}

def download_csv_generic(request, plotter_name: str, **kwargs):
    """
    [VERSÃO FINAL E CORRIGIDA]
    Gera e serve um arquivo CSV, garantindo que os parâmetros da URL
    (como programa_id) sejam incluídos nos filtros.
    """
    PlotterClass = PLOTTER_MAPPING.get(plotter_name)
    if not PlotterClass:
        raise Http404(f"Plotter '{plotter_name}' não encontrado.")

    # --- INÍCIO DA CORREÇÃO ---

    # 1. Extraímos o 'nome_plot' de kwargs, pois ele não é um filtro.
    #    O .pop() o remove do dicionário kwargs.
    nome_plot = kwargs.pop('nome_plot', None)
    if not nome_plot:
        raise Http404("O 'nome_plot' não foi fornecido na URL.")

    # 2. Instanciamos o plotter com os argumentos restantes em kwargs (ex: {'programa_id': 139}).
    plotter = PlotterClass(**kwargs)

    # 3. Criamos o dicionário de filtros a partir dos parâmetros da query (ex: ?ano_inicial=...).
    filtros = request.GET.dict().copy() # Usamos .copy() por segurança

    # 4. A PARTE CRUCIAL: Atualizamos os filtros com os argumentos da URL (kwargs).
    #    Isso adiciona {'programa_id': 139} ao dicionário de filtros.
    filtros.update(kwargs)

    # --- FIM DA CORREÇÃO ---

    # 5. Agora, passamos o dicionário de filtros COMPLETO para a BasePlots.
    df = plotter.get_dataframe_for_plot(nome_plot, filtros)

    if df.empty:
        return HttpResponse("Nenhum dado encontrado para os filtros selecionados.", status=404)

    # A geração da resposta CSV permanece a mesma.
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="{plotter_name}_{nome_plot}.csv"'},
    )
    df.to_csv(path_or_buf=response, index=False, sep=';')

    return response