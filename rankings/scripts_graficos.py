import pandas as pd
import numpy as np
from . import models
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly2, grafico_linha_plotly2
from baseGraficos import utils_plotly
from baseGraficos import models as m

class Grafico_ranking:
    def __init__(self):
        self.queryset = models.Resultado.objects
        self.queryset_graf = m.Grafico.objects

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

class Grafico_ranking2:
    def __init__(self):
        self.queryset_graf = m.Grafico.objects
    
    def listaGraficos(self):
        lista = []
        registros = self.queryset_graf.all()
        for r in registros:
            graf = utils_plotly.Grafico(r.tamanhoGrafico.tamanhoHorizontal, r.tamanhoGrafico.tamanhoVertical)
            lista.append(graf.escolher_grafico(r.estiloGrafico.numeroIdentificador, r.tituloGrafico, r.tituloEixoX, r.tituloEixoX, r.series))
        return(lista)
    
 