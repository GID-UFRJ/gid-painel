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

        self._clear_database() #Limpa todas as tabelas antes de popular (limpa valores órfãos nas tabelas de dimensão - talvez implementar uma flag pra isso no futuro...)

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
    
        # Criando tabelas de dimensão
        sexo_lookup = {s: self._get_or_create(PessoaSexo, 'sexo', s) for s in df['TP_SEXO'].unique() if s}
        pais_lookup = {p: self._get_or_create(PessoaPais, 'pais', p) for p in df['NM_PAIS_NACIONALIDADE'].unique() if p}
        tipo_nacionalidade_lookup = {
            t: self._get_or_create(PessoaTipoNacionalidade, 'ds_tipo_nacionalidade', t)
            for t in df['DS_TIPO_NACIONALIDADE'].unique() if t
        }
    
        for _, row in df.iterrows():
            if not row['ID_PESSOA_HASH']:
                continue
            
            # Conversão direta do ano para inteiro
            ano_nasc = int(row['AN_NASCIMENTO']) if row['AN_NASCIMENTO'] and row['AN_NASCIMENTO'].isdigit() else None
    
            Pessoa.objects.update_or_create(
                id_pessoa_hash=row['ID_PESSOA_HASH'],
                defaults={
                    'tp_sexo': sexo_lookup.get(row['TP_SEXO']),
                    'ano_nascimento': ano_nasc,
                    'pais_nacionalidade': pais_lookup.get(row['NM_PAIS_NACIONALIDADE']),
                    'tipo_nacionalidade': tipo_nacionalidade_lookup.get(row['DS_TIPO_NACIONALIDADE']),
                }
            )
        self.stdout.write(self.style.SUCCESS('Pessoas populadas.'))


    def _populate_programas(self):
        self.stdout.write('3. Populando Programas (base)...')
        path = os.path.join(DATA_DIR, 'programas.csv')
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING('Arquivo programas.csv não encontrado. Pulando.'))
            return
            
        df = pd.read_csv(path, dtype=str).fillna('')
        
        programas_para_criar = []
        for _, row in df.iterrows():
            if not row['ID_PROGRAMA_HASH']:
                continue
                
            an_inicio = int(row['AN_INICIO_PROGRAMA']) if row['AN_INICIO_PROGRAMA'].isdigit() else None
            
            # Usando update_or_create para garantir que não haja duplicatas se o script for executado novamente
            Programa.objects.update_or_create(
                id_programa_hash=row['ID_PROGRAMA_HASH'],
                defaults={
                    'an_inicio_programa': an_inicio
                }
            )
        self.stdout.write(self.style.SUCCESS('Programas (base) populados.'))

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
        self.stdout.write('5. Populando Ano-Programas (detalhes anuais)...')
        path = os.path.join(DATA_DIR, 'ano_programas.csv')
        df = pd.read_csv(path, dtype=str).fillna('')
        
        # Cache de objetos para performance
        anos = {a.ano_valor: a for a in Ano.objects.all()}
        programas = {p.id_programa_hash: p for p in Programa.objects.all()}

        for _, row in df.iterrows():
            # Tenta converter para int, tratando possíveis erros de valor
            try:
                ano_valor = int(float(row['AN_BASE']))
            except (ValueError, TypeError):
                self.stdout.write(self.style.WARNING(f"  -> Valor de AN_BASE inválido '{row['AN_BASE']}'. Pulando linha."))
                continue

            ano_obj = anos.get(ano_valor)
            programa_obj = programas.get(row['ID_PROGRAMA_HASH'])

            if not ano_obj or not programa_obj:
                self.stdout.write(self.style.WARNING(f"  -> Ano ou Programa não encontrado para a linha: {row.to_dict()}"))
                continue

            # Criar/obter objetos das tabelas de dimensão
            nm_programa_obj = self._get_or_create(ProgramaNome, 'nm_programa_ies', row['NM_PROGRAMA_IES'])
            grande_area_obj = self._get_or_create(ProgramaGrandeArea, 'nm_grande_area_conhecimento', row['NM_GRANDE_AREA_CONHECIMENTO'])
            area_conhecimento_obj = self._get_or_create(ProgramaAreaConhecimento, 'nm_area_conhecimento', row['NM_AREA_CONHECIMENTO'])
            area_avaliacao_obj = self._get_or_create(ProgramaAreaAvaliacao, 'cd_area_avaliacao', row['CD_AREA_AVALIACAO'], defaults={'nm_area_avaliacao': row['NM_AREA_AVALIACAO']})
            conceito_obj = self._get_or_create(ProgramaConceito, 'cd_conceito_programa', row['CD_CONCEITO_PROGRAMA'], defaults={'ds_conceito': row.get('DS_CONCEITO')})
            modalidade_obj = self._get_or_create(ProgramaModalidade, 'nm_modalidade_programa', row['NM_MODALIDADE_PROGRAMA'])
            situacao_obj = self._get_or_create(ProgramaSituacao, 'ds_situacao_programa', row['DS_SITUACAO_PROGRAMA'])
            
            in_rede_val = str(row.get('IN_REDE', '')).upper() == 'TRUE'

            AnoPrograma.objects.update_or_create(
                ano=ano_obj,
                programa=programa_obj,
                defaults={
                    'nm_programa_ies': nm_programa_obj,
                    'nm_modalidade_programa': modalidade_obj,
                    'grande_area': grande_area_obj,
                    'area_conhecimento': area_conhecimento_obj,
                    'area_avaliacao': area_avaliacao_obj,
                    'cd_conceito_programa': conceito_obj,
                    'in_rede': in_rede_val,
                    'situacao': situacao_obj
                }
            )
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
                titulacao = self._get_or_create(GrauDocente, 'nm_grau_titulacao', row['NM_GRAU_TITULACAO'])
                faixa_etaria = self._get_or_create(FaixaEtaria, 'ds_faixa_etaria', row['DS_FAIXA_ETARIA'])

                Docente.objects.update_or_create(
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

                Discente.objects.update_or_create(
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

    def _clear_database(self):
        self.stdout.write(self.style.WARNING("Limpando todas as tabelas (evitar valores órfãos graças a updates dos dados da CAPES)"))

        # A ordem importa por causa das FKs
        Producao.objects.all().delete()
        Docente.objects.all().delete()
        Discente.objects.all().delete()
        AnoPrograma.objects.all().delete()
        Curso.objects.all().delete()

        # Agora as tabelas de dimensão
        ProducaoIdentificador.objects.all().delete()
        ProducaoTpAutor.objects.all().delete()
        DocenteCategoria.objects.all().delete()
        DocenteVinculo.objects.all().delete()
        DocenteRegimeTrabalho.objects.all().delete()
        DocenteBolsaProdutividade.objects.all().delete()
        GrauDocente.objects.all().delete()
        GrauCurso.objects.all().delete()
        FaixaEtaria.objects.all().delete()
        ProgramaNome.objects.all().delete()
        ProgramaGrandeArea.objects.all().delete()
        ProgramaAreaConhecimento.objects.all().delete()
        ProgramaAreaAvaliacao.objects.all().delete()
        ProgramaConceito.objects.all().delete()
        ProgramaSituacao.objects.all().delete()
        Pessoa.objects.all().delete()
        PessoaSexo.objects.all().delete()
        PessoaPais.objects.all().delete()
        PessoaTipoNacionalidade.objects.all().delete()

        # Por último, tabelas base
        Programa.objects.all().delete()
        Ano.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Banco de dados limpo."))
