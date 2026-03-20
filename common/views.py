# common/views.py
from django.http import HttpResponse, Http404
from .utils.export_helpers import PLOTTER_MAPPING, get_csv_response

def download_csv_generic(request, plotter_name: str, **kwargs):
    PlotterClass = PLOTTER_MAPPING.get(plotter_name)
    if not PlotterClass:
        raise Http404(...)

    nome_plot = kwargs.pop('nome_plot', None)
    plotter = PlotterClass(**kwargs)
    
    filtros = request.GET.dict().copy()
    filtros.update(kwargs)

    # A lógica de "COMO gerar os dados" está encapsulada no Dispatcher/Strategy
    df = plotter.get_dataframe_for_plot(nome_plot, filtros)

    if df.empty:
        return HttpResponse("Vazio", status=404)

    # A lógica de "COMO transformar em arquivo" está no helper
    return get_csv_response(df, f"{plotter_name}_{nome_plot}")