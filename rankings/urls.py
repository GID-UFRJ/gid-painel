from django.urls import path
from . import views

app_name='rankings'

urlpatterns = [
    path("", views.index, name="index"),
    #path("academicos/", views.academicos, name="academicos"),
    #path("sustentabilidade/", views.sustentabilidade, name="sustentabilidade")

]