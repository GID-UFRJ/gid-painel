from django.urls import path

from . import views

app_name = 'openalex'

urlpatterns = [
    path("", views.index, name="index"),
    path("producao/", views.producao, name="producao"),
    path("impacto/", views.impacto, name="impacto"),
    path("colaboracao/", views.colaboracao, name="colaboracao"),
    path('graficos/<str:nome_plot>/', views.grafico_generico_openalex, name='grafico_generico_openalex'),
]