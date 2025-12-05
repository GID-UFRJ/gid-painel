from django.urls import path
from . import views

app_name='rankings'

urlpatterns = [
    path("", views.index, name="index"),
    path("academicos/", views.academicos, name="academicos"),
    path("sustentabilidade/", views.sustentabilidade, name="sustentabilidade"),
    # Endpoint Genérico do HTMX (Continua o mesmo, servindo ambas as páginas)
    path('graficos/<str:nome_plot>/', views.grafico_generico_rankings, name='grafico_generico'),
]