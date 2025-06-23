from django.db import models

# Create your models here.
class Painel(models.Model):
    nome = models.CharField(max_length=30)
    def __str__(self):
        return self.nome
    
class EstiloGrafico(models.Model):
    nomeEstilo = models.CharField(max_length=100)
    numeroIdentificador = models.IntegerField(default=1)
    def __str__(self):
        return f'{self.numeroIdentificador} - {self.nomeEstilo}'
    class Meta:
        ordering = ["numeroIdentificador", "nomeEstilo"]

class TamanhoGrafico(models.Model):
    tamanhoVertical = models.IntegerField()
    tamanhoHorizontal = models.IntegerField()
    def __str__(self):
        return f'{self.tamanhoVertical} x {self.tamanhoHorizontal}'

class Grafico(models.Model):
    #dados da exibição
    painel = models.ForeignKey(Painel, on_delete=models.CASCADE)
    posicaoNoPainel = models.IntegerField()
    tamanhoGrafico = models.ForeignKey(TamanhoGrafico, on_delete=models.CASCADE)
    estiloGrafico = models.ForeignKey(EstiloGrafico, on_delete=models.CASCADE)
    #dados do gráfico    
    tituloGrafico = models.CharField(max_length=100)
    tituloEixoX = models.CharField(max_length=100)
    tituloEixoY = models.CharField(max_length=100, default='')
    #serie
    series = models.JSONField(default=dict, null=True, blank=True, help_text='use formato de dicionário   --->   {"serie1": {"2010": 25, "2011": 50}}.   Para passar um elemento None pode usar null')
    def __str__(self):
        return f'{self.painel} -- {self.posicaoNoPainel} -- {self.tituloGrafico} -- {self.estiloGrafico.nomeEstilo}'
    class Meta:
        ordering = ["painel", "posicaoNoPainel"]