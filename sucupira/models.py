from django.db import models

# Tabelas de "Lookup" (dimensões simples)

class Ano(models.Model):
    ano_valor = models.IntegerField(unique=True, primary_key=True)

    def __str__(self):
        return str(self.ano_valor)

class PessoaSexo(models.Model):
    sexo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.sexo

class PessoaPais(models.Model):
    pais = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.pais

class ProgramaGrandeArea(models.Model):
    nm_grande_area_conhecimento = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nm_grande_area_conhecimento

class ProgramaAreaConhecimento(models.Model):
    nm_area_conhecimento = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nm_area_conhecimento

class ProgramaAreaAvaliacao(models.Model):
    cd_area_avaliacao = models.IntegerField(unique=True)
    nm_area_avaliacao = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.cd_area_avaliacao} - {self.nm_area_avaliacao}"

class GrauCurso(models.Model):
    nm_grau_curso = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nm_grau_curso

class ProgramaSituacao(models.Model):
    ds_situacao_programa = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ds_situacao_programa

class DocenteCategoria(models.Model):
    ds_categoria_docente = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ds_categoria_docente

class DocenteVinculo(models.Model):
    ds_tipo_vinculo_docente_ies = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ds_tipo_vinculo_docente_ies

class DocenteRegimeTrabalho(models.Model):
    ds_regime_trabalho = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ds_regime_trabalho
        
class DocenteBolsaProdutividade(models.Model):
    cd_cat_bolsa_produtividade = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.cd_cat_bolsa_produtividade

class DiscenteSituacao(models.Model):
    nm_situacao_discente = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nm_situacao_discente

class ProducaoIdentificador(models.Model):
    id_producao_hash = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.id_producao_hash


class ProducaoTpAutor(models.Model):
    tp_autor = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tp_autor


# Tabelas Principais

class Pessoa(models.Model):
    id_pessoa_hash = models.CharField(max_length=128, unique=True)
    tp_sexo = models.ForeignKey(PessoaSexo, on_delete=models.PROTECT, related_name='pessoas', default=None)
    ano_nascimento = models.IntegerField(null=True, blank=True)
    pais_nacionalidade = models.ForeignKey(PessoaPais, on_delete=models.PROTECT, related_name='pessoas', null=True, default=None)

    def __str__(self):
        return self.id_pessoa_hash

class Programa(models.Model):
    id_programa_hash = models.CharField(max_length=128, unique=True)
    nm_programa_ies = models.CharField(max_length=255)
    grande_area = models.ForeignKey(ProgramaGrandeArea, on_delete=models.PROTECT, related_name='programas')
    area_conhecimento = models.ForeignKey(ProgramaAreaConhecimento, on_delete=models.PROTECT, related_name='programas', null=True, blank=True)
    area_avaliacao = models.ForeignKey(ProgramaAreaAvaliacao, on_delete=models.PROTECT, related_name='programas')
    an_inicio_programa = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nm_programa_ies

class Curso(models.Model):
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='cursos')
    grau_curso = models.ForeignKey(GrauCurso, on_delete=models.PROTECT, related_name='cursos')
    an_inicio_curso = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['programa', 'grau_curso'], name='unique_programa_grau')
        ]

    def __str__(self):
        return f"{self.programa.nm_programa_ies} - {self.grau_curso.nm_grau_curso}"

class AnoPrograma(models.Model):
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name='programas_avaliados')
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='avaliacoes_anuais')
    cd_conceito_programa = models.CharField(max_length=5)
    in_rede = models.BooleanField(default=False)
    situacao = models.ForeignKey(ProgramaSituacao, on_delete=models.PROTECT, related_name='programas_no_ano')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ano', 'programa'], name='unique_ano_programa')
        ]
        
    def __str__(self):
        return f"{self.programa} ({self.ano}) - Conceito: {self.cd_conceito_programa}"


class Docente(models.Model):
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    categoria = models.ForeignKey(DocenteCategoria, on_delete=models.PROTECT, null=True, blank=True)
    vinculo = models.ForeignKey(DocenteVinculo, on_delete=models.PROTECT, null=True, blank=True)
    regime_trabalho = models.ForeignKey(DocenteRegimeTrabalho, on_delete=models.PROTECT, null=True, blank=True)
    bolsa_produtividade = models.ForeignKey(DocenteBolsaProdutividade, on_delete=models.PROTECT, null=True, blank=True)
    grau_titulacao = models.ForeignKey(GrauCurso, on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ano', 'pessoa', 'programa'], name='unique_docente_ano_programa')
        ]

    def __str__(self):
        return f"Docente {self.pessoa_id} em {self.programa_id} ({self.ano_id})"


class Discente(models.Model):
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    grau_academico = models.ForeignKey(GrauCurso, on_delete=models.PROTECT)
    st_ingressante = models.BooleanField(default=False)
    situacao = models.ForeignKey(DiscenteSituacao, on_delete=models.PROTECT)
    qt_mes_titulacao = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ano', 'pessoa', 'programa', 'grau_academico'], name='unique_discente_ano_programa_grau')
        ]

    def __str__(self):
        return f"Discente {self.pessoa_id} em {self.programa_id} ({self.ano_id})"


class Producao(models.Model):
    producao = models.ForeignKey(ProducaoIdentificador, on_delete=models.CASCADE)
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    autor_pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, null=True, blank=True) # Ligação com a pessoa autora
    tp_autor = models.ForeignKey(ProducaoTpAutor, on_delete=models.PROTECT)
    categoria_docente = models.ForeignKey(DocenteCategoria, on_delete=models.PROTECT, null=True, blank=True)
    nivel_discente = models.ForeignKey(GrauCurso, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.id_producao_hash