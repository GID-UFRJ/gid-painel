# sucupira/views.py

from collections import defaultdict
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import OuterRef, Subquery

# Importes padrão da sua aplicação
from .models import Programa, AnoPrograma, Curso
from common.utils.cache import cache_context_data

# O NOVO MOTOR: O Dispatcher e os Dicionários de Mapeamento
from common.utils.dispatcher import Dispatcher
from .utils.mapeamentos import (
    MAPEAMENTOS_DISCENTES,
    MAPEAMENTOS_DOCENTES,
    MAPEAMENTOS_PPG_GERAL,
    MAPEAMENTOS_PPG_INDIVIDUAL,
    MAPEAMENTOS_TODOS
)

# ==============================================================================
# VIEWS ESTÁTICAS E AUXILIARES
# ==============================================================================

def index(request):
    """Renderiza o índice do app, determinando o namespace a partir da URL."""
    namespace = request.resolver_match.namespace
    return render(request, f"sucupira/{namespace}/index.html")

# ==============================================================================
# VIEWS PARA A SEÇÃO PESSOAL (DISCENTES E DOCENTES)
# ==============================================================================

def pessoal_discentes(request):
    """Renderiza a página de análise de Discentes."""
    @cache_context_data(key_prefix='pessoal_discentes', timeout=3600)
    def get_cached_context():
        # Instancia o motor apenas com os gráficos de Pessoal
        p = Dispatcher(mapeamentos=MAPEAMENTOS_DISCENTES)

        context = {
            'discentes_ano_plot': p.generate_plot_html(nome_plot='discentes_por_ano', filtros_selecionados={}),
            'discentes_sunburst_plot': p.generate_plot_html(nome_plot='discentes_por_area_sunburst', filtros_selecionados={}),
            'top_paises_discentes_plot': p.generate_plot_html(nome_plot='top_paises_discentes', filtros_selecionados={}),
            'plotter': p, # Injeta para o sumário automático
        }
        return context

    return render(request, r'sucupira/pessoal/pessoal_discentes.html', get_cached_context())


def pessoal_docentes(request):
    """Renderiza a página de análise de Docentes."""
    @cache_context_data(key_prefix='pessoal_docentes', timeout=3600)
    def get_cached_context():
        p = Dispatcher(mapeamentos=MAPEAMENTOS_DOCENTES)

        context = {
            'docentes_ano_plot': p.generate_plot_html(nome_plot='docentes_por_ano', filtros_selecionados={}),
            'docentes_sunburst_plot': p.generate_plot_html(nome_plot='docentes_por_area_sunburst', filtros_selecionados={}),
            'top_paises_docentes_plot': p.generate_plot_html(nome_plot='top_paises_docentes', filtros_selecionados={}),
            'plotter': p, 
        }
        return context

    return render(request, r'sucupira/pessoal/pessoal_docentes.html', get_cached_context())

# ==============================================================================
# VIEW PARA A PÓS-GRADUAÇÃO DA UFRJ NO GERAL
# ==============================================================================

def posgrad_ufrj(request):
    """Página geral dos PPGs da UFRJ."""
    @cache_context_data(key_prefix='posgrad_ufrj', timeout=3600)
    def get_cached_context():
        p = Dispatcher(mapeamentos=MAPEAMENTOS_PPG_GERAL)

        context = {
            'programas_contagem_ano_plot': p.generate_plot_html(nome_plot='programas_contagem_por_ano', filtros_selecionados={}),
            'plotter': p,
        }
        return context

    return render(request, r'sucupira/posgrad/posgrad_ufrj.html', get_cached_context())

# ==============================================================================
# VIEWS PARA A LISTA E DETALHE DOS PROGRAMAS (PPGS)
# ==============================================================================

def ppgs(request):
    """Lista todos os programas de pós-graduação."""
    @cache_context_data(key_prefix='ppgs_list', timeout=3600)
    def get_cached_context():
        ultimo_ano_qs = AnoPrograma.objects.filter(programa=OuterRef('pk')).order_by('-ano__ano_valor')

        programas = Programa.objects.annotate(
            nm_programa_ies=Subquery(ultimo_ano_qs.values('nm_programa_ies__nm_programa_ies')[:1]), 
            grande_area_nome=Subquery(ultimo_ano_qs.values('grande_area__nm_grande_area_conhecimento')[:1]),
        ).order_by('grande_area_nome', 'nm_programa_ies')

        agrupados = defaultdict(list)
        for programa in programas:
            chave = programa.grande_area_nome or "Sem Grande Área"
            agrupados[chave].append(programa)

        return {'programas_agrupados': dict(sorted(agrupados.items()))}

    return render(request, 'sucupira/posgrad/ppgs.html', get_cached_context())


def ppg_detalhe(request, programa_id):
    """Renderiza a página de detalhes de um programa específico."""
    @cache_context_data(key_prefix='ppg_detalhe', timeout=3600)
    def get_cached_context(prog_id):
        p = Dispatcher(mapeamentos=MAPEAMENTOS_PPG_INDIVIDUAL)
        
        abas = [
            {"id": "programa", "label": "Programa", "icone": "fas fa-graduation-cap", "titulo": "Análise do Programa", "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_programa_conteudo.html"},
            {"id": "discentes", "label": "Discentes", "icone": "fas fa-user-graduate", "titulo": "Análise de Discentes", "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_discentes_conteudo.html"},
            {"id": "docentes", "label": "Docentes", "icone": "fas fa-chalkboard-teacher", "titulo": "Análise de Docentes", "template_name": "sucupira/partials/posgrad/ppg_detalhe/_aba_docentes_conteudo.html"},
        ]
        
        ultimo_ano_qs = AnoPrograma.objects.filter(programa_id=OuterRef('pk')).order_by('-ano__ano_valor')
        
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
        
        # Injeção do programa_id nos filtros iniciais
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
            "plotter": p, # Injeta para o sumário automático
        }
        return context

    return render(request, "sucupira/posgrad/ppg_detalhe.html", get_cached_context(prog_id=programa_id))

# ==============================================================================
# A "SUPER VIEW" GENÉRICA DO HTMX
# ==============================================================================

def grafico_generico_sucupira(request, nome_plot: str, **kwargs):
    """
    View ÚNICA para todas as requisições HTMX do aplicativo Sucupira.
    Substitui as antigas 'grafico_generico_pessoal', 'grafico_generico_posgrad_ufrj', etc.
    """
    # 1. Valida se o gráfico existe no sistema inteiro da Sucupira
    if nome_plot not in MAPEAMENTOS_TODOS:
        raise Http404(f"O gráfico '{nome_plot}' não está mapeado no sistema.")

    # 2. Instancia o motor com todos os mapeamentos
    plotter = Dispatcher(mapeamentos=MAPEAMENTOS_TODOS)

    # 3. Prepara os filtros juntando GET (Dropdowns HTMX) com kwargs da URL (programa_id)
    filtros = request.GET.dict().copy()
    filtros.update(kwargs) 

    # 4. Processa a mágica
    grafico_html = plotter.generate_plot_html(
        nome_plot=nome_plot,
        filtros_selecionados=filtros
    )
    
    return HttpResponse(grafico_html)