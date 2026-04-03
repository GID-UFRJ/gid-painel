# common/utils/plots_tipos/topn.py

import pandas as pd
from django.db.models import Count, Sum
from .base_plot import BasePlotStrategy

 ##Idealmente, seria bom fazer essa classe herdar de XYBase em vez de BasePlot
class TopNStrategy(BasePlotStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA GRÁFICOS DO TIPO "TOP N"

    Sabe como fazer queries que ordenam por um valor agregado e pegam os N
    primeiros resultados para exibição em um gráfico de barras.
    """

    def get_dataframe(self) -> pd.DataFrame:
        """
        Busca e prepara os dados para um gráfico Top N.
        """
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        try:
            campo_categoria = self.mapeamento["ranking_campo_categoria"]
            campo_valor = self.mapeamento.get("ranking_campo_valor", "id")
            agregacao_str = self.mapeamento.get("ranking_agregacao", "count")
            limite_padrao = self.mapeamento.get("ranking_limite_padrao", 10)
        except KeyError as e:
            raise KeyError(f"Mapeamento '{self.mapeamento['__tipo_entidade__']}' não possui a chave obrigatória para gráficos Top N: {e}")

        distinct = 'distinct' in agregacao_str.lower()
        agregacao_base = agregacao_str.split('_')[0]
        agg_map = {"count": Count(campo_valor, distinct=distinct), "sum": Sum(campo_valor)}
        agg_func = agg_map.get(agregacao_base)

        limite = int(self.filtros.get('limite', limite_padrao))

        dados = queryset.values(campo_categoria).annotate(total=agg_func).order_by('-total')[:limite]
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()
        
        # Invertemos e resetamos o índice para garantir o desenho correto do Plotly Express
        df = df.iloc[::-1].reset_index(drop=True)

        eixo_x_nome = self.mapeamento.get("eixo_x_nome", "Total")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", campo_categoria)

        df.rename(columns={
                    "total": eixo_x_nome,
                    campo_categoria: eixo_y_nome
                }, inplace=True)

        return df

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        """
        Gera o HTML do gráfico Top N, agora com suporte nativo ao hover_config!
        """
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"

        eixo_x_nome = self.mapeamento.get("eixo_x_nome", "Total")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", self.mapeamento["ranking_campo_categoria"])

        params = {
            "x": eixo_x_nome,
            "y": eixo_y_nome,
            "orientation": 'h', 
            "title": kwargs.get('titulo_override') or self.mapeamento.get("titulo_base", ""),
            "text": eixo_x_nome, 
        }

        # --- 1. LÓGICA DE CUSTOM DATA (Copiada do XY Base) ---
        hover_config = self.mapeamento.get("hover_config", {})
        if "custom_data_cols" in hover_config:
            params["custom_data"] = hover_config["custom_data_cols"]

        # --- 2. GERAÇÃO DO GRÁFICO BASE (pronto_para_plot=False) ---
        fig = self.plotter._gerar_grafico(df, tipo_grafico, params, pronto_para_plot=False, **kwargs)

        # ==========================================================
        # 3. APLICAÇÃO DE CUSTOMIZAÇÕES PÓS-GERAÇÃO
        # ==========================================================
        final_trace_config = self.mapeamento.get("trace_config", {}).copy()
        
        if "template" in hover_config:
            final_trace_config['hovertemplate'] = hover_config["template"]
            
        if final_trace_config:
            fig.update_traces(**final_trace_config)
            
        yaxes_config = self.mapeamento.get("yaxes_config")
        if yaxes_config:
            fig.update_yaxes(**yaxes_config)
        # ==========================================================

        # 4. Renderiza o HTML final
        config = {"responsive": True, "displaylogo": False}
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)