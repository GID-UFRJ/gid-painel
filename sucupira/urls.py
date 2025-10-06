from django.urls import path
from . import views

app_name = 'sucupira'

urlpatterns = [
    path('', views.index, name='index'),
    path('pessoal_ppg', views.pessoal_ppg, name='pessoal_ppg'),
    path('graficos/discentes-ano', views.grafico_discentes_por_ano, name='grafico_discentes_por_ano'),
    path('graficos/docentes-ano', views.grafico_docentes_por_ano, name='grafico_docentes_por_ano'),
    path('graficos/discentes-ano-ppg/<int:programa_id>/', views.grafico_discentes_por_ano_ppg, name='grafico_discentes_por_ano_ppg'),
    path('graficos/media-titulacao-ano-ppg/<int:programa_id>/', views.grafico_media_titulacao_por_ano_ppg, name='grafico_media_titulacao_por_ano_ppg'),
    path('graficos/docentes-ano-ppg/<int:programa_id>/', views.grafico_docentes_por_ano_ppg, name='grafico_docentes_por_ano_ppg'),
    path('graficos/conceito-programa-ano-ppg/<int:programa_id>/', views.grafico_conceito_programa_por_ano_ppg, name='grafico_conceito_programa_por_ano_ppg'),
    path('posgrad_ufrj/', views.posgrad_ufrj, name='posgrad_ufrj'),
    path('ppgs/', views.ppgs, name='ppgs'),
    path('ppgs/<int:programa_id>/', views.ppg_detalhe, name='ppg_detalhe'),
]