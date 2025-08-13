from django.db import models

# Create your models here.
class Escopo(models.Model):
    escopoId = models.IntegerField(primary_key=True)
    escopoNome = models.CharField(max_length=100, unique=True, null = False) #Default do django é null = False, mas preferi ser explícito aqui...
    escopoNomeCompleto = models.CharField(max_length=100, unique=True, null = True, blank = True) #Nome completo vai ser mais útil para identificar as ODS's. Pode ser nulo para outros escopos. Não necessariamente precisa ter apenas valores únicos, mas não vejo muita razão para ter duplicatas tbm.
    
    def __str__(self):
        return f"{self.escopoNome}"

class Ranking(models.Model):
    rankingId = models.IntegerField(primary_key=True)
    rankingNome = models.CharField(max_length=100, unique=True, null = False) 

    def __str__(self):
        return f"{self.rankingNome }"

class Ano(models.Model):
    anoId = models.IntegerField(primary_key=True)
    ano = models.IntegerField(unique=True, null=False)

    def __str__(self):
        return f"{self.ano}"

class Resultado(models.Model):
    resultadoId = models.AutoField(primary_key=True)
    ranking = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    escopo = models.ForeignKey(Escopo, on_delete=models.CASCADE)
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE)
    posicao = models.FloatField(null = False)
    pontuacaoGeral = models.FloatField(null = True, blank=True)

    class Meta:
        db_table_comment = "Resultados dos rankings em um dado escopo e ano"
        constraints = [
        models.UniqueConstraint(fields=['ranking', 'escopo', 'ano'], name='unique_resultados_tripla'), #Não achei como modelar chaves estrangeiras como chave primária composta, mas isso deve servir 
        ] 

    def __str__(self):
        return f"{self.ranking.rankingNome} | {self.escopo.escopoNome} | {self.ano.ano}"