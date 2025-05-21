import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html


def grafico_linha(df, array_x: str, array_y: str, titulo:str, grupo:str):
    pass

def grafico_barra_plotly(df, x: str, y: str, titulo:str | None='', grupo:str | None=''):
    fig = px.bar(df, x, y, title=titulo)
    fig = to_html(fig, full_html=False)
    return(fig)

def grafico_barra_plotly2(
    df, 
    x: str, 
    y: str, 
    titulo:str | None='', 
    titulo_eixo_x: str | None='', 
    titulo_eixo_y:str | None='', 
    tamanho_rotulo_dados:str | None=20,
    largura:int | None = 500,
    altura:int | None = 500, 
    orientacao:str | None='v'):
    
    fig = px.bar(df, x, y, title=titulo, width=largura, height=altura, text_auto=True, orientation=orientacao)
    fig.update_layout(
        title={'x': 0.5,'xanchor': 'center'}, 
        xaxis_title=titulo_eixo_x, 
        yaxis_title=titulo_eixo_y,
        plot_bgcolor='white',
        yaxis=dict(
            showgrid=True if orientacao=='v' else False,
            gridcolor='lightgrey',
            gridwidth=2            
        ),
        xaxis=dict(
            showgrid= True if orientacao!='v' else False,
            gridcolor='lightgrey',
            gridwidth=2            
        )
    )
    fig.update_traces(
        textposition='outside',
        textfont_weight='bold',
        textfont=dict(
            size=tamanho_rotulo_dados,
            color='blue'
        )
    )
    
    if orientacao=='v':
        y_max = max(fig.data[0].y)
        fig.update_yaxes(range=[0, y_max * 1.15])
    else:
        x_max = max(fig.data[0].x)
        fig.update_xaxes(range=[0, x_max * 1.15])
    fig = to_html(fig, full_html=False)
    return(fig)

def grafico_linha_plotly2(
    x: str, 
    y: str, 
    titulo:str | None='', 
    titulo_eixo_x: str | None='', 
    titulo_eixo_y:str | None='', 
    tamanho_rotulo_dados:str | None=20,
    largura:int | None = 500,
    altura:int | None = 500):
    

    fig = go.Figure(layout=go.Layout(width=750,height=500))
    fig.add_trace(
        go.Scatter(
            x=x, 
            y=y, 
            line=dict(color=None, width=6),
            mode=None,
            marker=dict(
                symbol='circle',  # ou 'square', 'circle', etc.
                size=20,
                color=None
            ),
        )
    )
    fig.update_layout(
        yaxis=dict(autorange='reversed')
    )
    
    fig = to_html(fig, full_html=False)
    return(fig)

def grafico_pizza(titulo, **arg_pie):
    pass

def grafico_kpi(valor: int, rotulo: str, exibir_percentual=False):
    pass
