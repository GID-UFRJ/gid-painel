from django.db import models

# Create your models here.
class Painel(models.Model):
    nome = models.CharField(max_length=30)
    def __str__(self):
        return self.nome
    
class EstiloGrafico(models.Model):
    nomeEstilo = models.CharField(max_length=30)
    detalheEstilo  = models.CharField(max_length=200)
    def __str__(self):
        return self.nomeEstilo

class TamanhoGrafico(models.Model):
    tamanhoVertical = models.IntegerField()
    tamanhoHorizontal = models.IntegerField()
    def __str__(self):
        return f'{self.tamanhoVertical} x {self.tamanhoHorizontal}'
    
class Serie(models.Model):
    nomeSerie = models.CharField(max_length=30)
    dadosSerie = models.JSONField()
    class Meta:
        ordering = ["nomeSerie"]
    def __str__(self):
        return self.nomeSerie

class Grafico(models.Model):
    #dados da exibição
    painel = models.ForeignKey(Painel, on_delete=models.CASCADE)
    posicaoNoPainel = models.IntegerField()
    tamanhoGrafico = models.ForeignKey(TamanhoGrafico, on_delete=models.CASCADE)
    estiloGrafico = models.ForeignKey(EstiloGrafico, on_delete=models.CASCADE)
    #dados do gráfico    
    tituloGrafico = models.CharField(max_length=100)
    tituloEixoGrafico = models.CharField(max_length=100)
    #serie
    series = models.ManyToManyField(Serie)
    def __str__(self):
        return self.tituloGrafico