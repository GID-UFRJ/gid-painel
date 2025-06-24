from django.urls import path
from . import views


urlpatterns = [
    path("<str:nome_painel>", views.view_graficos, name="url_grafico"),

]