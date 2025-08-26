from django.shortcuts import render
from .utils.plots import PlotsProducao, PlotsVisibilidade

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
                 
        'graf_01':p.producao_por_ano(ano_inicial=1990, ano_final=2024, filtro='Total'),
        #'graf_02':p.producao_por_ano_worktype(ano_inicial=1990, ano_final=2024),
        #'graf_03':p.producao_por_ano_worktype(ano_inicial=1990, 
        #                                      ano_final=2024,
        #                                      tipo_plot='barra'),
        #'graf_04': p.distribuicao_tematica_artigos(),
        #'graf_04':p.metricas_por_topico_artigos_plot(),
        #'graf_05':g.shanghai_mundo(),
        #'graf_06':g.shanghai_nacional(),
    }
)

def grafico_producao_por_ano(request):
    ano_inicial = int(request.GET.get("ano_inicial", 1990))
    ano_final = int(request.GET.get("ano_final", 2024))
    filtro = request.GET.get("filtro", "total")

    p = PlotsProducao()
    graf = p.producao_por_ano(ano_inicial=ano_inicial, ano_final=ano_final, filtro=filtro)

    return render(request, "openalex/partials/producao_por_ano.html", {"graf": graf})


def impacto(request):
    return(HttpResponse('Página em construção'))

 
def colaboracao(request):
    p = PlotsVisibilidade()

    return render(request, r'openalex/colaboracao.html', {
        'card_01':p.producao_total_citacoes(),
        'card_02':p.producao_colaboracao_nacional(),
        'card_03':p.producao_colaboracao_internacional(),

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
