import pandas as pd
import numpy as np
from rankings import models
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores
from gid.utils_scripts_graficos_plotly import grafico_linha_plotly2

class Grafico_ranking:
    def __init__(self):
        self.queryset = models.Resultado.objects

    def mundo(self, ranking:str | None = 'QS'):
        queryset = self.queryset.\
            filter(ranking__rankingNome=ranking, escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], f'{ranking} mundo', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)
    
    def americaLatina(self, ranking:str | None = 'QS'):
        queryset = self.queryset.\
            filter(ranking__rankingNome=ranking, escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS América Latina', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)
    
