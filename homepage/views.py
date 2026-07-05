from django.shortcuts import render
from .utils.plots import HomePlotter

from django.views.decorators.cache import cache_page

# Constante de tempo de cache (3600 segundos = 1 hora)
TEMPO_CACHE = 3600

@cache_page(TEMPO_CACHE)
def index(request): #Página principal
    return render(request, 'homepage/index.html')

@cache_page(TEMPO_CACHE)
def indicadores(request): #Página de indicadores
    return render(request, r'homepage/indicadores.html',{
        'plotter': HomePlotter()
    })

@cache_page(TEMPO_CACHE)
def creditos(request):
    return render(request, r'homepage/creditos.html')