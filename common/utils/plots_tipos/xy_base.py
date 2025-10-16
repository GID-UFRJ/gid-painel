# common/utils/plots_tipos/xy_base.py

import pandas as pd
from abc import abstractmethod
from .base import BasePlotStrategy
from pandas.api.types import CategoricalDtype

class XYBaseStrategy(BasePlotStrategy):
    """
    CLASSE BASE INTERMEDIÁRIA PARA PLOTS DE EIXOS XY (Barras, Linhas, etc.)

    Contém a lógica de GERAÇÃO DE PLOT que é compartilhada por todos os gráficos
    que usam um eixo X e um eixo Y.

    Deixa o método get_dataframe() como abstrato, pois a forma de obter os dados
    é o que diferencia as estratégias filhas (agregada vs. direta).
    """
    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        """As classes filhas devem implementar sua própria forma de buscar dados."""
        raise NotImplementedError

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
            """
            [VERSÃO FINAL E CORRIGIDA]
            Prepara TODOS os parâmetros, gera o gráfico base e, em seguida, aplica
            TODAS as customizações de trace (texto e hover) de uma só vez.
            """
            if df.empty:
                return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"

            # --- PREPARAÇÃO DOS PARÂMETROS (sem alterações) ---
            agrupamento = self.filtros.get("agrupamento")
            agrupamentos_validos = self.mapeamento.get("agrupamentos", {})
            grupo_plotly = None
            if agrupamento and agrupamento in agrupamentos_validos:
                grupo_plotly = agrupamento.replace('_', ' ').capitalize()

            eixo_x_nome = self.mapeamento["eixo_x_nome"]
            eixo_y_nome = self.mapeamento.get("eixo_y_nome", "Total")

            titulo_base = kwargs.get('titulo_override') or self.mapeamento['titulo_base']
            titulo_final = f"{titulo_base} por {eixo_x_nome}"
            if grupo_plotly:
                 titulo_final = f"{titulo_base} por {grupo_plotly}"

            category_orders_config = {}
            if grupo_plotly:
                custom_order = self.plotter.CATEGORY_ORDERS.get(agrupamento)
                if custom_order:
                    category_orders_config = {grupo_plotly: custom_order}

            params = {
                "x": eixo_x_nome, 
                "y": eixo_y_nome, 
                "color": grupo_plotly, 
                "title": titulo_final,
                "category_orders": category_orders_config,
            }

            # --- LÓGICA DE CUSTOM DATA (PARA O HOVER) ---
            # Preparamos os dados extras ANTES de gerar o gráfico.
            hover_config = self.mapeamento.get("hover_config", {})
            if "custom_data_cols" in hover_config:
                params["custom_data"] = hover_config["custom_data_cols"]

            # --- GERAÇÃO DO GRÁFICO BASE ---
            fig = self.plotter._gerar_grafico(df, tipo_grafico, params, pronto_para_plot=False, **kwargs)

            # ==========================================================
            # APLICAÇÃO DE CUSTOMIZAÇÕES PÓS-GERAÇÃO
            # ==========================================================
        
            # 1. Aplica configurações da "trace" (texto, hover)
            final_trace_config = self.mapeamento.get("trace_config", {}).copy()
            if "template" in hover_config:
                final_trace_config['hovertemplate'] = hover_config["template"]
            if final_trace_config:
                fig.update_traces(**final_trace_config)
                
            # 2. APLICA AS CONFIGURAÇÕES DO EIXO Y (SE EXISTIREM)
            # O operador `**` desempacota o dicionário, passando seus itens como
            # argumentos de palavra-chave para a função. Ex: range=[0, 7.5], tickmode='linear', ...
            yaxes_config = self.mapeamento.get("yaxes_config")
            if yaxes_config:
                fig.update_yaxes(**yaxes_config)
        
            # ==========================================================

            # Renderiza o HTML final
            config = {"responsive": True, "displaylogo": False}
            return fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)