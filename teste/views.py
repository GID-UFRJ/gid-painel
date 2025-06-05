from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers
from . import scripts_graficos

g=scripts_graficos.Grafico_ranking()

@cache_control(ranking='QS')
@vary_on_headers("HX-Request")
def atualizar_grafico(request):
    selected_option = request.GET.get('categoria', 'QS')
    if request.htmx:
        template_name = r'teste/grafico.html'
    else:
        template_name = r'teste/teste.html'

    return render(request, template_name, {
        'graf_01':g.mundo(selected_option),
        'graf_02':g.americaLatina(selected_option),
    })
