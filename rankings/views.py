# rankings/views.py
from django.shortcuts import render
from django.http import HttpResponse, Http404

# Importação nativa do cache do Django
from django.views.decorators.cache import cache_page

# Substituímos a classe antiga pelo novo motor universal
from common.utils.dispatcher import Dispatcher

# Importamos os dicionários de mapeamento
from .utils.mapeamentos import (
    MAPEAMENTOS_RANKINGS_ACADEMICOS,
    MAPEAMENTOS_RANKINGS_SUSTENTABILIDADE,
    MAPEAMENTOS_TODOS
)

# Constante de tempo de cache (3600 segundos = 1 hora)
TEMPO_CACHE = 3600


@cache_page(TEMPO_CACHE)
def index(request):
    return render(request, r'rankings/index.html')


@cache_page(TEMPO_CACHE)
def academicos(request):
    """Página exclusiva para Rankings Acadêmicos."""
    # 1. Instancia o motor usando APENAS o dicionário desta página
    plotter = Dispatcher(mapeamentos=MAPEAMENTOS_RANKINGS_ACADEMICOS)
    
    # 2. Define qual é o gráfico alvo desta view
    nome_plot = "academico_faixa"
    
    # 3. Em vez de chumbar os parâmetros na mão, pegamos os "filtros_padrao" direto do dicionário
    filtros_padrao = MAPEAMENTOS_RANKINGS_ACADEMICOS[nome_plot].get("filtros_padrao", {})
    
    # 4. Gera o HTML inicial via Server-Side Rendering
    grafico_inicial = plotter.generate_plot_html(nome_plot, filtros_padrao)
    
    context = {
        'evolucao_academico_plot': grafico_inicial, 
        'plotter': plotter, # Passamos o plotter para o template poder gerar o _indice_graficos
    }
    return render(request, "rankings/academicos.html", context)


@cache_page(TEMPO_CACHE)
def sustentabilidade(request):
    """Página exclusiva para Rankings de Sustentabilidade."""
    # 1. Instancia o motor com o dicionário de sustentabilidade
    plotter = Dispatcher(mapeamentos=MAPEAMENTOS_RANKINGS_SUSTENTABILIDADE)
    
    nome_plot = "sustentabilidade_faixa"
    filtros_padrao = MAPEAMENTOS_RANKINGS_SUSTENTABILIDADE[nome_plot].get("filtros_padrao", {})
    
    # 2. Gera o HTML inicial
    grafico_inicial = plotter.generate_plot_html(nome_plot, filtros_padrao)

    context = {
        'evolucao_sustentabilidade_plot': grafico_inicial,
        'plotter': plotter,
    }
    return render(request, "rankings/sustentabilidade.html", context)


@cache_page(TEMPO_CACHE)
def grafico_generico_rankings(request, nome_plot):
    """View HTMX que serve os gráficos para ambas as páginas."""
    
    # Validação de segurança inicial
    if nome_plot not in MAPEAMENTOS_TODOS:
        raise Http404(f"Gráfico '{nome_plot}' não encontrado nos mapeamentos de Rankings.")
    
    # 1. A view HTMX precisa ser capaz de atender qualquer gráfico, 
    # por isso usa o dicionário mestre (MAPEAMENTOS_TODOS)
    plotter = Dispatcher(mapeamentos=MAPEAMENTOS_TODOS)
    
    # 2. Pega os filtros do form HTMX (GET)
    filtros = request.GET.dict().copy()
    
    # 3. O Dispatcher gera o HTML purinho
    html = plotter.generate_plot_html(nome_plot, filtros)
    
    return HttpResponse(html)