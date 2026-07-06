import time
import itertools
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from sucupira.models import Programa

class Command(BaseCommand):
    help = 'Gera e salva no cache os gráficos de todos os PPGs do banco de dados.'

    def handle(self, *args, **options):
        # 1. Busca os dados reais
        ids_programas = list(Programa.objects.values_list('id', flat=True))
        if not ids_programas:
            self.stdout.write(self.style.ERROR("Nenhum programa encontrado no banco de dados."))
            return
            
        # 2. Prepara as combinações matemáticas
        filtros_possiveis = {
            'programa_id': ids_programas,
            'ano_inicial': [2018, 2019], 
            'ano_final': [2023, 2024],
        }
        
        chaves, valores = zip(*filtros_possiveis.items())
        todas_combinacoes = [dict(zip(chaves, p)) for p in itertools.product(*valores)]
        
        self.stdout.write(f"Iniciando aquecimento do cache para {len(todas_combinacoes)} gráficos...")

        # 3. Resolve a URL e prepara o Client silencioso
        try:
            url_alvo = reverse('sucupira:htmx_grafico_sucupira', kwargs={'nome_plot': 'discentes_por_ano_ppg'})
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro de URL: {e}"))
            return
            
        client = Client(SERVER_NAME='localhost')
        
        # Variáveis de métricas finais
        tamanho_total_bytes = 0
        sucessos = 0
        start_time = time.time()

        # 4. Executa silenciosamente
        for parametros in todas_combinacoes:
            try:
                resposta = client.get(url_alvo, data=parametros)
                if resposta.status_code == 200:
                    sucessos += 1
                    tamanho_total_bytes += len(resposta.content)
            except:
                # Ignora erros individuais silenciosamente para não quebrar o fluxo
                continue

        # 5. Imprime apenas o resumo final
        end_time = time.time()
        tamanho_mb = tamanho_total_bytes / (1024 * 1024)

        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS(f"AQUECIMENTO CONCLUÍDO!"))
        self.stdout.write(f"Tempo total: {round(end_time - start_time, 2)} segundos")
        self.stdout.write(f"Gráficos armazenados: {sucessos}")
        self.stdout.write(f"Tamanho na memória: ~{round(tamanho_mb, 2)} MB")