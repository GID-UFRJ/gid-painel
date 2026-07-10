# openalex/templatetags/openalex_tags.py
from django import template
from openalex.models import Year, WorkType

register = template.Library()

# Caminho base para os filtros atômicos (reaproveitando o do common)
PATH_FILTROS_ATOMICOS = "common/partials/filtros/"

@register.inclusion_tag("common/partials/_layout_de_filtros_dinamico.html", takes_context=True)
def render_filtros_producao(context, tipo, url_grafico, grafico_id, spinner_id, grafico_html, plotter_name, nome_plot):
    """
    Monta o formulário de filtros para a seção OpenAlex (Produção)
    """
    ctx = { 
        "url_grafico": url_grafico, 
        "grafico_id": grafico_id, 
        "spinner_id": spinner_id, 
        "grafico_html": grafico_html,
        "plotter_name": plotter_name,
        "nome_plot": nome_plot,
    }
    
    lista_de_filtros = []
    agrupamentos_disponiveis = {}

    if tipo == "producao_por_ano":
        # Compondo os filtros que você pediu: ano, agrupamento e tipo de gráfico
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_agrupamento.html",
            #f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_documento.html", # Se você tiver este filtro atômico
        ]
        
        # Dados para alimentar os selects
        ctx.update({
            "tipos_documento": WorkType.objects.all(),
            "anos_disponiveis": Year.objects.all().order_by('-year'),
        })
        
        # Agrupamentos que aparecem no dropdown do gráfico de barras
        agrupamentos_disponiveis = {
            'Acesso Aberto': 'acesso_aberto',
            'Tipo de Documento': 'tipo_documento',
            'Domínio': 'dominio',
        }

    elif tipo == "distribuicao_tematica":
        # Sunburst geralmente só precisa de filtro de limite ou ano
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
        ]
    
    elif tipo == "citacoes_por_ano":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_metrica_impacto.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_agrupamento.html",
        ]
        
        # Opções que aparecerão no dropdown de Métricas
        ctx["metricas_disponiveis"] = {
            'Total de Citações': 'total_citacoes',
            'Média de Citações': 'media',
            'Mediana de Citações': 'mediana',
            'Citações Acumuladas': 'total_citacoes_acumuladas',
            'Índice H': 'hindex',
            '% Artigos com FWCI > 1': 'fwci_acima_1'
        }
        
        # Agrupamentos permitidos para esse gráfico específico
        agrupamentos_disponiveis = {
            'Domínio': 'dominio',
            'Acesso Aberto': 'acesso_aberto',
        }
    
    elif tipo == "evolucao_colaboracao":
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_tipo_grafico.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_agrupamento.html",
        ]
        
        # Agrupamentos permitidos para Evolução de Colaboração
        agrupamentos_disponiveis = {
            'Domínio': 'dominio',
            'Acesso Aberto': 'acesso_aberto',
            'Tipo de Documento': 'tipo_documento',
        }

        request = context['request']

        ctx["filtros_genericos"] = [
            {
                "id": "abrangencia_evolucao", # Sufixo ID
                "name": "tipo_colaboracao", 
                "label": "Abrangência",
                "col_class": "col-md-3",
                "opcoes": {
                    'Nacional': 'nacional',
                    'Internacional': 'internacional',
                },
                "selecionado": request.GET.get('tipo_colaboracao', 'nacional') 
            }
        ]

    elif tipo == "top_instituicoes":
        # Pegamos a URL atual para saber o que o usuário escolheu
        request = context['request']
        
        ctx["filtros_genericos"] = [
            {
                "id": "abrangencia", # Sufixo do ID do HTML
                "name": "tipo_colaboracao", # O parâmetro que vai pra URL
                "label": "Abrangência",
                "col_class": "col-md-3",
                "opcoes": {
                    'Nacional': 'nacional',
                    'Internacional': 'internacional',
                },
                # Pega o valor da URL, se não existir, usa 'nacional' como padrão
                "selecionado": request.GET.get('tipo_colaboracao', 'nacional') 
            },
            {
                "id": "limite",
                "name": "limite",
                "label": "Mostrar",
                "col_class": "col-md-2",
                "opcoes": {
                    'Top 5': '5',
                    'Top 10': '10',
                    'Top 20': '20',
                    'Top 50': '50',
                },
                # Pega o valor da URL, se não existir, usa '10' como padrão
                "selecionado": request.GET.get('limite', '10')
            }
        ]

    elif tipo == "distribuicao_citacoes":
        # Para um histograma, precisamos do período de tempo e, opcionalmente, 
        # como o usuário quer fatiar/colorir essas barras (ex: por Acesso Aberto)
        lista_de_filtros = [
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_inicial.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_ano_final.html",
            f"{PATH_FILTROS_ATOMICOS}_filtro_agrupamento.html",
        ]
        
        # Agrupamentos permitidos para o Histograma de Citações
        # (Isso vai criar as barras empilhadas ou agrupadas dentro de cada "Bin")
        agrupamentos_disponiveis = {
            'Acesso Aberto': 'acesso_aberto',
            'Domínio': 'dominio', 
        }

    ctx['lista_de_filtros'] = lista_de_filtros
    ctx['agrupamentos_disponiveis'] = agrupamentos_disponiveis
    return ctx