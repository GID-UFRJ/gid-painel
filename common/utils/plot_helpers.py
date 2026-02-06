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

    sufixos = ['', 'mil', 'milhoões']
    
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