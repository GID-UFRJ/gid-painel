from django.shortcuts import render
from .utils.plots import HomePlotter

def index(request):
    return render(request, r'homepage/index.html',{
        'plotter': HomePlotter()
    })

def creditos(request):
    return render(request, r'homepage/creditos.html')