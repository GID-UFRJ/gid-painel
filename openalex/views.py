from django.shortcuts import render
from .utils.plots import PlotsProducao, PlotsImpacto, PlotsColaboracao

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, r'openalex/index.html')


# Create your views here.
def producao(request):
    print("1. Entrei na View Produção")
    p = PlotsProducao()


    html = p.generate_plot_html('distribuicao_tematica')
    print(f"4. Voltei para a View. Tamanho do HTML: {len(html)}")

    return render(request, 'openalex/producao.html', {
        # Em vez de p.producao_por_ano(...), use:
        'graf_01': p.generate_plot_html(
            nome_plot='producao_por_ano', 
            filtros_selecionados={'ano_inicial': 1990, 'ano_final': 2024}
        ),
        
        # Em vez de p.distribuicao_tematica_artigos(), use o nome que está no seu MAPEAMENTOS:
        #'graf_02': "<h1>Teste de Renderização</h1>",
        'graf_02': p.generate_plot_html(
            nome_plot='distribuicao_tematica', 
            filtros_selecionados={}
        ),
    })


def impacto(request):
    p = PlotsImpacto()
    return render(request, r'openalex/impacto.html', {
        #'card_01':p.producao_total_citacoes(),
        #'card_02':p.producao_total_hindex(),

        'graf_01':p.citacoes_por_ano(ano_inicial=1990, ano_final=2024),
        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
    }
)

def colaboracao(request):
    p = PlotsColaboracao()

    return render(request, r'openalex/colaboracao.html', {
        #'card_01':p.producao_colaboracao_nacional(),
        #'card_02':p.producao_colaboracao_internacional(),

        'graf_01':p.colaboracoes_por_ano(),
        'graf_02':p.top_instituicoes_colaboradoras(n_instituicoes=10, tipo_instituicao='nacional'),
        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
        #'graf_02':p.producao_por_ano_worktype(ano_inicial=1990, ano_final=2024),
        #'graf_03':p.producao_por_ano_worktype(ano_inicial=1990, 
        #                                      ano_final=2024,
        #                                      tipo_plot='barra'),
        #'graf_04': p.distribuicao_tematica_artigos(),
    }
)


def grafico_generico_producao(request, nome_plot):
    plotter = PlotsProducao() 
    
    filtros = request.GET.dict() 
   
    try:
        grafico_html = plotter.generate_plot_html(
            nome_plot=nome_plot,
            filtros_selecionados=filtros
        )
        return HttpResponse(grafico_html)
    except Exception as e:
        return HttpResponse(f"<div class='alert alert-danger'>Erro no plot '{nome_plot}': {e}</div>")