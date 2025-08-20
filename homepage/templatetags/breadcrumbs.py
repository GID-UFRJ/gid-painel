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
    url = '/'

    for part in parts:
        url += part + '/'
        name = part.replace('-', ' ').replace('_', ' ').capitalize()
        breadcrumbs.append((name, url))

    return breadcrumbs
