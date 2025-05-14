import pandas as pd
import numpy as np
from .models import Programas
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly

class Grafico_programa:
    def __init__(self):
        queryset = Programas.objects.filter(Q(situacao__situacaoNome__in=['Em Funcionamento'])).values('modalidade__modalidadeNome', 'situacao__situacaoNome', 'codigo', 'conceito')
        self.df_programa = pd.DataFrame.from_records(queryset)
        self.df_programa = self.df_programa[self.df_programa['codigo']!='43072003001P1'] # esta linha exclui PPG Ensino de Computação (em rede)
    def programas_modalidade(self):
        queryset = Programas.objects.\
            filter(modalidade__modalidadeNome__in=['PROFISSIONAL', 'ACADÊMICO'], situacao__situacaoNome__in=['Em Funcionamento']).\
            values('modalidade__modalidadeNome').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra(df['modalidade__modalidadeNome'], df['contagem'], 'Programas por modalidade')
        return(img)
    
    def programas_modalidade_plotly(self):
        queryset = Programas.objects.\
            filter(modalidade__modalidadeNome__in=['PROFISSIONAL', 'ACADÊMICO'], situacao__situacaoNome__in=['Em Funcionamento']).\
            values('modalidade__modalidadeNome').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly(df, 'modalidade__modalidadeNome', 'contagem', 'Programas por modalidade')
        return(img)

    def programas_modalidade2(self):
        df = self.df_programa
        df = df.groupby(['modalidade__modalidadeNome'], as_index=False)['codigo'].count()
        img = grafico_barra(df['modalidade__modalidadeNome'], df['codigo'], 'Programas por modalidade')
        return(img)
    def programas_nivel_academico(self):
        df = self.df_programa
        df = df.groupby(['modalidade__modalidadeNome'], as_index=False)['codigo'].count()
        img = grafico_barra(df['modalidade__modalidadeNome'], df['codigo'], 'Programas por modalidade')
        return(img)
    def programas_nivel_profissional(self):
        df = self.df_programa
        df = df.groupby(['modalidade__modalidadeNome'], as_index=False)['codigo'].count()
        img = grafico_barra(df['modalidade__modalidadeNome'], df['codigo'], 'Programas por modalidade')
        return(img)   
    def graf_kpi_programa(self):
        df = self.df_programa
        quant_programas = df['codigo'].drop_duplicates().count()
        img = grafico_kpi(quant_programas, 'Programas Stricto Sensu')
        return(img)
    
    def graf_kpi_programa_academicos(self):
        df = self.df_programa
        quant_programas = np.sum(np.where(df['modalidade__modalidadeNome']=='ACADÊMICO', 1, 0))
        img = grafico_kpi(quant_programas, 'Programas acadêmicos')
        return(img)
    
    def graf_kpi_programa_profissionais(self):
        df = self.df_programa
        quant_programas = np.sum(np.where(df['modalidade__modalidadeNome']=='PROFISSIONAL', 1, 0))
        img = grafico_kpi(quant_programas, 'Programas profissionais')
        return(img)

    def graf_kpi_programa_rede(self):
        df = self.df_programa
        quant_programas = 'teste'
        img = grafico_kpi(quant_programas, 'Programas em rede')
        return(img)
    

