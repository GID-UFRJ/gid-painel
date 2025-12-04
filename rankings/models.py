from django.db import models


class UpperCaseMixin(models.Model):
    class Meta:
        abstract = True

    # 1. Configuração padrão: Lista de campos para IGNORAR
    uppercase_exclude = []

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            # Pula se o campo estiver na lista de exclusão
            if field.name in self.uppercase_exclude:
                continue

            # Verifica se é texto e se tem valor
            if isinstance(field, (models.CharField, models.TextField)):
                valor_atual = getattr(self, field.name, None)
                if valor_atual and isinstance(valor_atual, str):
                    # Aplica a transformação
                    setattr(self, field.name, valor_atual.strip().upper())

        super().save(*args, **kwargs)

class RankingTipo(UpperCaseMixin):
    """Ex: Acadêmico, Sustentabilidade"""
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Ranking(UpperCaseMixin):
    """Ex: THE, Shanghai, THE IMPACT"""
    nome = models.CharField(max_length=200)
    tipo = models.ForeignKey(RankingTipo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nome', 'tipo')

    def __str__(self):
        return f"{self.nome} ({self.tipo.nome})"

class EscopoGeografico(UpperCaseMixin):
    """
    Refere-se EXCLUSIVAMENTE à abrangência geográfica.
    Ex: Mundo, América Latina, Nacional, Ásia.
    """
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class ODS(UpperCaseMixin):
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

class RankingEntrada(UpperCaseMixin):
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