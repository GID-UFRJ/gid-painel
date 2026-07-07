from django.db import models #Para criar as classes (models.Model)
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Subquery, Case, When, Value, BooleanField, Count, CharField #Para trabalhar com querysets
from django.db.models.functions import Coalesce    

#Nota: Django cria AutoFields automaticamente (nome da coluna = 'id') quando uma PK não é definida. Esse padrão é esperado por outras bibliotecas e resolvi aderir.
#Também foi preferir usar chaves substitutas/artificiais (surrogate) em vez de naturais, para fins de eficiência e tbm pq elas substituem chaves compostas, para as quais o django não tem um suporte muito desenvolvido


class WorkQuerySet(models.QuerySet):
    def autor_correspondente_ufrj(self):
        from .models import Authorship

        UFRJ_OPENALEX_ID = 'I122140584'
        
        corresp_ufrj = Authorship.objects.filter(
            work=OuterRef('pk'),
            is_corresponding=True,
            authorshipinstitution__institution__institution_id=UFRJ_OPENALEX_ID
        )

        return self.annotate(
            autor_correspondente_ufrj=Case(
                When(Exists(corresp_ufrj), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

    def com_tipo_documento_agrupado(self):
        """
        Calcula os tipos de documento com mais publicações globais. 
        Mantém o nome original deles, e transforma todos os outros em 'Outros'.
        """
        # 1. Pede ao banco para achar os 9 maiores tipos globais
        top_tipos = (
            self.values('worktype__worktype')
            .annotate(total=Count('id'))
            .order_by('-total')[:6] #altere o numero de categorias aqui
        )
        
        # 2. Extrai apenas os nomes para uma lista (ignorando nulos)
        lista_top = [
            item['worktype__worktype'] 
            for item in top_tipos 
            if item['worktype__worktype']
        ]

        # 3. Retorna a query anotando a NOVA coluna limpa
        return self.annotate(
            tipo_documento_limpo=Case(
                When(worktype__worktype__in=lista_top, then='worktype__worktype'),
                default=Value('others'), #valor dado aos agrupados
                output_field=CharField()
            )
        )
    
    def com_topico_principal(self):
        from .models import WorkTopic
        
        # Subquery base ordenada pelo maior score
        top_topic_qs = WorkTopic.objects.filter(work=OuterRef('pk')).order_by('-score')

        return self.annotate(
            top_domain=Coalesce(Subquery(top_topic_qs.values('topic__domain_name')[:1]), Value("Unclassified")),
            top_field=Coalesce(Subquery(top_topic_qs.values('topic__field_name')[:1]), Value("Unclassified")),
            top_subfield=Coalesce(Subquery(top_topic_qs.values('topic__subfield_name')[:1]), Value("Unclassified")),
        )
    
    def com_status_colaboracao(self):
        # Importe o modelo localmente como você já faz
        from .models import AuthorshipInstitution
        UFRJ_ID = 'I122140584'
    
        # Subquery: Existe alguma instituição BR nesse trabalho que não seja a UFRJ?
        parceiro_br = AuthorshipInstitution.objects.filter(
            authorship__work=OuterRef('pk'),
            institution__country_code='BR'
        ).exclude(
            institution__institution_id=UFRJ_ID
        )
    
        # Subquery: Existe alguma instituição nesse trabalho que não seja BR?
        parceiro_int = AuthorshipInstitution.objects.filter(
            authorship__work=OuterRef('pk'),
            institution__country_code__isnull=False
        ).exclude(
            institution__country_code='BR'
        )
    
        # Anotamos booleanos! Isso é super rápido e não quebra o GROUP BY
        return self.annotate(
            tem_colab_nacional=Exists(parceiro_br),
            tem_colab_internacional=Exists(parceiro_int)
        )
        


class Year(models.Model):
    year = models.IntegerField(unique=True)

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

class AuthorPosition(models.Model):
    position = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.position

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
    cited_by_count = models.IntegerField(db_index=True)
    primary_source = models.ForeignKey(PrimarySource, on_delete=models.CASCADE, null=True, blank=True)
    is_oa = models.BooleanField()
    oa_status = models.ForeignKey(OAStatus, on_delete=models.CASCADE)
    referenced_works_count = models.IntegerField()
    fwci = models.FloatField(null=True, blank=True)
    objects = WorkQuerySet.as_manager()

    class Meta:
            base_manager_name = 'objects'

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
    institution_name = models.CharField(max_length=255, db_index=True)
    country_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.institution_name
    
    def save(self, *args, **kwargs):
        # Convert empty strings to None before saving to the database
        if self.country_code == '':
            self.country_code = None
        super().save(*args, **kwargs)


class Author(models.Model):
    author_id = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.author_id

class Authorship(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_corresponding = models.BooleanField()
    author_position = models.ForeignKey(AuthorPosition, on_delete=models.CASCADE, null=True, blank=True)

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
