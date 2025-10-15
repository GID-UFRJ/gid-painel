import pandas as pd
import plotly.express as px
from plotly.io import to_html
import numpy as np
from ..models import Discente, Docente, Ano, GrauCurso
from django.db.models import F, Q, Count, Sum, Min, Avg, Max, Subquery, OuterRef, Case, When, Value, CharField, Exists 
from django.db.models.functions import Coalesce
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_linha_plotly, grafico_barra_plotly, grafico_barra_plotly2
from common.utils.baseplots import BasePlots
from django.shortcuts import render
from .mapeamentos import MAPEAMENTOS

# sucupira/utils/plots.py (ou onde sua classe está)

from django.db.models import Count, Max
from common.utils.baseplots import BasePlots
from .mapeamentos import MAPEAMENTOS
from sucupira.models import Discente, Docente, Ano

# Supondo que 'grafico_kpi' seja uma função que você já tenha
# from .kpi_generator import grafico_kpi 

class PlotsPessoal(BasePlots):
    '''Gráficos gerais sobre discentes e docentes da Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS

    # =========================================================================
    # MÉTODOS DE CARD (KPI) - MANTIDOS EXATAMENTE COMO OS ORIGINAIS
    # =========================================================================
    def cards_total_alunos_titulados_por_grau(self):
        # Query que conta alunos titulados por grau de curso
        qs = (
            Discente.objects
            .filter(situacao__nm_situacao_discente="TITULADO")
            .values("grau_academico__nm_grau_curso")
            .annotate(total=Count("id"))
            .order_by("grau_academico__nm_grau_curso")
        )

        # Transforma em dicionário {nome_curso: total}
        dados = {item["grau_academico__nm_grau_curso"]: item["total"] for item in qs}

        cards = []

        for grau, total in dados.items():
            img = grafico_kpi(
                valor=total,
                rotulo=f"Titulados - {grau}",
                cor='#4169E1',
            )
            cards.append(img)
        
        return cards

    def card_total_docentes_ultimo_ano(self):
        # Pega o último ano presente na base
        ultimo_ano = Ano.objects.aggregate(max_ano=Max("ano_valor"))["max_ano"]

        if ultimo_ano is None:
            return None

        # Conta docentes do último ano
        total = (
            Docente.objects
            .filter(ano__ano_valor=ultimo_ano)
            .values("pessoa_id")
            .distinct()
            .count()
        )

        img = grafico_kpi( 
            valor=total, 
            rotulo=f"Docentes em PPGs ({ultimo_ano})", cor='#4169E1',
            )
        
        return img




# Adicione a importação da sua função de limites de ano
# from .helpers import get_limites_de_ano_global

class PlotsPpgDetalhe(BasePlots):
    '''Gráficos específicos de um Programa de Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS

    def __init__(self, programa_id=None):
        if programa_id is None:
            raise ValueError("O ID do programa é obrigatório para PlotsPpgDetalhe.")
        self.programa_id = programa_id
