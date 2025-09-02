from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.shortcuts import HttpResponse
from .utils.plots import PlotsPessoal
from .models import Programa

# Create your views here.

def index(request): #index unificado
    namespace = request.resolver_match.namespace # pega o namespace atual (vem do include no urls.py principal)
    return render(request, f"sucupira/{namespace}/index.html")

def pessoal_ppg(request):
    p = PlotsPessoal()

    return render(request, r'sucupira/pessoal/pessoal_ppg.html', {
        'n_titulados_cards': p.cards_total_alunos_titulados_por_grau,
        'docentes_card': p.card_total_docentes_ultimo_ano,

    }
)


def grafico_discentes_por_ano(request):
    """
    View acionada pelo HTMX para atualizar o gráfico de discentes.
    """
    p = PlotsPessoal()

    # Pega os valores dos filtros do GET request
    grau_curso_id = request.GET.get('grau_curso', None)
    filtro_pessoal = request.GET.get('filtro_pessoal', None)
    situacao = request.GET.get('situacao', None)
    grande_area = request.GET.get('grande_area', None)
    ano_inicio = request.GET.get('ano_inicio', None)
    ano_final = request.GET.get('ano_final', None)

    # Gera o novo gráfico com os filtros aplicados
    graf = p.grafico_discentes_por_ano(
        grau_curso_id=grau_curso_id,
        filtro_pessoal=filtro_pessoal,
        situacao=situacao,
        grande_area=grande_area,
        ano_inicio=ano_inicio,
        ano_final=ano_final
    )
    
    context = {
        'graf': graf,
    }
    
    # Retorna apenas o HTML do gráfico
    return render(request, 'dashboard/partials/grafico_discentes_ano.html', context)



def posgrad_ufrj(request):
    return HttpResponse('Página em construção')

def ppgs(request):
    """
    Lista todos os programas de pós-graduação por grande area em ordem alfabética.
    """
    # Buscar todos os programas com a grande_area já carregada
    programas = Programa.objects.select_related('grande_area').order_by(
        'grande_area__nm_grande_area_conhecimento', 'nm_programa_ies'
    )

    # Agrupar por Grande Área
    agrupados = defaultdict(list)
    for programa in programas:
        chave = programa.grande_area.nm_grande_area_conhecimento
        agrupados[chave].append(programa)

    # Transformar em dict ordenado por chave (Grande Área)
    programas_agrupados = dict(sorted(agrupados.items()))

    context = {
        'programas_agrupados': programas_agrupados
    }
    return render(request, 'posgrad/ppgs.html', context)


def ppg_detalhe(request, programa_id):
    """
    Exibe os detalhes de um programa de pós-graduação.
    """
    # Tenta buscar o objeto Programa pelo ID, ou retorna 404 se não existir.
    programa = get_object_or_404(Programa, pk=programa_id)
    
    # Aqui, você pode buscar outros dados relacionados ao programa
    # para exibir no gráfico, por exemplo, docentes ou discentes.
    # Exemplo:
    # docentes = programa.docente_set.all().order_by('ano__ano_valor')
    
    context = {
        'programa': programa,
        # 'docentes': docentes, # Adicione outros dados aqui
    }
    
    return render(request, 'posgrad/ppg_detalhe.html', context)