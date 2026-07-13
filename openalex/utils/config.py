# Dicionário global com os IDs do OpenAlex das unidades da UFRJ
# Útil para remover duplicidades em contagens de parcerias externas

INSTITUICOES_UFRJ = {
    'MATRIZ': 'I122140584',
    'FAPERJ': 'I4210148226', 
    'HUCFF': 'I4210138087', #HU
    'VALONGO': 'I4210089367',
    'CIENCIAS_COGNICAO': 'I4210126836',
    'BIOFISICA': 'I4387153105',
    'CNPQ': 'I11385950',
    'CAPES': 'I4210097716',
}

# Já exportamos a lista de valores pronta para o Django ORM consumir no __in=[]
UFRJ_IDS_LIST = list(INSTITUICOES_UFRJ.values())