# homepage/utils/mapeamentos.py
from sucupira.models import Docente, Programa, Discente

# KPI: Total de Docentes (Consumindo do app Sucupira)
kpi_docentes_home = {
    "nome_plot": "kpi_docentes_ufrj",
    "estrategia_plot": "kpi",
    "modelo": Docente,
    "titulo_base": "Docentes Ativos",
    "icone": "fas fa-chalkboard-teacher",
    "cor": "#4169E1",
    "eixo_y_campo": "id",
    "eixo_y_agregacao": "count_distinct",
    "formatacao": "magnitude",
    "filtros": {
        "grande_area": "programa__ano_programa__grande_area__nm_grande_area_conhecimento",
        "ano": "ano__ano_valor",
    },
    "filtros_padrao": {"ano": 2024},
    "__tipo_entidade__": "sucupira_docente", # Importante para o seu _get_base_queryset
}

# KPI: Total de Programas
kpi_programas_home = {
    "nome_plot": "kpi_programas_ufrj",
    "estrategia_plot": "kpi",
    "modelo": Programa,
    "titulo_base": "Programas de Pós",
    "icone": "fas fa-graduation-cap",
    "cor": "#198754",
    "eixo_y_campo": "id",
    "eixo_y_agregacao": "count_distinct",
    "filtros": {},
    "filtros_padrao": {},
    "__tipo_entidade__": "sucupira_programa",
}

MAPEAMENTOS = {
    "kpi_docentes": kpi_docentes_home,
    "kpi_programas": kpi_programas_home,
}