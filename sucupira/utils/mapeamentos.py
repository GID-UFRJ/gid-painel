# sucupira/utils/mapeamentos.py

from sucupira.models import *

MAPEAMENTOS = {
    "discentes": {
        "modelo": Discente,
        "titulo": "Discentes por Ano",
        "agrupamentos": {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        },
        "filtros": {
            "situacao": "situacao__nm_situacao_discente",
            "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento", 
            "grau_curso": "grau_academico__nm_grau_curso",
        },
        "campo_agregacao": "pessoa_id", #Conta pessoas únicas
        "titulo_base": "Discentes",
    },

    "docentes": {
        "modelo": Docente,
        "titulo": "Docentes por Ano",
        "agrupamentos": {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        },
        "filtros": {
            "categoria_docente": "categoria__ds_categoria_docente",
            "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento", 
            "modalidade_programa": "programa__ano_programa__nm_modalidade_programa__nm_modalidade_programa",
            "bolsa_produtividade": "bolsa_produtividade__cd_cat_bolsa_produtividade",
        },
        "campo_agregacao": "pessoa_id",  # Ajuste conforme necessário
        "titulo_base": "Docentes",
    },

    "discentes_ppg": {
        "modelo": Discente,
        "titulo": "Discentes por Ano",
        "agrupamentos": {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        },
        "filtros": {
            "situacao": "situacao__nm_situacao_discente",
            "grau_curso": "grau_academico__nm_grau_curso",
            'programa_id': 'programa_id',
        },
        "campo_agregacao": "pessoa_id", #Conta pessoas únicas
        "titulo_base": "Discentes",
    },

    "docentes_ppg": {
        "modelo": Docente,
        "titulo": "Docentes por Ano",
        "agrupamentos": {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        },
        "filtros": {
            "categoria_docente": "categoria__ds_categoria_docente",
            "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento", 
            "bolsa_produtividade": "bolsa_produtividade__cd_cat_bolsa_produtividade",
            'programa_id': 'programa_id',

        },
        "campo_agregacao": "pessoa_id",  # Ajuste conforme necessário
        "titulo_base": "Docentes",
    },

    "media_titulacao_ppg": {
        "modelo": Discente,
        "titulo": "Média de Meses para a Titulação por Ano",
        "agrupamentos": {
            "sexo": "pessoa__tp_sexo__sexo",
            "nacionalidade": "pessoa__tipo_nacionalidade__ds_tipo_nacionalidade", 
            "faixa_etaria": "faixa_etaria__ds_faixa_etaria",
        },
        "filtros": {
            'programa_id': 'programa_id',
            
        },
        "agregação" : "avg",
        "campo_agregacao": "qt_mes_titulacao", 
        "titulo_base": "Discentes",
    },

    "conceito_programa": {
        "modelo": AnoPrograma,
        "titulo": "Evolução do Conceito do Programa",
        "agrupamentos": {
        },
        "filtros": {
            'programa_id': 'programa_id',
        },
        "agregação" : "avg",
        "campo_agregacao": "qt_mes_titulacao", #Conta pessoas únicas
        "titulo_base": "Discentes",
    },
}