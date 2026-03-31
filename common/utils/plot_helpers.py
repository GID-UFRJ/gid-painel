# common/utils/plot_helpers.py

from django.db.models import Min, Max
import pandas as pd
import re


def extrair_periodo(queryset, campo_ano):
    """Extrai min/max de um campo e retorna string formatada."""
    if not campo_ano:
        return None
        
    res = queryset.aggregate(min_a=Min(campo_ano), max_a=Max(campo_ano))
    min_a, max_a = res['min_a'], res['max_a']

    if min_a is None:
        return None
    return str(min_a) if min_a == max_a else f"{min_a}-{max_a}"


def formatar_decimal(valor, precisao=1):
    """Formata um número com casas decimais fixas."""
    if valor is None:
        return "0"
    try:
        return f"{float(valor):.{precisao}f}".replace(".", ",")
    except (ValueError, TypeError):
        return str(valor)


def formatar_magnitude(valor, precisao=1):
    """
    Transforma números grandes em strings legíveis (K, M, B, T).
    Ex: 1500 -> 1.5K | 2500000 -> 2.5M
    """
    if valor is None:
        return "0"
    
    try:
        valor_num = float(valor)
    except (ValueError, TypeError):
        return str(valor)

    if abs(valor_num) < 1000:
        # Se for inteiro (ex: 150.0), remove o .0
        if valor_num % 1 == 0:
            return str(int(valor_num))
        return str(valor_num)

    magnitude = 0
    # Limita até 'T' (Trilhões), mas pode ser expandido
    while abs(valor_num) >= 1000 and magnitude < 4:
        magnitude += 1
        valor_num /= 1000.0

    sufixos = ['', ' mil', ' milhões']
    
    # Formata com a precisão desejada e remove zeros à direita desnecessários
    # Ex: 1.50 -> 1.5 | 1.0 -> 1
    formato = f"{{:.{precisao}f}}"
    valor_final = formato.format(valor_num).rstrip('0').rstrip('.')
    
    return f"{valor_final}{sufixos[magnitude]}"

def formatar_percentual(valor, precisao=1):
    """Formata um valor como percentual."""
    if valor is None:
        return "0%"
    return f"{valor}%"



def calculate_h_index(citations, pre_reverse_sorted=False):
    """Calculates the H-index for a list of citation counts.
    
    Args:
        citations (list[int]): lista de contagens de citações
        pre_reverse_sorted (bool): se True, assume que já está em ordem decrescente
    """
    if isinstance(citations, pd.Series):
        citations = citations.tolist()
    
    if not citations:
        return 0

    if not pre_reverse_sorted:
        citations = sorted(citations, reverse=True)
    
    h_index = 0
    for i, c in enumerate(citations):
        if c >= (i + 1):
            h_index = i + 1
        else:
            break
    return h_index


def gerar_sigla(nome_instituicao: str) -> str:
    """
    Gera uma sigla a partir do nome de uma instituição, seguindo regras específicas:
    1. A própria palavra capitalizada, se for uma única palavra.
    2. Duas palavras, com a segunda em parênteses: primeira palavra capitalizada,
       seguida de hífen e das 3 primeiras letras da segunda, capitalizadas.
    3. Texto entre parênteses.
    4. As letras maiúsculas das string concatenadas.
    """
    if not isinstance(nome_instituicao, str) or not nome_instituicao:
        return ""

    palavras = nome_instituicao.split()
    
    # Condição 1: Se a string tem apenas uma palavra
    if len(palavras) == 1:
        return palavras[0].upper()

    # Condição 2: Se tem duas palavras, sendo a segunda entre parênteses
    if len(palavras) == 2 and palavras[1].startswith('(') and palavras[1].endswith(')'):
        primeira_palavra = palavras[0].upper()
        segunda_palavra = palavras[1].strip('()').upper()
        return f"{primeira_palavra}-{segunda_palavra[:3]}"

    # Condição 3: Se houver parênteses em qualquer outro formato
    match = re.search(r'\((.*?)\)', nome_instituicao)
    if match:
        sigla_paren = match.group(1).upper()
        if len(sigla_paren) > 1 and not sigla_paren.isdigit():
            return sigla_paren
        
    # Condição 4: Fallback: Junta todas as letras maiúsculas em uma única string
    sigla = ''.join(char for char in nome_instituicao if char.isupper())

    return sigla

def renomear_siglas_duplicadas(series_siglas: pd.Series) -> pd.Series:
    """
    Identifica siglas duplicadas em uma Series e renomeia as ocorrências
    subsequentes com um sufixo numérico (ex: SIGLA-1, SIGLA-2),
    usando um método otimizado com groupby.
    """
    if not isinstance(series_siglas, pd.Series):
        raise TypeError("A entrada deve ser uma Series do Pandas.")

    # Cria uma contagem cumulativa para cada sigla repetida
    contagem = series_siglas.groupby(series_siglas).cumcount()

    # Identifica as siglas que se repetem (contagem > 0)
    siglas_duplicadas_mask = contagem > 0

    # Cria a nova Series
    # Para duplicatas, anexa '-N'. Para únicas, mantém a sigla original.
    siglas_renomeadas = series_siglas.astype(str) + '-' + contagem.astype(str)
    siglas_renomeadas = siglas_renomeadas.mask(~siglas_duplicadas_mask, series_siglas)
    
    return siglas_renomeadas