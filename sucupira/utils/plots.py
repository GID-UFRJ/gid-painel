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

class PlotsPessoal(BasePlots):
    '''Gráficos sobre discentes/docentes da Pós-Graduação na UFRJ'''

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
        ano_inicial=2013,
        ano_final=2024,
        agrupamento="total",   # sexo | nacionalidade | faixa_etaria
        situacao="total",
        grande_area="total",
        grau_curso="total",
        tipo_grafico="barra",
    ):
        mapa_agrupamento = {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade",
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        }

        filtros = {
            "situacao__nm_situacao_discente": situacao,
            "programa__ano_programa__grande_area__nm_grande_area_conhecimento": grande_area,
            "grau_academico__nm_grau_curso": grau_curso,
        }
        return self._entidades_por_ano(
            modelo=Discente,
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=agrupamento,
            mapa_agrupamento=mapa_agrupamento,
            filtros=filtros,
            tipo_grafico=tipo_grafico,
            titulo_base="Discentes",
            campo_agregacao="pessoa_id",
            agregacao="count",
            distinct=True,
        )

    def docentes_por_ano(
        self,
        ano_inicial=2013,
        ano_final=2024,
        agrupamento="total",    # sexo | nacionalidade | faixa_etaria
        grande_area="total",
        modalidade="total",
        categoria_docente="total",
        bolsa_produtividade="total",
        tipo_grafico="barra",
    ):
        mapa_agrupamento = {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade",
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        }

        filtros = {
            "programa__ano_programa__grande_area__nm_grande_area_conhecimento": grande_area,
            "programa__ano_programa__nm_modalidade_programa__nm_modalidade_programa": modalidade,
            "categoria__ds_categoria_docente": categoria_docente,
            "bolsa_produtividade__cd_cat_bolsa_produtividade": bolsa_produtividade,
        }

        return self._entidades_por_ano(
            modelo=Docente,
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            agrupamento=agrupamento,
            mapa_agrupamento= mapa_agrupamento,
            filtros=filtros,
            tipo_grafico=tipo_grafico,
            titulo_base="Docentes",
            agregacao="count",
            campo_agregacao="pessoa_id", #Conta por id da tabela 'pessoa'
            distinct=True,  # evita contar a mesma pessoa mais de uma vez
        )