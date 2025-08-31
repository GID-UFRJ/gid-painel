import pandas as pd
import re

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