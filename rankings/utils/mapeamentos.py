# rankings/utils/mapeamentos.py
from rankings.models import RankingEntrada

import datetime

# Define o ano atual dinamicamente (ex: 2025)
ano_atual = datetime.date.today().year + 1

# --- Configuração Base (DRY: Don't Repeat Yourself) ---
# Definimos as configurações comuns de eixos para não repetir código
_config_faixa_base = {
    "estrategia_plot": "faixa", 
    "modelo": RankingEntrada,
    "titulo_base": "Evolução da Posição",
    
    "eixo_x_campo": "ano",
    "eixo_x_nome": "Ano",
    "eixo_x_tipo": "numerico_continuo",

    "eixo_y_min": "posicao_minima",
    "eixo_y_max": "posicao_maxima",
    "eixo_y_nome": "Posição",
    "eixo_y_invertido": True, # Inverte o eixo Y (1º lugar no topo)

    # Filtros disponíveis para a URL
    "filtros": {
        "ranking_nome": "ranking__nome",
        "escopo": "escopo_geografico__nome",
        "ano_inicial": "ano__gte",
        "ano_final": "ano__lte",
        "tipo_ranking": "ranking__tipo__nome",
        "ods": "ods__codigo",
    },
    
    # Agrupamentos disponíveis (caso venha a agrupar algo no futuro)
    "agrupamentos": {
        "ranking": "ranking__nome",
        "escopo": "escopo_geografico__nome",
        "ods": "ods__codigo",
    },
}

# --- Variação 1: Acadêmico ---
ranking_academico_faixa = _config_faixa_base.copy()

ranking_academico_faixa["nome_plot"] = "academico_faixa"

ranking_academico_faixa["filtros_padrao"] = {
    "tipo_ranking": "ACADÊMICO",
    "ano_inicial": 2018,
    "ano_final":ano_atual,
    "escopo": "MUNDO",
    # No acadêmico, o agrupamento padrão é por Ranking
}

# --- Variação 2: Sustentabilidade ---
ranking_sustentabilidade_faixa = _config_faixa_base.copy()

ranking_sustentabilidade_faixa["nome_plot"] = "sustentabilidade_faixa"

ranking_sustentabilidade_faixa["filtros_padrao"] = {
    "tipo_ranking": "SUSTENTABILIDADE",
    "ranking_nome": "THE IMPACT", # Default seguro para ODS
    "ano_inicial": 2019,
    "ano_final":ano_atual,
    "escopo": "MUNDO",

    # Na sustentabilidade, geralmente queremos comparar ODSs, mas o padrão aqui pode ser ranking
}

MAPEAMENTOS = {
    # Nomes internos que usaremos no PlotsRankings
    "academico_faixa": ranking_academico_faixa,
    "sustentabilidade_faixa": ranking_sustentabilidade_faixa,
}