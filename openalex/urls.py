from django.urls import path

from . import views

app_name = 'openalex'

urlpatterns = [
    path("", views.index, name="index"),
    path("producao/", views.producao, name="producao"),
    path("producao/graficos/prod-ano", views.grafico_producao_por_ano, name="grafico_producao_por_ano"),
    path("impacto/", views.impacto, name="impacto"),
    path("colaboracao/", views.colaboracao, name="colaboracao"),
]