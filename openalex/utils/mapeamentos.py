from ..models import Work, WorkTopic

MAPEAMENTOS_OPENALEX = {
    # 1. Total de publicações por ano
    "producao_por_ano": {
        "__tipo_entidade__": "producao_por_ano",
        "nome_plot": "producao_por_ano",
        "estrategia_plot": "aggregated",
        "modelo": Work,
        "titulo_base": "Total de publicações por ano",
        "eixo_x_campo": "pubyear__year",
        "eixo_x_nome": "Ano",
        "eixo_y_campo": "id",
        "eixo_y_nome": "Número de publicações",
        "eixo_y_agregacao": "count",
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
            # Se você tiver um filtro de tipo de documento:
            "tipo_producao": "worktype__worktype",
        },
        "filtros_padrao": {},
    },

    # 2. Distribuição temática por artigo
    "distribuicao_tematica": {
        "__tipo_entidade__": "distribuicao_tematica",
        "nome_plot": "distribuicao_tematica",
        "estrategia_plot": "hierarquico",
        "modelo": WorkTopic,
        "titulo_base": "Distribuição Temática de Artigos",
        "grafico_hierarquico_path": {
            "Domínio": "topic__domain_name",
            "Área": "topic__field_name",
            "Subárea": "topic__subfield_name"
        },
        "grafico_hierarquico_values_campo": "work_id",
        "grafico_hierarquico_values_nome": "Total de Artigos",
        "grafico_hierarquico_agregacao": "count_distinct",
        "filtros_padrao": {
            "work__worktype__worktype": "article"
        },
    },
}