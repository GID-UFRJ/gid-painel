from django.urls import path
from . import views


urlpatterns = [
    path('', views.atualizar_grafico, name='teste'),
]