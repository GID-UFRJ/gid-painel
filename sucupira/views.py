from django.core.cache import cache
from collections import defaultdict
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from .utils.plots import PlotsPessoal, PlotsPpgDetalhe
from .models import Programa, DiscenteSituacao, ProgramaGrandeArea, GrauCurso, AnoPrograma, Curso, Discente
from django.db.models import OuterRef, Subquery

# Create your views here.

def index(request): #index unificado
    namespace = request.resolver_match.namespace # pega o namespace atual (vem do include no urls.py principal)
    return render(request, f"sucupira/{namespace}/index.html")

def pessoal_ppg(request):
    p = PlotsPessoal()

    abas = [
        {
            "id": "discentes", 
            "label": "Discentes", 
            "icone": "fas fa-user-graduate", 
            "titulo": "Análise de Discentes",
            "template_name": "sucupira/partials/pessoal/_aba_discentes_conteudo.html"  # Caminho para o conteúdo
        },
        {
            "id": "docentes", 
            "label": "Docentes", 
            "icone": "fas fa-chalkboard-teacher", 
            "titulo": "Análise de Docentes",
            "template_name": "sucupira/partials/pessoal/_aba_docentes_conteudo.html"   # Caminho para o conteúdo
        },
    ]

    plots_cache_key = 'pessoal_ppg_initial_plots'
    contexto_plots = cache.get(plots_cache_key)

    if contexto_plots is None:
        contexto_plots = {
            ##Gráficos interativos iniciais
            #Aba discentes
            'discentes_ano_plot': p.discentes_por_ano(),
            'discentes_sunburst_plot': p.discentes_por_area_sunburst(),
            'top_paises_discentes_plot': p.top_paises_discentes(),
            #Aba docentes
            'docentes_ano_plot': p.docentes_por_ano(),
            'docentes_sunburst_plot': p.docentes_por_area_sunburst(),
            'top_paises_docentes_plot': p.top_paises_docentes(),
        }
        cache.set(plots_cache_key, contexto_plots, timeout=3600)

    context = {
        "abas": abas,
        'n_titulados_cards': p.cards_total_alunos_titulados_por_grau(),
        'docentes_card': p.card_total_docentes_ultimo_ano(),
    }
    context.update(contexto_plots)

    return render(request, r'sucupira/pessoal/pessoal_ppg.html', context)

def grafico_generico_pessoal(request, nome_plot: str):
    """
    View genérica para todos os gráficos da seção Pessoal.
    Chama dinamicamente o método correspondente em PlotsPessoal.
    """
    plotter = PlotsPessoal()
    
    # Verifica se o método solicitado existe na classe (por segurança)
    if not hasattr(plotter, nome_plot):
        raise Http404("Gráfico não encontrado.")

    # Pega o método da classe usando o nome fornecido na URL
    metodo_a_chamar = getattr(plotter, nome_plot)
    
    # Executa o método, passando os parâmetros da URL
    grafico_html = metodo_a_chamar(**request.GET.dict())
    
    return HttpResponse(grafico_html)


def posgrad_ufrj(request):
    return HttpResponse('Página em construção')

def ppgs(request):
    """
    Lista todos os programas de pós-graduação mostrando os dados do último ano.
    """

    # Subquery para buscar o último AnoPrograma de cada programa
    ultimo_ano_qs = AnoPrograma.objects.filter(
        programa=OuterRef('pk')
    ).order_by('-ano__ano_valor')  # ordena do mais recente

    # Anotando os campos que queremos do último ano
    programas = Programa.objects.annotate(
        nm_programa_ies=Subquery(ultimo_ano_qs.values('nm_programa_ies__nm_programa_ies')[:1]), 
        grande_area_nome=Subquery(ultimo_ano_qs.values('grande_area__nm_grande_area_conhecimento')[:1]),
        #ultimo_ano=Subquery(ultimo_ano_qs.values('ano__ano_valor')[:1]),
        #area_avaliacao_nome=Subquery(ultimo_ano_qs.values('area_avaliacao__nm_area_avaliacao')[:1]),
        #conceito_atual=Subquery(ultimo_ano_qs.values('cd_conceito_programa__cd_conceito_programa')[:1]),
        #situacao_atual=Subquery(ultimo_ano_qs.values('situacao__ds_situacao_programa')[:1]),
    ).order_by('grande_area_nome', 'nm_programa_ies')

    # Agrupar por grande área
    agrupados = defaultdict(list)
    for programa in programas:
        chave = programa.grande_area_nome or "Sem Grande Área"
        agrupados[chave].append(programa)

    # Transformar em dict ordenado por chave (Grande Área)
    programas_agrupados = dict(sorted(agrupados.items()))

    context = {
        'programas_agrupados': programas_agrupados
    }
    return render(request, 'sucupira/posgrad/ppgs.html', context)


def ppg_detalhe(request, programa_id):

    abas = [
        {
            "id": "programa", 
            "label": "Programa", 
            "icone": "fas fa-graduation-cap", 
            "titulo": "Análise do Programa",
            "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_programa_conteudo.html"   # Caminho para o conteúdo
        },
        {
            "id": "discentes", 
            "label": "Discentes", 
            "icone": "fas fa-user-graduate", 
            "titulo": "Análise de Discentes",
            "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_discentes_conteudo.html"  # Caminho para o conteúdo
        },
        {
            "id": "docentes", 
            "label": "Docentes", 
            "icone": "fas fa-chalkboard-teacher", 
            "titulo": "Análise de Docentes",
            "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_docentes_conteudo.html"   # Caminho para o conteúdo
        },
    ]

    p = PlotsPpgDetalhe(programa_id=programa_id)


    # A chave do cache DEVE ser única para cada programa
    plots_cache_key = f'ppg_detalhe_context_{programa_id}'
    contexto_plots = cache.get(plots_cache_key)

    # Se os plots para ESTE programa não estiverem no cache...
    if contexto_plots is None:
        # ...geramos apenas os gráficos para o estado inicial
        contexto_plots = {
            'conceito_programa_ano_plot': p.conceito_programa_por_ano(),
            'discentes_ano_plot': p.discentes_por_ano(),
            'docentes_ano_plot': p.docentes_por_ano(),
            'media_titulacao_ano_plot': p.media_titulacao_por_ano(),
            # Adicione outros plots iniciais da página de detalhes aqui, se houver
        }
        # Salvamos o dicionário de plots para ESTE programa no cache
        cache.set(plots_cache_key, contexto_plots, timeout=3600)

    # Subquery para o último AnoPrograma deste programa
    ultimo_ano_qs = AnoPrograma.objects.filter(
        programa_id=OuterRef('pk')
    ).order_by('-ano__ano_valor')


    # Obter o programa anotado com os campos do último ano
    programa = get_object_or_404(
        Programa.objects.annotate(
            ultimo_ano=Subquery(ultimo_ano_qs.values('ano__ano_valor')[:1]),
            grande_area_nome=Subquery(ultimo_ano_qs.values('grande_area__nm_grande_area_conhecimento')[:1]),
            area_avaliacao_nome=Subquery(ultimo_ano_qs.values('area_avaliacao__nm_area_avaliacao')[:1]),
            area_avaliacao_codigo=Subquery(ultimo_ano_qs.values('area_avaliacao__cd_area_avaliacao')[:1]),
            conceito_atual=Subquery(ultimo_ano_qs.values('cd_conceito_programa__cd_conceito_programa')[:1]),
            situacao_atual=Subquery(ultimo_ano_qs.values('situacao__ds_situacao_programa')[:1]),
            modalidade_atual=Subquery(ultimo_ano_qs.values('nm_modalidade_programa__nm_modalidade_programa')[:1]),
            nm_programa_ies=Subquery(ultimo_ano_qs.values('nm_programa_ies__nm_programa_ies')[:1])
        ),
        pk=programa_id
    )


    # Obter cursos do programa
    cursos = (
        Curso.objects
        .filter(programa_id=programa_id)
        .select_related("grau_curso")
        .order_by("grau_curso__nm_grau_curso")
    )

    params = request.GET.dict()

    try:
        params['ano_inicial'] = int(params.get('ano_inicial', 2013))
        params['ano_final'] = int(params.get('ano_final', 2023))
    except (ValueError, TypeError):
        params['ano_inicial'] = 2013
        params['ano_final'] = 2023

    context = {
        "abas": abas,
        "programa": programa,
        "cursos": cursos,

    }
    context.update(contexto_plots)

    return render(request, "sucupira/posgrad/ppg_detalhe.html", context)

def grafico_generico_ppg(request, programa_id: int, nome_plot: str):
    """
    View genérica para todos os gráficos da seção PPG Detalhe.
    Chama dinamicamente o método correspondente em PlotsPpgDetalhe.
    """
    plotter = PlotsPpgDetalhe(programa_id=programa_id)

    if not hasattr(plotter, nome_plot):
        raise Http404("Gráfico não encontrado.")

    metodo_a_chamar = getattr(plotter, nome_plot)
    grafico_html = metodo_a_chamar(**request.GET.dict())
    
    return HttpResponse(grafico_html)