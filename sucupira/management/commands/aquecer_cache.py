import time
import itertools
from django.core.management.base import BaseCommand
from django.test import Client

# Importe o modelo de Programa do seu app
from sucupira.models import Programa

class Command(BaseCommand):
    help = 'Gera e salva no cache os gráficos de todos os PPGs do banco de dados.'

    def handle(self, *args, **options):
        # 1. Puxa todos os IDs reais do banco de dados
        self.stdout.write("Consultando programas no banco de dados...")
        ids_programas = list(Programa.objects.values_list('id', flat=True))
        
        if not ids_programas:
            self.stdout.write(self.style.ERROR("Nenhum programa encontrado!"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"{len(ids_programas)} programas encontrados!"))

        # 2. Define as variações de filtros que queremos testar/aquecer
        # Dica: Mantenha as listas curtas para não gerar milhões de permutações
        filtros_possiveis = {
            'programa_id': ids_programas,
            'ano_inicial': [2018, 2019], 
            'ano_final': [2023, 2024],
        }

        # Gera as combinações matemáticas
        chaves, valores = zip(*filtros_possiveis.items())
        todas_combinacoes = [dict(zip(chaves, p)) for p in itertools.product(*valores)]
        
        total_requisicoes = len(todas_combinacoes)
        self.stdout.write(f"Iniciando requisições internas (Total: {total_requisicoes})...")
        
        # O Client simula um navegador acessando o seu site, mas sem gastar rede
        client = Client()
        
        # A URL alvo do seu gráfico HTMX (ajuste se o caminho for diferente)
        url_alvo = '/sucupira/grafico_generico/discentes_por_ano_ppg/'
        
        tamanho_total_bytes = 0
        sucessos = 0
        start_time = time.time()

        # 3. Dispara as simulações
        for index, parametros in enumerate(todas_combinacoes, 1):
            try:
                # Faz o GET simulado. O Django vai processar a view e o @cache_page vai salvar no Redis
                resposta = client.get(url_alvo, data=parametros)
                
                if resposta.status_code == 200:
                    sucessos += 1
                    tamanho_total_bytes += len(resposta.content)
                    
                if index % 50 == 0: # Printa a cada 50 pra não travar o terminal
                    self.stdout.write(f"Progresso: {index}/{total_requisicoes} processados...")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro na requisição {index}: {e}"))

        # 4. Exibe o relatório final
        end_time = time.time()
        tamanho_mb = tamanho_total_bytes / (1024 * 1024)

        self.stdout.write(self.style.SUCCESS("-" * 50))
        self.stdout.write(self.style.SUCCESS("TESTE E AQUECIMENTO FINALIZADOS!"))
        self.stdout.write(f"Tempo total: {round(end_time - start_time, 2)} segundos")
        self.stdout.write(f"Gráficos gerados/cacheados: {sucessos}/{total_requisicoes}")
        self.stdout.write(f"Tamanho total REAL na memória: ~{round(tamanho_mb, 2)} MB")