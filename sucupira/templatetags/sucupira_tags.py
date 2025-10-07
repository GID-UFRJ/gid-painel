# sucupira/templatetags/sucupira_tags.py

from django import template
from sucupira.models import (
    ProgramaGrandeArea, GrauCurso, DiscenteSituacao,
    ProgramaModalidade, DocenteCategoria, DocenteBolsaProdutividade, Ano
)

register = template.Library()

# Caminho base para os filtros atômicos para evitar repetição
PATH_FILTROS_ATOMicos = "common/partials/filtros/"

# =============================================================================
# TAG PARA A SEÇÃO "PESSOAL" (GERAL)
# =============================================================================
@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_pessoal(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Monta o formulário de filtros para a seção "Pessoal" compondo filtros atômicos.
    """
    ctx = { "url_grafico": url_grafico, "grafico_id": grafico_id, "spinner_id": spinner_id, "grafico_html": grafico_html }
    
    lista_de_filtros = []

    if tipo == "discentes":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_agrupamento.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_grande_area.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_grau_curso.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_situacao.html",
        ]
        ctx.update({
            "grandes_areas": ProgramaGrandeArea.objects.all(), "graus_curso": GrauCurso.objects.all(),
            "situacoes": DiscenteSituacao.objects.all(),
        })

    elif tipo == "docentes":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_agrupamento.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_grande_area.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_modalidade.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_categoria_docente.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_bolsa_produtividade.html",
        ]
        ctx.update({
            "grandes_areas": ProgramaGrandeArea.objects.all(), "modalidades": ProgramaModalidade.objects.all(),
            "categorias": DocenteCategoria.objects.all(), "bolsas": DocenteBolsaProdutividade.objects.all(),
        })

    elif tipo == 'sunburst':
        lista_de_filtros = [ f"{PATH_FILTROS_ATOMicos}_filtro_ano_unico.html" ]
        ctx.update({"anos_disponiveis": Ano.objects.all().order_by('-ano_valor')})

    else:
        raise ValueError(f"Tipo de filtro inválido para 'pessoal': {tipo}")

    ctx['lista_de_filtros'] = lista_de_filtros
    return ctx


# =============================================================================
# TAG PARA A SEÇÃO "PPG DETALHE"
# =============================================================================
@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_ppg_detalhe(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Monta o formulário de filtros para a seção "PPG Detalhe" compondo filtros atômicos.
    """
    ctx = { "url_grafico": url_grafico, "grafico_id": grafico_id, "spinner_id": spinner_id, "grafico_html": grafico_html }
    
    lista_de_filtros = []

    if tipo == "discentes":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html", f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_tipo_grafico.html", f"{PATH_FILTROS_ATOMicos}_filtro_agrupamento.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_grau_curso.html", f"{PATH_FILTROS_ATOMicos}_filtro_situacao.html",
        ]
        ctx.update({"graus_curso": GrauCurso.objects.all(), "situacoes": DiscenteSituacao.objects.all()})

    elif tipo == "docentes":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html", f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_tipo_grafico.html", f"{PATH_FILTROS_ATOMicos}_filtro_agrupamento.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_categoria_docente.html", f"{PATH_FILTROS_ATOMicos}_filtro_bolsa_produtividade.html",
        ]
        ctx.update({"categorias": DocenteCategoria.objects.all(), "bolsas": DocenteBolsaProdutividade.objects.all()})

    elif tipo == "media_titulacao":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html", f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMicos}_filtro_agrupamento.html", f"{PATH_FILTROS_ATOMicos}_filtro_grau_curso.html",
        ]
        ctx.update({"graus_curso": GrauCurso.objects.all()})
    
    elif tipo == "conceito_programa":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMicos}_filtro_ano_inicial.html", f"{PATH_FILTROS_ATOMicos}_filtro_ano_final.html",
        ]

    else:
        raise ValueError(f"Tipo de filtro inválido para 'ppg_detalhe': {tipo}")
        
    ctx['lista_de_filtros'] = lista_de_filtros
    return ctx