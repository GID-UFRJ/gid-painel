import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html

def retornar_plotly_ou_html(retornar_plotly, fig):
    if not retornar_plotly:
        fig = to_html(fig, full_html=False) #Modifica plotly para html se parametro for False

    return fig

def grafico_linha_plotly(
    df,  
    x: str,  
    y: str,  #
    grupo: str | None = None,  
    titulo: str = '',
    titulo_eixo_x: str = '',
    titulo_eixo_y: str = '',
    adicionar_rotulo_dados: bool = True,
    tamanho_rotulo_dados: int = 20,
    largura: int = 500,
    altura: int = 500,
    inverter_eixo_y: bool = False,
    y0: int = 0,
    retornar_plotly: bool = False,
    **kwargs,  # Adicionado para aceitar argumentos plotly adicionais
    ):
    """Gráfico de linha com suporte a agrupamento via Plotly Express.
    
    Args:
        df: DataFrame contendo os dados
        x: Nome da coluna para o eixo X
        y: Nome da coluna para o eixo Y
        grupo: Nome da coluna para agrupamento (opcional)
        **kwargs: Argumentos adicionais passados para px.line
    """
    range_y = [y0, df[y].max() * 1.2] if not inverter_eixo_y else [df[y].max() * 1.2, y0]

    fig = px.line(
        df,
        x=x,
        y=y,
        color=grupo,
        markers=True,
        text=y if adicionar_rotulo_dados else None,
        **kwargs
    )

    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        xaxis_title=titulo_eixo_x,
        yaxis_title=titulo_eixo_y,
        width=largura,
        height=altura,
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgrey', range=range_y),
        xaxis=dict(showgrid=False),
    )

    if adicionar_rotulo_dados:
        fig.update_traces(
            textposition='top center',
            textfont=dict(size=tamanho_rotulo_dados, color='blue', weight='bold')
        )

    return retornar_plotly_ou_html(retornar_plotly, fig)


def grafico_barra_plotly(
    df,
    x: str,
    y: str,
    titulo: str = '',
    grupo: str | None = None,
    titulo_eixo_x: str = '',
    titulo_eixo_y: str = '',
    adicionar_rotulo_dados: bool = True,
    tamanho_rotulo_dados: int = 20,
    largura: int = 500,
    altura: int = 500,
    retornar_plotly: bool = False,
    **kwargs,  # Captura todos os outros argumentos do plotly
):
    """Cria um gráfico de barras com Plotly Express, suportando agrupamento e rótulos."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=grupo,
        title=titulo,
        text=y if adicionar_rotulo_dados else None,
        **kwargs # Manda argumentos adicionais para a função plotly
    )

    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        xaxis_title=titulo_eixo_x,
        yaxis_title=titulo_eixo_y,
        width=largura,
        height=altura,
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        xaxis=dict(showgrid=False),
    )

    if adicionar_rotulo_dados:
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            textfont=dict(size=tamanho_rotulo_dados, color='black'),
        )

    return retornar_plotly_ou_html(retornar_plotly, fig)


def grafico_barra_plotly2(
    df,
    x: str,
    y: str,
    titulo: str | None = '',
    titulo_eixo_x: str | None = '',
    titulo_eixo_y: str | None = '',
    tamanho_rotulo_dados: str | None = 20,
    largura: int | None = 500,
    altura: int | None = 500,
    orientacao: str | None = 'v',
    retornar_plotly: bool = False,
    **kwargs,  # Captura todos os outros argumentos do plotly
):
    """Cria um gráfico de barras horizontal ou vertical com Plotly Express."""
    fig = px.bar(df, x, y, 
                 title=titulo, 
                 width=largura, 
                 height=altura, 
                 text_auto=True, 
                 orientation=orientacao,
                **kwargs,  # Captura todos os outros argumentos do plotly
                )

    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        xaxis_title=titulo_eixo_x,
        yaxis_title=titulo_eixo_y,
        plot_bgcolor='white',
        yaxis=dict(
            showgrid=True if orientacao == 'v' else False,
            gridcolor='lightgrey',
            gridwidth=0.001,
            griddash='dot'
        ),
        xaxis=dict(
            showgrid=True if orientacao != 'v' else False,
            gridcolor='lightgrey',
            gridwidth=0.001,
            griddash='dot'
        )
    )

    fig.update_traces(
        textposition='outside',
        textfont_weight='bold',
        textfont=dict(size=tamanho_rotulo_dados, color='blue')
    )

    if orientacao == 'v':
        y_max = max(fig.data[0].y)
        fig.update_yaxes(range=[0, y_max * 1.15])
    else:
        x_max = max(fig.data[0].x)
        fig.update_xaxes(range=[0, x_max * 1.15])

    return retornar_plotly_ou_html(retornar_plotly, fig)


def grafico_linha_plotly2(
    x: list,
    y: list,
    titulo: str | None = '',
    titulo_eixo_x: str | None = '',
    titulo_eixo_y: str | None = '',
    adicionar_rotulo_dados: bool | None = True,
    tamanho_rotulo_dados: str | None = 20,
    largura: int | None = 500,
    altura: int | None = 500,
    inverter_eixo_y: bool | None = False,
    y0: int | None = 0,
    retornar_plotly: bool = False,
    **kwargs,
):
    """Cria um gráfico de linha com Plotly Graph Objects."""
    y_series = pd.Series(y)
    
    range_y = [y0, y_series.max() * 1.2] if not inverter_eixo_y else [y_series.max() * 1.2, y0]

    modo = 'markers+lines'
    rotulo_dados = None
    if adicionar_rotulo_dados:
        modo = 'markers+text+lines'
        rotulo_dados = y

    fig = go.Figure(layout=go.Layout(width=largura, height=altura))
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            line=dict(color=None, width=6),
            marker=dict(symbol='circle', size=20, color=None),
            mode=modo,
            text=rotulo_dados,
            textposition='top center',
            line_shape='spline',
            **kwargs,
        )
    )

    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        xaxis_title=titulo_eixo_x,
        yaxis_title=titulo_eixo_y,
        plot_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.001, griddash='dot', range=range_y),
        xaxis=dict(showgrid=False, gridcolor='lightgrey', gridwidth=2)
    )

    fig.update_traces(
        textfont=dict(size=tamanho_rotulo_dados, color='blue', weight='bold')
    )

    return retornar_plotly_ou_html(retornar_plotly, fig)

def grafico_pizza(titulo, **arg_pie):
    pass

def grafico_kpi(valor: int, rotulo: str, exibir_percentual=False):
    pass
