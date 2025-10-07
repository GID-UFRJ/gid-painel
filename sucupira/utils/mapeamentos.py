# sucupira/utils/mapeamentos.py

from sucupira.models import Discente, Docente, AnoPrograma, FaixaEtaria

# =============================================================================
# RECEITAS DE GRÁFICOS - Versão adaptada para a BasePlots final
# =============================================================================

# --- Mapeamentos Gerais (para a classe PlotsPessoal) ---

discentes_geral_por_ano = {
    "modelo": Discente,
    "titulo_base": "Discentes na Pós-Graduação",
    
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "pessoa_id",
    "eixo_y_nome": "Número de Discentes",
    "eixo_y_agregacao": "count_distinct",

    "filtros": {
        "situacao": "situacao__nm_situacao_discente",
        "grau_curso": "grau_academico__nm_grau_curso",
        "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},

    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade",
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
}

docentes_geral_por_ano = {
    "modelo": Docente,
    "titulo_base": "Docentes na Pós-Graduação",
    
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "pessoa_id",
    "eixo_y_nome": "Número de Docentes",
    "eixo_y_agregacao": "count_distinct",

    "filtros": {
        "categoria_docente": "categoria__ds_categoria_docente",
        "bolsa_produtividade": "bolsa_produtividade__cd_cat_bolsa_produtividade",
        "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "modalidade": "programa__ano_programa__nm_modalidade_programa__nm_modalidade_programa",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},

    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade",
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
}

# --- Mapeamentos Específicos por PPG (para a classe PlotsPpgDetalhe) ---

discentes_por_ano_ppg = {
    "modelo": Discente,
    "titulo_base": "Discentes do Programa",
    
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "pessoa_id",
    "eixo_y_nome": "Número de Discentes",
    "eixo_y_agregacao": "count_distinct",

    "filtros": {
        "programa_id": "programa_id",
        "situacao": "situacao__nm_situacao_discente",
        "grau_curso": "grau_academico__nm_grau_curso",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},

    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade",
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
}

docentes_por_ano_ppg = {
    "modelo": Docente,
    "titulo_base": "Docentes do Programa",
    
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "pessoa_id",
    "eixo_y_nome": "Número de Docentes",
    "eixo_y_agregacao": "count_distinct",

    "filtros": {
        'programa_id': 'programa_id',
        "categoria_docente": "categoria__ds_categoria_docente",
        "bolsa_produtividade": "bolsa_produtividade__cd_cat_bolsa_produtividade",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},

    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
}


conceito_programa_por_ano = {
    "modelo": AnoPrograma,
    "titulo_base": "Evolução do Conceito CAPES do Programa",
    
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano da Avaliação",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "cd_conceito_programa__cd_conceito_programa",
    "eixo_y_nome": "Conceito CAPES",
    # Este é um gráfico direto, então não há 'eixo_y_agregacao'

    "filtros": {
        "programa_id": "programa_id",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},
}

media_titulacao_por_ano_ppg = {
    # --- Configurações Gerais ---
    "modelo": Discente,
    "titulo_base": "Tempo Médio para Titulação",
    
    # --- Eixo X ---
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano de Titulação",
    "eixo_x_tipo": "numerico_continuo",

    # --- Eixo Y (A Lógica Principal) ---
    "eixo_y_campo": "qt_mes_titulacao",        # O campo que queremos calcular a média
    "eixo_y_nome": "Média de Meses",          # O título que aparecerá no eixo Y
    "eixo_y_agregacao": "avg",                 # A operação de agregação: média (average)
    
    # --- Filtragem ---
    "filtros": {
        "programa_id": "programa_id",
        "situacao": "situacao__nm_situacao_discente",
        "grau_curso": "grau_academico__nm_grau_curso",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    # Este filtro padrão garante que a análise SEMPRE será feita apenas com titulados.
    "filtros_padrao": {
        "situacao": "TITULADO",
        "ano_inicial": 2013,
    },

    # --- Agrupamentos Opcionais ---
    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
}


discentes_por_area_sunburst = {
    "modelo": Discente,
    "titulo_base": "Distribuição de Discentes por Área do Conhecimento",

    # --- NOVAS CHAVES PARA GRÁFICOS HIERÁRQUICOS ---
    "grafico_hierarquico_path": {
        "Grande Área": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "Área de Conhecimento": "programa__ano_programa__area_conhecimento__nm_area_conhecimento",
    },
    "grafico_hierarquico_values_campo": "pessoa_id",
    "grafico_hierarquico_values_nome": "Quantidade",
    "grafico_hierarquico_agregacao": "count_distinct",

    # --- Filtros reutilizados ---
    "filtros": {
        "ano": "ano__ano_valor",
        "situacao": "situacao__nm_situacao_discente",
    },
    "filtros_padrao": {
        "ano": 2013, # Retrato de um ano específico
    },
}


docentes_por_area_sunburst = {
    "modelo": Docente,
    "titulo_base": "Distribuição de Docentes por Área do Conhecimento",

    # A hierarquia é a mesma, mas a busca parte do modelo Docente
    "grafico_hierarquico_path": {
        "Grande Área": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "Área de Conhecimento": "programa__ano_programa__area_conhecimento__nm_area_conhecimento",
    },
    
    # A contagem é sobre os docentes únicos
    "grafico_hierarquico_values_campo": "pessoa_id",
    "grafico_hierarquico_values_nome": "Quantidade",
    "grafico_hierarquico_agregacao": "count_distinct",

    "filtros": {
        "ano": "ano__ano_valor",
        #"categoria_docente": "categoria__ds_categoria_docente", # Filtro extra!
    },
    "filtros_padrao": {
        "ano": 2013, 
    },
}

top_paises_discentes = {
    "modelo": Discente,
    "titulo_base": "Top 10 Países de Procedência - Discentes",
    
    # --- Configurações de Ranking ---
    "ranking_campo_categoria": "pessoa__pais_nacionalidade__pais",
    "ranking_campo_valor": "pessoa_id",
    "ranking_agregacao": "count_distinct",
    "ranking_limite_padrao": 10,

    # --- Filtros ---
    "filtros": {
        "limite": None, # 'limite' não é um campo do modelo, é um parâmetro de controle
        "ano": "ano__ano_valor", # Podemos adicionar filtros extras se quisermos
    },
}

top_paises_docentes = {
    "modelo": Docente,
    "titulo_base": "Top 10 Países de Procedência - Docentes",
    "ranking_campo_categoria": "pessoa__pais_nacionalidade__pais",
    "ranking_campo_valor": "pessoa_id",
    "ranking_agregacao": "count_distinct",
    "ranking_limite_padrao": 10,
    "filtros": { "limite": None },
}


# =============================================================================
# DICIONÁRIO FINAL - Importado pelas classes de Plots
# =============================================================================
MAPEAMENTOS = {
    # Gráficos Gerais
    "discentes_geral": discentes_geral_por_ano,
    "discentes_sunburst": discentes_por_area_sunburst,
    "docentes_geral": docentes_geral_por_ano,
    "docentes_sunburst": docentes_por_area_sunburst,
    "top_paises_discentes": top_paises_discentes,
    "top_paises_docentes": top_paises_docentes,

    # Gráficos Específicos de um PPG
    "discentes_ppg": discentes_por_ano_ppg,
    "media_titulacao": media_titulacao_por_ano_ppg,
    "docentes_ppg": docentes_por_ano_ppg,
    "conceito_ppg": conceito_programa_por_ano,


}





# =============================================================================
# Exemplo: Gráfico Agregado com Eixo Categórico (Docentes por Faixa Etária)
# Um novo gráfico que não usa o ano como eixo principal.
# =============================================================================
#docentes_por_faixa_etaria = {
#    "modelo": Docente,
#    "titulo_base": "Distribuição de Docentes por Faixa Etária",
#    "eixo_x_campo": "faixa_etaria__ds_faixa_etaria", # Eixo X é categórico
#    "eixo_x_nome": "Faixa Etária",
#    "eixo_x_tipo": "categorico", # O padrão, mas explícito aqui por clareza
#    "filtros": {
#        "programa_id": "programa_id",
#        "ano": "ano__ano_valor", # Permite filtrar o gráfico para um ano específico
#        "categoria": "categoria__ds_categoria_docente",
#    },
#    "filtros_padrao": {
#        "ano": 2024 # Por padrão, mostra os dados do último ano
#    },
#    "agrupamentos": {
#        "sexo": "pessoa__tp_sexo__sexo",
#        "vinculo": "vinculo__ds_tipo_vinculo_docente_ies",
#    },
#    "campo_agregacao": "pessoa_id",
#    # Exemplo de como forçar uma ordenação customizada para o eixo X
#    "category_orders_override": {
#         'Faixa Etária': [f.ds_faixa_etaria for f in FaixaEtaria.objects.order_by('id')]
#    }
#}