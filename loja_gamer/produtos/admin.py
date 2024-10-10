from django.contrib import admin
from .models import Jogo, Equipamento, ItemCarrinho, Carrinho

@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'plataforma', 'preco_unitario', 'data_lancamento')

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'preco_unitario')

admin.site.register(ItemCarrinho)
admin.site.register(Carrinho)
