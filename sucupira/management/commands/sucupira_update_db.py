import os
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import *

# Define o diretório base apontando para os arquivos tratados do Sucupira[cite: 1]
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'importar/sucupira')

class Command(BaseCommand):
    help = 'Popula o banco de dados com os dados dos arquivos CSV de forma otimizada'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a população do banco de dados...'))

        # Limpa as tabelas existentes em ordem reversa de dependência (chaves estrangeiras)
        self._clear_database()

        # Executa as etapas de povoamento sequencialmente
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
        """Auxiliar simples para dados de menor volume ou dimensões isoladas."""
        if not value or pd.isna(value):
            return None
        kwargs = {field_name: value}
        obj, created = model.objects.get_or_create(**kwargs, defaults=defaults)
        return obj

    def _calcular_quadrienio(self, ano_valor):
        """Calcula a string descritiva do quadriênio e o índice numérico sequencial de ordenação."""
        if ano_valor < 2013:
            return "Pré-2013", 0
        indice_ciclo = (ano_valor - 2013) // 4
        ordem = indice_ciclo + 1
        inicio = 2013 + (indice_ciclo * 4)
        fim = inicio + 3
        return f"{inicio}-{fim}", ordem

    def _create_anos_from_csvs(self):
        """Cria e relaciona os anos e quadriênios lendo de forma otimizada os arquivos de escopo temporal."""
        self.stdout.write('1. Criando todos os ANOS e QUADRIÊNIOS necessários...')
        anos_necessarios = set()
        csv_files = ['ano_programas.csv', 'programas.csv']
        ano_cols = {'AN_BASE'}

        for file_name in csv_files:
            path = os.path.join(DATA_DIR, file_name)
            if os.path.exists(path):
                df = pd.read_csv(path, usecols=lambda c: c in ano_cols, dtype=str)
                for col in ano_cols:
                    if col in df.columns:
                        anos_necessarios.update(df[col].dropna().unique())

        for ano in sorted(ano for ano in anos_necessarios if str(ano).isdigit()):
            ano_int = int(ano)
            nome_quadrienio, ordem_val = self._calcular_quadrienio(ano_int)
            quad_obj, _ = Quadrienio.objects.get_or_create(
                ds_quadrienio=nome_quadrienio,
                defaults={'ordem': ordem_val}
            )
            Ano.objects.get_or_create(ano_valor=ano_int, defaults={'quadrienio': quad_obj})
        self.stdout.write(self.style.SUCCESS('ANOS e QUADRIÊNIOS criados.'))

    def _populate_pessoas(self):
        """Popula a tabela de pessoas de forma padrão por atualização/criação unitária."""
        self.stdout.write('2. Populando Pessoas...')
        path = os.path.join(DATA_DIR, 'pessoas.csv')
        if not os.path.exists(path):
            return
        df = pd.read_csv(path, dtype=str).fillna('')
    
        sexo_lookup = {s: self._get_or_create(PessoaSexo, 'sexo', s) for s in df['TP_SEXO'].unique() if s}
        pais_lookup = {p: self._get_or_create(PessoaPais, 'pais', p) for p in df['NM_PAIS_NACIONALIDADE'].unique() if p}
        tipo_nacionalidade_lookup = {
            t: self._get_or_create(PessoaTipoNacionalidade, 'ds_tipo_nacionalidade', t)
            for t in df['DS_TIPO_NACIONALIDADE'].unique() if t
        }
    
        for _, row in df.iterrows():
            if not row['ID_PESSOA_HASH']:
                continue
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
        """Popula os programas base."""
        self.stdout.write('3. Populando Programas (base)...')
        path = os.path.join(DATA_DIR, 'programas.csv')
        if not os.path.exists(path):
            return
            
        df = pd.read_csv(path, dtype=str).fillna('')
        for _, row in df.iterrows():
            if not row['ID_PROGRAMA_HASH']:
                continue
            an_inicio = int(row['AN_INICIO_PROGRAMA']) if row['AN_INICIO_PROGRAMA'].isdigit() else None
            Programa.objects.update_or_create(
                id_programa_hash=row['ID_PROGRAMA_HASH'],
                defaults={'an_inicio_programa': an_inicio}
            )
        self.stdout.write(self.style.SUCCESS('Programas (base) populados.'))

    def _populate_cursos(self):
        """Popula as relações de cursos."""
        self.stdout.write('4. Populando Cursos...')
        path = os.path.join(DATA_DIR, 'cursos.csv')
        if not os.path.exists(path):
            return
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
                continue
        self.stdout.write(self.style.SUCCESS('Cursos populados.'))

    def _populate_ano_programas(self):
        """Usa cache em memória para dimensões e bulk_create para inserção massiva otimizada de ano-programas."""
        self.stdout.write('5. Populando Ano-Programas (via bulk_create)...')
        path = os.path.join(DATA_DIR, 'ano_programas.csv')
        if not os.path.exists(path):
            return
        df = pd.read_csv(path, dtype=str).fillna('')
        
        anos = {a.ano_valor: a for a in Ano.objects.all()}
        programas = {p.id_programa_hash: p for p in Programa.objects.all()}
        
        nomes, grandes_areas, areas_conhec, avaliacoes, conceitos, modalidades, situacoes = {}, {}, {}, {}, {}, {}, {}

        objs_para_criar = []
        for _, row in df.iterrows():
            try:
                ano_valor = int(float(row['AN_BASE']))
            except (ValueError, TypeError):
                continue

            ano_obj = anos.get(ano_valor)
            programa_obj = programas.get(row['ID_PROGRAMA_HASH'])
            if not ano_obj or not programa_obj:
                continue

            # Cache local de chaves estrangeiras para evitar buscas repetidas no banco
            nm_prog = row['NM_PROGRAMA_IES']
            if nm_prog not in nomes:
                nomes[nm_prog], _ = ProgramaNome.objects.get_or_create(nm_programa_ies=nm_prog)
            
            g_area = row['NM_GRANDE_AREA_CONHECIMENTO']
            if g_area not in grandes_areas:
                grandes_areas[g_area], _ = ProgramaGrandeArea.objects.get_or_create(nm_grande_area_conhecimento=g_area)
                
            a_conhec = row['NM_AREA_CONHECIMENTO']
            if a_conhec and a_conhec not in areas_conhec:
                areas_conhec[a_conhec], _ = ProgramaAreaConhecimento.objects.get_or_create(nm_area_conhecimento=a_conhec)
                
            cd_av = row['CD_AREA_AVALIACAO']
            if cd_av not in avaliacoes:
                avaliacoes[cd_av], _ = ProgramaAreaAvaliacao.objects.get_or_create(
                    cd_area_avaliacao=int(cd_av), defaults={'nm_area_avaliacao': row['NM_AREA_AVALIACAO']}
                )
                
            cd_conc = row['CD_CONCEITO_PROGRAMA']
            if cd_conc not in conceitos:
                codigo_numerico = str(cd_conc)
                conceito_original = 'A' if codigo_numerico == '0' else codigo_numerico
                conceitos[cd_conc], _ = ProgramaConceito.objects.get_or_create(
                    cd_conceito_programa=int(cd_conc),
                    defaults={'ds_conceito': row.get('DS_CONCEITO'), 'cd_conceito_programa_original': conceito_original}
                )
                
            mod = row['NM_MODALIDADE_PROGRAMA']
            if mod not in modalidades:
                modalidades[mod], _ = ProgramaModalidade.objects.get_or_create(nm_modalidade_programa=mod)
                
            sit = row['DS_SITUACAO_PROGRAMA']
            if sit not in situacoes:
                situacoes[sit], _ = ProgramaSituacao.objects.get_or_create(ds_situacao_programa=sit)

            objs_para_criar.append(AnoPrograma(
                ano=ano_obj,
                programa=programa_obj,
                nm_programa_ies=nomes[nm_prog],
                nm_modalidade_programa=modalidades[mod],
                grande_area=grandes_areas[g_area],
                area_conhecimento=areas_conhec.get(a_conhec),
                area_avaliacao=avaliacoes[cd_av],
                cd_conceito_programa=conceitos[cd_conc],
                in_rede=str(row.get('IN_REDE', '')).upper() == 'TRUE',
                situacao=situacoes[sit]
            ))

        AnoPrograma.objects.bulk_create(objs_para_criar, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Ano-Programas populados via bulk.'))

    def _populate_docentes(self):
        """Insere docentes em lote de alta performance utilizando cache em memória de dimensões."""
        self.stdout.write('6. Populando Docentes (via bulk_create)...')
        path = os.path.join(DATA_DIR, 'docentes.csv')
        if not os.path.exists(path):
            return
        df = pd.read_csv(path, dtype=str).fillna('')

        anos = {a.ano_valor: a for a in Ano.objects.all()}
        pessoas = {p.id_pessoa_hash: p for p in Pessoa.objects.all()}
        programas = {p.id_programa_hash: p for p in Programa.objects.all()}

        categorias, vinculos, regimes, bolsas, titulacoes, faixas = {}, {}, {}, {}, {}, {}
        objs_para_criar = []

        for _, row in df.iterrows():
            try:
                ano = anos.get(int(row['AN_BASE']))
                pessoa = pessoas.get(row['ID_PESSOA_HASH'])
                programa = programas.get(row['ID_PROGRAMA_HASH'])
                if not ano or not pessoa or not programa:
                    continue

                cat_val = row.get('DS_CATEGORIA_DOCENTE')
                if cat_val and cat_val not in categorias:
                    categorias[cat_val], _ = DocenteCategoria.objects.get_or_create(ds_categoria_docente=cat_val)
                    
                vinc_val = row.get('DS_TIPO_VINCULO_DOCENTE_IES')
                if vinc_val and vinc_val not in vinculos:
                    vinculos[vinc_val], _ = DocenteVinculo.objects.get_or_create(ds_tipo_vinculo_docente_ies=vinc_val)
                    
                reg_val = row.get('DS_REGIME_TRABALHO')
                if reg_val and reg_val not in regimes:
                    regimes[reg_val], _ = DocenteRegimeTrabalho.objects.get_or_create(ds_regime_trabalho=reg_val)
                    
                bolsa_val = row.get('CD_CAT_BOLSA_PRODUTIVIDADE')
                if bolsa_val and bolsa_val not in bolsas:
                    bolsas[bolsa_val], _ = DocenteBolsaProdutividade.objects.get_or_create(cd_cat_bolsa_produtividade=bolsa_val)
                    
                tit_val = row.get('NM_GRAU_TITULACAO')
                if tit_val and tit_val not in titulacoes:
                    titulacoes[tit_val], _ = GrauDocente.objects.get_or_create(nm_grau_titulacao=tit_val)
                    
                faixa_val = row.get('DS_FAIXA_ETARIA')
                if faixa_val and faixa_val not in faixas:
                    faixas[faixa_val], _ = FaixaEtaria.objects.get_or_create(ds_faixa_etaria=faixa_val)

                objs_para_criar.append(Docente(
                    ano=ano,
                    pessoa=pessoa,
                    programa=programa,
                    categoria=categorias.get(cat_val),
                    vinculo=vinculos.get(vinc_val),
                    regime_trabalho=regimes.get(reg_val),
                    bolsa_produtividade=bolsas.get(bolsa_val),
                    grau_titulacao=titulacoes.get(tit_val),
                    faixa_etaria=faixas.get(faixa_val)
                ))
            except Exception:
                continue

        Docente.objects.bulk_create(objs_para_criar, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Docentes populados via bulk.'))

    def _populate_discentes(self):
        """Insere discentes em lote com conversão segura de dados decimais em inteiros."""
        self.stdout.write('7. Populando Discentes (via bulk_create)...')
        path = os.path.join(DATA_DIR, 'discentes.csv')
        if not os.path.exists(path):
            return
        df = pd.read_csv(path, dtype=str).fillna('')

        anos = {a.ano_valor: a for a in Ano.objects.all()}
        pessoas = {p.id_pessoa_hash: p for p in Pessoa.objects.all()}
        programas = {p.id_programa_hash: p for p in Programa.objects.all()}

        graus, situacoes, faixas = {}, {}, {}
        objs_para_criar = []

        for _, row in df.iterrows():
            try:
                ano = anos.get(int(row['AN_BASE']))
                pessoa = pessoas.get(row['ID_PESSOA_HASH'])
                programa = programas.get(row['ID_PROGRAMA_HASH'])
                if not ano or not pessoa or not programa:
                    continue

                grau_val = row.get('DS_GRAU_ACADEMICO_DISCENTE')
                if grau_val and grau_val not in graus:
                    graus[grau_val], _ = GrauCurso.objects.get_or_create(nm_grau_curso=grau_val)
                    
                sit_val = row.get('NM_SITUACAO_DISCENTE')
                if sit_val and sit_val not in situacoes:
                    situacoes[sit_val], _ = DiscenteSituacao.objects.get_or_create(nm_situacao_discente=sit_val)
                    
                faixa_val = row.get('DS_FAIXA_ETARIA')
                if faixa_val and faixa_val not in faixas:
                    faixas[faixa_val], _ = FaixaEtaria.objects.get_or_create(ds_faixa_etaria=faixa_val)

                objs_para_criar.append(Discente(
                    ano=ano,
                    pessoa=pessoa,
                    programa=programa,
                    grau_academico=graus[grau_val],
                    st_ingressante=row.get('ST_INGRESSANTE', '').upper() == 'TRUE' or row.get('ST_INGRESSANTE', '').upper() == 'SIM',
                    situacao=situacoes[sit_val],
                    qt_mes_titulacao=int(float(row.get('QT_MES_TITULACAO') or 0)),
                    faixa_etaria=faixas.get(faixa_val)
                ))
            except Exception:
                continue

        Discente.objects.bulk_create(objs_para_criar, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Discentes populados via bulk.'))

    def _populate_producao(self):
        """Popula a produção acadêmica de grande volume em lotes via bulk_create com cache auxiliar."""
        self.stdout.write('8. Populando Produção (via bulk_create)...')
        path = os.path.join(DATA_DIR, 'producao.csv')
        if not os.path.exists(path):
            return
        df = pd.read_csv(path, dtype=str).fillna('')

        anos = {a.ano_valor: a for a in Ano.objects.all()}
        programas = {p.id_programa_hash: p for p in Programa.objects.all()}
        pessoas = {p.id_pessoa_hash: p for p in Pessoa.objects.all()}

        identificadores, tipos_autor, cat_docentes, niveis_discente = {}, {}, {}, {}

        objs_para_criar = []
        for _, row in df.iterrows():
            try:
                hash_prod = row.get('ID_PRODUCAO_HASH')
                if not hash_prod or pd.isna(hash_prod):
                    continue

                ano = anos.get(int(row['AN_BASE']))
                programa = programas.get(row['ID_PROGRAMA_HASH'])
                if not ano or not programa:
                    continue

                autor_pessoa = pessoas.get(row['ID_PESSOA_HASH']) if row.get('ID_PESSOA_HASH') else None

                if hash_prod not in identificadores:
                    identificadores[hash_prod], _ = ProducaoIdentificador.objects.get_or_create(id_producao_hash=hash_prod)

                tp_autor_val = row.get('TP_AUTOR')
                if tp_autor_val and tp_autor_val not in tipos_autor:
                    tipos_autor[tp_autor_val], _ = ProducaoTpAutor.objects.get_or_create(tp_autor=tp_autor_val)

                cat_doc_val = row.get('NM_TP_CATEGORIA_DOCENTE')
                if cat_doc_val and cat_doc_val not in cat_docentes:
                    cat_docentes[cat_doc_val], _ = DocenteCategoria.objects.get_or_create(ds_categoria_docente=cat_doc_val)

                nivel_val = row.get('NM_NIVEL_DISCENTE')
                if nivel_val and nivel_val not in niveis_discente:
                    niveis_discente[nivel_val], _ = GrauCurso.objects.get_or_create(nm_grau_curso=nivel_val)

                objs_para_criar.append(Producao(
                    producao=identificadores[hash_prod],
                    ano=ano,
                    programa=programa,
                    autor_pessoa=autor_pessoa,
                    tp_autor=tipos_autor.get(tp_autor_val),
                    categoria_docente=cat_docentes.get(cat_doc_val),
                    nivel_discente=niveis_discente.get(nivel_val)
                ))
            except Exception:
                continue

        Producao.objects.bulk_create(objs_para_criar, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Produção populada via bulk.'))

    def _clear_database(self):
        """Esvazia as tabelas do banco em ordem correta respeitando as restrições de chaves estrangeiras."""
        self.stdout.write(self.style.WARNING("Limpando todas as tabelas"))
        Producao.objects.all().delete()
        Docente.objects.all().delete()
        Discente.objects.all().delete()
        AnoPrograma.objects.all().delete()
        Curso.objects.all().delete()
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
        Programa.objects.all().delete()
        Ano.objects.all().delete()
        Quadrienio.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Banco de dados limpo."))