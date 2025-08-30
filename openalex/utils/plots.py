import pandas as pd
import plotly.express as px
from plotly.io import to_html
import numpy as np
from ..models import Work, Year, WorkTopic, Institution, Authorship
from .misc import calculate_h_index
from django.db.models import F, Q, Count, Sum, Min, Avg, Max, Subquery, OuterRef, Case, When, Value, CharField, Exists
from gid.utils_scripts_graficos import cores, grafico_barra, grafico_kpi
from gid.utils_scripts_graficos_plotly import grafico_linha_plotly, grafico_barra_plotly, grafico_barra_plotly2


class PlotsProducao:
    '''Gráficos sobre a produção academica recuperada na OpenAlex'''

    def producao_total(self,):
        total = Work.objects.count()
        img = grafico_kpi(total, f'Total de documentos publicados', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return(img)
    
    def producao_total_artigos(self):
        total_artigos = Work.objects.filter(
            worktype__worktype='article'
            ).count()
        img = grafico_kpi(total_artigos, f'Artigos publicados em periódicos', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return(img)


    def producao_artigos_acesso_aberto(self):
        artigos_acesso_aberto = Work.objects.filter(
            is_oa=True).filter(
            worktype__worktype='article'
            ).count()
        img = grafico_kpi(artigos_acesso_aberto, f'Artigos em acesso aberto', cor='#4169E1',
                          exibir_magnitude=True)
        return(img)

    # NO MOMENTO, ESSE MÉTODO É INUTIL - REMOVER OU REFATORAR COMO FUNCAO FORA DA CLASSE
    def _inferir_intervalo_anos(self, ano_inicial=None, ano_final=None):
        if not ano_inicial:
            ano_inicial = Year.objects.aggregate(min=Min('year'))['min']
        if not ano_final:
            ano_final = Year.objects.aggregate(max=Min('year'))['max']
        return ano_inicial, ano_final
    

    def producao_por_ano(self, 
                         ano_inicial: int | None = None, 
                         ano_final: int | None = None, 
                         tipo_producao: str | None = 'total',
                         tipo_grafico: str | None = 'barra'):

        ano_inicial, ano_final = self._inferir_intervalo_anos(ano_inicial, ano_final)

        # Base query
        base_query = Work.objects.filter(
            pubyear__year__gte=str(ano_inicial),
            pubyear__year__lte=str(ano_final)
        )

        # Definições comuns
        eixo_x = "pubyear__year"
        eixo_y = "document_count"
        grupo = None
        titulo = "Total de publicações por ano"
        category_orders = {} #Usado para ordenar categorias na legenda dos plots

        if tipo_producao == 'acesso_aberto':
            docs_por_ano = base_query.values('pubyear__year', 'is_oa').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year', 'is_oa')

            df = pd.DataFrame.from_records(docs_por_ano)
            df['is_oa'] = df['is_oa'].map({True: 'Acesso Aberto', False: 'Acesso Fechado'})

            grupo = "is_oa"
            titulo = "Produção por ano e Acesso Aberto"
            category_orders = {grupo: ["Acesso Aberto", "Acesso Fechado"]}


        elif tipo_producao == 'tipo_documento':
            docs_por_ano = base_query.values('pubyear__year', 'worktype__worktype').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year', 'worktype__worktype')

            df = pd.DataFrame.from_records(docs_por_ano)
            grupo = "worktype__worktype"
            titulo = "Produção por ano e Tipo de Documento"
        
        elif tipo_producao == 'dominio':
            docs_por_dominio = WorkTopic.objects.filter(
                work__pubyear__year__gte=str(ano_inicial),
                work__pubyear__year__lte=str(ano_final)
            ).values(
                'work__pubyear__year',
                'topic__domain_name'
            ).annotate(
                document_count=Count('work', distinct=True)
            ).order_by('work__pubyear__year', 'topic__domain_name')

            df = pd.DataFrame.from_records(docs_por_dominio)
            eixo_x = "work__pubyear__year"
            eixo_y = "document_count"
            grupo = "topic__domain_name"
            titulo = "Produção por ano e Domínio"

        elif tipo_producao == 'autor_correspondente':
            # Subquery: existe correspondente da UFRJ?
            corresp_ufrj = Authorship.objects.filter(
                work=OuterRef('pk'),
                is_corresponding=True,
                authorshipinstitution__institution__institution_name="Universidade Federal do Rio de Janeiro"
            )

            # Subquery: existe correspondente em outra instituição (não UFRJ)?
            corresp_outro = Authorship.objects.filter(
                work=OuterRef('pk'),
                is_corresponding=True
            ).exclude(
                authorshipinstitution__institution__institution_name="Universidade Federal do Rio de Janeiro"
            )

            # Base: todos os trabalhos no intervalo
            works_qs = Work.objects.filter(
                pubyear__year__gte=str(ano_inicial),
                pubyear__year__lte=str(ano_final),
                worktype__worktype="article",
            ).annotate(
                has_corresp_ufrj=Exists(corresp_ufrj),
                has_corresp_outro=Exists(corresp_outro),
            ).annotate(
                categoria=Case(
                    When(has_corresp_ufrj=True, then=Value("UFRJ")),
                    When(has_corresp_outro=True, then=Value("Outro")),
                    default=Value("Não especificado"),
                    output_field=CharField()
                )
            )

            # Agregar por ano e categoria
            docs_corresp = works_qs.values('pubyear__year', 'categoria').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year', 'categoria')

            # Converter para DataFrame
            df = pd.DataFrame.from_records(docs_corresp)

            eixo_x = "pubyear__year"
            eixo_y = "document_count"
            grupo = "categoria"
            titulo = "Produção por ano (Artigos - Autor correspondente UFRJ / Outro / Não especificado)"
            category_orders = {grupo: ["UFRJ", "Outro", "Não especificado"]}

        else:  # total
            docs_por_ano = base_query.values('pubyear__year').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year')

            df = pd.DataFrame.from_records(docs_por_ano)


        # Construção do gráfico com plotly express
        if tipo_grafico == "barra":
            fig = px.bar(
                df,
                x=eixo_x,
                y=eixo_y,
                color=grupo,
                text=eixo_y,
                title=titulo,
                category_orders=category_orders,
            )

            fig.update_traces(texttemplate='%{text:.0f}', textfont_size=12, textposition='inside')

        else:  # linha
            fig = px.line(
                df,
                x=eixo_x,
                y=eixo_y,
                color=grupo,
                markers=True,
                title=titulo,
                category_orders=category_orders,
            )

        # Layout: sem largura fixa, apenas responsivo
        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis_title="Ano",
            yaxis_title="Número de publicações",
        )

        # Retorna o HTML responsivo
        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={"responsive": True})

    def distribuicao_tematica_artigos(self):
        # Query base: pegar todos os WorkTopics de artigos
        qs = WorkTopic.objects.filter(
            work__worktype__worktype='article'
        ).select_related('topic', 'work')

        df = pd.DataFrame.from_records(qs.values(
            'work_id',
            'topic__domain_name',
            'topic__field_name',
            'topic__subfield_name'
        ))

        # Remover duplicados para subfield
        df_subfield = df.drop_duplicates(subset=['work_id', 'topic__subfield_name'])
        # Contagem por subfield
        df_subfield['article_count'] = 1

        # Remover duplicados para field
        df_field = df.drop_duplicates(subset=['work_id', 'topic__field_name'])
        df_field['article_count'] = 1

        # Remover duplicados para domain
        df_domain = df.drop_duplicates(subset=['work_id', 'topic__domain_name'])
        df_domain['article_count'] = 1

        # Concatenar e agregar por nível para sunburst
        df_all = pd.concat([df_domain, df_field, df_subfield], ignore_index=True)
        df_agg = df_all.groupby(
            ['topic__domain_name', 'topic__field_name', 'topic__subfield_name'],
            as_index=False
        ).sum()

        # Criar gráfico sunburst
        fig = px.sunburst(
            df_agg.sort_values(by='topic__domain_name'),
            path=['topic__domain_name', 'topic__field_name', 'topic__subfield_name'],
            values='article_count'
        )

        # Layout responsivo, título e nota
        fig.update_layout(
            autosize=True,
            margin=dict(l=20, r=20, t=80, b=60),  # espaço extra embaixo para a nota
            title=dict(
                text="Distribuição Temática de Artigos",
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            annotations=[
                dict(
                    text="Nota: cada artigo pode ser classificado em mais de uma área",
                    x=0.5,
                    y=-0.05,           # posição abaixo do gráfico
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=12, color="gray"),
                    align="center"
                )
            ]
        )   

        # Retornar HTML
        return to_html(fig, full_html=False, include_plotlyjs='cdn', config={"responsive": True})


    def metricas_por_topico_artigos(self):
        # Step 1: Precompute authors per work
        authors_per_work_dict = dict(
            Authorship.objects.values('work_id')
            .annotate(n_authors=Count('author_id'))
            .values_list('work_id', 'n_authors')
        )

        # Step 2: Pull WorkTopic data
        raw_data_qs = WorkTopic.objects.filter(
            work__worktype__worktype='article'
        ).select_related('topic', 'work').values(
            'topic_id',
            'topic__topic_name',
            'topic__subfield_name',
            'topic__field_name',
            'topic__domain_name',
            'work_id',
            'work__cited_by_count',
        )

        raw_data_list = list(raw_data_qs)

        # Step 3: Convert to DataFrame and enrich
        df = pd.DataFrame(raw_data_list)
        df['n_authors_per_work'] = df['work_id'].map(authors_per_work_dict)

        # Step 4: Rename for clarity
        df = df.rename(columns={
            'topic__topic_name': 'topic_name',
            'topic__subfield_name': 'subfield_name',
            'topic__field_name': 'field_name',
            'topic__domain_name': 'domain_name',
            'work__cited_by_count': 'cited_by_count',
        })

        # Step 5: Group by topic, aggregate, round
        grouped = df.groupby(
            ['topic_id', 'topic_name', 'subfield_name', 'field_name', 'domain_name']
        ).agg(
            n_docs=('work_id', 'nunique'),
            mean_authors=('n_authors_per_work', 'mean'),
            citation_counts=('cited_by_count', lambda x: list(x))
        ).reset_index()

        grouped['mean_authors'] = grouped['mean_authors'].round(2)

        # Step 6: H-index calculation
        grouped['h_index'] = grouped['citation_counts'].apply(calculate_h_index)

        # Step 7: Drop intermediary column and sort
        final_df = grouped.drop(columns=['citation_counts']).sort_values(by='h_index', ascending=False).reset_index(drop=True)

        return final_df
    
    def metricas_por_topico_artigos_plot(self):
        df = self.metricas_por_topico_artigos()
        fig = px.scatter_3d(df.sort_values(by='domain_name'), 
                      x='n_docs', 
                      y='h_index', 
                      z='mean_authors', 
                      color = 'domain_name',
                      hover_name='subfield_name').update_layout(height=600)
                        
        fig.update_traces(marker=dict(size=5))  # Adjust size as needed

        fig = to_html(fig, full_html=False)
        return fig



class PlotsImpacto:
    '''Gráficos sobre citações, colaborações e outros aspectos relacionados 
    à visibilidade da produção academica recuperada na OpenAlex'''

    def producao_total_citacoes(self):
        total_citacoes = Work.objects.aggregate(soma_citacoes=Sum('cited_by_count'))['soma_citacoes']
        img = grafico_kpi(total_citacoes, 
                          f'Total de citações recebidas', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return(img)

    def producao_total_hindex(self):
        citacoes = list(
            Work.objects.order_by('-cited_by_count')
            .values_list('cited_by_count', flat=True)
        )

        h = calculate_h_index(citacoes, pre_reverse_sorted=True)

        img = grafico_kpi(
            h,
            f'Índice H institucional',
            cor='#4169E1'
        )
        return img

    def citacoes_por_ano(self,
                         ano_inicial: int | None = None,
                         ano_final: int | None = None,
                         tipo_producao: str | None = 'total',
                         metrica: str | None = 'total_citacoes',
                         tipo_grafico: str | None = 'barra'):
        """
        Gera gráficos de métricas de citação (Total, Acumulada, Média, Índice H)
        ao longo dos anos, com opção de agrupamento por Domínio ou Acesso Aberto.
        """

        print(f"ano_inicial={ano_inicial}, ano_final={ano_final}, tipo_producao={tipo_producao}, metrica={metrica}, tipo_grafico={tipo_grafico}")

        # --- 1. Coleta de Dados Brutos ---
        dados_brutos = []
        grupo = None
        
        if tipo_producao == 'dominio':
            query = WorkTopic.objects.filter(
                work__pubyear__year__gte=str(ano_inicial),
                work__pubyear__year__lte=str(ano_final)
            ).values(
                'work__pubyear__year', 
                'topic__domain_name', 
                'work__cited_by_count'  # <-- CORREÇÃO 1
            )
            dados_brutos = list(query)
            grupo = 'topic__domain_name'
            
        elif tipo_producao == 'acesso_aberto':
            query = Work.objects.filter(
                pubyear__year__gte=str(ano_inicial),
                pubyear__year__lte=str(ano_final)
            ).values(
                'pubyear__year', 
                'is_oa', 
                'cited_by_count'  
            )
            dados_brutos = list(query)
            grupo = 'is_oa'

        else: # 'total'
            query = Work.objects.filter(
                pubyear__year__gte=str(ano_inicial),
                pubyear__year__lte=str(ano_final)
            ).values(
                'pubyear__year', 
                'cited_by_count'  
            )
            dados_brutos = list(query)
        
        df = pd.DataFrame.from_records(dados_brutos)
        
        df.rename(columns={
            'work__pubyear__year': 'ano', 'pubyear__year': 'ano',
            'work__cited_by_count': 'citacoes', 
            'cited_by_count': 'citacoes',       
            'topic__domain_name': 'dominio',
        }, inplace=True)

        category_orders = {}

        if grupo == 'is_oa':
            df['is_oa'] = df['is_oa'].map({True: 'Acesso Aberto', False: 'Acesso Fechado'})
            category_orders = {grupo: ["Acesso Aberto", "Acesso Fechado"]}
            grupo_cols = ['ano', 'is_oa']

        elif grupo == 'topic__domain_name':
            grupo_cols = ['ano', 'dominio']
            grupo = 'dominio'
        else:
            grupo_cols = ['ano']

        # --- 2. Cálculo da Métrica ---
        eixo_x = "ano"
        eixo_y, titulo, yaxis_title = "", "", ""
        
        grouped = df.groupby(grupo_cols)

        if metrica == 'total_citacoes':
            df_final = grouped['citacoes'].sum().reset_index()
            eixo_y, titulo, yaxis_title = "citacoes", "Total de Citações por Ano", "Total de Citações"

        elif metrica == 'media':
            df_final = grouped['citacoes'].mean().reset_index()
            df_final['citacoes'] = df_final['citacoes'].round(2)
            eixo_y, titulo, yaxis_title = "citacoes", "Média de Citações por Ano", "Citações por Publicação (Média)"

        elif metrica == 'total_citacoes_acumuladas':
            soma_anual = df.groupby(grupo_cols)['citacoes'].sum().reset_index()
            if grupo:
                soma_anual['citacoes_acumuladas'] = soma_anual.groupby(grupo)['citacoes'].cumsum()
            else:
                soma_anual['citacoes_acumuladas'] = soma_anual['citacoes'].cumsum()
            df_final = soma_anual
            eixo_y, titulo, yaxis_title = "citacoes_acumuladas", "Total de Citações Acumuladas por Ano", "Total de Citações (Acumulado)"

        elif metrica == 'hindex':
            # Garanta que a função 'calculate_h_index' esteja importada.
            df_final = df.groupby(grupo_cols)['citacoes'].apply(calculate_h_index).reset_index(name='h_index')
            eixo_y, titulo, yaxis_title = "h_index", "Índice H por Ano de Publicação", "Índice H"
        
        else:
            raise ValueError(f"Métrica desconhecida: {metrica}")

        if grupo:
            titulo += f" (por { 'Domínio' if grupo == 'dominio' else 'Tipo de Acesso' })"

        # --- 3. Construção do Gráfico ---
        if tipo_grafico == "barra":
            fig = px.bar(
                df_final, x=eixo_x, y=eixo_y, color=grupo, text=eixo_y,
                title=titulo, category_orders=category_orders,
            )
            fig.update_traces(texttemplate='%{text:.2s}', textfont_size=12, textposition='inside')
        else:
            fig = px.line(
                df_final, x=eixo_x, y=eixo_y, color=grupo, markers=True,
                title=titulo, category_orders=category_orders,
            )

        fig.update_layout(
            autosize=True, margin=dict(l=40, r=40, t=60, b=40),
            xaxis_title="Ano de Publicação", yaxis_title=yaxis_title,
            legend_title_text='Grupo' if grupo else '',
        )
        
        if tipo_grafico == 'barra':
            fig.update_xaxes(type='category')

        return fig.to_html(full_html=False, include_plotlyjs='cdn', config={"responsive": True})

class PlotsColaboracao:
    '''Gráficos sobre colaboração institucional com base na 
    produção academica recuperada na OpenAlex'''


    def producao_colaboracao_nacional(self):
        id_ufrj = 'I122140584'
        total_colaboracao_nacional = Work.objects.annotate(
            br_inst_count=Count(
                'authorship__authorshipinstitution__institution', #Conta num de instituiçẽs distintas
                filter=Q(authorship__authorshipinstitution__institution__country_code='BR'), #Filtra apenas instituições BR
                distinct=True
            )
        ).filter(
            br_inst_count__gte=2
        ).count()

        img = grafico_kpi(total_colaboracao_nacional, 
                          f'Publicações em colaboração nacional', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return img
        

    def producao_colaboracao_internacional(self):
        total_colaboracao_internacional = Work.objects.annotate(
            contagem_paises =Count(
                'authorship__authorshipinstitution__institution__country_code',
                distinct=True
            )
        ).filter(
            contagem_paises__gt=1  # Mais que 1 país -> internacional
        ).count()

        img = grafico_kpi(total_colaboracao_internacional, 
                          f'Publicações em colaboração internacional', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return img    
        


    def top_instituicoes_colaboradoras(self, internacional: bool | None = False):
        ufrj_id = 'I122140584'

        filtro_pais = Q(country_code='BR') if not internacional else ~Q(country_code='BR')

        contagem_colaboracoes = Institution.objects.exclude(
            institution_id=ufrj_id
        ).filter(
            filtro_pais
        ).annotate(
            n_colabs=Count('authorshipinstitution__authorship__work', distinct=True)
        ).values(
            instituicao=F('institution_name'),
            n_colabs=F('n_colabs'),
            codigo_pais=F('country_code'),
        ).order_by('-n_colabs')[0:10]

        df = pd.DataFrame.from_records(contagem_colaboracoes)

        fig = grafico_barra_plotly(
            df,
            x='instituicao',
            y='n_colabs',
            titulo=f"Top instituições colaboradoras {'internacionais' if internacional else 'nacionais'}",
            titulo_eixo_x="Nome da instituição",
            titulo_eixo_y="Número de colaborações",
            adicionar_rotulo_dados=False,
            retornar_plotly=True,
            largura= 700,
            altura= 700,
            hover_data={
                "instituicao": True,
                "codigo_pais": True,
                "n_colabs": True,
                },
        )

        fig.update_layout( 
            xaxis_tickangle=-45,  # ou 45, 90, etc.
            )

        return to_html(fig, full_html=False)