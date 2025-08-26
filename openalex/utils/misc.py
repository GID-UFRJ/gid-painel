def calculate_h_index(citations):
    """Calculates the H-index for a list of citation counts."""
    if not citations:
        return 0
    citations = sorted(citations, reverse=True)
    h_index = 0
    for i, c in enumerate(citations):
        if c >= (i + 1):
            h_index = i + 1
        else:
            break
    return h_index