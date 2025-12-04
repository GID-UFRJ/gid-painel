import csv
import os
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
# IMPORTANTE: Substitua 'rankings' pelo nome real do seu app se for diferente
from rankings.models import RankingTipo, Ranking, EscopoGeografico, ODS, RankingEntrada

class Command(BaseCommand):
    help = 'Importa dados de ODS e Rankings automaticamente da pasta "importar/ranking"'

    def handle(self, *args, **options):
        # 1. Definir diretórios
        base_dir = settings.BASE_DIR
        diretorio_importacao = base_dir / 'importar' / 'ranking'
        arquivo_ods = diretorio_importacao / 'ods.csv'
        arquivo_rankings = diretorio_importacao / 'rankings.csv'

        self.stdout.write(self.style.WARNING(f'Buscando arquivos em: {diretorio_importacao}'))

        # 2. Validações
        if not os.path.isdir(diretorio_importacao):
            raise CommandError(f'O diretório não existe: {diretorio_importacao}')
        if not os.path.exists(arquivo_ods):
            raise CommandError(f'Arquivo de ODS não encontrado: {arquivo_ods}')
        if not os.path.exists(arquivo_rankings):
            raise CommandError(f'Arquivo de Rankings não encontrado: {arquivo_rankings}')

        # 3. Execução
        try:
            with transaction.atomic():
                self.importar_ods(arquivo_ods)
                self.importar_rankings(arquivo_rankings)
                
            self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro crítico durante a importação: {e}'))
            # Se quiser ver o erro completo, descomente a linha abaixo:
            # raise e

    def importar_ods(self, caminho):
        self.stdout.write(f'Lendo ODS de: {caminho.name}...')
        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # CONVERSÃO PARA UPPER AQUI
                codigo = row['escopoNome'].strip().upper()
                descricao = row['escopoNomeCompleto'].strip()

                ODS.objects.update_or_create(
                    codigo=codigo,
                    defaults={'descricao': descricao}
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'>> {count} ODS processadas.'))

    def importar_rankings(self, caminho):
        self.stdout.write(f'Lendo Rankings de: {caminho.name}...')
        
        # Strings "hardcoded" também devem ser UPPER para encontrar no banco
        tipo_academico, _ = RankingTipo.objects.get_or_create(nome="ACADÊMICO")
        tipo_sustentabilidade, _ = RankingTipo.objects.get_or_create(nome="SUSTENTABILIDADE")
        
        # Cache local para performance (chaves em UPPER)
        ods_existentes = set(ODS.objects.values_list('codigo', flat=True))

        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                # CONVERSÃO PARA UPPER AQUI (Essencial para get_or_create funcionar)
                raw_ranking = row['Ranking'].strip().upper()
                raw_tipo = row['Tipo'].strip().upper()
                raw_escopo = row['Escopo'].strip().upper()
                
                year = int(row['Year'])
                
                p_min_str = row.get('Posição Mínima', '').strip()
                p_max_str = row.get('Posição Máxima', '').strip()
                p_min = int(p_min_str) if p_min_str else (int(p_max_str) if p_max_str else 0)
                p_max = int(p_max_str) if p_max_str else p_min

                # Decisão do Tipo
                tipo_obj = tipo_academico if raw_tipo == "ACADÊMICO" else tipo_sustentabilidade
                
                # Decisão do Ranking Pai
                ranking_obj, _ = Ranking.objects.get_or_create(
                    nome=raw_ranking,
                    tipo=tipo_obj
                )
                
                # Decisão ODS vs Geo
                obj_ods = None
                obj_geo = None
                
                if raw_escopo in ods_existentes:
                    obj_ods = ODS.objects.get(codigo=raw_escopo)
                    obj_geo, _ = EscopoGeografico.objects.get_or_create(nome="MUNDO")
                else:
                    obj_geo, _ = EscopoGeografico.objects.get_or_create(nome=raw_escopo)
                
                # Update ou Create
                RankingEntrada.objects.update_or_create(
                    ranking=ranking_obj,
                    escopo_geografico=obj_geo,
                    ods=obj_ods,
                    ano=year,
                    defaults={
                        'posicao_minima': p_min,
                        'posicao_maxima': p_max
                    }
                )
                count += 1
                
                if count % 50 == 0:
                    self.stdout.write(f'   Processando linha {count}...', ending='\r')

            self.stdout.write(self.style.SUCCESS(f'>> {count} entradas de ranking processadas.'))