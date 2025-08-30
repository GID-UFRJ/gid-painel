import pandas as pd

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