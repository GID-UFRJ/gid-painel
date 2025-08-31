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

def grafico_colaboracoes_por_ano(request):
    """
    Gera um gráfico da produção científica da UFRJ em colaboração com outras 
    instituições (nacionais ou internacionais) ao longo do tempo.

    A função é acionada por HTMX e aceita os seguintes parâmetros via GET:
    - ano_inicial, ano_final: Filtra o período de publicação.
    - tipo_colaboracao: 'nacional' ou 'internacional'.
    - agrupamento: Como os dados serão divididos/coloridos no gráfico.
                   Opções: 'total', 'tipo_documento', 'acesso_aberto', 'dominio'.
    - tipo_grafico: 'barra' ou 'linha'.
    """
    # 1. Obter parâmetros do request com valores padrão
    ano_inicial = int(request.GET.get('ano_inicial', 2010))
    ano_final = int(request.GET.get('ano_final', 2023))
    tipo_colaboracao = request.GET.get('tipo_colaboracao', 'nacional')
    tipo_producao = request.GET.get('tipo_producao', 'total')
    tipo_grafico = request.GET.get('tipo_grafico', 'barra')

    p = PlotsColaboracao()
    graf = p.colaboracoes_por_ano(ano_inicial=ano_inicial, 
                                            ano_final=ano_final, 
                                            tipo_colaboracao=tipo_colaboracao, 
                                            tipo_producao=tipo_producao, 
                                            tipo_grafico=tipo_grafico
                                            )
    # Renderiza o partial específico para HTMX
    return render( request, 
                  "openalex/partials/_plot_reativo.html", 
                  {"graf": graf}
                  )


def grafico_top_colaboracoes(request):
    n_instituicoes = int(request.GET.get("n_instituicoes", 10))
    tipo_instituicao = request.GET.get('tipo_instituicao', 'nacional')
    
    p = PlotsColaboracao()
    graf = p.top_instituicoes_colaboradoras(
                            n_instituicoes=n_instituicoes,
                            tipo_instituicao=tipo_instituicao,
                            )

    # Renderiza o partial específico para HTMX
    return render( request, 
                  "openalex/partials/_plot_reativo.html", 
                  {"graf": graf}
                  )
