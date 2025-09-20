from django import template

register = template.Library()

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

@register.filter
def capitalizar_frase(frase: str) -> str:
    if not frase:
        return frase
    
    palavras = frase.split()
    if not palavras:
        return frase
    
    palavras[0] = palavras[0].capitalize()
    
    for i in range(1, len(palavras)):
        palavra = palavras[i]
        if palavra.lower() in EXCECOES:
            palavras[i] = palavra.lower()
        else:
            palavras[i] = palavra.capitalize()
    
    return ' '.join(palavras)