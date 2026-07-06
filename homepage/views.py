from django.shortcuts import render
from .utils.plots import HomePlotter

from django.views.decorators.cache import cache_page
from django.conf import settings


@cache_page(settings.CACHE_TIMEOUT_PAGINAS)
def index(request): #Página principal
    return render(request, 'homepage/index.html')

@cache_page(settings.CACHE_TIMEOUT_PAGINAS)
def indicadores(request): #Página de indicadores
    return render(request, r'homepage/indicadores.html',{
        'plotter': HomePlotter()
    })

@cache_page(settings.CACHE_TIMEOUT_PAGINAS)
def creditos(request):
    return render(request, r'homepage/creditos.html')