import csv
import os
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# IMPORTANTE: Ajuste 'rankings' para o nome do seu app, se for diferente
from rankings.models import RankingTipo, Ranking, EscopoGeografico, ODS, RankingEntrada

# Tabela fixa das 17 ODS da ONU
ODS_DATA = {
    'ODS_1': 'Erradicação da Pobreza',
    'ODS_2': 'Fome Zero e Agricultura Sustentável',
    'ODS_3': 'Saúde e Bem-Estar',
    'ODS_4': 'Educação de Qualidade',
    'ODS_5': 'Igualdade de Gênero',
    'ODS_6': 'Água Potável e Saneamento',
    'ODS_7': 'Energia Limpa e Acessível',
    'ODS_8': 'Trabalho Decente e Crescimento Econômico',
    'ODS_9': 'Indústria, Inovação e Infraestrutura',
    'ODS_10': 'Redução das Desigualdades',
    'ODS_11': 'Cidades e Comunidades Sustentáveis',
    'ODS_12': 'Consumo e Produção Responsáveis',
    'ODS_13': 'Ação Contra a Mudança Global do Clima',
    'ODS_14': 'Vida na Água',
    'ODS_15': 'Vida Terrestre',
    'ODS_16': 'Paz, Justiça e Instituições Eficazes',
    'ODS_17': 'Parcerias e Meios de Implementação'
}

class Command(BaseCommand):
    help = 'Importa dados de Rankings automaticamente e popula as ODSs necessárias'

    def handle(self, *args, **options):
        # 1. Definir diretórios
        base_dir = settings.BASE_DIR
        diretorio_importacao = base_dir / 'importar' / 'ranking'
        arquivo_rankings = diretorio_importacao / 'rankings.csv'

        self.stdout.write(self.style.WARNING(f'Buscando arquivo em: {arquivo_rankings}'))

        # 2. Validações
        if not os.path.isdir(diretorio_importacao):
            raise CommandError(f'O diretório não existe: {diretorio_importacao}')
        if not os.path.exists(arquivo_rankings):
            raise CommandError(f'Arquivo de Rankings não encontrado: {arquivo_rankings}')

        # 3. Execução
        try:
            with transaction.atomic():
                # PASSO 1: Descobre quais ODSs são usadas no CSV
                ods_utilizadas = self.obter_ods_utilizadas(arquivo_rankings)
                
                # PASSO 2: Registra apenas as ODSs que foram encontradas
                self.importar_ods(ods_utilizadas)
                
                # PASSO 3: Importa os rankings em si
                self.importar_rankings(arquivo_rankings)
                
            self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro crítico durante a importação: {e}'))
            # raise e  # Descomente para ver o traceback completo se precisar depurar

    def obter_ods_utilizadas(self, caminho):
        """Faz uma pré-leitura do rankings.csv para extrair os códigos ODS únicos."""
        self.stdout.write(f'Mapeando ODS utilizadas em: {caminho.name}...')
        ods_set = set()
        
        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_ods = row.get('ODS', '').strip().upper()
                if raw_ods:
                    ods_set.add(raw_ods)
                    
        self.stdout.write(self.style.SUCCESS(f'>> Foram encontradas {len(ods_set)} ODSs únicas nos rankings.'))
        return ods_set

    def importar_ods(self, ods_utilizadas):
        """Popula o banco com as ODSs detectadas usando o dicionário interno."""
        self.stdout.write('Populando tabela de ODS com os itens utilizados...')
        count = 0
        
        for codigo, descricao in ODS_DATA.items():
            if codigo in ods_utilizadas:
                ODS.objects.update_or_create(
                    codigo=codigo,
                    defaults={'descricao': descricao}
                )
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'>> {count} ODS cadastradas no banco.'))

    def importar_rankings(self, caminho):
        """Importa os dados definitivos de ranking cruzando com as ODSs."""
        self.stdout.write(f'Lendo Rankings de: {caminho.name}...')
        
        tipo_academico, _ = RankingTipo.objects.get_or_create(nome="ACADÊMICO")
        tipo_sustentabilidade, _ = RankingTipo.objects.get_or_create(nome="SUSTENTABILIDADE")
        
        # Cache local dos códigos de ODS para busca rápida
        ods_existentes = set(ODS.objects.values_list('codigo', flat=True))

        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                # 1. Leitura Básica
                raw_ranking = row['Ranking'].strip().upper()
                raw_tipo = row['Tipo'].strip().upper()
                raw_escopo = row['Escopo'].strip().upper()
                raw_ods = row.get('ODS', '').strip().upper() 
                
                year = int(row['Year'])
                
                p_min_str = row.get('Posição Mínima', '').strip()
                p_max_str = row.get('Posição Máxima', '').strip()
                p_min = int(p_min_str) if p_min_str else (int(p_max_str) if p_max_str else 0)
                p_max = int(p_max_str) if p_max_str else p_min

                # 2. Definição do Tipo
                tipo_obj = tipo_academico if raw_tipo == "ACADÊMICO" else tipo_sustentabilidade
                
                # 3. Definição do Ranking Pai
                ranking_obj, _ = Ranking.objects.get_or_create(
                    nome=raw_ranking,
                    tipo=tipo_obj
                )
                
                # 4. Definição do Escopo Geográfico
                obj_geo, _ = EscopoGeografico.objects.get_or_create(nome=raw_escopo)
                
                # 5. Definição da ODS 
                obj_ods = None
                if raw_ods and raw_ods in ods_existentes:
                    obj_ods = ODS.objects.get(codigo=raw_ods)
                
                # 6. Salvar/Atualizar Entrada
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