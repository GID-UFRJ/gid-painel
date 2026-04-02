from django.shortcuts import render
#from .utils.plots import PlotsProducao, PlotsImpacto, PlotsColaboracao
from common.utils.dispatcher import Dispatcher
from .utils.mapeamentos import MAPEAMENTOS_OPENALEX

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, r'openalex/index.html')


# Create your views here.
def producao(request):
    """
    View responsável por carregar a página de Produção pela PRIMEIRA VEZ.
    """
    print("1. Entrei na View Produção")
    
    # 1. Instanciamos o Dispatcher genérico
    p = Dispatcher()
    
    # 2. Acoplamos o "Cérebro" (O dicionário de receitas)
    p.MAPEAMENTOS = MAPEAMENTOS_OPENALEX

    # 3. Geramos os gráficos
    html_producao_ano = p.generate_plot_html(
        nome_plot='producao_por_ano', 
        filtros_selecionados={'ano_inicial': 1990, 'ano_final': 2024}
    )
    
    html_distribuicao = p.generate_plot_html(
        nome_plot='distribuicao_tematica', 
        filtros_selecionados={}
    )

    print(f"4. Voltei para a View. Tamanho do HTML (Temática): {len(html_distribuicao)}")

    # 4. Mandamos para o template
    return render(request, 'openalex/producao.html', {
        'graf_01': html_producao_ano,
        'graf_02': html_distribuicao,
    })

def impacto(request):
    """
    View responsável por carregar a página de Impacto pela PRIMEIRA VEZ.
    """
    p = Dispatcher()
    p.MAPEAMENTOS = MAPEAMENTOS_OPENALEX

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
            filtros_selecionados=filtros_iniciais_grafico
        ),
    }

    return render(request, 'openalex/impacto.html', context)



def colaboracao(request):
    """
    View responsável por carregar a página de Colaboração pela PRIMEIRA VEZ.
    """
    print("1. Entrei na View Colaboração")
    
    p = Dispatcher(mapeamentos=MAPEAMENTOS_OPENALEX)

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
    }

    return render(request, 'openalex/colaboracao.html', context)


#def impacto(request):
#    p = PlotsImpacto()
#    return render(request, r'openalex/impacto.html', {
#        #'card_01':p.producao_total_citacoes(),
#        #'card_02':p.producao_total_hindex(),
#
#        'graf_01':p.citacoes_por_ano(ano_inicial=1990, ano_final=2024),
#        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
#    }
#)
#
#def colaboracao(request):
#    p = PlotsColaboracao()
#
#    return render(request, r'openalex/colaboracao.html', {
#        #'card_01':p.producao_colaboracao_nacional(),
#        #'card_02':p.producao_colaboracao_internacional(),
#
#        'graf_01':p.colaboracoes_por_ano(),
#        'graf_02':p.top_instituicoes_colaboradoras(n_instituicoes=10, tipo_instituicao='nacional'),
#        #'graf_02':p.top_instituicoes_colaboradoras(internacional=True),
#        #'graf_02':p.producao_por_ano_worktype(ano_inicial=1990, ano_final=2024),
#        #'graf_03':p.producao_por_ano_worktype(ano_inicial=1990, 
#        #                                      ano_final=2024,
#        #                                      tipo_plot='barra'),
#        #'graf_04': p.distribuicao_tematica_artigos(),
#    }
#)


#def impacto(request):
#    context = {
#        'titulo_pagina': 'Impacto',
#        'mensagem': 'Esta página está em manutenção. Estamos trabalhando na nova arquitetura do backend.'
#    }
#    return render(request, 'common/manutencao.html', context)

#def colaboracao(request):
#    context = {
#        'titulo_pagina': 'Colaboração',
#        'mensagem': 'Esta página está em manutenção. Estamos trabalhando na nova arquitetura do backend.'
#    }
#    return render(request, 'common/manutencao.html', context)


#def grafico_generico_producao(request, nome_plot):
#    plotter = PlotsProducao() 
#    
#    filtros = request.GET.dict() 
#   
#    try:
#        grafico_html = plotter.generate_plot_html(
#            nome_plot=nome_plot,
#            filtros_selecionados=filtros
#        )
#        return HttpResponse(grafico_html)
#    except Exception as e:
#        return HttpResponse(f"<div class='alert alert-danger'>Erro no plot '{nome_plot}': {e}</div>")


def grafico_generico_openalex(request, nome_plot):
    """
    View acionada pelo HTMX. Recebe requisições via AJAX quando o usuário 
    muda um dropdown (ex: muda de 'Total' para 'Índice H').
    """
    p = Dispatcher()
    p.MAPEAMENTOS = MAPEAMENTOS_OPENALEX

    # 1. Pega todos os filtros da URL (ex: ?ano_inicial=2000&metrica=hindex)
    filtros_selecionados = request.GET.dict()

    # 2. O Dispatcher processa a mágica
    grafico_html = p.generate_plot_html(
        nome_plot=nome_plot, 
        filtros_selecionados=filtros_selecionados
    )

    # 3. Retorna APENAS o HTML do gráfico (para o HTMX injetar na tela)
    return HttpResponse(grafico_html)