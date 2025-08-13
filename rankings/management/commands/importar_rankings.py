import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Escopo, Ranking, Ano, Resultado

from django.conf import settings
from gid.utils_scripts_etl import df_to_dw

class Command(BaseCommand):
    help = 'Importa dados para os modelos a partir de um arquivo CSV usando pandas.'

    @transaction.atomic
    def handle(self, *args, **options):

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/ranking/escopo.csv')
        df_to_dw(df, Escopo, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/ranking/ranking.csv')
        df_to_dw(df, Ranking, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/ranking/ano.csv')
        df_to_dw(df, Ano, True)
        df = None

        df = pd.read_csv(f'{settings.BASE_DIR}/importar/ranking/resultado.csv')
        df_to_dw(df, Resultado, True)
        df = None
