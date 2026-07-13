# common/utils/plots_tipos/hierarquico.py

import pandas as pd
from django.db.models import Count, Sum, Avg
from .base_plot import BasePlotStrategy

class HierarchicalPlotStrategy(BasePlotStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA PLOTS HIERÁRQUICOS (Sunburst, Treemap)

    Sabe como fazer queries agrupando por múltiplos níveis (o 'path') e como
    gerar visualizações que mostram essa estrutura hierárquica.
    """

    def _get_raw_dataframe(self) -> pd.DataFrame:
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

        # DEBUG: Veja isso no seu terminal onde roda o runserver
        print(f"DEBUG SUNBURST: Colunas encontradas: {df.columns.tolist()}")
        print(f"DEBUG SUNBURST: Total de linhas no DF: {len(df)}")

        if df.empty:
            return pd.DataFrame()
        
        # O Plotly exige que todos os caminhos da hierarquia sejam strings válidas.
        # Vamos remover nulos ou substituí-los antes de renomear.
        campos_originais = list(self.mapeamento["grafico_hierarquico_path"].values())
        df = df.dropna(subset=campos_originais) # Remove o que for Nulo nos níveis
        for col in campos_originais:
            df = df[df[col] != ""]

        # Renomeia as colunas do banco para os nomes amigáveis que serão usados no gráfico
        mapa_renomeacao = {v: k for k, v in path_config.items()}
        df.rename(columns=mapa_renomeacao, inplace=True)
        
        # Renomeia a coluna de valor agregado para o nome amigável
        values_nome = self.mapeamento.get("grafico_hierarquico_values_nome", "Total")
        df.rename(columns={'total_agregado': values_nome}, inplace=True)

        return df

    def _build_figure(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
            """
            Implementação para pegar o DataFrame hierárquico e gerar o HTML do gráfico.
            A lógica de cores (alfabética/mapa) já foi resolvida pela BasePlotStrategy
            e injetada aqui através do **kwargs.
            """
            if df.empty:
                return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
    
            # --- Construção dos Parâmetros Específicos para o Gráfico ---
            titulo_override = kwargs.pop('titulo_override', None)
            titulo = titulo_override or self.mapeamento.get("titulo_base", "")
    
            path_list = list(self.mapeamento["grafico_hierarquico_path"].keys())
            
            # Parâmetros estruturais do gráfico hierárquico
            params = {
                "path": path_list, 
                "values": self.mapeamento.get("grafico_hierarquico_values_nome", "Total"),
                "title": titulo,
            }
    
            # =======================================================
            # RECEPÇÃO DAS CORES (A Mágica da Classe Mãe)
            # =======================================================
            # O Cérebro (BasePlotStrategy) já verificou os dados, ordenou alfabeticamente 
            # (ignorando maiúsculas/minúsculas) e gerou o dicionário perfeito. 
            # Nós apenas pegamos da mochila (kwargs) e passamos para o Plotly:
            
            if 'color' in kwargs:
                params['color'] = kwargs.pop('color')
            else:
                # Se por acaso nenhum mapeamento de cor foi pedido, o fallback é o nó raiz
                params['color'] = path_list[0] if path_list else None
    
            if 'color_discrete_map' in kwargs:
                params['color_discrete_map'] = kwargs.pop('color_discrete_map')
            # =======================================================
            
            # Pega a função de plotagem correta (ex: px.sunburst) 
            func = self.plotter.PLOT_FUNCS.get(tipo_grafico)
            if not func:
                raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não suportado.")
    
            # Gera a figura! O Plotly usará as fatias ordenadas por tamanho,
            # mas consultará o nosso mapa blindado para decidir a cor.
            fig = func(df, **params)
            
            # --- Aplica customizações específicas (Sunburst) ---
            if tipo_grafico == 'sunburst':
                fig.update_traces(textinfo="label+percent entry")
                fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
                fig.add_annotation(
                    text="Para retornar ao gráfico original, clique no centro dele.",
                    xref="paper", yref="paper",
                    x=0.5, y=0, # y=0 coloca o texto exatamente na base do círculo
                    yshift=-30,
                    font=dict(size=12, color="#6c757d"),
                    showarrow=False,
                    xanchor="center"
                )
    
            #Retorna o objeto fig
            return fig
