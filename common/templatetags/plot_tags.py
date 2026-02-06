from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def render_kpi(context, plotter_instance, nome_plot):
    """
    Renderiza um card de KPI a partir de um plotter e um nome de mapeamento.
    Uso: {% render_kpi plotter "total_docentes" %}
    """
    request = context.get('request')
    # Pegamos os filtros da URL (GET) para que o KPI seja dinâmico
    filtros = request.GET if request else {}
    
    # Chamamos o motor que você acabou de construir
    html_card = plotter_instance.generate_plot_html(nome_plot, filtros)
    
    return mark_safe(html_card)