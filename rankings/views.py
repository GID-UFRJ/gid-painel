from django.shortcuts import render
from . import scripts_graficos
from django.http import HttpResponse, Http404
from .utils.plots import PlotsRankings
#
#
def index(request):
    return(render(request, r'rankings/index.html'))

def academicos(request):
    """Página exclusiva para Rankings Acadêmicos."""
    # 1. Instancia a classe de plots
    plotter = PlotsRankings()
    
    # 2. Gera o gráfico inicial manualmente com os parâmetros padrão
    # Defina aqui o que você quer que apareça primeiro
    grafico_inicial = plotter.evolucao_academico(
        ranking_nome="THE", 
        ano_inicial="2018",
        escopo="MUNDO"
    )
    # Contexto vazio para ativar o Lazy Loading do template
    context = {
        'evolucao_academico_plot': grafico_inicial, 
    }
    return render(request, "rankings/academicos.html", context)

def sustentabilidade(request):
    """Página exclusiva para Rankings de Sustentabilidade."""
    # 1. Instancia o plotter
    plotter = PlotsRankings()
    
    # 2. Gera o gráfico inicial manualmente (Server-Side Rendering)
    # IMPORTANTE: Passamos 'ods="ODS_3"' para garantir que o THE IMPACT
    # venha filtrado corretamente logo de cara.
    grafico_inicial = plotter.evolucao_sustentabilidade(
        ranking_nome="THE IMPACT",
        ods="None", 
        ano_inicial="2019"
    )

    context = {
        'evolucao_sustentabilidade_plot': grafico_inicial,
    }
    return render(request, "rankings/sustentabilidade.html", context)

def grafico_generico_rankings(request, nome_plot):
    """View HTMX que serve os gráficos para ambas as páginas."""
    plotter = PlotsRankings()
    if not hasattr(plotter, nome_plot):
        raise Http404
    
    metodo = getattr(plotter, nome_plot)
    # Retorna o HTML puro
    return HttpResponse(metodo(**request.GET.dict()))




#
#def classificacao(request):
#    g=scripts_graficos.Grafico_ranking()
#
#    return render(request, r'rankings/relatorio_rankings.html', {
#        'card_01':g.kpi_qs_americaLatina(),
#        'card_02':g.kpi_the_americaLatina(),
#        'card_03':g.kpi_shanghaiNacional(),
#
#        'graf_01':g.qs_mundo(),
#        'graf_02':g.qs_americaLatina(),
#        'graf_03':g.the_mundo(),
#        'graf_04':g.the_americaLatina(),
#        'graf_05':g.shanghai_mundo(),
#        'graf_06':g.shanghai_nacional(),
#    })