from django.db import models

#Nota: Django cria AutoFields automaticamente (nome da coluna = 'id') quando uma PK não é definida. Esse padrão é esperado por outras bibliotecas e resolvi aderir.
#Também foi preferir usar chaves substitutas/artificiais (surrogate) em vez de naturais, para fins de eficiência e tbm pq elas substituem chaves compostas, para as quais o django não tem um suporte muito desenvolvido

from django.db import models

class Year(models.Model):
    year = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.year

class WorkType(models.Model):
    worktype = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.worktype

class OAStatus(models.Model):
    oa_status = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.oa_status

class PrimarySource(models.Model):
    source_id = models.CharField(max_length=100, unique=True)
    source_name = models.CharField(max_length=255)
    source_issn_l = models.CharField(max_length=50)
    is_oa = models.BooleanField()
    host_organization_id = models.CharField(max_length=100)
    host_organization_name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.source_name

class Work(models.Model):
    work_id = models.CharField(max_length=100, unique=True)
    doi = models.CharField(max_length=255, blank=True)
    work_title = models.TextField()
    pubyear = models.ForeignKey(Year, on_delete=models.CASCADE)
    worktype = models.ForeignKey(WorkType, on_delete=models.CASCADE)
    cited_by_count = models.IntegerField()
    primary_source = models.ForeignKey(PrimarySource, on_delete=models.CASCADE)
    is_oa = models.BooleanField()
    oa_status = models.ForeignKey(OAStatus, on_delete=models.CASCADE)
    referenced_works_count = models.IntegerField()
    indexed_in = models.JSONField()

    def __str__(self):
        return self.work_title

class Institution(models.Model):
    institution_id = models.CharField(max_length=100, unique=True)
    institution_name = models.CharField(max_length=255)
    #ror = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)

    def __str__(self):
        return self.institution_name

class Authorship(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    author_id = models.CharField(max_length=100)
    author_position = models.CharField(max_length=20)
    is_corresponding = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["work", "author_id"], name="unique_work_author")
        ]

    def __str__(self):
        return f"Author {self.author_id} - Work {self.work}"

class AuthorshipInstitution(models.Model):
    authorship = models.ForeignKey(Authorship, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["authorship", "institution"], name="unique_authorship_institution")
        ]

    def __str__(self):
        return f" Authorship {self.authorship} @ institution {self.institution}"

class CitedByYear(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    cited_count = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["work", "year"], name="unique_work_year")
        ]

    def __str__(self):
        return f"Work {self.work} ({self.year.year}): {self.cited_count} citations"

class Topic(models.Model):
    topic_id = models.CharField(max_length=100, unique=True)
    topic_name = models.CharField(max_length=255)
    #subfield_id = models.CharField(max_length=100)
    subfield_name = models.CharField(max_length=255)
    #field_id = models.CharField(max_length=100)
    field_name = models.CharField(max_length=255)
    #domain_id = models.CharField(max_length=100)
    domain_name = models.CharField(max_length=255)

    def __str__(self):
        return self.topic_name

class WorkTopic(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["work", "topic"], name="unique_work_topic")
        ]

    def __str__(self):
        return f"Work {self.work} - Topic {self.topic} ({self.score})"
