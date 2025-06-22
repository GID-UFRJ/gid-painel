from django.shortcuts import render
from . import models
from . import utils_plotly

# Create your views here.
def view_graficos(request, nome_painel):

    lista = []
    registros = models.Grafico.objects.filter(painel__nome = nome_painel)
    for r in registros:
        graf = utils_plotly.Grafico(r.tamanhoGrafico.tamanhoHorizontal, r.tamanhoGrafico.tamanhoVertical)
        lista.append(graf.grafico_linha_com_marcador_grande_para_rankings(r.tituloGrafico, r.tituloEixoGrafico, list(r.series.keys())[0], r.series))

    return render(request, r'baseGraficos/relatorio.html', {
        'graficos':lista
    })
