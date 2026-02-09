# homepage/utils/mapeamentos.py
from sucupira.models import Docente, Programa, Discente, AnoPrograma
from openalex.models import Work
from django.db.models import Q
from rankings.models import RankingEntrada

ID_UFRJ = "I122140584"
cor_profissional =  '#ff0000'
cor_mestrado =  '#00ff00'
cor_doutorado = '#0000ff'

MAPEAMENTOS = {

    # Total de documentos publicados (Geral)
    "kpi_total_documentos": {
        "nome_plot": "kpi_total_documentos",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Total de Documentos",
        "icone": "fas fa-file-alt",
        "cor": "#6c757d",
        "eixo_y_campo": "work_id",
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
    },

    # Total de artigos publicados em periódicos ('article')
    "kpi_total_artigos": {
        "nome_plot": "kpi_total_artigos",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Artigos em Periódicos",
        "icone": "fas fa-newspaper",
        "cor": "#007bff",
        "eixo_y_campo": "work_id",
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
        "filtros_padrao": {"worktype__worktype": "article"},
    },

    # Total de artigos publicados em acesso aberto (is_oa=True)
    "kpi_total_oa": {
        "nome_plot": "kpi_total_oa",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Artigos em Acesso Aberto",
        "icone": "fas fa-lock-open",
        "cor": "#28a745",
        "eixo_y_campo": "work_id",
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
        "filtros_padrao": {"is_oa": True},
    },

    # Total de citações recebidas por artigos
    "kpi_total_citacoes_artigos": {
        "nome_plot": "kpi_total_citacoes_artigos",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Citações (Artigos)",
        "icone": "fas fa-quote-right",
        "cor": "#fd7e14",
        "eixo_y_campo": "cited_by_count",
        "eixo_y_agregacao": "sum",
        "formatacao": "magnitude",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
        "filtros_padrao": {"worktype__worktype": "article"},
    },

    # KPI: Colaboração Nacional (Pelo menos um parceiro BR além da UFRJ)
    "kpi_colaboracao_nacional": {
        "nome_plot": "kpi_colaboracao_nacional",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Colaboração Nacional",
        "icone": "fas fa-map-marked-alt",
        "cor": "#28a745",
        "eixo_y_campo": "work_id",
        "eixo_y_agregacao": "count_distinct",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
        "filtros_padrao": {
            # 1. Filtramos trabalhos que possuem a UFRJ (para garantir que é da casa)
            "ufrj": Q(authorship__authorshipinstitution__institution__institution_id=ID_UFRJ),
            # 2. E que possuem OUTRA instituição brasileira
            "parceiro_br": Q(authorship__authorshipinstitution__institution__country_code="BR") & 
                          ~Q(authorship__authorshipinstitution__institution__institution_id=ID_UFRJ)
        },
    },

    # KPI: Colaboração Internacional (Pelo menos um parceiro fora do BR)
    "kpi_colaboracao_internacional": {
        "nome_plot": "kpi_colaboracao_internacional",
        "estrategia_plot": "kpi",
        "modelo": Work,
        "titulo_base": "Colaboração Internacional",
        "icone": "fas fa-globe-americas",
        "cor": "#6f42c1",
        "eixo_y_campo": "work_id",
        "eixo_y_agregacao": "count_distinct",
        "filtrar_ultimo_ano": False,
        "mostrar_periodo": "pubyear__year",
        "filtros_padrao": {
            # 1. Filtramos trabalhos que possuem a UFRJ
            "ufrj": Q(authorship__authorshipinstitution__institution__institution_id=ID_UFRJ),
            # 2. E que possuem pelo menos uma instituição estrangeira
            "parceiro_estrangeiro": ~Q(authorship__authorshipinstitution__institution__country_code="BR")
        },
    },

    # KPI: Total de Docentes (Consumindo do app Sucupira)
    "kpi_docentes_home": {
        "nome_plot": "kpi_docentes_ufrj",
        "estrategia_plot": "kpi",
        "modelo": Docente,
        "titulo_base": "Docentes Ativos",
        "icone": "fas fa-chalkboard-teacher",
        "cor": "#4169E1",
        
        # IMPORTANTE: Para contar professores únicos, agregamos sobre a FK de Pessoa
        "eixo_y_campo": "pessoa_id", 
        "eixo_y_agregacao": "count_distinct",
        
        #"formatacao": "magnitude",
        "__tipo_entidade__": "sucupira_docente",
        
        # Lógica de Automação:
        "mostrar_periodo": "ano_id",       # Usa a PK do Ano para descobrir o período
        "filtrar_ultimo_ano": True,        # Ativa a busca pelo Max(ano_id) no banco
        
        "filtros": {},         # Vazio, pois você não quer filtros manuais agora
        "filtros_padrao": {},  # Vazio, para não travar em 2024
    },


    # Total de docentes bolsistas
    "kpi_docentes_bolsistas": {
        "nome_plot": "kpi_docentes_bolsistas",
        "estrategia_plot": "kpi",
        "modelo": Docente,
        "titulo_base": "Bolsistas de Produtividade",
        "icone": "fas fa-award", # Ícone de medalha/prêmio
        "cor": "#FFD700", # Dourado
        "eixo_y_campo": "pessoa_id",
        "eixo_y_agregacao": "count_distinct",
        #"formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        # O pulo do gato: filtramos onde o campo de bolsa não é nulo
        "filtros_padrao": {"bolsa_produtividade__isnull": False},
        "filtros": {},
    },

    #Docentes Dedicação Exclusiva
    "kpi_docentes_de": {
        "nome_plot": "kpi_docentes_de",
        "estrategia_plot": "kpi",
        "modelo": Docente,
        "titulo_base": "Docentes em Dedicação Exclusiva",
        "icone": "fas fa-briefcase",
        "cor": "#dc3545", # Vermelho para destaque
        "eixo_y_campo": "pessoa_id",
        "eixo_y_agregacao": "count_distinct",
        "filtrar_ultimo_ano": True,
        "mostrar_periodo": "ano_id",
        "filtros_padrao": {"regime_trabalho__ds_regime_trabalho": "DEDICAÇÃO EXCLUSIVA"}, # Ajuste para o valor exato no seu banco
    },

    #Docentes estrangeiros
    "kpi_docentes_estrangeiros": {
        "nome_plot": "kpi_docentes_estrangeiros",
        "estrategia_plot": "kpi",
        "modelo": Docente,
        "titulo_base": "Docentes Estrangeiros",
        "icone": "fas fa-globe-americas",
        "cor": "#6f42c1", # Roxo
        "eixo_y_campo": "pessoa_id",
        "eixo_y_agregacao": "count_distinct",
        "filtrar_ultimo_ano": True,
        "mostrar_periodo": "ano_id",
        # Filtra onde o país não é Brasil (ajuste o nome do país conforme sua tabela PessoaPais)
        "filtros_padrao": {
            # Usamos ~Q para dizer "NÃO é Brasil"
            "estrangeiro": ~Q(pessoa__pais_nacionalidade__pais="BRASIL")
        },
    },

    # KPI: Total de Programas
    "kpi_programas_home": {
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
        "mostrar_periodo": "ano_programa__ano_id",
        "filtrar_ultimo_ano": True,
    },

    # KPI: Programas com Conceito Máximo (7)
    "kpi_programas_nota_7": {
        "nome_plot": "kpi_programas_nota_7",
        "estrategia_plot": "kpi",
        "modelo": AnoPrograma,
        "titulo_base": "Programas Nota 7",
        "icone": "fas fa-trophy",
        "cor": "#FFD700", # Dourado
        "eixo_y_campo": "programa_id",
        "eixo_y_agregacao": "count_distinct",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {"cd_conceito_programa__cd_conceito_programa": 7},
        "filtros": {},
    },

    # KPI: Total de Programas Acadêmicos
    "kpi_programas_academicos": {
        "nome_plot": "kpi_programas_academicos",
        "estrategia_plot": "kpi",
        "modelo": AnoPrograma,
        "titulo_base": "Programas Acadêmicos",
        "icone": "fas fa-university",
        "cor": "#0d6efd",
        "eixo_y_campo": "programa_id",
        "eixo_y_agregacao": "count_distinct",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {"nm_modalidade_programa__nm_modalidade_programa": "ACADÊMICO"},
        "filtros": {},
    },

    # KPI: Total de Programas Profissionais
    "kpi_programas_profissionais": {
        "nome_plot": "kpi_programas_profissionais",
        "estrategia_plot": "kpi",
        "modelo": AnoPrograma,
        "titulo_base": "Programas Profissionais",
        "icone": "fas fa-user-tie",
        "cor": "#198754",
        "eixo_y_campo": "programa_id",
        "eixo_y_agregacao": "count_distinct",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {"nm_modalidade_programa__nm_modalidade_programa": "PROFISSIONAL"},
        "filtros": {},
    },

"kpi_media_titulacao_doutorado": {
        "nome_plot": "kpi_media_titulacao_doutorado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Média Titulação Doutorado",
        "icone": "fas fa-hourglass-half",
        "cor": "#20c997",
        "eixo_y_campo": "qt_mes_titulacao",
        "eixo_y_agregacao": "avg",
        "sufixo": "meses", # Adiciona a unidade no card
        "formatacao": "decimal", # Para mostrar ex: 44.5
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {
            "situacao__nm_situacao_discente": "TITULADO",
            "grau_academico__nm_grau_curso": "DOUTORADO"
        },
        "filtros": {},
    },

    "kpi_media_titulacao_mestrado": {
        "nome_plot": "kpi_media_titulacao_mestrado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Média Titulação Mestrado",
        "icone": "fas fa-hourglass-half",
        "cor": "#17a2b8",
        "eixo_y_campo": "qt_mes_titulacao",
        "eixo_y_agregacao": "avg",
        "sufixo": "meses",
        "formatacao": "decimal",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {
            "situacao__nm_situacao_discente": "TITULADO",
            "grau_academico__nm_grau_curso": "MESTRADO"
        },
        "filtros": {},
    },

    "kpi_media_titulacao_profissional": {
        "nome_plot": "kpi_media_titulacao_profissional",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Média Titulação M. Profissional",
        "icone": "fas fa-hourglass-half",
        "cor": "#6c757d",
        "eixo_y_campo": "qt_mes_titulacao",
        "eixo_y_agregacao": "avg",
        "sufixo": "meses",
        "formatacao": "decimal",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True,
        "filtros_padrao": {
            "situacao__nm_situacao_discente": "TITULADO",
            "grau_academico__nm_grau_curso": "MESTRADO PROFISSIONAL"
        },
        "filtros": {},
    },


    # --- TITULADOS (HISTÓRICO ACUMULADO) ---
    "kpi_titulados_doutorado": {
        "nome_plot": "kpi_titulados_doutorado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Egressos Doutorado",
        "icone": "fas fa-user-graduate",
        "cor": cor_doutorado,
        "eixo_y_campo": "pessoa_id",
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": False, # Queremos o histórico todo
        "filtros_padrao": {"situacao__nm_situacao_discente": "TITULADO", "grau_academico__nm_grau_curso": "DOUTORADO"},
        "filtros": {},
    },

    "kpi_titulados_mestrado": {
        "nome_plot": "kpi_titulados_mestrado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Egressos Mestrado",
        "icone": "fas fa-user-graduate",
        "cor": cor_mestrado,
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtros_padrao": {"situacao__nm_situacao_discente": "TITULADO", "grau_academico__nm_grau_curso": "MESTRADO"},
        "filtros": {},
    },

    "kpi_titulados_profissional": {
        "nome_plot": "kpi_titulados_profissional",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Egressos Mestrado Profissional",
        "icone": "fas fa-user-graduate",
        "cor": cor_profissional,
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtros_padrao": {"situacao__nm_situacao_discente": "TITULADO", "grau_academico__nm_grau_curso": "MESTRADO PROFISSIONAL"},
        "filtros": {},
    },


    # --- MATRICULADOS (APENAS ÚLTIMO ANO) ---
    "kpi_matriculados_doutorado": {
        "nome_plot": "kpi_matriculados_doutorado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Matriculados Doutorado",
        "icone": "fas fa-user-clock",
        "cor": cor_doutorado,
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True, # Apenas o ano mais recente da DB
        "filtros_padrao": {"situacao__nm_situacao_discente": "MATRICULADO", "grau_academico__nm_grau_curso": "DOUTORADO"},
        "filtros": {},
    },

    # --- MATRICULADOS (APENAS ÚLTIMO ANO) ---
    "kpi_matriculados_mestrado": {
        "nome_plot": "kpi_matriculados_mestrado",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Matriculados Mestrado",
        "icone": "fas fa-user-clock",
        "cor": cor_mestrado,
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True, # Apenas o ano mais recente da DB
        "filtros_padrao": {"situacao__nm_situacao_discente": "MATRICULADO", "grau_academico__nm_grau_curso": "MESTRADO"},
        "filtros": {},
    },


    # --- MATRICULADOS (APENAS ÚLTIMO ANO) ---
    "kpi_matriculados_profissional": {
        "nome_plot": "kpi_matriculados_profissional",
        "estrategia_plot": "kpi",
        "modelo": Discente,
        "titulo_base": "Matriculados Mestrado Profissional",
        "icone": "fas fa-user-clock",
        "cor": cor_profissional,
        "eixo_y_agregacao": "count_distinct",
        "formatacao": "magnitude",
        "mostrar_periodo": "ano_id",
        "filtrar_ultimo_ano": True, # Apenas o ano mais recente da DB
        "filtros_padrao": {"situacao__nm_situacao_discente": "MATRICULADO", "grau_academico__nm_grau_curso": "MESTRADO PROFISSIONAL"},
        "filtros": {},
    },

"kpi_posicao_qs_latam": {
        "nome_plot": "kpi_posicao_qs_latam",
        "estrategia_plot": "ranking_kpi",
        "modelo": RankingEntrada,
        "titulo_base": "QS América Latina",
        "icone": "fas fa-medal",
        "cor": "#1a4789",
        "eixo_y_campo": "posicao_minima",
        "eixo_y_agregacao": "min",
        "sufixo": "º",
        "filtrar_ultimo_ano": True,
        "mostrar_periodo": "ano",
        "filtros_padrao": {
            "ranking__nome": "QS",
            "ranking__tipo__nome__icontains": "ACADÊMICO", # Especifica o tipo 1
            "escopo_geografico__nome__icontains": "LATINA",
            #"ods__isnull": True
        },
        "filtros": {},
    },

 "kpi_posicao_the_latam": {
         "nome_plot": "kpi_posicao_the_latam",
         "estrategia_plot": "ranking_kpi",
         "modelo": RankingEntrada,
         "titulo_base": "THE América Latina",
         "icone": "fas fa-award",
         "cor": "#e6192e",
         "mostrar_periodo": "ano",
         "filtrar_ultimo_ano": True,
         "filtros_padrao": {
             # Verifique se o nome do ranking não é apenas "THE", 
             # mas sim "THE Latin America" no seu banco
             "ranking__nome": "THE", 
             "escopo_geografico__nome__icontains": "LATINA",
             #"ods__isnull": True
         },
         # Se sua estratégia aceitar, force o campo de valor:
         "valor_field": "posicao_absoluta", 
     },

}