from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.shortcuts import HttpResponse
from .models import Programa

# Create your views here.

def index(request):
    return render(request, 'sucupira/index.html')

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
    return render(request, 'sucupira/ppgs.html', context)


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
    
    return render(request, 'sucupira/ppg_detalhe.html', context)