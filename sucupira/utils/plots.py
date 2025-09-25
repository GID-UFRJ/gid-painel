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
from .mapeamentos import MAPEAMENTOS

class PlotsPessoal(BasePlots):
    '''Gráficos sobre discentes/docentes da Pós-Graduação na UFRJ'''
    MAPEAMENTOS = MAPEAMENTOS

    def cards_total_alunos_titulados_por_grau(self):

        # Query que conta alunos titulados por grau de curso
        qs = (
            Discente.objects
            .filter(situacao__nm_situacao_discente="TITULADO") #Não adicionei o 'Mudança de nível sem defesa' ainda
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
            return None  # ou {}, se preferir vazio

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

    def discentes_por_ano(
        self,
        ano_inicial=2013, ano_final=2024, agrupamento="total",
        tipo_grafico="barra", **kwargs
    ):
        """
        Gera gráfico de discentes por ano.
        Argumentos de filtro (ex: situacao='Ativo') são passados via **kwargs.
        """
        return self._entidades_por_ano(
            tipo_entidade="discentes",
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=None if agrupamento == "total" else agrupamento,
            filtros_selecionados=kwargs,
            tipo_grafico=tipo_grafico,
            distinct=True,
        )

    def docentes_por_ano(
        self,
        ano_inicial=2013, ano_final=2024, agrupamento="total",
        tipo_grafico="barra", **kwargs
    ):
        """
        Gera gráfico de docentes por ano.
        Argumentos de filtro (ex: grande_area='Ciências Exatas') são passados via **kwargs.
        """
        return self._entidades_por_ano(
            tipo_entidade="docentes",
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=None if agrupamento == "total" else agrupamento,
            filtros_selecionados=kwargs,
            tipo_grafico=tipo_grafico,
            distinct=True,
        )

class PlotsPpgDetalhe(BasePlots):
    '''Gráficos sobre discentes/docentes da Pós-Graduação na UFRJ'''
    MAPEAMENTOS = MAPEAMENTOS
    def __init__(self, programa_id=None):
        self.programa_id = programa_id

    def discentes_por_ano(
        self,
        ano_inicial=2013, ano_final=2024, agrupamento="total",
        tipo_grafico="barra", **kwargs
    ):
        """
        Gera gráfico de discentes por ano.
        Argumentos de filtro (ex: situacao='Ativo') são passados via **kwargs.
        """
        if self.programa_id:
            kwargs["programa_id"] = self.programa_id
        return self._entidades_por_ano(
            tipo_entidade="discentes_ppg",
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=None if agrupamento == "total" else agrupamento,
            filtros_selecionados=kwargs,
            tipo_grafico=tipo_grafico,
            distinct=True,
        )

    def docentes_por_ano(
        self,
        ano_inicial=2013, ano_final=2024, agrupamento="total",
        tipo_grafico="barra", **kwargs
    ):
        """
        Gera gráfico de docentes por ano.
        Argumentos de filtro (ex: grande_area='Ciências Exatas') são passados via **kwargs.
        """
        if self.programa_id:
            kwargs["programa_id"] = self.programa_id

        return self._entidades_por_ano(
            tipo_entidade="docentes_ppg",
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=None if agrupamento == "total" else agrupamento,
            filtros_selecionados=kwargs,
            tipo_grafico=tipo_grafico,
            distinct=True,
        )
