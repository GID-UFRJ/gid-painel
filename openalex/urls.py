from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("producao/", views.producao, name="producao"),
    path("visibilidade/", views.visibilidade, name="visibilidade"),
]