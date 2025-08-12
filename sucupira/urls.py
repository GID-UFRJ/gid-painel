from django.urls import path
from . import views

app_name = 'sucupira'

urlpatterns = [
    path('', views.index, name='index'),
    path('posgrad_ufrj/', views.posgrad_ufrj, name='posgrad_ufrj'),
    path('ppgs/', views.ppgs, name='ppgs'),
]