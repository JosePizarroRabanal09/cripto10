from django.contrib import admin
from .models import Guerrero, UserInfo, CompraCofre,Compra, HistorialGold, Withdraw, Tower,RegistroCompra,life,Cofre

@admin.register(Guerrero)
class GuerreroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rareza', 'produccion_min', 'produccion_max', 'precio', 'cooldown')

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'guerrero', 'fecha_compra', 'total', 'cooldown_actual', 'habilitado_farmear', 'hora_habilitacion')

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_wallet', 'gold')

@admin.register(HistorialGold)
class HistorialGoldAdmin(admin.ModelAdmin):
    list_display = ('user', 'guerrero', 'oro_ganado', 'fecha')
    list_filter = ('user',)  # Agrupar por usuario

@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'fecha_retiro', 'status')  # Cambia 'date' y 'hour' a 'datetime'
    list_filter = ('user',)  # Filtro por usuario
    
@admin.register(Tower)
class TowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'observacion', 'tipo', 'price', 'stock', 'imagen')
    
    
@admin.register(RegistroCompra)
class RegistroCompraAdmin(admin.ModelAdmin):
    list_display = ('user', 'tower', 'fecha_compra')
    
@admin.register(life)
class LifeAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'last_updated')
    list_filter = ('user',)  # Filtro por usuario
    
@admin.register(Cofre)
class CofreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'sonido','precio')
    
    
@admin.register(CompraCofre)
class CompraCofreAdmin(admin.ModelAdmin):
    list_display = ('user','cofre','fecha_compra','cofre_abierto')