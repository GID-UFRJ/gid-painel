from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.shortcuts import HttpResponse
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

    return render(request, r'sucupira/pessoal/pessoal_ppg.html', {
        "abas": abas,
        'n_titulados_cards': p.cards_total_alunos_titulados_por_grau,
        'docentes_card': p.card_total_docentes_ultimo_ano,
        'discentes_ano_plot': p.discentes_por_ano(),
        'docentes_ano_plot': p.docentes_por_ano(),
    }
)

def grafico_discentes_por_ano(request):
    """
    View acionada pelo HTMX para atualizar o gráfico de discentes.
    Refatorada para funcionar com o novo modelo de PlotsPessoal.
    """
    plotter = PlotsPessoal()

    # Coleta todos os parâmetros da URL em um único dicionário.
    # A classe PlotsPessoal saberá como usar cada um.
    params = request.GET.dict()

    # Converte os anos para inteiros, com valores padrão seguros.
    try:
        params['ano_inicial'] = int(params.get('ano_inicial', 2013))
        params['ano_final'] = int(params.get('ano_final', 2024))
    except (ValueError, TypeError):
        params['ano_inicial'] = 2013
        params['ano_final'] = 2024
    
    # Gera o gráfico passando todos os parâmetros de uma vez.
    # Os argumentos da assinatura do método (ano_inicial, agrupamento, etc.)
    # serão extraídos, e o restante (situacao, grau_curso) será capturado
    # pelo **kwargs dentro do método.
    graf = plotter.discentes_por_ano(**params)
    
    return render(request, "common/partials/_plot_reativo.html", {'graf': graf})


def grafico_docentes_por_ano(request):
    """
    View acionada pelo HTMX para atualizar o gráfico de docentes.
    Refatorada para funcionar com o novo modelo de PlotsPessoal.
    """
    plotter = PlotsPessoal()

    # Coleta todos os parâmetros da URL.
    params = request.GET.dict()

    # Garante que os anos sejam inteiros.
    try:
        params['ano_inicial'] = int(params.get('ano_inicial', 2013))
        params['ano_final'] = int(params.get('ano_final', 2024))
    except (ValueError, TypeError):
        params['ano_inicial'] = 2013
        params['ano_final'] = 2024

    # A chamada para gerar o gráfico é idêntica, apenas mudando o método.
    graf = plotter.docentes_por_ano(**params)
    
    return render(request, "common/partials/_plot_reativo.html", {'graf': graf})


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




#from django.shortcuts import render, get_object_or_404
#from django.db.models import Avg
#import pandas as pd
#import plotly.express as px
#from .models import Programa, Discente, GrauCurso, Curso


#def gerar_grafico(programa_id, grau_nome, titulo_extra=""):
#    """
#    Gera um gráfico de tempo médio de titulação para um determinado grau.
#    Retorna HTML do gráfico ou None se não houver dados.
#    """
#    grau = GrauCurso.objects.filter(nm_grau_curso__iexact=grau_nome).first()
#    if not grau:
#        return None
#
#
#
#    qs = (
#        Discente.objects
#        .filter(
#            programa_id=programa_id,
#            grau_academico=grau,
#            situacao__nm_situacao_discente__icontains="TITULADO",
#        )
#        .exclude(qt_mes_titulacao=0)  # opcional: remove valores 0
#        .values("ano__ano_valor")
#        .annotate(media_qt_mes=Avg("qt_mes_titulacao"))
#        .order_by("ano__ano_valor")
#    )
#
#    df = pd.DataFrame(list(qs))
#    if df.empty:
#        return None
#
#    df.rename(columns={"ano__ano_valor": "Ano", "media_qt_mes": "Média"}, inplace=True)
#
#    fig = px.line(
#        df,
#        x="Ano",
#        y="Média",
#        markers=True,
#        title=f"Média de meses para titulação ({grau_nome}{titulo_extra})",
#    )
#    fig.update_traces(connectgaps=True)
#    fig.update_layout(
#        autosize=True,
#        margin=dict(l=40, r=40, t=60, b=40),
#        xaxis_title="Ano",
#        yaxis_title="Média de meses para titulação",
#        xaxis=dict(type="category"),
#    )
#    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})
#
#

def ppg_detalhe(request, programa_id):

    abas = [
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

    p = PlotsPpgDetalhe(programa_id=programa_id)

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

    # Gerar gráficos
    #graficos = {}
    #for grau_nome in ["Mestrado", "Doutorado", "Mestrado Acadêmico"]:
    #    grafico_html = gerar_grafico(programa_id, grau_nome)
    #    if grafico_html:
    #        graficos[grau_nome] = grafico_html

    context = {
        "abas": abas,
        "programa": programa,
        "cursos": cursos,
        'discentes_ano_plot': p.discentes_por_ano(**params),
        'docentes_ano_plot': p.docentes_por_ano(**params),

    }

    return render(request, "sucupira/posgrad/ppg_detalhe.html", context)


def grafico_discentes_por_ano_ppg(request, programa_id):
    """
    View acionada pelo HTMX para atualizar o gráfico de discentes.
    Refatorada para funcionar com o novo modelo de PlotsPessoal.
    """
    plotter = PlotsPpgDetalhe(programa_id=programa_id)

    # Coleta todos os parâmetros da URL em um único dicionário.
    # A classe PlotsPessoal saberá como usar cada um.
    params = request.GET.dict()

    # Converte os anos para inteiros, com valores padrão seguros.
    try:
        params['ano_inicial'] = int(params.get('ano_inicial', 2013))
        params['ano_final'] = int(params.get('ano_final', 2024))
    except (ValueError, TypeError):
        params['ano_inicial'] = 2013
        params['ano_final'] = 2024
    
    # Gera o gráfico passando todos os parâmetros de uma vez.
    # Os argumentos da assinatura do método (ano_inicial, agrupamento, etc.)
    # serão extraídos, e o restante (situacao, grau_curso) será capturado
    # pelo **kwargs dentro do método.
    graf = plotter.discentes_por_ano(**params)
    
    return render(request, "common/partials/_plot_reativo.html", {'graf': graf})


def grafico_docentes_por_ano_ppg(request, programa_id):
    """
    View acionada pelo HTMX para atualizar o gráfico de docentes.
    Refatorada para funcionar com o novo modelo de PlotsPessoal.
    """
    plotter = PlotsPpgDetalhe(programa_id=programa_id)

    # Coleta todos os parâmetros da URL.
    params = request.GET.dict()

    # Garante que os anos sejam inteiros.
    try:
        params['ano_inicial'] = int(params.get('ano_inicial', 2013))
        params['ano_final'] = int(params.get('ano_final', 2024))
    except (ValueError, TypeError):
        params['ano_inicial'] = 2013
        params['ano_final'] = 2024

    # A chamada para gerar o gráfico é idêntica, apenas mudando o método.
    graf = plotter.docentes_por_ano(**params)
    
    return render(request, "common/partials/_plot_reativo.html", {'graf': graf})

