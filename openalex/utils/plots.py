import pandas as pd
import plotly.express as px
from plotly.io import to_html
import numpy as np
from ..models import Work, Year, WorkTopic, Institution, Authorship
from .misc import calculate_h_index
from django.db.models import F, Q, Count, Sum, Min, Max, Subquery, OuterRef, Case, When, Value
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

    
    def _inferir_intervalo_anos(self, ano_inicial=None, ano_final=None):
        if not ano_inicial:
            ano_inicial = Year.objects.aggregate(min=Min('year'))['min']
        if not ano_final:
            ano_final = Year.objects.aggregate(max=Min('year'))['max']
        return ano_inicial, ano_final
    

    def producao_por_ano(self, 
                         ano_inicial: int | None = None, 
                         ano_final: int | None = None, 
                         filtro: str | None = 'total'):

        ano_inicial, ano_final = self._inferir_intervalo_anos(ano_inicial, ano_final)

        # Define a dictionary for common plotting parameters
        plot_params = {
            'x': 'pubyear__year', 
            'y': 'document_count',
            'titulo_eixo_x': 'Ano',
            'titulo_eixo_y': 'Número de publicações',
            'largura': 1900,
        }

        # Base query
        base_query = Work.objects.filter(
            pubyear__year__gte=str(ano_inicial),
            pubyear__year__lte=str(ano_final)
        )

        if filtro == 'acesso_aberto':
            docs_por_ano = base_query.values('pubyear__year', 'is_oa').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year', 'is_oa')

            df = pd.DataFrame.from_records(docs_por_ano)
            df['is_oa'] = df['is_oa'].map({True: 'Acesso Aberto', False: 'Acesso Fechado'})

            # Add filter-specific parameters to the dictionary
            plot_params.update({
                'grupo': 'is_oa',
                'titulo': 'Produção por ano e Acesso Aberto',
            })

        elif filtro == 'tipo_documento':
            docs_por_ano = base_query.values('pubyear__year', 'worktype__worktype').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year', 'worktype__worktype')

            df = pd.DataFrame.from_records(docs_por_ano)

            # Add filter-specific parameters
            plot_params.update({
                'grupo': 'worktype__worktype',
                'titulo': 'Produção por ano e Tipo de Documento',
            })

        else:  # Default filter: 'total'
            docs_por_ano = base_query.values('pubyear__year').annotate(
                document_count=Count('id')
            ).order_by('pubyear__year')

            df = pd.DataFrame.from_records(docs_por_ano)

            # Add filter-specific parameters
            plot_params.update({
                'titulo': 'Total de publicações por ano',
            })

        # Call the plotting function with the dynamically generated parameters
        img = grafico_linha_plotly(df, **plot_params)
    
        return img

    def distribuicao_tematica_artigos(self):
        contagem_temas_principais = WorkTopic.objects.filter(
            pk__in=Subquery(
                WorkTopic.objects.filter(
                    work=OuterRef('work')
                ).order_by('-score').values('pk')[:1]
            ),
            work__worktype__worktype='article'  # Filter for articles only
        ).select_related(
            'topic',
            'work',
            'work__worktype',  # Optimizes the worktype join
        ).values(
            'topic__domain_name',
            'topic__field_name',
            'topic__subfield_name',
        ).annotate(
            article_count=Count('work')  # Count of works where this topic is top
        ).order_by('-article_count')
        df = pd.DataFrame.from_records(contagem_temas_principais)
        img = px.sunburst(df.sort_values(by='topic__domain_name'),
                          path=[
                            'topic__domain_name',
                            'topic__field_name',
                            'topic__subfield_name',
                          ], values = 'article_count').update_layout(height=800)
        img = to_html(img, full_html=False)
        return img


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


class PlotsVisibilidade:
    '''Gráficos sobre citações, colaborações e outros aspectos relacionados 
    à visibilidade da produção academica recuperada na OpenAlex'''

    def producao_total_citacoes(self):
        total_citacoes = Work.objects.aggregate(soma_citacoes=Sum('cited_by_count'))['soma_citacoes']
        img = grafico_kpi(total_citacoes, 
                          f'Total de citações recebidas', 
                          cor='#4169E1',
                          exibir_magnitude=True)
        return(img)

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