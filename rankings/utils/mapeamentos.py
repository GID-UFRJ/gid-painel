# rankings/utils/mapeamentos.py
from rankings.models import RankingEntrada
import datetime

# Define o ano atual dinamicamente
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

    "filtros": {
        "ranking_nome": "ranking__nome",
        "escopo": "escopo_geografico__nome",
        "ano_inicial": "ano__gte",
        "ano_final": "ano__lte",
        "tipo_ranking": "ranking__tipo__nome",
        "ods": "ods__codigo",
    },
    
    "agrupamentos": {
        "ranking": "ranking__nome",
        "escopo": "escopo_geografico__nome",
        "ods": "ods__codigo",
    },
}

# --- Variação 1: Acadêmico ---
ranking_academico_faixa = _config_faixa_base.copy()
ranking_academico_faixa.update({
    "nome_plot": "academico_faixa",
    "filtros_padrao": {
        "tipo_ranking": "ACADÊMICO",
        "ranking_nome": "THE",
        "ano_inicial": 2018,
        "ano_final": ano_atual,
        "escopo": "MUNDO",
    }
})

# --- Variação 2: Sustentabilidade ---
ranking_sustentabilidade_faixa = _config_faixa_base.copy()
ranking_sustentabilidade_faixa.update({
    "nome_plot": "sustentabilidade_faixa",
    "filtros_padrao": {
        "tipo_ranking": "SUSTENTABILIDADE",
        "ranking_nome": "THE IMPACT", 
        #"ods__isnull": True,
        "ano_inicial": 2019,
        "ano_final": ano_atual,
        "escopo": "MUNDO",
    }
})


# =========================================================
# DICIONÁRIOS POR PÁGINA (Para uso nas Views de cada página)
# =========================================================

MAPEAMENTOS_RANKINGS_ACADEMICOS = {
    "academico_faixa": ranking_academico_faixa,
}

MAPEAMENTOS_RANKINGS_SUSTENTABILIDADE = {
    "sustentabilidade_faixa": ranking_sustentabilidade_faixa,
}


# =========================================================
# DICIONÁRIO MESTRE (Para o motor de CSV e Dispatcher Global)
# =========================================================

# O operador ** extrai tudo dos dicionários menores e combina num só
MAPEAMENTOS_TODOS = {
    **MAPEAMENTOS_RANKINGS_ACADEMICOS,
    **MAPEAMENTOS_RANKINGS_SUSTENTABILIDADE,
}