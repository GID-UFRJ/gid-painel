from django.urls import path
from . import views

app_name = 'sucupira'

urlpatterns = [
    # ==========================================
    # 1. PÁGINAS PRINCIPAIS (Views Estáticas)
    # ==========================================
    path('', views.index, name='index'),

    path('pessoal_discentes/', views.pessoal_discentes, name='pessoal_discentes'),
    path('pessoal_docentes/', views.pessoal_docentes, name='pessoal_docentes'),

    path('posgrad_ufrj/', views.posgrad_ufrj, name='posgrad_ufrj'),
    
    path('ppgs/', views.ppgs, name='ppgs'),
    # Usei <str:programa_id> por precaução, caso os códigos da CAPES tenham letras ou zeros à esquerda. 
    # Se o seu ID for puramente numérico (AutoField), pode manter <int:programa_id>.
    path('ppgs/<str:programa_id>/', views.ppg_detalhe, name='ppg_detalhe'),

    # ==========================================
    # 2. ENDPOINTS GENÉRICOS (HTMX / Gráficos)
    # ==========================================
    
    # Rota para os gráficos gerais (Pessoal e UFRJ)
    path('htmx/grafico/<str:nome_plot>/', views.grafico_generico_sucupira, name='htmx_grafico_sucupira'),

    # Rota para os gráficos de um PPG específico (passa o programa_id via kwargs)
    path('htmx/grafico/<str:nome_plot>/<str:programa_id>/', views.grafico_generico_sucupira, name='htmx_grafico_ppg_detalhe'),
]