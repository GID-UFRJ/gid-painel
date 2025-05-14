import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Programas, Nivel, Centro, Unidade, Situacao, Modalidade, AreaBasica, AreaAvaliacao, Rede
from django.conf import settings

class Command(BaseCommand):
    help = 'Importa dados para o modelo Programas a partir de um arquivo CSV usando pandas.'

    @transaction.atomic
    def handle(self, *args, **options):
    

        Nivel.objects.all().delete()
        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/nivel.csv')
        for _, row in df.iterrows():
            nivel = Nivel(
                nivelId=row['nivelId'],
                nivelNome=row['nivel'],
            )
            nivel.save()


        Programas.objects.all().delete()
        df = pd.read_csv(f'{settings.BASE_DIR}/importar/programa/fato.csv')
        for _, row in df.iterrows():
            programa = Programas(
                codigo=row['codigo'],
                conceito=row['conceito'],
                nivel_id=row['nivelId'],
                centro_id=row['centroId'],
                unidade_id=row['unidadeId'],
                situacao_id=row['situacaoId'],
                modalidade_id=row['modalidadeId'],
                areaBasica_id=row['areaBasicaId'],
                areaAvaliacao_id=row['areaAvaliacaoId'],
                rede_id=row['redeId'],
                ativos=0 if pd.isna(row['ativos']) else int(row['ativos']),
                ingressantes=0 if pd.isna(row['ingressantes']) else int(row['ingressantes']),
                cancelados=0 if pd.isna(row['cancelados']) else int(row['cancelados']),
                trancados=0 if pd.isna(row['trancados']) else int(row['trancados']),
                abandonos=0 if pd.isna(row['abandonos']) else int(row['abandonos']),
            )
            programa.save()
            self.stdout.write(self.style.SUCCESS(f"Importado: {row['codigo']}"))
         