import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html

class Grafico:
    def __init__(self, largura: int | None=750, altura: int | None=500):
        self.fig = go.Figure(layout=go.Layout(width=largura,height=altura))

    def __config_titulo(self, titulo:str | None =''):
        self.fig.update_layout(title=dict(text = titulo, x= 0.5, xanchor= 'center'))
        return(self)
    
    def __config_titulo_eixo_x(self, titulo_eixo_x:str | None=''):
        self.fig.update_layout(xaxis_title=titulo_eixo_x)
        return(self)
    
    def __config_titulo_eixo_y(self, titulo_eixo_y:str | None=''):
        self.fig.update_layout(yaxis_title=titulo_eixo_y)
        return(self)
    
    def __config_cor_fundo(self, bgcolor:str | None='white'):
        self.fig.update_layout(plot_bgcolor=bgcolor)

    def __config_grid_x(self): 
        self.fig.update_layout(xaxis=dict(showgrid=False, gridcolor='lightgrey', gridwidth=2))
        return(self)
    
    def __config_grid_y(self): 
        self.fig.update_layout(yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=0.001, griddash='dot'))
        return(self)

    def __config_linha(self, x: list, y: list):        
        self.fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=None, width=6)))
        return(self)
    
    def __config_linha_com_marcador(self, x: list, y: list, serie:str, espessura_linha:int | None=6, tamanho_marcador:int | None=20, posicao_texto:str | None='middle center', cor_fonte:int | None='black'):        
        self.fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers+text', name=serie,
                                      line=dict(color=None, width=espessura_linha), 
                                      marker=dict(symbol='circle', size=tamanho_marcador, color=None),
                                      textfont=dict(color=cor_fonte, size=18, family='Arial Black', weight='bold'),
                                      text=y, textposition=posicao_texto
                                      ))
        return(self)
    
    def __config_bar(self, x: list, y: list):        
        self.fig.add_trace(go.Bar(x=x, y=y))
        return(self)
    
    def __hover_template(self):
        self.fig.update_traces(hovertemplate = "Y: {y}<BR>X: {x}")

    def __config_marcador(self, x: list, y: list):        
        self.fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(symbol='circle', size=20, color=None)))
        return(self)

    def __config_texto(self, x: list, y: list, tamanho_rotulo_dados:str | None=20):
        self.fig.add_trace(go.Scatter(x=x, y=y,  mode='text', text=y, textposition='top center', line_shape='spline'))
        self.fig.update_traces(textfont=dict(size=tamanho_rotulo_dados, color='blue', weight='bold'))
        return(self)

    def __config_eixo_y_0(self):
        max_y = max([y for trace in self.fig.data for y in trace.y if y is not None]) * 1.2
        self.fig.update_layout(yaxis=dict(range=[0, max_y]))
        return(self)
    
    def __config_eixo_y_0_inverso(self):
        max_y = max([y for trace in self.fig.data for y in trace.y if y is not None]) * 1.2
        self.fig.update_layout(yaxis=dict(range=[max_y, 0]))
        return(self)
    
    def __exportar_html(self):
        fig = to_html(self.fig, full_html=False)
        return(fig)
    
    def grafico_linha_com_marcador_grande_para_rankings(self, titulo:str, titulo_eixo_x:str, titulo_eixo_y:str, dicionario:dict):
        '''
        exemplo de dicionário
        
            {"serie":{"2020":130,"2021":132, "2022":140}}
            
            {"serie1":{"2020":130,"2021":132, "2022":140}, "serie2":{"2020":230,"2021":134, "2022":160}}

        '''
        self.__config_titulo(titulo)
        self.__config_titulo_eixo_x(titulo_eixo_x)
        self.__config_titulo_eixo_y(titulo_eixo_y)
        self.__config_cor_fundo()
        self.__config_grid_x()
        self.__config_grid_y()
        for serie in dicionario:
            dados = dicionario[serie]
            dados_x = list(dados.keys())
            dados_y = list(dados.values())
            self.__config_linha_com_marcador(dados_x, dados_y, serie, tamanho_marcador=50)
        self.__config_eixo_y_0_inverso()        
        self.__hover_template()
        return(self.__exportar_html())
    
    def grafico_linha_com_marcador_grande(self, titulo:str, titulo_eixo_x:str, titulo_eixo_y:str, x:list, y:list):
        self.__config_titulo(titulo)
        self.__config_titulo_eixo_x(titulo_eixo_x)
        self.__config_titulo_eixo_y(titulo_eixo_y)
        self.__config_cor_fundo()
        self.__config_grid_x()
        self.__config_grid_y()
        self.__config_linha_com_marcador(x, y, tamanho_marcador=50)
        self.__config_eixo_y_0_inverso()        
        self.__hover_template()
        return(self.__exportar_html())

    def grafico_linha_com_marcador_pequeno(self, titulo:str, titulo_eixo_x:str, titulo_eixo_y:str, x:list, y:list):
        self.__config_titulo(titulo)
        self.__config_titulo_eixo_x(titulo_eixo_x)
        self.__config_titulo_eixo_y(titulo_eixo_y)
        self.__config_cor_fundo()
        self.__config_grid_x()
        self.__config_grid_y()
        self.__config_linha_com_marcador(x, y, tamanho_marcador=20, posicao_texto='top center', cor_fonte='blue')
        self.__config_eixo_y_0()     
        self.__hover_template()   
        return(self.__exportar_html())

    def grafico_bar(self):
        self.__config_titulo()
        self.__config_titulo_eixo_x()
        self.__config_titulo_eixo_y()
        self.__config_cor_fundo()
        self.__config_grid_x()
        self.__config_grid_y()
        self.__config_bar()
        self.__config_marcador()
        self.__config_texto()
        return(self.__exportar_html())




