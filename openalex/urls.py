from django.urls import path

from . import views

app_name = 'openalex'

urlpatterns = [
    path("", views.index, name="index"),
    path("producao/", views.producao, name="producao"),
    path("colaboracao/", views.colaboracao, name="colaboracao"),
]