from collections import defaultdict
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import OuterRef, Subquery

# Importe os modelos, as classes de plotagem (que agora estão simplificadas) e o decorador
from .models import Programa, AnoPrograma, Curso
from .utils.plots import PlotsPessoal, PlotsPpgDetalhe, PlotsPpgUfrj
from common.utils.cache import cache_context_data


# ==============================================================================
# VIEWS ESTÁTICAS E AUXILIARES
# ==============================================================================

def index(request):
    """Renderiza o índice do app, determinando o namespace a partir da URL."""
    namespace = request.resolver_match.namespace
    return render(request, f"sucupira/{namespace}/index.html")



# ==============================================================================
# VIEWS PARA A SEÇÃO "PESSOAL PPG" (GERAL)
# ==============================================================================

def pessoal_ppg(request):
    """
    Renderiza a página principal do dashboard "Pessoal", com cache para performance.
    """
    @cache_context_data(key_prefix='pessoal_ppg', timeout=3600)
    def get_cached_context():
        """
        Gera e cacheia o contexto completo, usando a nova arquitetura de orquestração
        para criar os plots iniciais.
        """
        p = PlotsPessoal()

        abas = [
            {
                "id": "discentes",
                "label": "Discentes",
                "icone": "fas fa-user-graduate",
                "titulo": "Análise de Discentes",
                "template_name": "sucupira/partials/pessoal/_aba_discentes_conteudo.html"
            },
            {
                "id": "docentes",
                "label": "Docentes",
                "icone": "fas fa-chalkboard-teacher",
                "titulo": "Análise de Docentes",
                "template_name": "sucupira/partials/pessoal/_aba_docentes_conteudo.html"
            },
        ]

        contexto_cards = {
            'n_titulados_cards': p.cards_total_alunos_titulados_por_grau(),
            'docentes_card': p.card_total_docentes_ultimo_ano(),
        }

        contexto_plots = {
            'discentes_ano_plot': p.generate_plot_html(nome_plot='discentes_por_ano', filtros_selecionados={}),
            'discentes_sunburst_plot': p.generate_plot_html(nome_plot='discentes_por_area_sunburst', filtros_selecionados={}),
            'top_paises_discentes_plot': p.generate_plot_html(nome_plot='top_paises_discentes', filtros_selecionados={}),
            'docentes_ano_plot': p.generate_plot_html(nome_plot='docentes_por_ano', filtros_selecionados={}),
            'docentes_sunburst_plot': p.generate_plot_html(nome_plot='docentes_por_area_sunburst', filtros_selecionados={}),
            'top_paises_docentes_plot': p.generate_plot_html(nome_plot='top_paises_docentes', filtros_selecionados={}),
        }
        
        context = {
            "abas": abas,
            **contexto_cards,
            **contexto_plots,
        }
        return context

    context = get_cached_context()
    return render(request, r'sucupira/pessoal/pessoal_ppg.html', context)


def grafico_generico_pessoal(request, nome_plot: str):
    """
    View genérica para as atualizações HTMX da seção Pessoal.
    """
    plotter = PlotsPessoal()
    
    grafico_html = plotter.generate_plot_html(
        nome_plot=nome_plot,
        filtros_selecionados=request.GET.dict()
    )
    
    return HttpResponse(grafico_html)

# ==============================================================================
# VIEW PARA A PÓS-GRADUAÇÃO DA UFRJ NO GERAL (POSGRAD_UFRJ)
# ==============================================================================

def posgrad_ufrj(request):
    """Placeholder para uma futura página."""
    @cache_context_data(key_prefix='posgrad_ufrj', timeout=3600)
    def get_cached_context():
        """
        Gera e cacheia o contexto completo, usando a nova arquitetura de orquestração
        para criar os plots iniciais.
        """
        p = PlotsPpgUfrj()

        abas = [
            {
                "id": "ppgs_ufrj",
                "label": "PPGs UFRJ",
                "icone": "fas fa-graduation-cap",
                "titulo": "Análise dos PPGs da UFRJ",
                "template_name": "sucupira/partials/posgrad/posgrad_ufrj/_aba_ppgs_ufrj_conteudo.html"
            }
        ]

        # Note que 'cards_programas_por_modalidade' retorna uma lista,
        # então vamos juntá-la com os outros cards.
        card_total = p.card_total_programas_ultimo_ano()
        cards_modalidade = p.cards_programas_por_modalidade()
        card_conceito_max = p.card_total_programas_conceito_maximo()

        # Juntamos todos os cards em uma única lista para o template
        todos_os_cards = ([card_total] if card_total else []) + \
                         (cards_modalidade or []) + \
                         ([card_conceito_max] if card_conceito_max else [])

        contexto_cards = {
            'cards': todos_os_cards
        }

        contexto_plots = {
            'programas_contagem_ano_plot': p.generate_plot_html(nome_plot='programas_contagem_por_ano', filtros_selecionados={}),
        }
        
        context = {
            "abas": abas,
            **contexto_cards,
            **contexto_plots,
        }

        return context

    context = get_cached_context()
    return render(request, r'sucupira/posgrad/posgrad_ufrj.html', context)



def grafico_generico_posgrad_ufrj(request, nome_plot: str):
    """
    View genérica para as atualizações HTMX da seção Pessoal.
    """
    plotter = PlotsPpgUfrj()

    grafico_html = plotter.generate_plot_html(
        nome_plot=nome_plot,
        filtros_selecionados=request.GET.dict()
    )

    return HttpResponse(grafico_html)


# ==============================================================================
# VIEW PARA A LISTA DE PROGRAMAS (PPGS)
# ==============================================================================

def ppgs(request):
    """
    Lista todos os programas de pós-graduação, usando cache para otimizar a performance.
    """
    @cache_context_data(key_prefix='ppgs_list', timeout=3600)
    def get_cached_context():
        """
        Contém a lógica pesada de buscar e agrupar os programas, que só é
        executada se o resultado não estiver no cache.
        """
        ultimo_ano_qs = AnoPrograma.objects.filter(programa=OuterRef('pk')).order_by('-ano__ano_valor')

        # --- ANOTAÇÕES COMPLETAS RESTAURADAS AQUI ---
        programas = Programa.objects.annotate(
            nm_programa_ies=Subquery(ultimo_ano_qs.values('nm_programa_ies__nm_programa_ies')[:1]), 
            grande_area_nome=Subquery(ultimo_ano_qs.values('grande_area__nm_grande_area_conhecimento')[:1]),
        ).order_by('grande_area_nome', 'nm_programa_ies')

        agrupados = defaultdict(list)
        for programa in programas:
            chave = programa.grande_area_nome or "Sem Grande Área"
            agrupados[chave].append(programa)

        programas_agrupados = dict(sorted(agrupados.items()))
        
        return {'programas_agrupados': programas_agrupados}

    context = get_cached_context()
    return render(request, 'sucupira/posgrad/ppgs.html', context)


# ==============================================================================
# VIEWS PARA A PÁGINA "DETALHE DO PPG"
# ==============================================================================

def ppg_detalhe(request, programa_id):
    """
    Renderiza a página de detalhes de um programa, com cache dinâmico por programa.
    """
    @cache_context_data(key_prefix='ppg_detalhe', timeout=3600)
    def get_cached_context(prog_id):
        """Gera e cacheia o contexto para um programa específico."""
        p = PlotsPpgDetalhe(programa_id=prog_id)
        
        # --- DEFINIÇÃO DAS ABAS COMPLETA RESTAURADA AQUI ---
        abas = [
            {
                "id": "programa", 
                "label": "Programa", 
                "icone": "fas fa-graduation-cap", 
                "titulo": "Análise do Programa",
                "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_programa_conteudo.html"
            },
            {
                "id": "discentes", 
                "label": "Discentes", 
                "icone": "fas fa-user-graduate", 
                "titulo": "Análise de Discentes",
                "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_discentes_conteudo.html"
            },
            {
                "id": "docentes", 
                "label": "Docentes", 
                "icone": "fas fa-chalkboard-teacher", 
                "titulo": "Análise de Docentes",
                "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_docentes_conteudo.html"
            },
        ]
        
        ultimo_ano_qs = AnoPrograma.objects.filter(programa_id=OuterRef('pk')).order_by('-ano__ano_valor')
        
        # --- ANOTAÇÕES COMPLETAS RESTAURADAS AQUI ---
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
            pk=prog_id
        )
        cursos = Curso.objects.filter(programa_id=prog_id).select_related("grau_curso").order_by("grau_curso__nm_grau_curso")
        
        filtros_iniciais = {'programa_id': prog_id}
        contexto_plots = {
            'conceito_programa_ano_plot': p.generate_plot_html(nome_plot='conceito_programa_por_ano', filtros_selecionados=filtros_iniciais),
            'discentes_ano_plot': p.generate_plot_html(nome_plot='discentes_por_ano_ppg', filtros_selecionados=filtros_iniciais),
            'docentes_ano_plot': p.generate_plot_html(nome_plot='docentes_por_ano_ppg', filtros_selecionados=filtros_iniciais),
            'media_titulacao_ano_plot': p.generate_plot_html(nome_plot='media_titulacao_por_ano', filtros_selecionados=filtros_iniciais),
        }

        context = {
            "abas": abas,
            "programa": programa,
            "cursos": cursos,
            **contexto_plots,
        }
        return context

    context = get_cached_context(prog_id=programa_id)
    return render(request, "sucupira/posgrad/ppg_detalhe.html", context)


def grafico_generico_ppg(request, **kwargs):
    """
    View genérica para as atualizações HTMX da seção Detalhe do PPG.
    """
    # --- INÍCIO DA CORREÇÃO ---
    # 1. Extraímos o 'nome_plot' dos argumentos da URL.
    nome_plot = kwargs.pop('nome_plot', None)
    if not nome_plot:
        raise Http404("O 'nome_plot' não foi fornecido na URL.")

    # 2. O 'kwargs' restante agora contém apenas o 'programa_id'.
    plotter = PlotsPpgDetalhe(**kwargs)
    # --- FIM DA CORREÇÃO ---

    filtros = request.GET.dict()
    # Adicionamos o programa_id aos filtros para que a estratégia o receba.
    filtros['programa_id'] = kwargs.get('programa_id')

    grafico_html = plotter.generate_plot_html(
        nome_plot=nome_plot,
        filtros_selecionados=filtros
    )
    
    return HttpResponse(grafico_html)