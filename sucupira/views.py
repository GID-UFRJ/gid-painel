from collections import defaultdict
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from .utils.plots import PlotsPessoal, PlotsPpgDetalhe
from .models import Programa, DiscenteSituacao, ProgramaGrandeArea, GrauCurso, AnoPrograma, Curso, Discente
from django.db.models import OuterRef, Subquery
from common.utils.cache import cache_context_data

# Create your views here.

def index(request): #index unificado
    namespace = request.resolver_match.namespace # pega o namespace atual (vem do include no urls.py principal)
    return render(request, f"sucupira/{namespace}/index.html")

# ==============================================================================
# VIEW PARA A PÁGINA "PESSOAL PPG"
# ==============================================================================
def pessoal_ppg(request):

    # A função decorada abaixo lida com a criação de todo o contexto da página.
    # O decorador irá interceptar a chamada, verificar o cache e, se necessário,
    # executar esta função para gerar os dados.
    @cache_context_data(key_prefix='pessoal_ppg')
    def get_cached_context():
        """
        Esta função interna contém toda a lógica "cara" que queremos cachear.
        Ela é responsável por gerar o contexto completo para a página pessoal_ppg.
        """
        
        # Instanciamos a classe de plots, que usaremos para gerar cards e gráficos.
        p = PlotsPessoal()

        # Definição da estrutura das abas, mantida dentro da função por enquanto.
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

        # ETAPA 1: Gerar os dados dos cards (KPIs).
        # Agrupamos todas as chamadas relacionadas aos cards em um dicionário próprio
        # para manter o código organizado.
        contexto_cards = {
            'n_titulados_cards': p.cards_total_alunos_titulados_por_grau(),
            'docentes_card': p.card_total_docentes_ultimo_ano(),
        }

        # ETAPA 2: Gerar os dados dos plots (a parte mais pesada e demorada).
        # Agrupamos todas as chamadas de plotagem em seu próprio dicionário.
        contexto_plots = {
            'discentes_ano_plot': p.discentes_por_ano(),
            'discentes_sunburst_plot': p.discentes_por_area_sunburst(),
            'top_paises_discentes_plot': p.top_paises_discentes(),
            'docentes_ano_plot': p.docentes_por_ano(),
            'docentes_sunburst_plot': p.docentes_por_area_sunburst(),
            'top_paises_docentes_plot': p.top_paises_docentes(),
        }
        
        # ETAPA 3: Montar o contexto final, combinando todas as partes.
        # Esta é a estrutura final que será enviada para o template (e para o cache).
        context = {
            "abas": abas,
            
            # O operador `**` (desempacotamento de dicionário) "funde" os dicionários
            # de cards e plots diretamente no contexto final. É uma forma limpa
            # e moderna de combinar múltiplos dicionários.
            **contexto_cards,
            **contexto_plots,
        }
        
        return context

    # A lógica principal da view agora é muito simples:
    # Apenas chama a função com cache e renderiza o template com o resultado.
    context = get_cached_context()
    
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
    Lista todos os programas de pós-graduação, usando cache para otimizar a performance.
    """

    # Aplicamos o decorador à nossa função interna.
    # Damos a ele um prefixo de chave único para não colidir com outros caches.
    @cache_context_data(key_prefix='ppgs_list') 
    def get_cached_context():
        """
        Esta função contém toda a lógica pesada de buscar e agrupar os programas.
        Ela só será executada se o resultado não estiver no cache.
        """
        
        # --- TODA A SUA LÓGICA ORIGINAL VAI AQUI DENTRO ---

        # Subquery para buscar o último AnoPrograma de cada programa
        ultimo_ano_qs = AnoPrograma.objects.filter(
            programa=OuterRef('pk')
        ).order_by('-ano__ano_valor')

        # Anotando os campos que queremos do último ano
        programas = Programa.objects.annotate(
            nm_programa_ies=Subquery(ultimo_ano_qs.values('nm_programa_ies__nm_programa_ies')[:1]), 
            grande_area_nome=Subquery(ultimo_ano_qs.values('grande_area__nm_grande_area_conhecimento')[:1]),
        ).order_by('grande_area_nome', 'nm_programa_ies')

        # Agrupar por grande área
        agrupados = defaultdict(list)
        for programa in programas:
            chave = programa.grande_area_nome or "Sem Grande Área"
            agrupados[chave].append(programa)

        # Transformar em dict ordenado por chave (Grande Área)
        programas_agrupados = dict(sorted(agrupados.items()))

        # A função retorna o dicionário de contexto completo que será cacheado.
        context = {
            'programas_agrupados': programas_agrupados
        }
        return context

    # A lógica principal da view é apenas chamar a função com cache.
    context = get_cached_context()
    
    return render(request, 'sucupira/posgrad/ppgs.html', context)



# ==============================================================================
# VIEW PARA A PÁGINA "DETALHE DO PPG"
# ==============================================================================
def ppg_detalhe(request, programa_id):

    # O decorador usará o valor de 'prog_id' para criar uma chave de cache única
    # para cada programa, garantindo que os dados não se misturem.
    @cache_context_data(key_prefix='ppg_detalhe')
    def get_cached_context(prog_id):
        """
        Gera e cacheia o contexto para a página de detalhes de um programa específico.
        """
        
        # Definição da estrutura das abas, mantida dentro da função.
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
        
        # ETAPA 1: Fazer as consultas pesadas ao banco de dados.
        # Deve-se de usar 'prog_id', o argumento da função interna.
        p = PlotsPpgDetalhe(programa_id=prog_id)
        
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
                # ... outras anotações para buscar os dados mais recentes do programa ...
            ),
            pk=prog_id
        )
        cursos = Curso.objects.filter(programa_id=prog_id).select_related("grau_curso").order_by("grau_curso__nm_grau_curso")
        
        # ETAPA 2: Gerar os plots iniciais para esta página.
        contexto_plots = {
            'conceito_programa_ano_plot': p.conceito_programa_por_ano(),
            'discentes_ano_plot': p.discentes_por_ano(),
            'docentes_ano_plot': p.docentes_por_ano(),
            'media_titulacao_ano_plot': p.media_titulacao_por_ano(),
            # Adicione outros plots que devem ser pré-renderizados aqui.
        }

        # ETAPA 3: Montar o contexto final.
        context = {
            "abas": abas,
            "programa": programa,
            "cursos": cursos,
            
            # Desempacota o dicionário de plots no contexto final.
            **contexto_plots,
        }
        
        return context

    # Chamamos a função decorada, passando o 'programa_id' da URL.
    # O decorador usará este valor para criar sua chave de cache única.
    context = get_cached_context(prog_id=programa_id)
    
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