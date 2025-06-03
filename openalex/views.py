from django.shortcuts import render
from .plots import PlotsProducao, PlotsVisibilidade

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Página com dados da OpenAlex em construção...")


# Create your views here.
def producao(request):
    p = PlotsProducao()

    return render(request, r'rankings/relatorio_rankings.html', {
        'card_01':p.producao_total(),
        'card_02':p.producao_total_artigos(),
        'card_03':p.producao_artigos_acesso_aberto(),
        #'card_04':p.producao_total_citacoes(),
                 
        'graf_01':p.producao_por_ano(ano_inicial=1990, ano_final=2024),
        #'graf_02':g.qs_americaLatina(),
        #'graf_03':g.the_mundo(),
        #'graf_04':g.the_americaLatina(),
        #'graf_05':g.shanghai_mundo(),
        #'graf_06':g.shanghai_nacional(),
    }
)
 
def visibilidade(request):
    return render(request, r'openalex/visibilidade.html', {'placeholder': 'Página em construção'})
