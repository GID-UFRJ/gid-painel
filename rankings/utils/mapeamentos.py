# rankings/utils/mapeamentos.py
from rankings.models import RankingEntrada

# Receita para Rankings Acadêmicos
evolucao_ranking_academico = {
    "modelo": RankingEntrada,
    "titulo_base": "Evolução da Posição no Ranking",
    
    "eixo_x_campo": "ano",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "posicao_minima", # Usamos a posição mínima como referência
    "eixo_y_nome": "Posição (Menor é Melhor)",
    "eixo_y_agregacao": "min", # Queremos o valor exato (ou o mínimo se houver duplicidade estranha)

    "filtros": {
        "ranking_nome": "ranking__nome",
        "escopo": "escopo_geografico__nome",
        "ano_inicial": "ano__gte",
        "ano_final": "ano__lte",
        # Filtro fixo para garantir que só pegamos acadêmicos
        "tipo_ranking": "ranking__tipo__nome", 
    },
    "filtros_padrao": {
        "tipo_ranking": "ACADÊMICO",
        "ano_inicial": 2018,
    },
    "agrupamentos": {
        "ranking": "ranking__nome", # Para comparar diferentes rankings (ex: THE vs QS)
        "escopo": "escopo_geografico__nome",
    },
}

# Receita para Rankings de Sustentabilidade (Com ODS)
evolucao_ranking_sustentabilidade = {
    "modelo": RankingEntrada,
    "titulo_base": "Desempenho em Sustentabilidade (ODS)",
    
    "eixo_x_campo": "ano",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_campo": "posicao_minima",
    "eixo_y_nome": "Posição",
    "eixo_y_agregacao": "min",

    "filtros": {
        "ranking_nome": "ranking__nome",
        "ods": "ods__codigo", # Filtro extra importante aqui!
        "ano_inicial": "ano__gte",
        "ano_final": "ano__lte",
        "tipo_ranking": "ranking__tipo__nome",
    },
    "filtros_padrao": {
        "tipo_ranking": "SUSTENTABILIDADE",
        "ano_inicial": 2019,
    },
    "agrupamentos": {
        "ods": "ods__codigo", # Para comparar performance entre diferentes ODS
        "ranking": "ranking__nome",
    },
}

MAPEAMENTOS = {
    "ranking_academico_evolucao": evolucao_ranking_academico,
    "ranking_sustentabilidade_evolucao": evolucao_ranking_sustentabilidade,
}