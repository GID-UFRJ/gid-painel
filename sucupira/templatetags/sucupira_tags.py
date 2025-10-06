from django import template
from sucupira.models import (
    ProgramaGrandeArea, GrauCurso, DiscenteSituacao,
    ProgramaModalidade, DocenteCategoria, DocenteBolsaProdutividade, Ano
)

register = template.Library()


@register.inclusion_tag("common/partials/_placeholder_filtros.html", takes_context=True)
def render_filtros_pessoal(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Templatetag genérica e flexível para renderizar diferentes layouts de filtros
    para a seção "Pessoal".
    """
    # Contexto base com informações do gráfico
    ctx = {
        "url_grafico": url_grafico,
        "grafico_id": grafico_id,
        "spinner_id": spinner_id,
        "grafico_html": grafico_html,
    }
    
    template_a_renderizar = ""

    # --- Casos que usam o layout COMPOSTO ---
    if tipo in ["discentes", "docentes"]:
        template_a_renderizar = "sucupira/partials/pessoal/_filtros_pessoal_por_ano.html"
        
        # Adiciona filtros comuns ao layout composto
        ctx["grandes_areas"] = ProgramaGrandeArea.objects.all().order_by("nm_grande_area_conhecimento")
        
        # Adiciona filtros e partials específicos
        if tipo == "discentes":
            ctx.update({
                "partial_filtros": "sucupira/partials/pessoal/_filtros_discentes.html",
                "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
                "situacoes": DiscenteSituacao.objects.all().order_by("nm_situacao_discente"),
            })
        elif tipo == "docentes":
            ctx.update({
                "partial_filtros": "sucupira/partials/pessoal/_filtros_docentes.html",
                "modalidades": ProgramaModalidade.objects.all().order_by("nm_modalidade_programa"),
                "categorias": DocenteCategoria.objects.all().order_by("ds_categoria_docente"),
                "bolsas": DocenteBolsaProdutividade.objects.all().order_by("cd_cat_bolsa_produtividade"),
            })

    # --- Casos que usam um layout SIMPLES E ESPECÍFICO ---
    elif tipo == 'sunburst':
        template_a_renderizar = "sucupira/partials/pessoal/_form_filtro_ano_unico.html"
        
        # Adiciona apenas os dados necessários para este template
        ctx.update({
            "anos_disponiveis": Ano.objects.all().order_by('-ano_valor'),
        })

    else:
        raise ValueError(f"Tipo de filtro inválido: {tipo}")

    # O 'placeholder.html' irá renderizar o template que escolhemos dinamicamente
    context['template_to_render'] = template_a_renderizar
    context.update(ctx)
    return context



@register.inclusion_tag("sucupira/partials/posgrad/ppg_detalhe/_render_filtros_wrapper.html")
def render_filtros_ppg_detalhe(tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Templatetag genérica que monta um formulário de filtros em camadas.
    """
    # ==================== LINHA DE DEBUG ====================
    print(f"--- DEBUG TEMPLATETAG: Executando para o tipo = '{tipo}' ---")
    # ========================================================

    context = {
        "url_grafico": url_grafico,
        "grafico_id": grafico_id,
        "spinner_id": spinner_id,
        "grafico_html": grafico_html,
        # Placeholders para os partials
        "partial_filtros_comuns": None,
        "partial_filtros_especificos": None,
    }

    # Casos que precisam da Camada 2 (Comuns) e Camada 3 (Específicos)
    if tipo in ["discentes", "docentes", "media_titulacao"]:
        context["partial_filtros_comuns"] = "sucupira/partials/posgrad/ppg_detalhe/_partial_filtros_comuns.html"
        
        if tipo == "discentes":
            context["partial_filtros_especificos"] = "sucupira/partials/posgrad/ppg_detalhe/_filtros_discentes.html"
            context.update({
                "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
                "situacoes": DiscenteSituacao.objects.all().order_by("nm_situacao_discente"),
            })
        elif tipo == "media_titulacao":
            context["partial_filtros_especificos"] = "sucupira/partials/posgrad/ppg_detalhe/_filtros_media_titulacao.html"
            context.update({
                "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
            })
        elif tipo == "docentes":
            context["partial_filtros_especificos"] = "sucupira/partials/posgrad/ppg_detalhe/_filtros_docentes.html"
            context.update({
                "categorias": DocenteCategoria.objects.all().order_by("ds_categoria_docente"),
                "bolsas": DocenteBolsaProdutividade.objects.all().order_by("cd_cat_bolsa_produtividade"),
            })

    # Casos que precisam apenas da Camada 1 (Base)
    elif tipo == "conceito_programa":
        # Não faz nada, os placeholders continuarão None e os includes não serão renderizados
        pass
    
    else:
        raise ValueError(f"Tipo de filtro inválido: {tipo}")

    return context