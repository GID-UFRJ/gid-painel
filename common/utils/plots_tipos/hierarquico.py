# common/utils/plots_tipos/hierarquico.py

import pandas as pd
from django.db.models import Count, Sum, Avg
from .base import BasePlotStrategy # Importa a classe base do mesmo pacote

class HierarchicalPlotStrategy(BasePlotStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA PLOTS HIERÁRQUICOS (Sunburst, Treemap)

    Sabe como fazer queries agrupando por múltiplos níveis (o 'path') e como
    gerar visualizações que mostram essa estrutura hierárquica.
    """

    def get_dataframe(self) -> pd.DataFrame:
        """
        Implementação para buscar e preparar dados para um gráfico hierárquico.
        """
        # Usa o método auxiliar do "artesão" (BasePlots) para obter o queryset inicial
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        # Extrai as configurações específicas de hierarquia da "receita" (mapeamento)
        try:
            path_config = self.mapeamento["grafico_hierarquico_path"]
            values_campo = self.mapeamento["grafico_hierarquico_values_campo"]
            agregacao_str = self.mapeamento.get("grafico_hierarquico_agregacao", "count")
        except KeyError as e:
            raise KeyError(f"Mapeamento '{self.mapeamento['__tipo_entidade__']}' não possui a chave obrigatória para gráficos hierárquicos: {e}")

        # Constrói a função de agregação do Django
        distinct = 'distinct' in agregacao_str.lower()
        agregacao_base = agregacao_str.split('_')[0]
        agg_map = {"count": Count(values_campo, distinct=distinct), "sum": Sum(values_campo), "avg": Avg(values_campo)}
        agg_func = agg_map.get(agregacao_base.lower())
        if not agg_func:
            raise ValueError(f"Agregação '{agregacao_base}' não suportada.")

        # Executa a query, agrupando por todos os campos no 'path'
        campos_do_path = list(path_config.values())
        dados = queryset.values(*campos_do_path).annotate(total_agregado=agg_func).order_by()
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        # Renomeia as colunas do banco para os nomes amigáveis que serão usados no gráfico
        mapa_renomeacao = {v: k for k, v in path_config.items()}
        df.rename(columns=mapa_renomeacao, inplace=True)
        
        # Renomeia a coluna de valor agregado para o nome amigável
        values_nome = self.mapeamento.get("grafico_hierarquico_values_nome", "Total")
        df.rename(columns={'total_agregado': values_nome}, inplace=True)

        return df

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        """
        Implementação para pegar o DataFrame hierárquico e gerar o HTML do gráfico.
        """
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"

        # --- Construção dos Parâmetros Específicos para o Gráfico ---
        titulo_override = kwargs.get('titulo_override')
        titulo = titulo_override or self.mapeamento.get("titulo_base", "")
        
        # Parâmetros para gráficos hierárquicos são diferentes (path, values)
        params = {
            "path": list(self.mapeamento["grafico_hierarquico_path"].keys()), # Usa os nomes amigáveis
            "values": self.mapeamento.get("grafico_hierarquico_values_nome", "Total"),
            "title": titulo,
        }
        
        # Pega a função de plotagem correta (ex: px.sunburst) do "artesão" (BasePlots)
        func = self.plotter.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não suportado.")

        fig = func(df, **params)
        
        # --- Aplica customizações específicas para certos tipos de gráficos ---
        if tipo_grafico == 'sunburst':
            fig.update_traces(textinfo="label+percent entry")
            fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

        # Renderiza o HTML final
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})