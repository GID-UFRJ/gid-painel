from django.db import models

# Create your models here.

class AreaAvaliacao(models.Model):
    areaAvaliacaoId = models.IntegerField(primary_key=True)
    areaAvaliacaoNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.areaAvaliacaoNome
    
class AreaBasica(models.Model):
    areaBasicaId = models.IntegerField(primary_key=True)
    areaBasicaNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.areaBasicaNome
    
class Centro(models.Model):
    centroId = models.IntegerField(primary_key=True)
    centroNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.centroNome

class Modalidade(models.Model):
    modalidadeId = models.IntegerField(primary_key=True)
    modalidadeNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.modalidadeNome

class Nivel(models.Model):
    nivelId = models.IntegerField(primary_key=True)
    nivelNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.nivelNome

class Rede(models.Model):
    redeId = models.IntegerField(primary_key=True)
    redeNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.redeNome

class Situacao(models.Model):
    situacaoId = models.IntegerField(primary_key=True)
    situacaoNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.situacaoNome
    
class Unidade(models.Model):
    unidadeId = models.IntegerField(primary_key=True)
    unidadeNome = models.CharField(max_length=100, unique=True, null = True)
    def __str__(self):
        return self.unidadeNome

class Programas(models.Model):
    cursoId = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=13)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, null=True)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, null=True)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True)
    conceito = models.CharField(max_length=2)
    situacao = models.ForeignKey(Situacao, on_delete=models.CASCADE, null=True)
    modalidade = models.ForeignKey(Modalidade, on_delete=models.CASCADE, null=True)
    areaBasica = models.ForeignKey(AreaBasica, on_delete=models.CASCADE, null=True)
    areaAvaliacao = models.ForeignKey(AreaAvaliacao, on_delete=models.CASCADE, null=True)
    rede = models.ForeignKey(Rede, on_delete=models.CASCADE, null=True)     
    ativos = models.IntegerField(null=True)
    ingressantes = models.IntegerField(null=True)
    cancelados = models.IntegerField(null=True)
    trancados = models.IntegerField(null=True)
    abandonos = models.IntegerField(null=True)

    def __str__(self):
        exibir = f'{self.codigo}'
        return exibir

