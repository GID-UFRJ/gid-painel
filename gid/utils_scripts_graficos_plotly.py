import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html


def grafico_linha(df, array_x: str, array_y: str, titulo:str, grupo:str):
    pass

def grafico_barra_plotly(df, x: str, y: str, titulo:str | None='', grupo:str | None=''):
    fig = px.bar(df, x, y, title=titulo)
    fig = to_html(fig, full_html=False)
    return(fig)

def grafico_pizza(titulo, **arg_pie):
    pass

def grafico_kpi(valor: int, rotulo: str, exibir_percentual=False):
    pass
