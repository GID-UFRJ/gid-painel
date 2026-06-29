# rankings/templatetags/rankings_tags.py
from django import template
from django.db.models import Max
from rankings.models import Ranking, EscopoGeografico, ODS, RankingEntrada

register = template.Library()
PATH_FILTROS = "common/partials/filtros/"


@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_rankings(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html, plotter_name="rankings", nome_plot=None): 
    ctx = { 
        "url_grafico": url_grafico, 
        "grafico_id": grafico_id, 
        "spinner_id": spinner_id, 
        "grafico_html": grafico_html,
        "plotter_name": plotter_name,
        "nome_plot": nome_plot
    }

    lista = []

    # Filtros comuns de data e agrupamento
    base_filters = [
        f"{PATH_FILTROS}_filtro_ano_inicial.html",
        f"{PATH_FILTROS}_filtro_ano_final.html",
    ]

    if tipo == "academico":
        max_ano_db = RankingEntrada.objects.filter(
        ranking__tipo__nome__in=["ACADÊMICO", "SUSTENTABILIDADE"]
        ).aggregate(Max('ano'))['ano__max']

        lista = base_filters + [
            f"{PATH_FILTROS}_filtro_ranking_nome.html",
            f"{PATH_FILTROS}_filtro_ranking_escopo.html",
        ]
        # Contexto específico (apenas rankings acadêmicos no dropdown)
        ctx["rankings"] = Ranking.objects.filter(tipo__nome="ACADÊMICO")
        ctx["escopos"] = EscopoGeografico.objects.all()
        ctx["ano_final_padrao"] = max_ano_db

    elif tipo == "sustentabilidade":
        max_ano_db = RankingEntrada.objects.filter(
        ranking__tipo__nome__in=["ACADÊMICO", "SUSTENTABILIDADE"]
        ).aggregate(Max('ano'))['ano__max']


        lista = base_filters + [
            f"{PATH_FILTROS}_filtro_ranking_nome.html",
            f"{PATH_FILTROS}_filtro_ranking_escopo.html",
            f"{PATH_FILTROS}_filtro_ranking_ods.html",
        ]
        ctx["rankings"] = Ranking.objects.filter(tipo__nome="SUSTENTABILIDADE")
        ctx["escopos"] = EscopoGeografico.objects.all()
        ctx["odss"] = ODS.objects.all() # Cuidado com o nome da variavel no template
        ctx["escopo_padrao"] = "MUNDO" 
        ctx["ano_final_padrao"] = max_ano_db

    else:
        raise ValueError(f"Tipo inválido: {tipo}")

    ctx['lista_de_filtros'] = lista
    return ctx