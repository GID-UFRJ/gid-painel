import pandas as pd
import numpy as np
from .models import Programas
from django.db.models import Q, Count
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_barra_plotly, grafico_barra_plotly2

class Grafico_programa:
    def __init__(self):
        queryset = Programas.objects.filter(Q(situacao__situacaoNome__in=['Em Funcionamento'])).values('modalidade__modalidadeNome', 'situacao__situacaoNome', 'codigo', 'conceito')
        self.df_programa = pd.DataFrame.from_records(queryset)
        self.df_programa = self.df_programa[self.df_programa['codigo']!='43072003001P1'] # esta linha exclui PPG Ensino de Computação (em rede)
        self.queryset = Programas.objects.\
            filter(situacao__situacaoNome__in=['Em Funcionamento']).exclude(codigo='43072003001P1')

    def programas_modalidade_plotly(self):
        queryset = self.queryset.\
            values('modalidade__modalidadeNome').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'modalidade__modalidadeNome', 'contagem', 'Programas por modalidade', 'modalidade')
        return(img)
    
    def programas_centro_plotly(self):
        queryset = self.queryset.\
            values('centro__centroNome').\
            annotate(contagem=Count('codigo', distinct=True)).\
            order_by('contagem')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'contagem', 'centro__centroNome','Programas por centro', 'centro', largura=1000, orientacao='h')
        return(img)

    def programas_rede_plotly(self):
        queryset = self.queryset.\
            values('rede__redeNome').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'rede__redeNome', 'contagem', 'Programas por rede', 'rede')
        return(img)

    def programasAcademicos_conceito_plotly(self):
        queryset = self.queryset.filter(modalidade__modalidadeNome__in=['ACADÊMICO']).\
            values('conceito').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'conceito', 'contagem', 'Programas acadêmico por conceito', 'conceito')
        return(img)
    
    def programasProfissionais_conceito_plotly(self):
        queryset = self.queryset.filter(modalidade__modalidadeNome__in=['PROFISSIONAL']).\
            values('conceito').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'conceito', 'contagem', 'Programas acadêmico por conceito', 'conceito')
        return(img)
    
    def programas_unidade_plotly(self):
        queryset = self.queryset.\
            values('unidade__unidadeNome').\
            annotate(contagem=Count('codigo', distinct=True)).\
            order_by('contagem')
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra_plotly2(df, 'contagem', 'unidade__unidadeNome','Programas por unidade', 'unidade', largura=750, altura = 1000,orientacao='h')
        return(img)

    def programas_areaAvaliacao_plotly(self):
        queryset = self.queryset.\
            values('areaAvaliacao__areaAvaliacaoNome').\
            annotate(contagem=Count('codigo', distinct=True)).\
            order_by('contagem')
        df = pd.DataFrame.from_records(queryset)
        df['areaAvaliacao__areaAvaliacaoNome'] = df['areaAvaliacao__areaAvaliacaoNome'].str.strip()
        img = grafico_barra_plotly2(df, 'contagem', 'areaAvaliacao__areaAvaliacaoNome','Programas por Área de Avaliacao', 'areaAvaliacao', largura=750, altura = 1000,orientacao='h')
        return(img)




    #legado
    
    def programas_modalidade(self):
        queryset = Programas.objects.\
            filter(modalidade__modalidadeNome__in=['PROFISSIONAL', 'ACADÊMICO'], situacao__situacaoNome__in=['Em Funcionamento']).\
            values('modalidade__modalidadeNome').\
            annotate(contagem=Count('codigo', distinct=True))
        df = pd.DataFrame.from_records(queryset)
        img = grafico_barra(df['modalidade__modalidadeNome'], df['contagem'], 'Programas por modalidade')
        return(img)
    
 
    def graf_kpi_programa(self):
        resultado = self.queryset.aggregate(total=Count('codigo', distinct=True))
        img = grafico_kpi(resultado['total'], 'Programas Stricto Sensu')
        return(img)
    
    def graf_kpi_programa_academicos(self):
        resultado = self.queryset.filter(modalidade__modalidadeNome__in=['ACADÊMICO']).aggregate(total=Count('codigo', distinct=True))
        img = grafico_kpi(resultado['total'], 'Programas Stricto Sensu')
        return(img)
    
    def graf_kpi_programa_profissionais(self):
        resultado = self.queryset.filter(modalidade__modalidadeNome__in=['PROFISSIONAL']).aggregate(total=Count('codigo', distinct=True))
        img = grafico_kpi(resultado['total'], 'Programas Stricto Sensu')
        return(img)

    def graf_kpi_programa_rede(self):
        df = self.df_programa
        quant_programas = 'teste'
        img = grafico_kpi(quant_programas, 'Programas em rede')
        return(img)
    

