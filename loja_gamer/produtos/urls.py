from django.urls import path
from . import views

urlpatterns = [
    path('jogos/', views.listar_jogos, name='listar_jogos'),
    path('equipamentos/', views.listar_equipamentos, name='listar_equipamentos'),
]