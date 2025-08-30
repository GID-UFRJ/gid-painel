from django.shortcuts import render
from .utils.plots import PlotsProducao, PlotsImpacto, PlotsColaboracao

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, r'openalex/index.html')


# Create your views here.
def producao(request):
    p = PlotsProducao()

    return render(request, r'openalex/producao.html', {
        'card_01':p.producao_total(),
        'card_02':p.producao_total_artigos(),
        'card_03':p.producao_artigos_acesso_aberto(),
        #'card_04':p.producao_total_citacoes(),
                 
        'graf_01':p.producao_por_ano(ano_inicial=1990, ano_final=2024),
        'graf_02': p.distribuicao_tematica_artigos(),
    }
)

def grafico_producao_por_ano(request):
    ano_inicial = int(request.GET.get("ano_inicial", 1990))
    ano_final = int(request.GET.get("ano_final", 2024))
    tipo_producao = request.GET.get("tipo_producao", "total")
    tipo_grafico = request.GET.get("tipo_grafico", "barra")


    p = PlotsProducao()
    graf = p.producao_por_ano(ano_inicial=ano_inicial, 
                              ano_final=ano_final, 
                              tipo_producao=tipo_producao, 
                              tipo_grafico=tipo_grafico,
                              )

    return render( request, 
                  "openalex/partials/_plot_reativo.html", 
                  {"graf": graf} 
                  )


def impacto(request):
    p = PlotsImpacto()
    return render(request, r'openalex/impacto.html', {
        'card_01':p.producao_total_citacoes(),
        'card_02':p.producao_total_hindex(),

        'graf_01':p.citacoes_por_ano(ano_inicial=1990, ano_final=2024),
        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
    }
)

def grafico_citacoes_por_ano(request):
    ano_inicial = int(request.GET.get("ano_inicial", 1990))
    ano_final = int(request.GET.get("ano_final", 2024))
    tipo_producao = request.GET.get("tipo_producao", "total")
    metrica = request.GET.get("metrica", "total_citacoes")
    tipo_grafico = request.GET.get("tipo_grafico", "barra")

    p = PlotsImpacto()
    graf = p.citacoes_por_ano(ano_inicial=ano_inicial, 
                              ano_final=ano_final, 
                              tipo_producao=tipo_producao, 
                              metrica=metrica, 
                              tipo_grafico=tipo_grafico,
                              )

    # Renderiza o partial específico para HTMX
    return render( request, 
                  "openalex/partials/_plot_reativo.html", 
                  {"graf": graf}
                  )

def colaboracao(request):
    p = PlotsColaboracao()

    return render(request, r'openalex/colaboracao.html', {
        'card_01':p.producao_colaboracao_nacional(),
        'card_02':p.producao_colaboracao_internacional(),

        'graf_01':p.top_instituicoes_colaboradoras(internacional=False),
        'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
        #'graf_02':p.producao_por_ano_worktype(ano_inicial=1990, ano_final=2024),
        #'graf_03':p.producao_por_ano_worktype(ano_inicial=1990, 
        #                                      ano_final=2024,
        #                                      tipo_plot='barra'),
        #'graf_04': p.distribuicao_tematica_artigos(),
    }
)

