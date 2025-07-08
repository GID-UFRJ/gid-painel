from django.shortcuts import render
from .plots import PlotsProducao, PlotsVisibilidade

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Página com dados da OpenAlex em construção...")


# Create your views here.
def producao(request):
    p = PlotsProducao()

    return render(request, r'openalex/producao.html', {
        'card_01':p.producao_total(),
        'card_02':p.producao_total_artigos(),
        'card_03':p.producao_artigos_acesso_aberto(),
        #'card_04':p.producao_total_citacoes(),
                 
        'graf_01':p.producao_por_ano(ano_inicial=1990, ano_final=2024),
        'graf_02':p.producao_por_ano_worktype(ano_inicial=1990, ano_final=2024),
        'graf_03':p.producao_por_ano_worktype(ano_inicial=1990, 
                                              ano_final=2024,
                                              tipo_plot='barra'),
        'graf_04': p.distribuicao_tematica_artigos(),
        'graf_04':p.metricas_por_topico_artigos_plot(),
        #'graf_05':g.shanghai_mundo(),
        #'graf_06':g.shanghai_nacional(),
    }
)
 
def visibilidade(request):
    p = PlotsVisibilidade()

    return render(request, r'openalex/visibilidade.html', {
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
