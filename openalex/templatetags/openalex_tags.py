# openalex/templatetags/openalex_tags.py
from django import template
from openalex.models import Year, WorkType

register = template.Library()

# Caminho base para os filtros atômicos (reaproveitando o do common)
PATH_FILTROS_ATOMICOS = "common/partials/filtros/"

@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_producao(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html, plotter_name, nome_plot):
    """
    Monta o formulário de filtros para a seção OpenAlex (Produção)
    """
    ctx = { 
        "url_grafico": url_grafico, 
        "grafico_id": grafico_id, 
        "spinner_id": spinner_id, 
        "grafico_html": grafico_html,
        "plotter_name": plotter_name,
        "nome_plot": nome_plot,
    }
    
    lista_de_filtros = []
    agrupamentos_disponiveis = {}

    if tipo == "producao_por_ano":
        # Compondo os filtros que você pediu: ano, agrupamento e tipo de gráfico
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_agrupamento.html",
            #f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_documento.html", # Se você tiver este filtro atômico
        ]
        
        # Dados para alimentar os selects
        ctx.update({
            "tipos_documento": WorkType.objects.all(),
            "anos_disponiveis": Year.objects.all().order_by('-year'),
        })
        
        # Agrupamentos que aparecem no dropdown do gráfico de barras
        agrupamentos_disponiveis = {
            'Acesso Aberto': 'acesso_aberto',
            'Tipo de Documento': 'tipo_documento',
            'Domínio': 'dominio',
        }

    elif tipo == "distribuicao_tematica":
        # Sunburst geralmente só precisa de filtro de limite ou ano
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
        ]

    ctx['lista_de_filtros'] = lista_de_filtros
    ctx['agrupamentos_disponiveis'] = agrupamentos_disponiveis
    return ctx