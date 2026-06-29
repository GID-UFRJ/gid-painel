from django.shortcuts import render
from .utils.plots import HomePlotter


def index(request): #Página principal
    return render(request, 'homepage/index.html')

def indicadores(request): #Página de indicadores
    return render(request, r'homepage/indicadores.html',{
        'plotter': HomePlotter()
    })

def creditos(request):
    return render(request, r'homepage/creditos.html')