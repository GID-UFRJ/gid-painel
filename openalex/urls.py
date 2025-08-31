from django.urls import path

from . import views

app_name = 'openalex'

urlpatterns = [
    path("", views.index, name="index"),
    path("producao/", views.producao, name="producao"),
    path("graficos/prod-ano", views.grafico_producao_por_ano, name="grafico_producao_por_ano"),
    path("graficos/cit-ano", views.grafico_citacoes_por_ano, name="grafico_citacoes_por_ano"),
    path("graficos/colab-ano", views.grafico_colaboracoes_por_ano, name="grafico_colaboracoes_por_ano"),
    path("graficos/top-colab", views.grafico_top_colaboracoes, name="grafico_top_colaboracoes"),
    path("impacto/", views.impacto, name="impacto"),
    path("colaboracao/", views.colaboracao, name="colaboracao"),
]