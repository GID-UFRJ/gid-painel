from ..models import Work, WorkTopic, Institution
from django.db.models import Q
from .traducoes import OPENALEX_TRADUCOES

# ==========================================
# 1. PAINEL DE PRODUÇÃO
# ==========================================
MAPEAMENTOS_PRODUCAO = {
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
        #"paleta_cores": ['#004a80', '#d32f2f', '#b0bec5', '#2ca02c'],
        #"paleta": ['#2ca02c', '#ff7f0e', '#9467bd', '#1f77b4'],
        # Mapeamos os filtros reativos (HTMX) aqui:
        "agrupamentos": {
            "acesso_aberto": "is_oa",
            #"tipo_documento": "worktype__worktype",
            "tipo_documento": "tipo_documento_limpo",
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
        "queries_condicionais": {
            "tipo_documento": "com_tipo_documento_agrupado",
            "autor_correspondente": "autor_correspondente_ufrj"
        },

        'substituicoes': OPENALEX_TRADUCOES
    },

    # 2. Distribuição temática por artigo
    "distribuicao_tematica": {
        "__tipo_entidade__": "distribuicao_tematica",
        "nome_plot": "distribuicao_tematica",
        "estrategia_plot": "hierarchical", 
        "modelo": Work,
        "queries_obrigatorias": [
            "com_topico_principal", # A filtragem por tópico principal
        ],

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
        "filtros_padrao": {
            "ignorar_nulos": Q(worktopic__isnull=False)
        },

        'substituicoes': OPENALEX_TRADUCOES

    },
}

# ==========================================
# 2. PAINEL DE IMPACTO
# ==========================================

MAPEAMENTOS_IMPACTO = {
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

        'substituicoes': OPENALEX_TRADUCOES
    },
}

# ==========================================
# 3. PAINEL DE COLABORAÇÃO
# ==========================================
MAPEAMENTOS_COLABORACAO = {
    # 1. Evolução da Colaboração 
    "evolucao_colaboracao": {
        "__tipo_entidade__": "evolucao_colaboracao",
        "nome_plot": "evolucao_colaboracao",
        "estrategia_plot": "evolucao_colaboracao",
        "modelo": Work,
        "queries_obrigatorias": ["com_status_colaboracao"], # <- NOVO HOOK AQUI
        "titulo_base": "Colaborações por Ano",
        "eixo_x_campo": "pubyear__year",
        "eixo_x_nome": "Ano de Publicação",
        "campo_valor": "id",
        "agregacao": "count",
        "eixo_y_nome": "Número de Publicações",
        "eixo_y_agregacao": "count_distinct",
        "filtros": {
            "ano_inicial": "pubyear__year__gte",
            "ano_final": "pubyear__year__lte",
            "tem_colab_nacional": "tem_colab_nacional",         # <- FILTRO MAPEADO
            "tem_colab_internacional": "tem_colab_internacional", # <- FILTRO MAPEADO
        },
        "agrupamentos": {
            "acesso_aberto": "is_oa",
            #"tipo_documento": "worktype__worktype",
            "tipo_documento": "tipo_documento_limpo",
            "dominio": "worktopic__topic__domain_name",
        },
        "labels_customizadas": {
            "acesso_aberto": "Acesso aberto",
            "tipo_documento": "Tipo de Documento",
            "dominio": "Domínio"
        },
        "queries_condicionais": {
            "tipo_documento": "com_tipo_documento_agrupado",
        },

        'substituicoes': OPENALEX_TRADUCOES
    },

    # 2. Top Instituições (Usa a nova Strategy e o modelo Institution!)
    "top_instituicoes": {
            "__tipo_entidade__": "top_instituicoes",
            "nome_plot": "top_instituicoes",
            "estrategia_plot": "top_instituicoes",
            "modelo": Institution, # O modelo base do ranking
            "titulo_base": "Top Instituições Colaboradoras",

            # --- CONFIGURAÇÕES OBRIGATÓRIAS DO TOP N ---
            "ranking_campo_categoria": "institution_name", # O campo que vai aparecer no eixo Y (os nomes)
            "ranking_campo_valor": "authorshipinstitution__authorship__work__id", # O que vamos contar (os trabalhos)
            "ranking_agregacao": "count_distinct", # Conta trabalhos únicos

            # Eixos para a renderização visual do Plotly
            "eixo_x_nome": "Número de Colaborações",
            "eixo_y_nome": "Instituição",

            "filtros": {
                # Avisa o Dispatcher para não jogar essa chave fora
                "tipo_colaboracao": "tipo_colaboracao",
            },

            # O UFRJ_ID (se precisar excluir a própria UFRJ do ranking de colaborações)
            "filtros_padrao": {
                # Descomente e ajuste se não quiser que a UFRJ apareça em 1º lugar no próprio painel
                "excluir_ufrj": ~Q(institution_id="I122140584"),
            },

            "hover_config": {
                "custom_data_cols": ["Nome Completo"],
                "template": "<b>%{customdata[0]}</b><br>Colaborações: %{x}<extra></extra>"
            },

        },
}

# ==========================================
# DICIONARIO COM TODOS OS MAPEAMENTOS (PARA)
# ==========================================
MAPEAMENTOS_TODOS = {
    **MAPEAMENTOS_PRODUCAO,
    **MAPEAMENTOS_IMPACTO,
    **MAPEAMENTOS_COLABORACAO
}