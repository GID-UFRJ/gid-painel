from django import template
from sucupira.models import (
    ProgramaGrandeArea, GrauCurso, DiscenteSituacao,
    ProgramaModalidade, DocenteCategoria, DocenteBolsaProdutividade
)

register = template.Library()


@register.inclusion_tag("sucupira/partials/pessoal/_filtros_pessoal_por_ano.html")
def render_filtros_pessoal(tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Templatetag genérica para renderizar filtros de docentes ou discentes.
    Mantém partials separados, mas evita duplicação de código.
    """
    #contexto geral
    context = {
        # filtros comuns a todos os gráficos
        "grandes_areas": ProgramaGrandeArea.objects.all().order_by("nm_grande_area_conhecimento"),
        # parâmetros do gráfico
        "url_grafico": url_grafico,
        "grafico_id": grafico_id,
        "spinner_id": spinner_id,
        "grafico_html": grafico_html,
    }

    # filtros específicos
    if tipo == "discentes":
        context.update({
            "partial_filtros": "sucupira/partials/pessoal/_filtros_discentes.html",
            "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
            "situacoes": DiscenteSituacao.objects.all().order_by("nm_situacao_discente"),
        })
    elif tipo == "docentes":
        context.update({
            "partial_filtros": "sucupira/partials/pessoal/_filtros_docentes.html",
            "modalidades": ProgramaModalidade.objects.all().order_by("nm_modalidade_programa"),
            "categorias": DocenteCategoria.objects.all().order_by("ds_categoria_docente"),
            "bolsas": DocenteBolsaProdutividade.objects.all().order_by("cd_cat_bolsa_produtividade"),
        })
    else:
        raise ValueError("Tipo de filtro inválido")

    return context


@register.inclusion_tag("sucupira/partials/posgrad/ppg_detalhe/_filtros_ppg_detalhe_por_ano.html")
def render_filtros_ppg_detalhe(tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Templatetag genérica para renderizar filtros de docentes ou discentes.
    Mantém partials separados, mas evita duplicação de código.
    """
    #contexto geral
    context = {
        # filtros comuns a todos os gráficos
        # parâmetros do gráfico
        "url_grafico": url_grafico,
        "grafico_id": grafico_id,
        "spinner_id": spinner_id,
        "grafico_html": grafico_html,
    }

    # filtros específicos
    if tipo == "discentes":
        context.update({
            "partial_filtros": "sucupira/partials/posgrad/ppg_detalhe/_filtros_discentes.html",
            "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
            "situacoes": DiscenteSituacao.objects.all().order_by("nm_situacao_discente"),
        })
    elif tipo == "docentes":
        context.update({
            "partial_filtros": "sucupira/partials/posgrad/ppg_detalhe/_filtros_docentes.html",
            "categorias": DocenteCategoria.objects.all().order_by("ds_categoria_docente"),
            "bolsas": DocenteBolsaProdutividade.objects.all().order_by("cd_cat_bolsa_produtividade"),
        })
    else:
        raise ValueError("Tipo de filtro inválido")

    return context