from django.shortcuts import render
from . import scripts_graficos

# Create your views here.
def rankings(request):
    g=scripts_graficos.Grafico_ranking()

    return render(request, r'rankings/relatorio_rankings.html', {
        'card_01':g.kpi_qs_americaLatina(),
        'card_02':g.kpi_the_americaLatina(),
        'card_03':g.kpi_shanghaiNacional(),

        'graf_01':g.qs_mundo(),
        'graf_02':g.qs_americaLatina(),
        'graf_03':g.the_mundo(),
        'graf_04':g.the_americaLatina(),
        'graf_05':g.shanghai_mundo(),
        'graf_06':g.shanghai_nacional_novo(),

    })