from django import template
from urllib.parse import unquote

register = template.Library()

@register.simple_tag(takes_context=True)
def breadcrumbs(context):
    request = context['request']
    path = request.path

    #print(f"DEBUG: request.path = {path}")  # <---- DEBUG

    parts = [unquote(p) for p in path.strip('/').split('/') if p]
    #print(f"DEBUG: parts = {parts}")  # <---- DEBUG

    breadcrumbs = []

    # Adiciona "Início" sempre como primeiro item
    breadcrumbs.append(("Início", "/"))

    url = '/'

    for part in parts:
        url += part + '/'
        name = part.replace('-', ' ').replace('_', ' ').capitalize()
        breadcrumbs.append((name, url))

    return breadcrumbs

@register.inclusion_tag('common/partials/_abas_componente.html', takes_context=True)
def render_abas(context, abas, abas_id="default-abas"):
    """
    Renderiza um componente de abas Bootstrap.

    A variável 'abas' deve ser uma lista de dicionários. Cada dicionário DEVE conter:
    - 'id': um identificador único para a aba.
    - 'label': o texto que aparece no botão da aba.
    - 'icone': a classe do ícone usado no botão da aba (ex: 'fas fa-user') - Opcional.
    - 'titulo': o título que aparece dentro do conteúdo da aba.
    - 'template_name': o caminho para o template que contém o conteúdo da aba.
    """

    ctx = context.flatten()  # pega todas as variáveis do contexto pai
    ctx.update({
        'abas': abas,
        'abas_id': abas_id,
    }) # adiciona o contexto das abas
    return ctx