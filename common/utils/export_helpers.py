# common/utils/export_helpers.py
from django.http import HttpResponse 
from sucupira.utils.plots import PlotsPessoal, PlotsPpgDetalhe, PlotsPpgUfrj
from openalex.utils.plots import PlotsProducao

#NOTA: Esses helpers são usados na view do app common, para centralizar a exportacao dos dados (em csv) de todos os gráficos 
#A view e url que tomam conta dessa exportacao estão no próprio app 'common'

# Mapeamento das classes dos plots
PLOTTER_MAPPING = {
    'pessoal': PlotsPessoal,
    'ppg_detalhe': PlotsPpgDetalhe,
    'posgrad_ufrj': PlotsPpgUfrj,
    'openalex': PlotsProducao,
}

def get_csv_response(df, filename):
    """Encapsula a criação do objeto HttpResponse para CSV."""
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
    )
    df.to_csv(path_or_buf=response, index=False, sep=';')
    return response