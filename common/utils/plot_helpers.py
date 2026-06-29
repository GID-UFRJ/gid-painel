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


DICIONARIO_CURADO = {
    # Nomes traduzidos para o inglês (comuns no OpenAlex/Bases internacionais)
    "NUCLEAR ENGINEERING INSTITUTE": "IEN",
    "VALONGO OBSERVATORY": "OBS. VALONGO",
    "NATIONAL COUNCIL FOR SCIENTIFIC AND TECHNOLOGICAL DEVELOPMENT": "CNPQ",
    "MILITARY INSTITUTE OF ENGINEERING": "IME",
    "ESTÁCIO (BRAZIL)": "ESTÁCIO",
    "STATE UNIVERSITY OF NORTE FLUMINENSE": "UENF",
    "NATIONAL INSTITUTE OF SCIENCE AND TECHNOLOGY FOR STRUCTURAL BIOLOGY AND BIOIMAGING": "INBEB",
    "FEDERAL CENTER FOR TECHNOLOGICAL EDUCATION CELSO SUCKOW DA FONSECA": "CEFET/RJ",
    "BRAZILIAN AGRICULTURAL RESEARCH CORPORATION": "EMBRAPA",
    "D’OR INSTITUTE FOR RESEARCH AND EDUCATION": "IDOR",
    "RIO DE JANEIRO FEDERAL INSTITUTE OF EDUCATION, SCIENCE AND TECHNOLOGY": "IFRJ",
    "PETROBRAS (BRAZIL)": "PETROBRAS",
    "PONTIFICAL CATHOLIC UNIVERSITY OF RIO DE JANEIRO": "PUC-RIO",

    # Instituições em português
    "UNIVERSIDADE FEDERAL DO MARANHÃO": "UFMA",
    "UNIVERSIDADE FEDERAL DO AMAZONAS": "UFAM",
    "UNIVERSIDADE FEDERAL DE VIÇOSA": "UFV",
    "UNIVERSIDADE UNIGRANRIO": "UNIGRANRIO",
    "CENTRO DE TECNOLOGIA MINERAL": "CETEM",
    "UNIVERSIDADE FEDERAL DE SANTA MARIA": "UFSM",
    "INSTITUTO DE PESQUISAS JARDIM BOTÂNICO DO RIO DE JANEIRO": "JBRJ",
    "UNIVERSIDADE FEDERAL DE SÃO CARLOS": "UFSCAR",
    "UNIVERSIDADE FEDERAL DE GOIÁS": "UFG",
    "ESCOLA NACIONAL DE SAÚDE PÚBLICA": "ENSP",
    "UNIVERSIDADE FEDERAL DA PARAÍBA": "UFPB",
    "UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE": "UFRN",
    "UNIVERSIDADE FEDERAL DO PARÁ": "UFPA",
    "INSTITUTO NACIONAL DE METROLOGIA, QUALIDADE E TECNOLOGIA": "INMETRO",
    "UNIVERSIDADE FEDERAL DE PERNAMBUCO": "UFPE",
    "UNIVERSIDADE FEDERAL DO CEARÁ": "UFC",
    "CENTRO BRASILEIRO DE PESQUISAS FÍSICAS": "CBPF",
    "UNIVERSIDADE FEDERAL DO ESPÍRITO SANTO": "UFES",
    "UNIVERSIDADE FEDERAL DA BAHIA": "UFBA",
    "UNIVERSIDADE DE BRASÍLIA": "UNB",
    "UNIVERSIDADE FEDERAL DO PARANÁ": "UFPR",
    "INSTITUTO NACIONAL DO CÂNCER": "INCA",
    "UNIVERSIDADE FEDERAL DE SANTA CATARINA": "UFSC",
    "UNIVERSIDADE ESTADUAL PAULISTA (UNESP)": "UNESP",
    "FUNDAÇÃO CARLOS CHAGAS FILHO DE AMPARO À PESQUISA DO ESTADO DO RIO DE JANEIRO": "FAPERJ",
    "UNIVERSIDADE FEDERAL DE SÃO PAULO": "UNIFESP",
    "UNIVERSIDADE FEDERAL DE JUIZ DE FORA": "UFJF",
    "UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL": "UFRGS",
    "UNIVERSIDADE FEDERAL RURAL DO RIO DE JANEIRO": "UFRRJ",
    "UNIVERSIDADE FEDERAL DE MINAS GERAIS": "UFMG",
    "UNIVERSIDADE ESTADUAL DE CAMPINAS (UNICAMP)": "UNICAMP",
    "HOSPITAL UNIVERSITÁRIO CLEMENTINO FRAGA FILHO": "HUCFF",
    "UNIVERSIDADE FEDERAL DO ESTADO DO RIO DE JANEIRO": "UNIRIO",
    "UNIVERSIDADE DE SÃO PAULO": "USP",
    "FUNDAÇÃO OSWALDO CRUZ": "FIOCRUZ",
    "UNIVERSIDADE FEDERAL FLUMINENSE": "UFF",
    "UNIVERSIDADE DO ESTADO DO RIO DE JANEIRO": "UERJ"
}

def gerar_sigla(nome_instituicao: str, dicionario_excecoes: dict = None) -> str:
    """
    Gera uma sigla a partir do nome de uma instituição, seguindo regras específicas:
    1. A própria palavra capitalizada, se for uma única palavra.
    2. Duas palavras, com a segunda em parênteses: primeira palavra capitalizada,
       seguida de hífen e das 3 primeiras letras da segunda, capitalizadas.
    3. Texto entre parênteses.
    4. As letras maiúsculas das string concatenadas.
    *Prioriza um dicionário de exceções fornecido; se não encontrar, aplica regras estruturais.
    """

    if dicionario_excecoes is None:
        dicionario_excecoes = DICIONARIO_CURADO


    if not isinstance(nome_instituicao, str) or not nome_instituicao:
        return ""

    nome_clean = nome_instituicao.strip()
    nome_upper = nome_clean.upper()

    # --- PRECEDÊNCIA MÁXIMA: Dicionário Curado ---
    # Verifica se o nome (em maiúsculas) existe no dicionário. Se sim, retorna a sigla curada.
    if dicionario_excecoes and nome_upper in dicionario_excecoes:
        return dicionario_excecoes[nome_upper]

    palavras = nome_clean.split()
    
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