import pandas as pd
import plotly.express as px
from plotly.io import to_html
import numpy as np
from ..models import Discente, Docente, Ano, GrauCurso
from django.db.models import F, Q, Count, Sum, Min, Avg, Max, Subquery, OuterRef, Case, When, Value, CharField, Exists 
from django.db.models.functions import Coalesce
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_linha_plotly, grafico_barra_plotly, grafico_barra_plotly2


class PlotsPessoal:
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

#    def discentes_por_ano(
#        self,
#        ano_inicial: int | None = 2013,
#        ano_final: int | None = 2024,
#        agrupamento: str | None = 'total',
#        situacao: str | None = 'total',
#        grande_area: str | None = 'total',
#        grau_curso: str | None = 'total', 
#        tipo_grafico: str | None = 'barra'
#    ):
#        """
#        Gera um gráfico da contagem de discentes por ano, com filtros e agrupamentos dinâmicos.
#        """
#    
#        # --- 1. Construção da Query Dinâmica ---
#        queryset = Discente.objects.filter(
#            ano__ano_valor__gte=ano_inicial,
#            ano__ano_valor__lte=ano_final
#        )
#    
#        if situacao and situacao != 'total':
#            queryset = queryset.filter(situacao__nm_situacao_discente=situacao)
#    
#        if grande_area and grande_area != 'total':
#            queryset = queryset.filter(programa__grande_area__nm_grande_area_conhecimento=grande_area)
#    
#        if grau_curso and grau_curso != 'total':
#            queryset = queryset.filter(grau_academico__nm_grau_curso=grau_curso)
#    
#        # --- 2. Definir agrupamento ---
#        mapa_agrupamento = {
#            'sexo': 'pessoa__tp_sexo__sexo',
#            'nacionalidade': 'pessoa__tipo_nacionalidade__ds_tipo_nacionalidade',
#            'faixa_etaria': 'faixa_etaria__ds_faixa_etaria'
#        }
#    
#        campo_grupo = mapa_agrupamento.get(agrupamento)
#        category_orders = {}
#    
#        # --- 3. Agrupar e contar ---
#        if campo_grupo:
#            dados = queryset.values('ano__ano_valor', campo_grupo).annotate(
#                total_discentes=Count('id')
#            ).order_by('ano__ano_valor')
#        else:
#            dados = queryset.values('ano__ano_valor').annotate(
#                total_discentes=Count('id')
#            ).order_by('ano__ano_valor')
#    
#        df = pd.DataFrame(list(dados))
#        if df.empty:
#            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
#    
#        # --- 4. Renomear colunas ---
#        df.rename(columns={'ano__ano_valor': 'ano', 'total_discentes': 'Discentes'}, inplace=True)
#        if campo_grupo:
#            grupo_plotly = campo_grupo.split('__')[-1]
#            df[grupo_plotly] = df[campo_grupo].fillna('Não informado')
#    
#            # --- 5. Ordenação das categorias ---
#            if agrupamento == 'sexo':
#                category_orders[grupo_plotly] = ['M', 'F', 'D']
#            else:
#                category_orders[grupo_plotly] = sorted(df[grupo_plotly].unique())
#        else:
#            grupo_plotly = None
#    
#        # --- 6. Criar título ---
#        titulo = f"Total de Discentes por Ano ({ano_inicial}-{ano_final})"
#    
#        # --- 7. Criar gráfico ---
#        if tipo_grafico == "barra":
#            fig = px.bar(
#                df,
#                x='ano',
#                y='Discentes',
#                color=grupo_plotly,
#                text='Discentes',
#                title=titulo,
#                category_orders=category_orders,
#                barmode='group'
#            )
#            fig.update_traces(textposition='outside')
#        else:
#            fig = px.line(
#                df,
#                x='ano',
#                y='Discentes',
#                color=grupo_plotly,
#                markers=True,
#                title=titulo,
#                category_orders=category_orders
#            )
#    
#        fig.update_layout(
#            autosize=True,
#            margin=dict(l=40, r=40, t=60, b=40),
#            xaxis_title="Ano",
#            yaxis_title="Número de Discentes",
#            legend_title_text=agrupamento.replace('_', ' ').title() if grupo_plotly else '',
#            xaxis=dict(type='category')
#        )
#    
#        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={"responsive": True})
#

#    def discentes_por_ano( 
#        self,
#        ano_inicial: int | None = 2013,
#        ano_final: int | None = 2024,
#        agrupamento: str | None = 'total',
#        situacao: str | None = 'total',
#        grande_area: str | None = 'total',
#        grau_curso: str | None = 'total', 
#        tipo_grafico: str | None = 'barra'
#    ):
#        """
#        Gera um gráfico da contagem de discentes por ano, com filtros e agrupamentos dinâmicos.
#        FUNCAO PROVISORIA - ADICIONA TODOS OS ANOS VAZIOS, OCUPANDO ESPACO INUTIL NO GRAFICO...
#        """
#    
#        # --- 1. Construção da Query Dinâmica ---
#        queryset = Discente.objects.filter(
#            ano__ano_valor__gte=ano_inicial,
#            ano__ano_valor__lte=ano_final
#        )
#    
#        if situacao and situacao != 'total':
#            queryset = queryset.filter(situacao__nm_situacao_discente=situacao)
#    
#        if grande_area and grande_area != 'total':
#            queryset = queryset.filter(programa__ano_programa__grande_area__nm_grande_area_conhecimento=grande_area)
#    
#        if grau_curso and grau_curso != 'total':
#            queryset = queryset.filter(grau_academico__nm_grau_curso=grau_curso)
#    
#        # --- 2. Definir agrupamento ---
#        mapa_agrupamento = {
#            'sexo': 'pessoa__tp_sexo__sexo',
#            'nacionalidade': 'pessoa__tipo_nacionalidade__ds_tipo_nacionalidade',
#            'faixa_etaria': 'faixa_etaria__ds_faixa_etaria'
#        }
#    
#        campo_grupo = mapa_agrupamento.get(agrupamento)
#        category_orders = {}
#    
#        # --- 3. Agrupar e contar ---
#        if campo_grupo:
#            dados = queryset.values('ano__ano_valor', campo_grupo).annotate(
#                total_discentes=Count('id')
#            ).order_by('ano__ano_valor')
#        else:
#            dados = queryset.values('ano__ano_valor').annotate(
#                total_discentes=Count('id')
#            ).order_by('ano__ano_valor')
#    
#        df = pd.DataFrame(list(dados))
#        if df.empty:
#            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
#    
#        # --- 4. Renomear colunas ---
#        df.rename(columns={'ano__ano_valor': 'ano', 'total_discentes': 'Discentes'}, inplace=True)
#        
#        # --- 5. Preencher anos faltantes ---
#        # Criar um DataFrame com todos os anos no intervalo
#        todos_anos = pd.DataFrame({'ano': range(ano_inicial, ano_final + 1)})
#        
#        if campo_grupo:
#            grupo_plotly = campo_grupo.split('__')[-1]
#            df[grupo_plotly] = df[campo_grupo].fillna('Não informado')
#    
#            # Para cada categoria, garantir que todos os anos estejam presentes
#            categorias = df[grupo_plotly].unique()
#            dfs_preenchidos = []
#            
#            for categoria in categorias:
#                df_categoria = df[df[grupo_plotly] == categoria].copy()
#                df_completo = todos_anos.merge(df_categoria, on='ano', how='left')
#                df_completo[grupo_plotly].fillna(categoria, inplace=True)
#                df_completo['Discentes'].fillna(0, inplace=True)
#                dfs_preenchidos.append(df_completo)
#            
#            # Combinar todos os DataFrames
#            df = pd.concat(dfs_preenchidos, ignore_index=True)
#            
#            # --- 6. Ordenação das categorias ---
#            if agrupamento == 'sexo':
#                # Usar CategoricalDtype para garantir a ordem correta
#                from pandas.api.types import CategoricalDtype
#                cat_type = CategoricalDtype(categories=['M', 'F', 'D'], ordered=True)
#                df[grupo_plotly] = df[grupo_plotly].astype(cat_type)
#                category_orders[grupo_plotly] = ['M', 'F', 'D']
#            else:
#                # Para outras categorias, usar a ordem natural
#                category_orders[grupo_plotly] = sorted(df[grupo_plotly].unique())
#        else:
#            grupo_plotly = None
#            # Preencher anos faltantes mesmo quando não há agrupamento
#            df = todos_anos.merge(df, on='ano', how='left').fillna(0)
#    
#        # Ordenar por ano para garantir a sequência correta
#        df.sort_values('ano', inplace=True)
#    
#        # --- 7. Criar título ---
#        titulo = f"Total de Discentes por Ano ({ano_inicial}-{ano_final})"
#    
#        # --- 8. Criar gráfico ---
#        if tipo_grafico == "barra":
#            fig = px.bar(
#                df,
#                x='ano',
#                y='Discentes',
#                color=grupo_plotly,
#                text='Discentes',
#                title=titulo,
#                category_orders=category_orders,
#                barmode='group'
#            )
#            fig.update_traces(textposition='outside')
#        else:
#            fig = px.line(
#                df,
#                x='ano',
#                y='Discentes',
#                color=grupo_plotly,
#                markers=True,
#                title=titulo,
#                category_orders=category_orders
#            )
#            
#            # Para gráficos de linha, garantir que os pontos sejam conectados
#            fig.update_traces(connectgaps=True)
#    
#        fig.update_layout(
#            autosize=True,
#            margin=dict(l=40, r=40, t=60, b=40),
#            xaxis_title="Ano",
#            yaxis_title="Número de Discentes",
#            legend_title_text=agrupamento.replace('_', ' ').title() if grupo_plotly else '',
#            xaxis=dict(type='category')
#        )
#    
#        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={"responsive": True})
#
#    def docentes_por_ano(
#        ano_inicial: int | None = 2013,
#        ano_final: int | None = 2024,
#        agrupamento: str | None = 'total',   # 'nacionalidade', 'sexo', 'faixa_etaria'
#        grande_area: str | None = 'total',
#        modalidade: str | None = 'total',
#        categoria_docente: str | None = 'total',
#        tipo_grafico: str | None = 'barra'
#    ):
#        """
#        Gera gráfico da contagem de docentes por ano,
#        com filtros e agrupamentos dinâmicos.
#        """
#
#        # --- 1. Construção da Query Dinâmica ---
#        queryset = Docente.objects.filter(
#            ano__ano_valor__gte=ano_inicial,
#            ano__ano_valor__lte=ano_final
#        )
#
#        # filtros
#        if grande_area and grande_area != 'total':
#            queryset = queryset.filter(
#                programa__ano_programa__grande_area__nm_grande_area_conhecimento=grande_area
#            )
#
#        if modalidade and modalidade != 'total':
#            queryset = queryset.filter(
#                programa__ano_programa__nm_modalidade_programa__nm_modalidade_programa=modalidade
#            )
#
#        if categoria_docente and categoria_docente != 'total':
#            queryset = queryset.filter(
#                categoria__ds_categoria_docente=categoria_docente
#            )
#
#        # --- 2. Definir agrupamento ---
#        mapa_agrupamento = {
#            'sexo': 'pessoa__tp_sexo__sexo',
#            'nacionalidade': 'pessoa__tipo_nacionalidade__ds_tipo_nacionalidade',
#            'faixa_etaria': 'faixa_etaria__ds_faixa_etaria'
#        }
#
#        campo_grupo = mapa_agrupamento.get(agrupamento)
#        category_orders = {}
#
#        # --- 3. Agrupar e contar ---
#        if campo_grupo:
#            dados = queryset.values('ano__ano_valor', campo_grupo).annotate(
#                total_docentes=Count('id', distinct=True)
#            ).order_by('ano__ano_valor')
#        else:
#            dados = queryset.values('ano__ano_valor').annotate(
#                total_docentes=Count('id', distinct=True)
#            ).order_by('ano__ano_valor')
#
#        df = pd.DataFrame(list(dados))
#        if df.empty:
#            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
#
#        # --- 4. Renomear colunas ---
#        df.rename(columns={'ano__ano_valor': 'ano', 'total_docentes': 'Docentes'}, inplace=True)
#
#        # --- 5. Preencher anos faltantes ---
#        todos_anos = pd.DataFrame({'ano': range(ano_inicial, ano_final + 1)})
#
#        if campo_grupo:
#            grupo_plotly = campo_grupo.split('__')[-1]
#            df[grupo_plotly] = df[campo_grupo].fillna('Não informado')
#
#            categorias = df[grupo_plotly].unique()
#            dfs_preenchidos = []
#            for categoria in categorias:
#                df_categoria = df[df[grupo_plotly] == categoria].copy()
#                df_completo = todos_anos.merge(df_categoria, on='ano', how='left')
#                df_completo[grupo_plotly].fillna(categoria, inplace=True)
#                df_completo['Docentes'].fillna(0, inplace=True)
#                dfs_preenchidos.append(df_completo)
#            df = pd.concat(dfs_preenchidos, ignore_index=True)
#
#            # ordenação de categorias
#            if agrupamento == 'sexo':
#                from pandas.api.types import CategoricalDtype
#                cat_type = CategoricalDtype(categories=['M', 'F', 'D'], ordered=True)
#                df[grupo_plotly] = df[grupo_plotly].astype(cat_type)
#                category_orders[grupo_plotly] = ['M', 'F', 'D']
#            else:
#                category_orders[grupo_plotly] = sorted(df[grupo_plotly].unique())
#        else:
#            grupo_plotly = None
#            df = todos_anos.merge(df, on='ano', how='left').fillna(0)
#
#        df.sort_values('ano', inplace=True)
#
#        # --- 6. Criar título ---
#        titulo = f"Total de Docentes por Ano ({ano_inicial}-{ano_final})"
#
#        # --- 7. Criar gráfico ---
#        if tipo_grafico == "barra":
#            fig = px.bar(
#                df,
#                x='ano',
#                y='Docentes',
#                color=grupo_plotly,
#                text='Docentes',
#                title=titulo,
#                category_orders=category_orders,
#                barmode='group'
#            )
#            fig.update_traces(textposition='outside')
#        else:
#            fig = px.line(
#                df,
#                x='ano',
#                y='Docentes',
#                color=grupo_plotly,
#                markers=True,
#                title=titulo,
#                category_orders=category_orders
#            )
#            fig.update_traces(connectgaps=True)
#
#        fig.update_layout(
#            autosize=True,
#            margin=dict(l=40, r=40, t=60, b=40),
#            xaxis_title="Ano",
#            yaxis_title="Número de Docentes",
#            legend_title_text=agrupamento.replace('_', ' ').title() if grupo_plotly else '',
#            xaxis=dict(type='category')
#        )
#
#        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={"responsive": True})



    def _entidades_por_ano(
        self,
        modelo,
        ano_inicial: int,
        ano_final: int,
        agrupamento: str | None,
        mapa_agrupamento: dict,
        filtros: dict,
        tipo_grafico: str,
        titulo_base: str,
    ):
        """
        Função genérica para gerar gráficos de entidades (Docentes, Discentes, etc.) por ano.
        """

        # --- 1. Query base ---
        queryset = modelo.objects.filter(
            ano__ano_valor__gte=ano_inicial,
            ano__ano_valor__lte=ano_final
        )

        # aplicar filtros
        for campo, valor in filtros.items():
            if valor and valor != "total":
                kwargs = {campo: valor}
                queryset = queryset.filter(**kwargs)

        # --- 2. Agrupamento ---
        campo_grupo = mapa_agrupamento.get(agrupamento)
        category_orders = {}

        if campo_grupo:
            dados = queryset.values("ano__ano_valor", campo_grupo).annotate(
                total=Count("id", distinct=True)
            ).order_by("ano__ano_valor")
        else:
            dados = queryset.values("ano__ano_valor").annotate(
                total=Count("id", distinct=True)
            ).order_by("ano__ano_valor")

        df = pd.DataFrame(list(dados))
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"

        df.rename(columns={"ano__ano_valor": "ano", "total": "Total"}, inplace=True)

        # --- 3. Preencher anos faltantes ---
        todos_anos = pd.DataFrame({"ano": range(ano_inicial, ano_final + 1)})

        if campo_grupo:
            grupo_plotly = campo_grupo.split("__")[-1]
            df[grupo_plotly] = df[campo_grupo].fillna("Não informado")

            categorias = df[grupo_plotly].unique()
            dfs_preenchidos = []
            for categoria in categorias:
                df_categoria = df[df[grupo_plotly] == categoria].copy()
                df_completo = todos_anos.merge(df_categoria, on="ano", how="left")
                df_completo[grupo_plotly].fillna(categoria, inplace=True)
                df_completo["Total"].fillna(0, inplace=True)
                dfs_preenchidos.append(df_completo)
            df = pd.concat(dfs_preenchidos, ignore_index=True)

            if agrupamento == "sexo":
                from pandas.api.types import CategoricalDtype
                cat_type = CategoricalDtype(categories=["M", "F", "D"], ordered=True)
                df[grupo_plotly] = df[grupo_plotly].astype(cat_type)
                category_orders[grupo_plotly] = ["M", "F", "D"]
            else:
                category_orders[grupo_plotly] = sorted(df[grupo_plotly].unique())
        else:
            grupo_plotly = None
            df = todos_anos.merge(df, on="ano", how="left").fillna(0)

        df.sort_values("ano", inplace=True)

        # --- 4. Criar título ---
        titulo = f"{titulo_base} ({ano_inicial}-{ano_final})"

        # --- 5. Gerar gráfico ---
        if tipo_grafico == "barra":
            fig = px.bar(
                df,
                x="ano",
                y="Total",
                color=grupo_plotly,
                text="Total",
                title=titulo,
                category_orders=category_orders,
                barmode="group",
            )
            fig.update_traces(textposition="outside")
        else:
            fig = px.line(
                df,
                x="ano",
                y="Total",
                color=grupo_plotly,
                markers=True,
                title=titulo,
                category_orders=category_orders,
            )
            fig.update_traces(connectgaps=True)

        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis_title="Ano",
            yaxis_title=titulo_base,
            legend_title_text=agrupamento.replace("_", " ").title() if grupo_plotly else "",
            xaxis=dict(type="category"),
        )

        return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})


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
            Discente,
            ano_inicial,
            ano_final,
            agrupamento,
            mapa_agrupamento,
            filtros,
            tipo_grafico,
            "Total de Discentes por Ano",
        )

    def docentes_por_ano(
        self,
        ano_inicial=2013,
        ano_final=2024,
        agrupamento="total",    # sexo | nacionalidade | faixa_etaria
        grande_area="total",
        modalidade="total",
        categoria_docente="total",
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
        }

        return self._entidades_por_ano(
            Docente,
            ano_inicial,
            ano_final,
            agrupamento,
            mapa_agrupamento,
            filtros,
            tipo_grafico,
            "Total de Docentes por Ano",
        )
