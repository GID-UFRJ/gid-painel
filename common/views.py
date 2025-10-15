from django.http import HttpResponse, Http404
import pandas as pd

# Importe TODAS as suas classes de plotagem de todos os apps
from sucupira.utils.plots import PlotsPessoal, PlotsPpgDetalhe
# from rankings.utils.plots import PlotsRankings # Exemplo de como adicionar no futuro

# --- O MAPA QUE CONECTA O MUNDO EXTERNO (URL) ÀS SUAS CLASSES ---
PLOTTER_MAPPING = {
    'pessoal': PlotsPessoal,
    'ppg_detalhe': PlotsPpgDetalhe,
    # 'rankings': PlotsRankings, # Exemplo de como registrar um novo app no futuro
}

def download_csv_generic(request, plotter_name: str, **kwargs):
    """
    UMA VIEW PARA GOVERNAR TODOS OS DOWNLOADS.

    Gera e serve um arquivo CSV com base no 'plotter_name' e nos filtros da URL.
    Usa 'kwargs' para capturar argumentos extras como 'programa_id'.
    """
    
    # 1. Encontra a classe de plotter correta usando o mapa.
    PlotterClass = PLOTTER_MAPPING.get(plotter_name)
    if not PlotterClass:
        raise Http404(f"Plotter '{plotter_name}' não encontrado.")

    # 2. Instancia a classe, passando argumentos extras (como programa_id) se necessário.
    try:
        plotter = PlotterClass(**kwargs)
    except TypeError:
        # Lida com o caso de uma classe não esperar argumentos (como PlotsPessoal).
        plotter = PlotterClass()
        
    # Extrai o nome do plot da URL (o último argumento capturado)
    # Esta é uma forma robusta de garantir que sempre pegamos o nome do plot.
    nome_plot = kwargs.get('nome_plot')
    if not nome_plot:
         # Fallback para URLs mais antigas, se necessário, mas o padrão novo é melhor.
         # Este erro indica um problema na configuração da URL.
        raise Http404("O 'nome_plot' não foi fornecido na URL.")

    # 3. Usa o método público da BasePlots para obter o DataFrame já filtrado.
    df = plotter.get_dataframe_for_plot(nome_plot, request.GET.dict())

    if df.empty:
        return HttpResponse("Nenhum dado encontrado para os filtros selecionados.", status=404)

    # 4. Gera a resposta CSV.
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig', # 'utf-8-sig' garante compatibilidade com Excel
        headers={'Content-Disposition': f'attachment; filename="{plotter_name}_{nome_plot}.csv"'},
    )
    # Usa o Pandas para escrever o CSV diretamente na resposta, usando ';' como separador.
    df.to_csv(path_or_buf=response, index=False, sep=';')

    return response