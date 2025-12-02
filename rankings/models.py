from django.db import models

class RankingTipo(models.Model):
    """Ex: Acadêmico, Sustentabilidade"""
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Ranking(models.Model):
    """Ex: THE, Shanghai, THE IMPACT"""
    nome = models.CharField(max_length=200)
    tipo = models.ForeignKey(RankingTipo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nome', 'tipo')

    def __str__(self):
        return f"{self.nome} ({self.tipo.nome})"

class EscopoGeografico(models.Model):
    """
    Refere-se EXCLUSIVAMENTE à abrangência geográfica.
    Ex: Mundo, América Latina, Nacional, Ásia.
    """
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class ODS(models.Model):
    """
    Objetivos de Desenvolvimento Sustentável.
    Ex: ODS_3, ODS_4.
    """
    codigo = models.CharField(max_length=20, unique=True, help_text="Ex: ODS_3")
    descricao = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Saúde e Bem-Estar")

    def __str__(self):
        if self.descricao:
            return f"{self.codigo} - {self.descricao}"
        return self.codigo

class RankingEntrada(models.Model):
    ranking = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    
    # Separação clara entre ONDE e O QUÊ
    escopo_geografico = models.ForeignKey(EscopoGeografico, on_delete=models.PROTECT) # Evita deletar o escopo se houver entradas
    ods = models.ForeignKey(ODS, null=True, blank=True, on_delete=models.SET_NULL, help_text="Deixe em branco para rankings gerais ou institucionais")

    ano = models.IntegerField()
    posicao_minima = models.IntegerField()
    posicao_maxima = models.IntegerField()

    class Meta:
        verbose_name = "Entrada de Ranking"
        verbose_name_plural = "Entradas de Ranking"
        # Garante que não haja duplicidade de dados para o mesmo ano/ranking/escopo/ods
        unique_together = ('ranking', 'escopo_geografico', 'ods', 'ano')
        ordering = ['-ano', 'ranking']

    def __str__(self):
        tema = self.ods.codigo if self.ods else "Geral"
        return f"{self.ranking} | {self.escopo_geografico} | {tema} | {self.ano}"