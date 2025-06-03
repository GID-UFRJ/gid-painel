from django.db import models
from django.core.exceptions import ValidationError

#Nota: Django cria AutoFields automaticamente (nome da coluna = 'id') quando uma PK não é definida. Esse padrão é esperado por outras bibliotecas e resolvi aderir.
#Também foi preferir usar chaves substitutas/artificiais (surrogate) em vez de naturais, para fins de eficiência e tbm pq elas substituem chaves compostas, para as quais o django não tem um suporte muito desenvolvido

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
    # source_id can sometimes be None if there's no primary location/source data
    source_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # These fields can also be missing from OpenAlex primary_location.source data
    source_name = models.CharField(max_length=255, null=True, blank=True)
    source_issn_l = models.CharField(max_length=50, null=True, blank=True)
    is_oa = models.BooleanField(null=True) # Booleans can also be null
    host_organization_id = models.CharField(max_length=100, null=True, blank=True)
    host_organization_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.source_name or f"Unnamed primary source"
    

class Work(models.Model):
    work_id = models.CharField(max_length=100, unique=True)
    doi = models.CharField(max_length=255, null=True, blank=True)
    work_title = models.TextField(null=True, blank=True) #Surprisingly, some records can have missing work_titles
    pubyear = models.ForeignKey(Year, on_delete=models.CASCADE)
    worktype = models.ForeignKey(WorkType, on_delete=models.CASCADE)
    cited_by_count = models.IntegerField()
    primary_source = models.ForeignKey(PrimarySource, on_delete=models.CASCADE, null=True, blank=True)
    is_oa = models.BooleanField()
    oa_status = models.ForeignKey(OAStatus, on_delete=models.CASCADE)
    referenced_works_count = models.IntegerField()

    def __str__(self):
        return self.work_title or self.work_id #Fallback for title

    def clean(self):
        if not self.doi and not self.work_title:
            raise ValidationError("A Work record must have either a DOI or a title.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures clean() is called
        super().save(*args, **kwargs)


class Institution(models.Model):
    institution_id = models.CharField(max_length=100, unique=True)
    institution_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=10)

    def __str__(self):
        return self.institution_name


class Author(models.Model):
    author_id = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.author_id

class Authorship(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_corresponding = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["work", "author"], name="unique_work_author")
        ]

    def __str__(self):
        return f"Author {self.author} - Work {self.work}"

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
    subfield_name = models.CharField(max_length=255)
    field_name = models.CharField(max_length=255)
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
