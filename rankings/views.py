from django.shortcuts import render
from . import scripts_graficos

# Create your views here.
def rankings(request):
    g=scripts_graficos.Grafico_ranking()
    graf=scripts_graficos.Grafico_ranking2()

    return render(request, r'rankings/relatorio_rankings.html', {
        'card_01':g.kpi_qs_americaLatina(),
        'card_02':g.kpi_the_americaLatina(),
        'card_03':g.kpi_shanghaiNacional(),

        'graficos':graf.listaGraficos()
    })