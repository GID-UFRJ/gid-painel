# em common/urls.py

from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    # As URLs apontam para a MESMA view genérica. O Django tentará a mais específica primeiro.

    # URL para plotters que precisam de um ID extra (ex: ppg_detalhe)
    # Ex: /download/csv/ppg_detalhe/154/discentes_por_ano/
    path('download/csv/<str:plotter_name>/<int:programa_id>/<str:nome_plot>/', 
         views.download_csv_generic, name='download_csv_generic_with_id'),

    # URL para plotters simples (ex: pessoal)
    # Ex: /download/csv/pessoal/discentes_por_ano/
    path('download/csv/<str:plotter_name>/<str:nome_plot>/', 
         views.download_csv_generic, name='download_csv_generic'),
]