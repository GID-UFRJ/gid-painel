import pandas as pd
import plotly.express as px
from plotly.io import to_html
import numpy as np
from ..models import Discente, Docente, Ano, GrauCurso
from django.db.models import F, Q, Count, Sum, Min, Avg, Max, Subquery, OuterRef, Case, When, Value, CharField, Exists 
from django.db.models.functions import Coalesce
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_linha_plotly, grafico_barra_plotly, grafico_barra_plotly2
from django.shortcuts import render
from .mapeamentos import MAPEAMENTOS

# sucupira/utils/plots.py (ou onde sua classe está)

from django.db.models import Count, Max
from common.utils.dispatcher import Dispatcher
from .mapeamentos import MAPEAMENTOS
from sucupira.models import Discente, Docente, Ano, AnoPrograma

# Supondo que 'grafico_kpi' seja uma função que você já tenha
# from .kpi_generator import grafico_kpi 

class PlotsPessoal(Dispatcher):
    '''Gráficos gerais sobre discentes e docentes da Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS


class PlotsPpgDetalhe(Dispatcher):
    '''Gráficos específicos de um Programa de Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS

    def __init__(self, programa_id=None):
        if programa_id is None:
            raise ValueError("O ID do programa é obrigatório para PlotsPpgDetalhe.")
        self.programa_id = programa_id


class PlotsPpgUfrj(Dispatcher):
    '''Gráficos específicos sobre os PPGS da UFRJ'''
    MAPEAMENTOS = MAPEAMENTOS