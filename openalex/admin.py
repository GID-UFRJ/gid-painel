from django.contrib import admin

# Register your models here.
from .models import (
    Year,
    WorkType,
    OAStatus,
    PrimarySource,
    Work,
    Institution,
    Authorship,
    AuthorshipInstitution,
    CitedByYear,
    Topic,
    WorkTopic,
)

admin.site.register(Year)
admin.site.register(WorkType)
admin.site.register(OAStatus)
admin.site.register(PrimarySource)
admin.site.register(Work)
admin.site.register(Institution)
admin.site.register(Authorship)
admin.site.register(AuthorshipInstitution)
admin.site.register(CitedByYear)
admin.site.register(Topic)
admin.site.register(WorkTopic)