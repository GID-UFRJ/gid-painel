from django.urls import path
from . import views

app_name = 'sucupira'

urlpatterns = [
    path('', views.index, name='index'),
    path('pessoal_ppg', views.pessoal_ppg, name='pessoal_ppg'),
    path('graficos/discentes-ano', views.grafico_discentes_por_ano, name='grafico_discentes_por_ano'),
    path('graficos/docentes-ano', views.grafico_docentes_por_ano, name='grafico_docentes_por_ano'),
    path('posgrad_ufrj/', views.posgrad_ufrj, name='posgrad_ufrj'),
    path('ppgs/', views.ppgs, name='ppgs'),
    path('ppgs/<int:programa_id>/', views.ppg_detalhe, name='ppg_detalhe'),
]