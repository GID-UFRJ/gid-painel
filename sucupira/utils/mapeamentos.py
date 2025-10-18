# sucupira/utils/mapeamentos.py

from sucupira.models import Discente, Docente, AnoPrograma, FaixaEtaria

# =============================================================================
# RECEITAS DE GRÁFICOS - Versão Final com Configuração Unificada
# =============================================================================

# --- Mapeamentos Gerais (para a classe PlotsPessoal) ---

discentes_geral_por_ano = {
    "nome_plot": "discentes_por_ano",        # <-- ADICIONADO: O nome público para URLs e templates.
    "estrategia_plot": "aggregated",      # <-- ADICIONADO: A "ferramenta" a ser usada.
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
    "nome_plot": "docentes_por_ano",         # <-- ADICIONADO
    "estrategia_plot": "aggregated",      # <-- ADICIONADO
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
    "nome_plot": "discentes_por_ano_ppg",         # <-- ADICIONADO
    "estrategia_plot": "aggregated",      # <-- ADICIONADO
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
    "nome_plot": "docentes_por_ano_ppg",         # <-- ADICIONADO
    "estrategia_plot": "aggregated",      # <-- ADICIONADO
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
    "nome_plot": "conceito_programa_por_ano", # <-- ADICIONADO
    "estrategia_plot": "direct",      # <-- ADICIONADO
    "tipo_grafico_padrao": "linha",
    "modelo": AnoPrograma,
    "titulo_base": "Evolução do Conceito CAPES do Programa",
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano da Avaliação",
    "eixo_x_tipo": "numerico_continuo",
    "eixo_y_campo": "cd_conceito_programa__cd_conceito_programa",
    "eixo_y_nome": "Conceito CAPES",
    "filtros": {
        "programa_id": "programa_id",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"ano_inicial": 2013},
    "yaxes_config": {
        "range": [0, 7.5],      # Define o intervalo do eixo Y de 0 a 7.5
        "tickmode": 'linear',   # Garante que os "ticks" (marcações) sejam lineares
        "tick0": 0,             # Começa a primeira marcação no 0
        "dtick": 1              # O intervalo entre cada marcação é 1 (0, 1, 2, ...)
    }
}

media_titulacao_por_ano_ppg = {
    "nome_plot": "media_titulacao_por_ano",  # <-- ADICIONADO
    "estrategia_plot": "aggregated",      # <-- ADICIONADO
    "modelo": Discente,
    "titulo_base": "Tempo Médio para Titulação",
    "eixo_x_campo": "ano__ano_valor",
    "eixo_x_nome": "Ano de Titulação",
    "eixo_x_tipo": "numerico_continuo",
    "eixo_y_campo": "qt_mes_titulacao",
    "eixo_y_nome": "Média de Meses",
    "eixo_y_agregacao": "avg",
    "filtros": {
        "programa_id": "programa_id",
        "situacao": "situacao__nm_situacao_discente",
        "grau_curso": "grau_academico__nm_grau_curso",
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
    },
    "filtros_padrao": {"situacao": "TITULADO", "ano_inicial": 2013},
    "agrupamentos": {
        "sexo": "pessoa__tp_sexo__sexo",
        "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
        "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
    },
    # Configuração para a aparência da "trace" (a barra/linha em si)
    "trace_config": {
        "texttemplate": "%{y:.1f}"  # Formata o texto na barra para 1 casa decimal
    },

    # Configuração para o tooltip (hover)
    "hover_config": {
        # Diz ao Plotly para incluir a coluna 'Contagem' nos dados de hover
        "custom_data_cols": ["Contagem"], 
        
        # Define o template do hover.
        # %{y:.1f} -> valor do eixo y, formatado com 1 casa decimal
        # %{customdata[0]} -> o primeiro item de 'custom_data_cols', ou seja, a Contagem
        "template": "<b>%{x}</b><br>Média: %{y} meses<br>Nº de Alunos: %{customdata[0]}<extra></extra>"
    },
}

discentes_por_area_sunburst = {
    "nome_plot": "discentes_por_area_sunburst", # <-- ADICIONADO
    "estrategia_plot": "hierarchical",      # <-- ADICIONADO
    "tipo_grafico": "sunburst",
    "modelo": Discente,
    "titulo_base": "Distribuição de Discentes por Área do Conhecimento",
    "grafico_hierarquico_path": {
        "Grande Área": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "Área de Conhecimento": "programa__ano_programa__area_conhecimento__nm_area_conhecimento",
    },
    "grafico_hierarquico_values_campo": "pessoa_id",
    "grafico_hierarquico_values_nome": "Quantidade",
    "grafico_hierarquico_agregacao": "count_distinct",
    "filtros": {"ano": "ano__ano_valor", "situacao": "situacao__nm_situacao_discente"},
    "filtros_padrao": {"ano": 2013},
}

docentes_por_area_sunburst = {
    "nome_plot": "docentes_por_area_sunburst", # <-- ADICIONADO
    "estrategia_plot": "hierarchical",      # <-- ADICIONADO
    "tipo_grafico": "sunburst",
    "modelo": Docente,
    "titulo_base": "Distribuição de Docentes por Área do Conhecimento",
    "grafico_hierarquico_path": {
        "Grande Área": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "Área de Conhecimento": "programa__ano_programa__area_conhecimento__nm_area_conhecimento",
    },
    "grafico_hierarquico_values_campo": "pessoa_id",
    "grafico_hierarquico_values_nome": "Quantidade",
    "grafico_hierarquico_agregacao": "count_distinct",
    "filtros": {"ano": "ano__ano_valor"},
    "filtros_padrao": {"ano": 2013},
}

top_paises_discentes = {
    "nome_plot": "top_paises_discentes",     # <-- ADICIONADO
    "estrategia_plot": "topn",            # <-- ADICIONADO
    "modelo": Discente,
    "titulo_base": "Top 10 Países de Procedência - Discentes",
    "ranking_campo_categoria": "pessoa__pais_nacionalidade__pais",
    "ranking_campo_valor": "pessoa_id",
    "ranking_agregacao": "count_distinct",
    "ranking_limite_padrao": 10,
    "filtros": {"limite": None, "ano": "ano__ano_valor"},
}

top_paises_docentes = {
    "nome_plot": "top_paises_docentes",      # <-- ADICIONADO
    "estrategia_plot": "topn",            # <-- ADICIONADO
    "modelo": Docente,
    "titulo_base": "Top 10 Países de Procedência - Docentes",
    "ranking_campo_categoria": "pessoa__pais_nacionalidade__pais",
    "ranking_campo_valor": "pessoa_id",
    "ranking_agregacao": "count_distinct",
    "ranking_limite_padrao": 10,
    "filtros": { "limite": None },
}

programas_contagem_por_ano = {
    "nome_plot": "programas_contagem_por_ano", # Nome público único para URL/template
    "estrategia_plot": "aggregated",      # Usamos a estratégia existente!
    #"tipo_grafico_padrao": "linha",         # Começa como linha
    "modelo": AnoPrograma,                # <<< Fonte principal dos dados
    "titulo_base": "Número de Programas Registrados", # Título mais preciso
    "eixo_x_campo": "ano__ano_valor",     # Agruparemos pelo ano do registro
    "eixo_x_nome": "Ano do Registro",
    "eixo_x_tipo": "numerico_continuo",   # Ajuda o Plotly a desenhar linhas
    "eixo_y_campo": "programa_id",        # <<< O que queremos contar
    "eixo_y_nome": "Número de Programas",
    "eixo_y_agregacao": "count_distinct", # <<< A operação: contar programas únicos por ano
    
    # Filtros que o usuário poderá aplicar (diretamente nos campos de AnoPrograma)
    "filtros": {
        "ano_inicial": "ano__ano_valor__gte",
        "ano_final": "ano__ano_valor__lte",
        "modalidade": "nm_modalidade_programa__nm_modalidade_programa",
        "grande_area": "grande_area__nm_grande_area_conhecimento", # Adicionando filtro por área
        # Adicione outros filtros se desejar (ex: area_avaliacao)
    },

    # Filtro padrão sugerido: contar apenas programas ativos por padrão
    "filtros_padrao": {
    },

    # Agrupamento que o usuário poderá escolher
    "agrupamentos": {
        "conceito": "cd_conceito_programa__cd_conceito_programa",
        "in_rede": "in_rede",
    },
}



# =============================================================================
# DICIONÁRIO FINAL - Importado pelas classes de Plots
# =============================================================================
MAPEAMENTOS = {
    # Gráficos Gerais
    "discentes_geral": discentes_geral_por_ano,
    "docentes_geral": docentes_geral_por_ano,
    "discentes_sunburst": discentes_por_area_sunburst,
    "docentes_sunburst": docentes_por_area_sunburst,
    "top_paises_discentes": top_paises_discentes,
    "top_paises_docentes": top_paises_docentes,

    # Gráficos para todas as PPGs da UFRJ
    "programas_contagem": programas_contagem_por_ano,


    # Gráficos Específicos de um PPG
    "discentes_ppg": discentes_por_ano_ppg,
    "docentes_ppg": docentes_por_ano_ppg,
    "conceito_ppg": conceito_programa_por_ano,
    "media_titulacao": media_titulacao_por_ano_ppg,
}