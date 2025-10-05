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


    # =========================================================================
    # MÉTODOS DE GRÁFICO - ADAPTADOS PARA A NOVA BasePlots
    # =========================================================================
    def discentes_por_ano(
        self,
        tipo_grafico="barra",
        titulo_override: str | None = None,
        **kwargs
    ):
        """
        # ADAPTADO
        Gera gráfico de discentes por ano.
        Argumentos de filtro (ex: ano_inicial, situacao) são passados via **kwargs.
        """
        # A nova BasePlots lida com os filtros diretamente
        return self._gerar_grafico_agregado(
            tipo_entidade="discentes_geral", # Usa o mapeamento geral "discentes"
            tipo_grafico=tipo_grafico,
            filtros_selecionados=kwargs,
            agrupamento=kwargs.get("agrupamento"),
            titulo_override=titulo_override,
            distinct=True,
        )

    def docentes_por_ano(
        self,
        tipo_grafico="barra",
        titulo_override: str | None = None,
        **kwargs
    ):
        """
        # ADAPTADO
        Gera gráfico de docentes por ano.
        Argumentos de filtro (ex: ano_final, grande_area) são passados via **kwargs.
        """
        return self._gerar_grafico_agregado(
            tipo_entidade="docentes_geral", # Usa o mapeamento geral "docentes"
            tipo_grafico=tipo_grafico,
            filtros_selecionados=kwargs,
            agrupamento=kwargs.get("agrupamento"),
            titulo_override=titulo_override,
            distinct=True,
        )


# sucupira/utils/plots.py (ou onde sua classe está)

from django.shortcuts import render
# Adicione a importação da sua função de limites de ano
# from .helpers import get_limites_de_ano_global

class PlotsPpgDetalhe(BasePlots):
    '''Gráficos específicos de um Programa de Pós-Graduação.'''
    MAPEAMENTOS = MAPEAMENTOS

    def __init__(self, programa_id=None):
        if programa_id is None:
            raise ValueError("O ID do programa é obrigatório para PlotsPpgDetalhe.")
        self.programa_id = programa_id

    @staticmethod
    def gerar_grafico_view(request, programa_id, metodo_plot):
        """
        # ADAPTADO
        View genérica que agora usa defaults dinâmicos para os anos.
        """
        plotter = PlotsPpgDetalhe(programa_id=programa_id)
        
        # Opcional, mas recomendado: use defaults do DB para os anos
        # limites_db = get_limites_de_ano_global()
        # ano_inicial_default = limites_db['min_ano']
        # ano_final_default = limites_db['max_ano']
        
        # Fallback caso não use a função acima
        ano_inicial_default = 2013
        ano_final_default = 2025 # Usando o ano atual + 1 como default

        # Extrai os parâmetros da URL, aplicando os defaults
        params = request.GET.dict()
        params.setdefault('ano_inicial', ano_inicial_default)
        params.setdefault('ano_final', ano_final_default)

        # Chama o método de plotagem dinamicamente
        if hasattr(plotter, metodo_plot):
            metodo = getattr(plotter, metodo_plot)
            graf = metodo(**params)
        else:
            graf = f"<p class='text-danger'>Erro: Método de plotagem '{metodo_plot}' não encontrado.</p>"

        return render(request, "common/partials/_plot_reativo.html", {'graf': graf})

    def discentes_por_ano(
        self,
        tipo_grafico="barra",
        titulo_override: str | None = None,
        **kwargs
    ):
        """
        # ADAPTADO E SIMPLIFICADO
        Gera gráfico de discentes por ano para um programa específico.
        """
        # Adiciona o filtro de programa_id que é mandatório para esta classe
        kwargs['programa_id'] = self.programa_id
        
        return self._gerar_grafico_agregado(
            tipo_entidade="discentes_ppg",
            tipo_grafico=tipo_grafico,
            filtros_selecionados=kwargs,
            agrupamento=kwargs.get("agrupamento"),
            titulo_override=titulo_override,
            distinct=True,
        )
 
    def docentes_por_ano(
        self,
        tipo_grafico="barra",
        titulo_override: str | None = None,
        **kwargs
    ):
        """
        # ADAPTADO
        Gera gráfico de docentes por ano para um programa específico.
        """
        kwargs['programa_id'] = self.programa_id

        return self._gerar_grafico_agregado(
            tipo_entidade="docentes_ppg",
            tipo_grafico=tipo_grafico,
            filtros_selecionados=kwargs,
            agrupamento=kwargs.get("agrupamento"),
            titulo_override=titulo_override,
            distinct=True,
        )
    
    def conceito_programa_por_ano(
        self,
        tipo_grafico="linha",
        titulo_override: str | None = None,
        **kwargs
    ):
        """
        # CORRIGIDO E ADAPTADO
        Gera gráfico da evolução do conceito do programa.
        """
        kwargs['programa_id'] = self.programa_id
        
        # Corrigido para chamar o método de gráfico direto e o mapeamento correto
        return self._gerar_grafico_direto(
            tipo_entidade="conceito_ppg", 
            tipo_grafico=tipo_grafico,
            filtros_selecionados=kwargs,
            titulo_override=titulo_override,
        )