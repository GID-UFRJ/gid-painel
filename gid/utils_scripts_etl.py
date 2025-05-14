from django.db import models
from django.db.models.query import QuerySet
import pandas as pd

def df_to_dw(df: pd.DataFrame, Modelo: models.Model, apagar_dados_anteriores: bool | None=False)-> QuerySet:
            
    if apagar_dados_anteriores:
        Modelo.objects.all().delete()
    
    #atributos_modelo_sem_id = [atributo.name for atributo in Modelo._meta.fields]
    atributos_modelo_com_id = [f'{atributo.name}_id' if atributo.is_relation else atributo.name for atributo in Modelo._meta.fields]
    print(f'nome dos atributos da entidade do banco de dados: \n {sorted(atributos_modelo_com_id)}')
    print(f'nome das colunas do arquivo csv: \n{sorted(df.columns)}')

    objetos = [
        Modelo(**{col: row[col] for col in atributos_modelo_com_id})
        for _, row in df.iterrows()
    ]

    Modelo.objects.bulk_create(objetos)



