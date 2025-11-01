from django.urls import path
from . import views

app_name = 'sucupira'

urlpatterns = [
    #Endpoints das páginas dos painéis em si
    path('', views.index, name='index'),

    # ROTA ANTIGA (página com abas)
    #path('pessoal_ppg', views.pessoal_ppg, name='pessoal_ppg'),

    path('pessoal_discentes/', views.pessoal_discentes, name='pessoal_discentes'),
    path('pessoal_docentes/', views.pessoal_docentes, name='pessoal_docentes'),

    path('posgrad_ufrj/', views.posgrad_ufrj, name='posgrad_ufrj'),
    path('ppgs/', views.ppgs, name='ppgs'),
    path('ppgs/<int:programa_id>/', views.ppg_detalhe, name='ppg_detalhe'),

    #Endpoints genéricos para gráficos reativos

    # Endpoint para todos os gráficos da seção "Pessoal"
    path('graficos/pessoal/<str:nome_plot>/', views.grafico_generico_pessoal, name='grafico_generico_pessoal'),

    # Endpoint para todos os gráficos da seção "PosGrad UFRJ"
    path('graficos/posgrad_ufrj/<str:nome_plot>/', views.grafico_generico_posgrad_ufrj, name='grafico_generico_posgrad_ufrj'),

    # Endpoint para todos os gráficos da seção "PPG Detalhe"
    path('graficos/ppg/<int:programa_id>/<str:nome_plot>/', views.grafico_generico_ppg, name='grafico_generico_ppg'),
]