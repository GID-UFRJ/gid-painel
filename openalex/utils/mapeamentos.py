from ..models import Work, WorkTopic

MAPEAMENTOS_OPENALEX = {
    # 1. Total de publicações por ano
    "producao_por_ano": {
        "__tipo_entidade__": "producao_por_ano",
        "nome_plot": "producao_por_ano",
        "estrategia_plot": "aggregated",
        "modelo": Work,
        "queryset_hook": "autor_correspondente_ufrj",
        "titulo_base": "Total de publicações por ano",
        "eixo_x_campo": "pubyear__year",
        "eixo_x_nome": "Ano",
        "eixo_y_campo": "id",
        "eixo_y_nome": "Número de publicações",
        "eixo_y_agregacao": "count",
        #"paleta_cores": ['#004a80', '#d32f2f', '#b0bec5', '#2ca02c'],
        "paleta": ['#2ca02c', '#ff7f0e', '#9467bd', '#1f77b4'],
        # Mapeamos os filtros reativos (HTMX) aqui:
        "agrupamentos": {
            "acesso_aberto": "is_oa",
            "tipo_documento": "worktype__worktype",
            "dominio": "worktopic__topic__domain_name",
            "autor_correspondente": "autor_correspondente_ufrj",
        },
        "filtros": {
            "ano_inicial": "pubyear__year__gte",
            "ano_final": "pubyear__year__lte",
        },
        "filtros_padrao": {},
        "labels_customizadas": {
            "dominio": "Domínio",
    },
    },

    # 2. Distribuição temática por artigo
    "distribuicao_tematica": {
        "__tipo_entidade__": "distribuicao_tematica",
        "nome_plot": "distribuicao_tematica",
        "estrategia_plot": "hierarchical", 
        "modelo": Work,
        "queryset_hook": "com_topico_principal",
        "titulo_base": "Distribuição Temática (Tópico Principal)",
    
        "grafico_hierarquico_path": {
            "Domínio": "top_domain",   # Nome da anotação no QuerySet
            "Campo": "top_field",      # Nome da anotação no QuerySet
            "Subcampo": "top_subfield", # Nome da anotação no QuerySet
        },
    
        "grafico_hierarquico_values_campo": "id",
        "grafico_hierarquico_values_nome": "Total de Artigos",
        "grafico_hierarquico_agregacao": "count",
    
        "tipo_grafico_padrao": "sunburst",
        "filtros": {
            "ano_inicial": "pubyear__year__gte",
            "ano_final": "pubyear__year__lte",
        },
        "filtros_padrao": {},
    },

    "citacoes_por_ano" : {
        "nome_plot": "citacoes_por_ano",
        "estrategia_plot": "impacto",  # Aponta para a nossa nova Strategy
        "tipo_grafico_padrao": "linha", 
        "modelo": Work, 
        "titulo_base": "Evolução do Impacto",
    
        "eixo_x_campo": "pubyear__year",
        "eixo_x_nome": "Ano de Publicação",
    
        "campo_valor": "cited_by_count", # Qual campo vamos somar/calcular H-index
        "eixo_y_nome": "Métrica de Impacto",

        "nomes_das_metricas": {
            "total_citacoes": "Total de Citações",
            "media": "Média de Citações",
            "total_citacoes_acumuladas": "Citações Acumuladas",
            "hindex": "Índice H",
        },
    
        "filtros": {
            "ano_inicial": "pubyear__year__gte",
            "ano_final": "pubyear__year__lte",
            "metrica": None, # [total_citacoes, media, total_citacoes_acumuladas, hindex]
        },

        "agrupamentos": {
            "dominio": "worktopic__topic__domain_name", 
            "acesso_aberto": "is_oa",
        },

        "labels_customizadas": {
            "dominio": "Domínio",
    },
}

}