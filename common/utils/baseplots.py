# common/utils/baseplots.py
from django.db.models import Count, Sum, Avg, Max, Min
import pandas as pd
import plotly.express as px

class BasePlots:
    '''
    Classe base auxiliar relacionadas à plotagem 
    Engloba tanto a geração de gráficos quanto a recuperação dos dados para o mesmo
    (Se a classe crescer demais, podemos separar essas duas funcionalidades em classes distintas)
    '''

    #Cada app vai ter sua(s) própria(s) subclasse(s) e mapeamentos de filtros e agrupamentos
    @property
    def MAPEAMENTOS(self):
        raise NotImplementedError("Subclasses devem implementar o atributo MAPEAMENTOS")

    def _get_mapeamento(self, tipo_entidade):
        mapeamento = self.MAPEAMENTOS.get(tipo_entidade)  # Usa o property
        if not mapeamento:
            raise ValueError(f"Tipo de entidade '{tipo_entidade}' não encontrado")
        return mapeamento

    # Defaults para ordenação de categorias
    CATEGORY_ORDERS = {
        "sexo": ["M", "F", "D"],
        # você pode adicionar outros defaults aqui
    }

    # Funções de plot
    PLOT_FUNCS = {
        "barra": px.bar,
        "linha": px.line,
    }

    # Configurações específicas de cada gráfico
    PLOT_CONFIGS = {
        "barra": {"text": "Total", "barmode": "group"},
        "linha": {"markers": True},
    }


    def _gerar_grafico(self, df: pd.DataFrame, tipo_grafico: str, params: dict):
        func = self.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não suportado.")

        plot_args = self.PLOT_CONFIGS.get(tipo_grafico, {}).copy()
        plot_args.update({k: v for k, v in params.items() if v is not None})

        fig = func(df, **plot_args)

        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis_title=params.get("x", ""),
            yaxis_title=params.get("y", ""),
            legend_title_text=params.get("color", ""),
            xaxis=dict(type="category"),
        )

        if tipo_grafico == "barra":
            fig.update_traces(textposition="outside")
        else:
            fig.update_traces(connectgaps=True)

        return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})


    def _entidades_por_ano(
        self,
        tipo_entidade: str,
        ano_inicial: int,
        ano_final: int,
        tipo_grafico: str,
        agrupamento: str | None,
        filtros_selecionados: dict,
        **kwargs,
    ):
        """
        Função genérica e refatorada para gerar gráficos por ano usando MAPEAMENTOS.

        Args:
            tipo_entidade (str): A chave do MAPEAMENTOS a ser usada (ex: 'discentes').
            ano_inicial (int): Ano inicial do período.
            ano_final (int): Ano final do período.
            tipo_grafico (str): 'barra' ou 'linha'.
            agrupamento (str | None): Chave do agrupamento a ser aplicado (ex: 'sexo').
            filtros_selecionados (dict): Dicionário com os filtros a serem aplicados (ex: {'situacao': 'Ativo'}).
            **kwargs: Opções extras como 'agregacao', 'distinct', 'category_orders_override'.
        """
        # --- 1. Obter configurações do mapeamento ---
        mapeamento = self._get_mapeamento(tipo_entidade)
        modelo = mapeamento["modelo"]
        mapa_agrupamento = mapeamento["agrupamentos"]
        mapa_filtros = mapeamento["filtros"]
        titulo_base = mapeamento["titulo_base"]
        
        # Obtém configurações com valores default
        campo_agregacao = mapeamento.get("campo_agregacao", "id")
        agregacao = kwargs.get('agregacao', 'count')
        distinct = kwargs.get('distinct', True if "id" in campo_agregacao else False)
        category_orders_override = kwargs.get('category_orders_override')

        # --- 2. Query base e Filtros ---
        queryset = modelo.objects.filter(
            ano__ano_valor__gte=ano_inicial,
            ano__ano_valor__lte=ano_final
        )
        
        # Aplica filtros com base no mapeamento
        for chave_filtro, valor in filtros_selecionados.items():
            if valor and valor.lower() != "total":
                campo_real = mapa_filtros.get(chave_filtro)
                if campo_real:
                    queryset = queryset.filter(**{campo_real: valor})

        # --- 3. Definir agregação ---
        if isinstance(agregacao, str):
            agg_map = {
                "count": Count(campo_agregacao, distinct=distinct),
                "sum": Sum(campo_agregacao),
                "avg": Avg(campo_agregacao),
            }
            agg_func = agg_map.get(agregacao.lower())
            if not agg_func:
                raise ValueError(f"Agregação '{agregacao}' não suportada.")
        else:
            agg_func = agregacao # Permite passar um objeto de agregação customizado

        # --- 4. Agrupamento ---
        campo_grupo = mapa_agrupamento.get(agrupamento)
        
        if campo_grupo:
            dados = queryset.values("ano__ano_valor", campo_grupo).annotate(Total=agg_func).order_by("ano__ano_valor")
        else:
            dados = queryset.values("ano__ano_valor").annotate(Total=agg_func).order_by("ano__ano_valor")
        
        df = pd.DataFrame(list(dados))
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"

        df.rename(columns={"ano__ano_valor": "Ano"}, inplace=True)

        # --- 5. Preencher anos faltantes e processar dados ---
        todos_anos = pd.DataFrame({"Ano": range(ano_inicial, ano_final + 1)})
        category_orders = {}
        grupo_plotly = None

        if campo_grupo:
            grupo_plotly = agrupamento # Usar o nome amigável para o gráfico
            df.rename(columns={campo_grupo: grupo_plotly}, inplace=True)
            df[grupo_plotly] = df[grupo_plotly].fillna("Não informado")

            # Pivota e preenche para garantir que todos os anos apareçam para todas as categorias
            df_pivot = df.pivot_table(index='Ano', columns=grupo_plotly, values='Total', fill_value=0)
            df_pivot = df_pivot.reindex(range(ano_inicial, ano_final + 1), fill_value=0)
            df = df_pivot.reset_index().melt(id_vars='Ano', value_name='Total', var_name=grupo_plotly)

            # --- Ordenação de categorias ---
            final_category_orders = self.CATEGORY_ORDERS.copy()
            if category_orders_override:
                final_category_orders.update(category_orders_override)

            if grupo_plotly in final_category_orders:
                from pandas.api.types import CategoricalDtype
                cat_dtype = CategoricalDtype(categories=final_category_orders[grupo_plotly], ordered=True)
                df[grupo_plotly] = df[grupo_plotly].astype(cat_dtype)
            
            df.sort_values(by=['Ano', grupo_plotly], inplace=True)

        else: # Sem agrupamento
            df = todos_anos.merge(df, on="Ano", how="left").fillna(0)
            df.sort_values("Ano", inplace=True)

        # --- 6. Título e Geração do Gráfico ---
        titulo = f"{titulo_base} por Ano ({ano_inicial}-{ano_final})"
        if agrupamento:
            titulo = f"{titulo_base} por {agrupamento.replace('_', ' ').capitalize()} ({ano_inicial}-{ano_final})"

        params = {
            "x": "Ano",
            "y": "Total",
            "color": grupo_plotly,
            "title": titulo,
        }

        return self._gerar_grafico(df, tipo_grafico, params)
