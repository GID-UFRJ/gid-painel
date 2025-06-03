import pandas as pd
import numpy as np
from .models import Work, Year
from django.db.models import Q, Count, Sum, Min, Max
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly2, grafico_linha_plotly2

class PlotsProducao:
    '''Gráficos sobre a produção academica recuperada na OpenAlex'''

    def producao_total(self):
        total = Work.objects.count()
        img = grafico_kpi(total, f'Total de documentos publicados', cor='#4169E1')
        return(img)
    
    def producao_total_artigos(self):
        total_artigos = Work.objects.filter(
            worktype__worktype='article'
            ).count()
        img = grafico_kpi(total_artigos, f'Artigos publicados em periódicos', cor='#4169E1')
        return(img)


    def producao_artigos_acesso_aberto(self):
        artigos_acesso_aberto = Work.objects.filter(
            is_oa=True).filter(
            worktype__worktype='article'
            ).count()
        img = grafico_kpi(artigos_acesso_aberto, f'Artigos em acesso aberto', cor='#4169E1')
        return(img)

    def producao_total_citacoes(self):
        total_citacoes = Work.objects.aggregate(soma_citacoes=Sum('cited_by_count'))['soma_citacoes']
        img = grafico_kpi(total_citacoes, f'Total de citações recebidas', cor='#4169E1')
        return(img)
    
    def _inferir_intervalo_anos(self, ano_inicial=None, ano_final=None):
        if not ano_inicial:
            ano_inicial = Year.objects.aggregate(min=Min('year'))['min']
        if not ano_final:
            ano_final = Year.objects.aggregate(max=Min('year'))['max']
        return ano_inicial, ano_final

    
    def producao_por_ano(self, 
                         ano_inicial:int | None = None, 
                         ano_final:int | None = None):
        ano_inicial, ano_final = self._inferir_intervalo_anos(ano_inicial, ano_final)
        docs_por_ano = Work.objects.filter(
                pubyear__year__gte=str(ano_inicial), # Converte para string pois Year.year é CharField
                pubyear__year__lte=str(ano_final)
        ).values('pubyear__year').annotate(
            document_count=Count('id') # Or Count('work_id') or Count('*')
            ).order_by('pubyear__year') # Optional: order the results by year
        df = pd.DataFrame.from_records(docs_por_ano)
        img = grafico_linha_plotly2(x=df['pubyear__year'], 
                                    y=df['document_count'],
                                    titulo='Total de publicações por ano',
                                    titulo_eixo_x='Ano',
                                    titulo_eixo_y='Número de publicações',
                                    #adicionar_rotulo_dados=False,
                                    tamanho_rotulo_dados=10,
                                    largura=1900,
        )
        return img


 

    #def kpi_qs_americaLatina(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='QS', escopo__escopoNome='Am. Latina').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'QS - América Latina (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
    #    return(img)

    #def kpi_the_americaLatina(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='THE', escopo__escopoNome='Am. Latina').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'THE - América Latina (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
    #    return(img)

    #def kpi_shanghaiNacional(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Nacional').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_kpi(int(df[df['ano__ano']==df['ano__ano'].max()]['posicao'].values[0]), f'Shanghai - Nacional (ano: {df["ano__ano"].max()})', cor='#4169E1', exibir_posicao=True)
    #    return(img)


    #def qs_mundo(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='QS', escopo__escopoNome='Mundo').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS mundo', 'ano', 'posição', largura=750, inverter_eixo_y=True)
    #    return(img)
    
    #def qs_americaLatina(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='QS', escopo__escopoNome='Am. Latina').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'QS América Latina', 'ano', 'posição', largura=750, inverter_eixo_y=True)
    #    return(img)

    #def the_mundo(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='THE', escopo__escopoNome='Mundo').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'THE mundo', 'ano', 'posição', tamanho_rotulo_dados=15, largura=750, inverter_eixo_y=True)
    #    return(img)
    
    #def the_americaLatina(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='THE', escopo__escopoNome='Am. Latina').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'THE América Latina', 'ano', 'posição', largura=750, inverter_eixo_y=True)
    #    return(img)
    
    #def shanghai_mundo(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Mundo').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'Shanghai mundo', 'ano', 'posição', largura=750, tamanho_rotulo_dados=15, inverter_eixo_y=True)
    #    return(img)
    
    #def shanghai_nacional(self):
    #    queryset = self.queryset.\
    #        filter(ranking__rankingNome='Shanghai', escopo__escopoNome='Nacional').\
    #        values('ano__ano', 'posicao')
    #    df = pd.DataFrame.from_records(queryset)
    #    img = grafico_linha_plotly2(df['ano__ano'], df['posicao'], 'Shanghai Nacional', 'ano', 'posição', largura=750, inverter_eixo_y=True)
    #    return(img)

class PlotsVisibilidade:
    def __init__(self):
        self.queryset = Work.objects
