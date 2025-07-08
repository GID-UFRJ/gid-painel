from django.shortcuts import render
from . import models
from . import utils_plotly

# Create your views here.
def view_graficos(request, nome_painel):

    lista = []
    registros = models.Grafico.objects.filter(painel__nome = nome_painel)
    for r in registros:
        graf = utils_plotly.Grafico(r.tamanhoGrafico.tamanhoHorizontal, r.tamanhoGrafico.tamanhoVertical)
        lista.append(graf.escolher_grafico(r.estiloGrafico.numeroIdentificador, r.tituloGrafico, r.tituloEixoX, r.tituloEixoY, r.series))

    return render(request, r'baseGraficos/relatorio.html', {
        'graficos':lista
    })


def view_graficos_producao(request, cod_ppg):
    ppg = models.ListaSucupira.objects.filter(codPrograma = cod_ppg).first()

    lista = []
    registros = models.GraficoSucupira.objects.filter(painel = cod_ppg)
    for r in registros:
        graf = utils_plotly.Grafico(r.tamanhoGrafico.tamanhoHorizontal, r.tamanhoGrafico.tamanhoVertical)
        lista.append(graf.escolher_grafico(r.estiloGrafico.numeroIdentificador, r.tituloGrafico, r.tituloEixoX, r.tituloEixoY, r.series))

    return render(request, r'baseGraficos/relatorio_ppg.html', {
        'ppg':ppg,
        'graficos':lista,
    })

def view_lista_ppg(request):

    #codigos = models.GraficoSucupira.objects.values_list('painel', flat=True).distinct()
    ppg = models.ListaSucupira.objects.all()

    return render(request, r'baseGraficos/listappg.html', {
        'ppgs':ppg
    })