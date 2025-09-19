from django import template
from sucupira.models import (
    ProgramaGrandeArea, GrauCurso, DiscenteSituacao,
    ProgramaModalidade, DocenteCategoria, DocenteBolsaProdutividade
)

register = template.Library()


@register.inclusion_tag("sucupira/partials/_plot_pessoal_por_ano.html")
def render_filtros_pessoal(tipo, url_grafico, grafico_id, spinner_id, grafico_html):
    """
    Templatetag genérica para renderizar filtros de docentes ou discentes.
    Mantém partials separados, mas evita duplicação de código.
    """
    #contexto geral
    context = {
        # filtros comuns a todos os gráficos
        "grandes_areas": ProgramaGrandeArea.objects.all().order_by("nm_grande_area_conhecimento"),
        # parâmetros do gráfico
        "url_grafico": url_grafico,
        "grafico_id": grafico_id,
        "spinner_id": spinner_id,
        "grafico_html": grafico_html,
    }

    # filtros específicos
    if tipo == "discentes":
        context.update({
            "partial_filtros": "sucupira/partials/_filtros_discentes.html",
            "graus_curso": GrauCurso.objects.all().order_by("nm_grau_curso"),
            "situacoes": DiscenteSituacao.objects.all().order_by("nm_situacao_discente"),
        })
    elif tipo == "docentes":
        context.update({
            "partial_filtros": "sucupira/partials/_filtros_docentes.html",
            "modalidades": ProgramaModalidade.objects.all().order_by("nm_modalidade_programa"),
            "categorias": DocenteCategoria.objects.all().order_by("ds_categoria_docente"),
            "bolsas": DocenteBolsaProdutividade.objects.all().order_by("cd_cat_bolsa_produtividade"),
        })
    else:
        raise ValueError("Tipo de filtro inválido")

    return context


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
