from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from produtos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.pagina_inicial, name='pagina_inicial'),  # Página inicial redireciona para a lista de jogos
    path('jogos/', include('produtos.urls')),  # URL para os jogos
    path('equipamentos/', include('produtos.urls')),# URL para os equipamentos
    path('carrinho/', views.visualizar_carrinho, name='visualizar_carrinho'),
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido-concluido/', views.pedido_concluido, name='pedido_concluido'),
    path('remover-item/<int:item_id>/', views.remover_item, name='remover_item'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)