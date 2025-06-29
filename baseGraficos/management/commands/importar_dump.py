import pandas as pd
from django.core.management.base import BaseCommand
from django.core.management import call_command

from django.db import transaction
from baseGraficos.models import GraficoSucupira, ListaSucupira
from django.conf import settings

class Command(BaseCommand):
    help = 'Importa dados para o modelo Sucupira'

    @transaction.atomic
    def handle(self, *args, **options):
    
        GraficoSucupira.objects.all().delete()
        print(GraficoSucupira.objects.all())
        call_command('loaddata', '/app/dump/dump_sucupira_producao_artigos_periodicos')

        ListaSucupira.objects.all().delete()
        print(ListaSucupira.objects.all())
        call_command('loaddata', '/app/dump/dump_sucupira_lista_programa')
