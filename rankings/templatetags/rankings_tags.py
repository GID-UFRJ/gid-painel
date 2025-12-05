# rankings/templatetags/rankings_tags.py
from django import template
from rankings.models import Ranking, EscopoGeografico, ODS

register = template.Library()
PATH_FILTROS = "common/partials/filtros/"

@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_rankings(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    ctx = { "url_grafico": url_grafico, "grafico_id": grafico_id, "spinner_id": spinner_id, "grafico_html": grafico_html }
    lista = []

    # Filtros comuns de data e agrupamento
    base_filters = [
        f"{PATH_FILTROS}_filtro_ano_inicial.html",
        f"{PATH_FILTROS}_filtro_ano_final.html",
    ]

    if tipo == "academico":
        lista = base_filters + [
            f"{PATH_FILTROS}_filtro_ranking_nome.html",
            f"{PATH_FILTROS}_filtro_ranking_escopo.html",
        ]
        # Contexto específico (apenas rankings acadêmicos no dropdown)
        ctx["rankings"] = Ranking.objects.filter(tipo__nome="ACADÊMICO")
        ctx["escopos"] = EscopoGeografico.objects.all()

    elif tipo == "sustentabilidade":
        lista = base_filters + [
            f"{PATH_FILTROS}_filtro_ranking_nome.html",
            f"{PATH_FILTROS}_filtro_ranking_ods.html",
        ]
        ctx["rankings"] = Ranking.objects.filter(tipo__nome="SUSTENTABILIDADE")
        ctx["odss"] = ODS.objects.all() # Cuidado com o nome da variavel no template

    else:
        raise ValueError(f"Tipo inválido: {tipo}")

    ctx['lista_de_filtros'] = lista
    return ctx