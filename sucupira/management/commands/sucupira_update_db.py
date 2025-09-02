import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import *

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'importar/sucupira')

class Command(BaseCommand):
    help = 'Popula o banco de dados com os dados dos arquivos CSV'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a população do banco de dados...'))

        self._create_anos_from_csvs()
        self._populate_pessoas()
        self._populate_programas()
        self._populate_cursos()
        self._populate_ano_programas()
        self._populate_docentes()
        self._populate_discentes()
        self._populate_producao()

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))

    def _get_or_create(self, model, field_name, value, defaults=None):
        if not value or pd.isna(value):
            return None
        kwargs = {field_name: value}
        obj, created = model.objects.get_or_create(**kwargs, defaults=defaults)
        if created:
            self.stdout.write(f'  -> Criado {model.__name__}: {value}')
        return obj

    def _create_anos_from_csvs(self):
        self.stdout.write('1. Criando todos os ANOS necessários...')
        anos_necessarios = set()
        csv_files = ['ano_programas.csv', 'discentes.csv', 'docentes.csv', 'pessoas.csv', 'producao.csv', 'programas.csv']
        ano_cols = {'AN_BASE'} #Anos de nascimento ou de criação dos programas,cursos não são utilizados aqui, apenas os anos de análise mesmo

        for file_name in csv_files:
            path = os.path.join(DATA_DIR, file_name)
            if os.path.exists(path):
                df = pd.read_csv(path, dtype=str)
                for col in ano_cols:
                    if col in df.columns:
                        anos_necessarios.update(df[col].dropna().unique())

        for ano in sorted(ano for ano in anos_necessarios if str(ano).isdigit()):
            Ano.objects.get_or_create(ano_valor=int(ano))
        self.stdout.write(self.style.SUCCESS('ANOS criados.'))

    def _populate_pessoas(self):
        self.stdout.write('2. Populando Pessoas...')
        path = os.path.join(DATA_DIR, 'pessoas.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        # Criando tabelas de dimensão juntamente com dicionários para preenchimentos dos campos em
        sexo_lookup = {s: self._get_or_create(PessoaSexo, 'sexo', s) for s in df['TP_SEXO'].unique() if s}
        pais_lookup = {p: self._get_or_create(PessoaPais, 'pais', p) for p in df['NM_PAIS_NACIONALIDADE'].unique() if p}
        
        # O campo 'ano_nascimento' é um IntegerField, portanto o valor será atribuído diretamente.
        for _, row in df.iterrows():
            if not row['ID_PESSOA_HASH']:
                continue
            
            # Conversão direta do ano para inteiro.
            ano_nasc = None
            if row['AN_NASCIMENTO'] and row['AN_NASCIMENTO'].isdigit():
                ano_nasc = int(row['AN_NASCIMENTO'])

            # Atribuição dos valores das colunas
            Pessoa.objects.update_or_create(
                id_pessoa_hash=row['ID_PESSOA_HASH'],
                defaults={
                    'tp_sexo': sexo_lookup.get(row['TP_SEXO']),
                    'ano_nascimento': ano_nasc, #Ano de nascimento é passado diretamente
                    'pais_nacionalidade': pais_lookup.get(row['NM_PAIS_NACIONALIDADE'])
                }
            )
        self.stdout.write(self.style.SUCCESS('Pessoas populadas.'))

    def _populate_programas(self):
        self.stdout.write('3. Populando Programas...')
        path = os.path.join(DATA_DIR, 'programas.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            grande_area = self._get_or_create(ProgramaGrandeArea, 'nm_grande_area_conhecimento', row['NM_GRANDE_AREA_CONHECIMENTO'])
            area = self._get_or_create(ProgramaAreaConhecimento, 'nm_area_conhecimento', row['NM_AREA_CONHECIMENTO'])
            area_aval = self._get_or_create(ProgramaAreaAvaliacao, 'cd_area_avaliacao', row['CD_AREA_AVALIACAO'], defaults={'nm_area_avaliacao': row['NM_AREA_AVALIACAO']})

            # Conversão direta do ano para inteiro.
            ano_inicio_programa = None
            if row['AN_INICIO_PROGRAMA'] and row['AN_INICIO_PROGRAMA'].isdigit():
                ano_inicio_programa = int(row['AN_INICIO_PROGRAMA'])



            Programa.objects.update_or_create(
                id_programa_hash=row['ID_PROGRAMA_HASH'],
                defaults={
                    'nm_programa_ies': row['NM_PROGRAMA_IES'],
                    'grande_area': grande_area,
                    'area_conhecimento': area,
                    'area_avaliacao': area_aval,
                    'an_inicio_programa': ano_inicio_programa, #Ano de início do programa é passado diretamente
                }
            )
        self.stdout.write(self.style.SUCCESS('Programas populados.'))

    def _populate_cursos(self):
        self.stdout.write('4. Populando Cursos...')
        path = os.path.join(DATA_DIR, 'cursos.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            try:
                programa = Programa.objects.get(id_programa_hash=row['ID_PROGRAMA_HASH'])
                grau = self._get_or_create(GrauCurso, 'nm_grau_curso', row['NM_GRAU_PROGRAMA'])
                Curso.objects.get_or_create(
                    programa=programa,
                    grau_curso=grau,
                    defaults={'an_inicio_curso': int(row['AN_INICIO_CURSO'])}
                )
            except Programa.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  -> Programa com hash {row['ID_PROGRAMA_HASH']} não encontrado."))
                continue
        self.stdout.write(self.style.SUCCESS('Cursos populados.'))

    def _populate_ano_programas(self):
        self.stdout.write('5. Populando Ano-Programas...')
        path = os.path.join(DATA_DIR, 'ano_programas.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            try:
                ano = Ano.objects.get(ano_valor=int(row['AN_BASE']))
                programa = Programa.objects.get(id_programa_hash=row['ID_PROGRAMA_HASH'])
                situacao = self._get_or_create(ProgramaSituacao, 'ds_situacao_programa', row['DS_SITUACAO_PROGRAMA'])

                AnoPrograma.objects.get_or_create(
                    ano=ano,
                    programa=programa,
                    defaults={
                        'cd_conceito_programa': row['CD_CONCEITO_PROGRAMA'],
                        'in_rede': row['IN_REDE'].upper() == 'S', # Assumindo 'S' ou 'N' como valores comuns
                        'situacao': situacao
                    }
                )
            except (Programa.DoesNotExist, Ano.DoesNotExist):
                self.stdout.write(self.style.WARNING(f"  -> Ano ou Programa não encontrado para a linha: {row.to_dict()}"))
                continue
        self.stdout.write(self.style.SUCCESS('Ano-Programas populados.'))

    def _populate_docentes(self):
        self.stdout.write('6. Populando Docentes...')
        path = os.path.join(DATA_DIR, 'docentes.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            try:
                ano = Ano.objects.get(ano_valor=int(row['AN_BASE']))
                pessoa = Pessoa.objects.get(id_pessoa_hash=row['ID_PESSOA_HASH'])
                programa = Programa.objects.get(id_programa_hash=row['ID_PROGRAMA_HASH'])

                categoria = self._get_or_create(DocenteCategoria, 'ds_categoria_docente', row['DS_CATEGORIA_DOCENTE'])
                vinculo = self._get_or_create(DocenteVinculo, 'ds_tipo_vinculo_docente_ies', row['DS_TIPO_VINCULO_DOCENTE_IES'])
                regime = self._get_or_create(DocenteRegimeTrabalho, 'ds_regime_trabalho', row['DS_REGIME_TRABALHO'])
                bolsa = self._get_or_create(DocenteBolsaProdutividade, 'cd_cat_bolsa_produtividade', row['CD_CAT_BOLSA_PRODUTIVIDADE'])
                titulacao = self._get_or_create(GrauCurso, 'nm_grau_curso', row['NM_GRAU_TITULACAO'])
                faixa_etaria = self._get_or_create(FaixaEtaria, 'ds_faixa_etaria', row['DS_FAIXA_ETARIA'])

                Docente.objects.get_or_create(
                    ano=ano,
                    pessoa=pessoa,
                    programa=programa,
                    defaults={
                        'categoria': categoria,
                        'vinculo': vinculo,
                        'regime_trabalho': regime,
                        'bolsa_produtividade': bolsa,
                        'grau_titulacao': titulacao,
                        'faixa_etaria': faixa_etaria,
                    }
                )
            except (Pessoa.DoesNotExist, Programa.DoesNotExist, Ano.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f"  -> Objeto relacionado não encontrado para a linha do docente: {row['ID_PESSOA_HASH']}. Erro: {e}"))
                continue
        self.stdout.write(self.style.SUCCESS('Docentes populados.'))

    def _populate_discentes(self):
        self.stdout.write('7. Populando Discentes...')
        path = os.path.join(DATA_DIR, 'discentes.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            try:
                ano = Ano.objects.get(ano_valor=int(row['AN_BASE']))
                pessoa = Pessoa.objects.get(id_pessoa_hash=row['ID_PESSOA_HASH'])
                programa = Programa.objects.get(id_programa_hash=row['ID_PROGRAMA_HASH'])

                grau = self._get_or_create(GrauCurso, 'nm_grau_curso', row['DS_GRAU_ACADEMICO_DISCENTE'])
                situacao = self._get_or_create(DiscenteSituacao, 'nm_situacao_discente', row['NM_SITUACAO_DISCENTE'])
                faixa_etaria = self._get_or_create(FaixaEtaria, 'ds_faixa_etaria', row['DS_FAIXA_ETARIA'])

                Discente.objects.get_or_create(
                    ano=ano,
                    pessoa=pessoa,
                    programa=programa,
                    grau_academico=grau,
                    defaults={
                        'st_ingressante': row['ST_INGRESSANTE'].upper() == 'S',
                        'situacao': situacao,
                        'qt_mes_titulacao': int(row['QT_MES_TITULACAO'] or 0),
                        'faixa_etaria': faixa_etaria,
                    }
                )
            except (Pessoa.DoesNotExist, Programa.DoesNotExist, Ano.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f"  -> Objeto relacionado não encontrado para a linha do discente: {row['ID_PESSOA_HASH']}. Erro: {e}"))
                continue
        self.stdout.write(self.style.SUCCESS('Discentes populados.'))

    def _populate_producao(self):
        self.stdout.write('8. Populando Produção...')
        path = os.path.join(DATA_DIR, 'producao.csv')
        df = pd.read_csv(path, dtype=str).fillna('')

        for _, row in df.iterrows():
            try:
                # Criar/obter o objeto da tabela de lookup 'ProducaoIdentificador' primeiro.
                id_prod_obj = self._get_or_create(ProducaoIdentificador, 'id_producao_hash', row['ID_PRODUCAO_HASH'])
                if not id_prod_obj:
                    continue # Pula a linha se o hash da produção estiver vazio.

                ano = Ano.objects.get(ano_valor=int(row['AN_BASE']))
                programa = Programa.objects.get(id_programa_hash=row['ID_PROGRAMA_HASH'])
                # O autor pode não existir na tabela Pessoa, então usamos .get() para evitar erro
                autor_pessoa = Pessoa.objects.get(id_pessoa_hash=row['ID_PESSOA_HASH']) if row['ID_PESSOA_HASH'] else None

                tp_autor = self._get_or_create(ProducaoTpAutor, 'tp_autor', row['TP_AUTOR'])
                cat_docente = self._get_or_create(DocenteCategoria, 'ds_categoria_docente', row.get('NM_TP_CATEGORIA_DOCENTE'))
                nivel_discente = self._get_or_create(GrauCurso, 'nm_grau_curso', row.get('NM_NIVEL_DISCENTE'))

                # A chave de busca é uma combinação que define unicamente a autoria de uma produção.
                # 'get_or_create' é utilizado, já que  cada linha do CSV representa uma relação de autoria única.
                Producao.objects.get_or_create(
                    producao=id_prod_obj,
                    ano=ano,
                    programa=programa,
                    autor_pessoa=autor_pessoa,
                    defaults={
                        'tp_autor': tp_autor,
                        'categoria_docente': cat_docente,
                        'nivel_discente': nivel_discente
                    }
                )
            except (Programa.DoesNotExist, Ano.DoesNotExist, Pessoa.DoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f"  -> Objeto relacionado não encontrado para a linha de produção: {row['ID_PRODUCAO_HASH']}. Erro: {e}"))
                continue
        self.stdout.write(self.style.SUCCESS('Produção populada.'))