from django.urls import path
from .views import view_analise_ppg

app_name = 'programa'

urlpatterns = [
    path('', view_analise_ppg),
    path('ppgs', view_analise_ppg, name='ppgs'),
]