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
    - Eixo Y Invertido (Padrão para Rankings: 1 é melhor que 100).
    - Suporte a filtro explícito de 'Sem ODS' (Geral).
    - Se Min == Max: Plota linha sólida única.
    - Se Min != Max: Plota faixa (Melhor=Sólida, Pior=Pontilhada).
    - Legendas informativas estáticas.
    - Tooltips individuais limpos.
    """

    def _get_raw_dataframe(self) -> pd.DataFrame:
        """
        Busca os dados considerando dois campos Y (min e max) em vez de um.
        Trata explicitamente o caso de filtro 'None'/'Empty' para buscar campos nulos.
        Aplica filtros padrão do mapeamento para evitar duplicidade de nomes (QS Acadêmico vs QS Sustentabilidade).
        """
        filtros_modificados = self.filtros.copy()

        # --- 1. MERGE DE DEFAULTS ---
        defaults = self.mapeamento.get("filtros_padrao", {})
        for chave, valor in defaults.items():
            if chave not in filtros_modificados:
                filtros_modificados[chave] = valor

        # --- 2. BLINDAGEM DO ODS ---
        # Tenta pegar o valor de qualquer jeito que o motor possa ter enviado
        valor_ods = filtros_modificados.get('ods__codigo') or filtros_modificados.get('ods')

        # Se for vazio, string vazia, ou "None", nós padronizamos para None
        if valor_ods in ['None', '', None]:
            valor_ods = None
            # Limpamos o dicionário para a query base não tentar filtrar por vazio
            filtros_modificados.pop('ods__codigo', None)
            filtros_modificados.pop('ods', None)

        # --- 3. QUERY BASE ---
        queryset, _, _ = self.plotter._get_base_queryset(
            self.mapeamento['__tipo_entidade__'], 
            filtros_modificados
        )

        # --- 4. A CURA DO ZIGUE-ZAGUE ---
        # Se NÃO tem um ODS selecionado, nós TEMOS que filtrar só os nulos (Visão Geral),
        # caso contrário ele plota os 17 ODSs no mesmo ano formando linhas verticais.
        if not valor_ods:
            queryset = queryset.filter(ods__isnull=True)

        # --- 5. PREPARAÇÃO DOS CAMPOS (O resto continua igual...) ---
        eixo_x = self.mapeamento["eixo_x_campo"]
        y_min = self.mapeamento["eixo_y_min"]
        y_max = self.mapeamento["eixo_y_max"]

        campos = [eixo_x, y_min, y_max]

        agrupamento = self.filtros.get("agrupamento")
        campo_grupo = None

        if agrupamento:
            campo_grupo = self.mapeamento["agrupamentos"].get(agrupamento)
            if campo_grupo:
                campos.append(campo_grupo)

        # --- 6. EXECUÇÃO E DATAFRAME ---
        # Adicionamos distinct() para evitar duplicatas puras de banco, caso existam
        dados = queryset.values(*campos).order_by(eixo_x).distinct()
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        # Renomeação padronizada
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

    def _build_figure(self, df: pd.DataFrame, **kwargs) -> str:
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"

        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        titulo = kwargs.get('title') or self.mapeamento.get("titulo_base", "")

        fig = go.Figure()
        
        palette = cycle(px.colors.qualitative.Plotly)
        grupos = df['grupo'].unique()

        for grupo, cor in zip(grupos, palette):
            sub_df = df[df['grupo'] == grupo].sort_values(by=eixo_x_nome)

            # Verifica se é um ranking exato (Min == Max em todos os pontos)
            eh_ranking_exato = sub_df['y_min'].equals(sub_df['y_max'])

            if eh_ranking_exato:
                # --- CENÁRIO A: Linha Única (Posição Exata) ---
                fig.add_trace(go.Scatter(
                    x=sub_df[eixo_x_nome],
                    y=sub_df['y_min'],
                    mode='lines+markers',
                    line=dict(color=cor, shape='spline', width=3),
                    
                    showlegend=True,
                    # Se houver múltiplos grupos (comparação), usa o nome do grupo. 
                    # Se for ranking único, usa "Posição" ou o nome do grupo.
                    name=str(grupo),
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
                    
                    # Visual: Pontilhada
                    line=dict(color=cor, shape='spline', width=3, dash='dot'), 
                    
                    showlegend=True,
                    name="Pior Posição", 
                    legendgroup=str(grupo),
                    
                    hovertemplate="Pior Posição: %{y}<extra></extra>",
                ))

                # 2. MELHOR POSIÇÃO (Mínimo Numérico) -> CONTÍNUA + PREENCHIMENTO
                fig.add_trace(go.Scatter(
                    x=sub_df[eixo_x_nome],
                    y=sub_df['y_min'],
                    mode='lines+markers',
                    
                    # Visual: Sólida
                    line=dict(color=cor, shape='spline', width=3, dash='solid'), 
                    
                    fill='tonexty', 
                    fillcolor=self._hex_to_rgba(cor, 0.2),
                    
                    showlegend=True,
                    name="Melhor Posição",
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
            
            # Tooltips individuais (sem ícones agrupados)
            hovermode="x",
            
            # Distância (em px) para ativar o "imã" do spike. 
            # Deve ficar aqui no root do layout, não dentro de xaxis.
            spikedistance=30,

            # --- CONFIGURAÇÃO DO EIXO X (Spikes/Guias) ---
            xaxis=dict(
                type='category',
                showspikes=True,      # Ativa a linha guia
                spikemode='across',   # Linha atravessa o gráfico
                spikesnap='data',     # A linha "gruda" no dado (ano), não segue o mouse no vazio
                
                showline=True, 
                showgrid=True
            ),
            # ---------------------------------------------
            
            # Legenda Estática
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                itemclick=False,       # Desativa clique simples
                itemdoubleclick=False  # Desativa clique duplo
            ),

            # Inverte o eixo Y se configurado (Rankings: 1 no topo)
            yaxis=dict(autorange="reversed") if self.mapeamento.get('eixo_y_invertido', False) else {}
        )

        config = {"responsive": True, "displaylogo": False}
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)

    def _hex_to_rgba(self, hex_color, alpha):
        """Método utilitário para converter cor Hex para RGBA com transparência."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"rgba({r},{g},{b},{alpha})"
        return hex_color