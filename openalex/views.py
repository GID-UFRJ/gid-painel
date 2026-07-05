from django.shortcuts import render
#from .utils.plots import PlotsProducao, PlotsImpacto, PlotsColaboracao
from common.utils.dispatcher import Dispatcher
from .utils.mapeamentos import MAPEAMENTOS_PRODUCAO, MAPEAMENTOS_IMPACTO, MAPEAMENTOS_COLABORACAO, MAPEAMENTOS_TODOS

#Ferramenta de cache
from django.views.decorators.cache import cache_page

# Create your views here.
from django.http import HttpResponse


# Constante de tempo
TEMPO_CACHE = 3600

def index(request):
    return render(request, r'openalex/index.html')


@cache_page(TEMPO_CACHE)
def producao(request):
    """
    View responsável por carregar a página de Produção pela PRIMEIRA VEZ.
    """
    print("1. Entrei na View Produção")
    
    # 1. Instanciamos o Dispatcher com os mapeamentos
    p = Dispatcher(mapeamentos=MAPEAMENTOS_PRODUCAO)
    

    # 2. Geramos os gráficos
    html_producao_ano = p.generate_plot_html(
        nome_plot='producao_por_ano', 
        filtros_selecionados={'ano_inicial': 2013, 'ano_final': 2024}
    )
    
    html_distribuicao = p.generate_plot_html(
        nome_plot='distribuicao_tematica', 
        filtros_selecionados={}
    )

    print(f"4. Voltei para a View. Tamanho do HTML (Temática): {len(html_distribuicao)}")

    # 3. Mandamos para o template
    return render(request, 'openalex/producao.html', {
        'graf_01': html_producao_ano,
        'graf_02': html_distribuicao,
        'plotter': p, #Usado APENAS para mostrar o sumário dos plots
    })

@cache_page(TEMPO_CACHE)
def impacto(request):
    """
    View responsável por carregar a página de Impacto pela PRIMEIRA VEZ.
    """
    p = Dispatcher(mapeamentos=MAPEAMENTOS_IMPACTO)

    # Definimos os filtros iniciais para quando o usuário abre a página
    filtros_iniciais_grafico = {
        'ano_inicial': 2013,
        'ano_final': 2024,
        'metrica': 'total_citacoes' # O gráfico já nasce exibindo o total
    }

    context = {
        # Gráfico Principal (Passamos os filtros iniciais)
        'graf_01': p.generate_plot_html(
            nome_plot='citacoes_por_ano', 
            filtros_selecionados=filtros_iniciais_grafico,
        ),
        # Gráfico Secundário (distribuicao)
        'graf_02': p.generate_plot_html(
            nome_plot="distribuicao_citacoes", 
            filtros=request.GET),
        'plotter': p, #Usado APENAS para mostrar o sumário dos plots
    }

    return render(request, 'openalex/impacto.html', context)


@cache_page(TEMPO_CACHE)
def colaboracao(request):
    """
    View responsável por carregar a página de Colaboração pela PRIMEIRA VEZ.
    """
    print("1. Entrei na View Colaboração")
    
    p = Dispatcher(mapeamentos=MAPEAMENTOS_COLABORACAO)

    # Filtros iniciais para os gráficos nascerem preenchidos
    filtros_evolucao = {
        'ano_inicial': 2013, 
        'ano_final': 2024,
        # Você pode escolher se a página nasce mostrando Nacional ou Internacional
    }
    
    filtros_top = {
        'tipo_colaboracao': 'nacional', # Nasce mostrando BR
        'limite': 10 # Nasce como Top 10
    }

    context = {
        # 1. Gráfico de Evolução (Atualizado para o novo nome unificado)
        'graf_01': p.generate_plot_html(
            nome_plot='evolucao_colaboracao',  # <--- AQUI ESTAVA O NOME ANTIGO
            filtros_selecionados=filtros_evolucao
        ),
        
        # 2. Gráfico de Top Instituições
        'graf_02': p.generate_plot_html(
            nome_plot='top_instituicoes', 
            filtros_selecionados=filtros_top
        ),
        'plotter': p, #Usado APENAS para mostrar o sumário dos plots
    }

    return render(request, 'openalex/colaboracao.html', context)

@cache_page(TEMPO_CACHE)
def grafico_generico_openalex(request, nome_plot):
    """
    View acionada pelo HTMX. Recebe requisições via AJAX quando o usuário 
    muda um dropdown (ex: muda de 'Total' para 'Índice H').
    """

    p = Dispatcher(mapeamentos=MAPEAMENTOS_TODOS)

    # 1. Pega todos os filtros da URL (ex: ?ano_inicial=2000&metrica=hindex)
    filtros_selecionados = request.GET.dict()

    # 2. O Dispatcher processa a mágica
    grafico_html = p.generate_plot_html(
        nome_plot=nome_plot, 
        filtros_selecionados=filtros_selecionados
    )

    # 3. Retorna APENAS o HTML do gráfico (para o HTMX injetar na tela)
    return HttpResponse(grafico_html)