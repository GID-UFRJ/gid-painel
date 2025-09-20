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
        modelo,
        ano_inicial: int,
        ano_final: int,
        agrupamento: str | None,
        mapa_agrupamento: dict,
        filtros: dict,
        tipo_grafico: str,
        titulo_base: str,
        campo_agregacao: str = "id",
        agregacao: str | object = "count",
        distinct: bool = False,
        category_orders_override: dict | None = None,  # permite sobrescrever defaults
    ):
        """
        Função genérica para gerar gráficos por ano.
        """
        # --- 1. Query base ---
        queryset = modelo.objects.filter(
            ano__ano_valor__gte=ano_inicial,
            ano__ano_valor__lte=ano_final
        )

        for campo, valor in filtros.items():
            if valor and valor != "total":
                queryset = queryset.filter(**{campo: valor})

        # --- 2. Definir agregação ---
        if isinstance(agregacao, str):
            agg_map = {
                "count": Count(campo_agregacao, distinct=distinct),
                "sum": Sum(campo_agregacao),
                "avg": Avg(campo_agregacao),
                "max": Max(campo_agregacao),
                "min": Min(campo_agregacao),
            }
            agg_func = agg_map.get(agregacao.lower())
            if not agg_func:
                raise ValueError(f"Agregação '{agregacao}' não suportada.")
        else:
            agg_func = agregacao

        # --- 3. Agrupamento ---
        campo_grupo = mapa_agrupamento.get(agrupamento)
        category_orders = {}

        if campo_grupo:
            dados = queryset.values("ano__ano_valor", campo_grupo).annotate(total=agg_func).order_by("ano__ano_valor")
        else:
            dados = queryset.values("ano__ano_valor").annotate(total=agg_func).order_by("ano__ano_valor")

        df = pd.DataFrame(list(dados))
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"

        df.rename(columns={"ano__ano_valor": "ano", "total": "Total"}, inplace=True)

        # --- 4. Preencher anos faltantes ---
        todos_anos = pd.DataFrame({"ano": range(ano_inicial, ano_final + 1)})

        if campo_grupo:
            grupo_plotly = campo_grupo.split("__")[-1]
            df[grupo_plotly] = df[campo_grupo].fillna("Não informado")

            dfs_preenchidos = []
            for categoria in df[grupo_plotly].unique():
                df_cat = df[df[grupo_plotly] == categoria].copy()
                df_completo = todos_anos.merge(df_cat, on="ano", how="left")
                df_completo[grupo_plotly].fillna(categoria, inplace=True)
                df_completo["Total"].fillna(0, inplace=True)
                dfs_preenchidos.append(df_completo)
            df = pd.concat(dfs_preenchidos, ignore_index=True)

            # --- 5. Ordenação de categorias ---
            final_category_orders = self.CATEGORY_ORDERS.copy()
            if category_orders_override:
                final_category_orders.update(category_orders_override)

            if grupo_plotly in final_category_orders:
                from pandas.api.types import CategoricalDtype
                df[grupo_plotly] = df[grupo_plotly].astype(
                    CategoricalDtype(categories=final_category_orders[grupo_plotly], ordered=True)
                )
                category_orders[grupo_plotly] = final_category_orders[grupo_plotly]
            else:
                category_orders[grupo_plotly] = sorted(df[grupo_plotly].unique())
        else:
            grupo_plotly = None
            df = todos_anos.merge(df, on="ano", how="left").fillna(0)

        df.sort_values("ano", inplace=True)

        # --- 6. Título ---
        titulo = f"{titulo_base} ({ano_inicial}-{ano_final})"

        # --- 7. Chamar gerador de gráfico ---
        params = {
            "x": "ano",
            "y": "Total",
            "color": grupo_plotly,
            "title": titulo,
            "category_orders": category_orders,
        }

        return self._gerar_grafico(df, tipo_grafico, params)