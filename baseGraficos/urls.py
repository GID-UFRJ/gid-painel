from django.urls import path
from . import views


urlpatterns = [
    path("ppg", views.view_lista_ppg, name="url_lista_ppg"),
    path("<str:nome_painel>", views.view_graficos, name="url_grafico_painel"),
    path("ppg/<str:cod_ppg>", views.view_graficos_producao, name="url_grafico_ppg"),
]