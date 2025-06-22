from django.contrib import admin
from . import models
from django.forms import Textarea

admin.site.register(models.Grafico)
admin.site.register(models.Painel)
admin.site.register(models.EstiloGrafico)
admin.site.register(models.TamanhoGrafico)
