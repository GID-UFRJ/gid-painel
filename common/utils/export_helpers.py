# common/utils/export_helpers.py
from django.http import HttpResponse 

# Importe os Dicionários Mestres
from openalex.utils.mapeamentos import MAPEAMENTOS_TODOS as MAP_OPENALEX
from sucupira.utils.mapeamentos import MAPEAMENTOS_TODOS as MAP_SUCUPIRA
# from rankings.utils.mapeamentos import MAPEAMENTOS_TODOS as MAP_RANKINGS

# Mapeamento de App -> Dicionário
DICIONARIOS_MAPEAMENTO = {
    'openalex': MAP_OPENALEX,
    'sucupira': MAP_SUCUPIRA,
    # 'rankings': MAP_RANKINGS,
}

def get_csv_response(df, filename):
    """Encapsula a criação do objeto HttpResponse para CSV."""
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
    )
    df.to_csv(path_or_buf=response, index=False, sep=';')
    return response