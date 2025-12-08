# common/utils/plots_tipos/faixa.py

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from itertools import cycle
from .xy_base import XYBaseStrategy

class RangeAreaStrategy(XYBaseStrategy):
    """
    Estratégia para gerar gráficos de Faixa (Ribbon/Range Area).
    
    Características:
    - Eixo Y Invertido.
    - Se Min != Max: Exibe legendas explícitas "Melhor Posição" e "Pior Posição".
    - Legenda estática (cliques desativados).
    """

    def get_dataframe(self) -> pd.DataFrame:
        # 1. Query
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)

        eixo_x = self.mapeamento["eixo_x_campo"]
        y_min = self.mapeamento["eixo_y_min"]
        y_max = self.mapeamento["eixo_y_max"]
        
        campos = [eixo_x, y_min, y_max]
        
        # 2. Agrupamento (opcional)
        agrupamento = self.filtros.get("agrupamento")
        campo_grupo = None
        
        if agrupamento:
            campo_grupo = self.mapeamento["agrupamentos"].get(agrupamento)
            if campo_grupo:
                campos.append(campo_grupo)

        # 3. Execução
        dados = queryset.values(*campos).order_by(eixo_x)
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        # 4. Renomeação
        rename_map = {
            eixo_x: self.mapeamento["eixo_x_nome"],
            y_min: "y_min",
            y_max: "y_max"
        }
        
        if campo_grupo:
            rename_map[campo_grupo] = "grupo"
        else:
            df['grupo'] = self.mapeamento.get('titulo_base', 'Ranking')

        df.rename(columns=rename_map, inplace=True)
        return df

    def generate_plot(self, df: pd.DataFrame, **kwargs) -> str:
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"

        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        titulo = kwargs.get('title') or self.mapeamento.get("titulo_base", "")

        fig = go.Figure()
        
        palette = cycle(px.colors.qualitative.Plotly)
        grupos = df['grupo'].unique()

        for grupo, cor in zip(grupos, palette):
            sub_df = df[df['grupo'] == grupo].sort_values(by=eixo_x_nome)

            eh_ranking_exato = sub_df['y_min'].equals(sub_df['y_max'])

            if eh_ranking_exato:
                # --- CENÁRIO A: Linha Única ---
                fig.add_trace(go.Scatter(
                    x=sub_df[eixo_x_nome],
                    y=sub_df['y_min'],
                    mode='lines+markers',
                    line=dict(color=cor, shape='spline', width=3),
                    
                    showlegend=True,
                    name="Posição", # Nome do ranking se for linha única
                    legendgroup=str(grupo),
                    
                    hovertemplate="Posição: %{y}<extra></extra>",
                ))

            else:
                # --- CENÁRIO B: Faixa (Range) ---
                
                # 1. PIOR POSIÇÃO (Máximo Numérico) -> PONTILHADA
                fig.add_trace(go.Scatter(
                    x=sub_df[eixo_x_nome],
                    y=sub_df['y_max'],
                    mode='lines+markers',
                    
                    line=dict(color=cor, shape='spline', width=3, dash='dot'), 
                    
                    showlegend=True,
                    name="Pior Posição", # <--- ISSO CORRIGE O "trace 1"
                    legendgroup=str(grupo),
                    
                    hovertemplate="Pior Posição: %{y}<extra></extra>",
                ))

                # 2. MELHOR POSIÇÃO (Mínimo Numérico) -> CONTÍNUA
                fig.add_trace(go.Scatter(
                    x=sub_df[eixo_x_nome],
                    y=sub_df['y_min'],
                    mode='lines+markers',
                    
                    line=dict(color=cor, shape='spline', width=3, dash='solid'), 
                    
                    fill='tonexty', 
                    fillcolor=self._hex_to_rgba(cor, 0.2),
                    
                    showlegend=True,
                    name="Melhor Posição", # <--- ISSO CORRIGE O "trace 2"
                    legendgroup=str(grupo),
                    
                    hovertemplate="Melhor Posição: %{y}<extra></extra>",
                    customdata=sub_df['y_max']
                ))

        # Configuração do Layout
        fig.update_layout(
            title=titulo,
            xaxis_title=eixo_x_nome,
            yaxis_title=self.mapeamento.get("eixo_y_nome", "Posição"),
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            
            # --- MUDANÇA AQUI ---
            # De: hovermode="x unified"
            # Para: hovermode="x"
            # Isso cria tooltips individuais e remove a lista com ícones
            hovermode="x",
            spikedistance=30,
            # --------------------

            # Opcional: Adiciona uma linha vertical guia (Spike) para facilitar a leitura
            # já que removemos o 'unified' que tinha a linha por padrão.
            xaxis=dict(
                showspikes=True, 
                spikemode='across', 
                spikesnap='data', 
                showline=True, 
                showgrid=True
            ),
            
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                itemclick=False,
                itemdoubleclick=False
            ),

            yaxis=dict(autorange="reversed") if self.mapeamento.get('eixo_y_invertido', False) else {}
        )

        config = {"responsive": True, "displaylogo": False}
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)

    def _hex_to_rgba(self, hex_color, alpha):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"rgba({r},{g},{b},{alpha})"
        return hex_color