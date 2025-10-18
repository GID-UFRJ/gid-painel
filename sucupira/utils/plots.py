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
from sucupira.models import Discente, Docente, Ano, AnoPrograma

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



class PlotsPpgDetalhe(BasePlots):
    '''Gráficos específicos de um Programa de Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS

    def __init__(self, programa_id=None):
        if programa_id is None:
            raise ValueError("O ID do programa é obrigatório para PlotsPpgDetalhe.")
        self.programa_id = programa_id


class PlotsPpgUfrj(BasePlots):
    '''Gráficos específicos sobre os PPGS da UFRJ'''
    MAPEAMENTOS = MAPEAMENTOS

    def _get_ultimo_ano(self):
        """
        [NOVO MÉTODO AUXILIAR]
        Busca o último ano com registros. É chamado a cada requisição,
        garantindo que o dado esteja sempre atualizado.
        """
        return Ano.objects.aggregate(max_ano=Max("ano_valor"))["max_ano"]

    def card_total_programas_ultimo_ano(self):
        """
        [CORRIGIDO] Conta o total de programas únicos no último ano registrado.
        """
        ultimo_ano = self._get_ultimo_ano()
        if ultimo_ano is None:
            return None

        total = (
            AnoPrograma.objects
            .filter(ano__ano_valor=ultimo_ano)
            .values("programa_id")
            .distinct()
            .count()
        )

        img = grafico_kpi( 
            valor=total, 
            rotulo=f"PPGs ({ultimo_ano})", 
            cor='#4169E1',
        )
        return img
    
    def cards_programas_por_modalidade(self):
        """
        [CORRIGIDO] Gera um card para cada modalidade de programa, contando
        quantos programas pertencem a cada uma no último ano.
        """
        ultimo_ano = self._get_ultimo_ano()
        if ultimo_ano is None:
            return [] # Retorna uma lista vazia se não houver dados

        qs = (
            AnoPrograma.objects
            .filter(ano__ano_valor=ultimo_ano)
            .values("nm_modalidade_programa__nm_modalidade_programa")
            .annotate(total=Count("programa_id", distinct=True))
            .order_by("nm_modalidade_programa__nm_modalidade_programa")
        )

        dados = {item["nm_modalidade_programa__nm_modalidade_programa"]: item["total"] for item in qs}
        cards = []
        for modalidade, total in dados.items():
            img = grafico_kpi(
                valor=total,
                rotulo=f"PPGs {modalidade}",
                cor='#4169E1',
            )
            cards.append(img)
        return cards

    def card_total_programas_conceito_maximo(self):
        """
        [CORRIGIDO] Conta quantos programas atingiram o conceito máximo (6 ou 7)
        no último ano registrado.
        """
        ultimo_ano = self._get_ultimo_ano()
        if ultimo_ano is None:
            return None

        # Filtra por conceitos considerados máximos
        total = (
            AnoPrograma.objects
            .filter(
                ano__ano_valor=ultimo_ano,
                cd_conceito_programa__cd_conceito_programa__in=[7] # Filtro por conceito 6 ou 7
            )
            .values("programa_id")
            .distinct()
            .count()
        )

        img = grafico_kpi( 
            valor=total, 
            rotulo=f"PPGs CAPES 7 ({ultimo_ano})", 
            cor='#28a745', # Cor diferente para destaque
        )
        return img

