import pandas as pd
import numpy as np
from . import models
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly2, grafico_linha_plotly2

class Grafico_ranking:
    def __init__(self):
        self.queryset = models.Resultado.objects

    def qs_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='QS', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        print(df)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS mundo', 'ano', 'posição', largura=750)
        return(img)
    
    def qs_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='QS', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        print(df)
        img = grafico_barra_plotly2(df, 'ano__ano', 'posicao', 'QS América Latina', 'ano', 'posição', largura=750)
        return(img)

    def the_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='THE', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        print(df)
        img = grafico_barra_plotly2(df, 'ano__ano', 'posicao', 'THE mundo', 'ano', 'posição', largura=750)
        return(img)
    
    def the_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='THE', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        print(df)
        img = grafico_barra_plotly2(df, 'ano__ano', 'posicao', 'THE América Latina', 'ano', 'posição', largura=750)
        return(img)
    
    def shanghai_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'ano__ano', 'posicao', 'Shanghai mundo', 'ano', 'posição', largura=750)
        return(img)
    
    def shanghai_nacional(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Nacional').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'ano__ano', 'posicao', 'Shanghai Nacional', 'ano', 'posição', largura=750)
        return(img)
