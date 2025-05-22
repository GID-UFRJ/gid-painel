import pandas as pd
import numpy as np
from . import models
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly2, grafico_linha_plotly2

class Grafico_ranking:
    def __init__(self):
        self.queryset = models.Resultado.objects

    def kpi_qs_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='QS', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'QS - América Latina (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
        return(img)

    def kpi_the_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='THE', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'THE - América Latina (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
        return(img)

    def kpi_shanghaiNacional(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Nacional').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'Shanghai - Nacional (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
        return(img)


    def qs_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='QS', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS mundo', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)
    
    def qs_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='QS', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS América Latina', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)

    def the_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='THE', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'THE mundo', 'ano', 'posição', tamanho_rotulo_dados=15, largura=750, inverter_eixo_y=True)
        return(img)
    
    def the_americaLatina(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='THE', escopo__escopoNome='Am. Latina').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'THE América Latina', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)
    
    def shanghai_mundo(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Mundo').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'Shanghai mundo', 'ano', 'posição', largura=750, tamanho_rotulo_dados=15, inverter_eixo_y=True)
        return(img)
    
    def shanghai_nacional(self):
        queryset = self.queryset.\
            filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Nacional').\
            values('ano__ano', 'posicao')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'Shanghai Nacional', 'ano', 'posição', largura=750, inverter_eixo_y=True)
        return(img)
