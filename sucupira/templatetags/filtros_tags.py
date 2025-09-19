from django import template
from ..models import DiscenteSituacao, ProgramaGrandeArea, GrauCurso

register = template.Library()

#Tags para filtros específicos do gráfico de discentes
@register.inclusion_tag('sucupira/partials/_plot_pessoal_por_ano.html')
def render_filtros_discentes(url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Monta os dados para os filtros de discentes e renderiza o partial
    junto com o gráfico.
    """
    return {
        # filtros
        'situacoes': DiscenteSituacao.objects.all().order_by('nm_situacao_discente'),
        'grandes_areas': ProgramaGrandeArea.objects.all().order_by('nm_grande_area_conhecimento'),
        'graus_curso': GrauCurso.objects.all().order_by('nm_grau_curso').exclude,

        # parâmetros do gráfico
        'url_grafico': url_grafico,
        'grafico_id': grafico_id,
        'spinner_id': spinner_id,
        'grafico_html': grafico_html,
    }



#Conectivos que não devem ser capitalizados
EXCECOES = [
    'de', 'da', 'do', 'das', 'dos', 'em', 'por', 'com', 'para',
    'a', 'e', 'o', 'as', 'os', 'à', 'às', 'ao', 'aos',
    'no', 'na', 'nas', 'nos',
    'pelo', 'pela', 'pelos', 'pelas',
    'um', 'uma', 'uns', 'umas',
    'entre', 'até', 'sem', 'sob', 'sobre', 'trás', 'perante',
    'como', 'após', 'que', 'se', 'mas', 'porque', 'quando', 'onde',
    'qual', 'quais', 'quem',
    'cujo', 'cuja', 'cujos', 'cujas'
]

#Filtro aplicável ao valor das tags
@register.filter
def capitalizar_frase(frase: str) -> str:
    if not frase:
        return frase
    
    palavras = frase.split()
    if not palavras:
        return frase
    
    # primeira palavra sempre capitalizada
    palavras[0] = palavras[0].capitalize()
    
    for i in range(1, len(palavras)):
        palavra = palavras[i]
        if palavra.lower() in EXCECOES:
            palavras[i] = palavra.lower()
        else:
            palavras[i] = palavra.capitalize()
    
    return ' '.join(palavras)
