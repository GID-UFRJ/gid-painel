import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Programas, Nivel, Centro, Unidade, Situacao, Modalidade, AreaBasica, AreaAvaliacao, Rede

from django.conf import settings
from gid.utils_scripts_etl import df_to_dw

class Command(BaseCommand):
    help = 'Importa dados para os modelos a partir de um arquivo CSV usando pandas.'

    @transaction.atomic
    def handle(self, *args, **options):

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/areaavaliacao.csv')
        df_to_dw(df, AreaAvaliacao, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/areabasica.csv')
        df_to_dw(df, AreaBasica, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/centro.csv')
        df_to_dw(df, Centro, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/modalidade.csv')
        df_to_dw(df, Modalidade, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/nivel.csv')
        df_to_dw(df, Nivel, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/rede.csv')
        df_to_dw(df, Rede, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/situacao.csv')
        df_to_dw(df, Situacao, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/unidade.csv')
        df_to_dw(df, Unidade, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/fato.csv')
        df['ativos'] = df['ativos'].fillna(0)
        df['ingressantes'] = df['ingressantes'].fillna(0)
        df['cancelados'] = df['cancelados'].fillna(0)
        df['trancados'] = df['trancados'].fillna(0)
        df['abandonos'] = df['abandonos'].fillna(0)
        df_to_dw(df, Programas, True)
        df = None




