from django.contrib import admin
from django.urls import path
from myapp.views import home, user_login,abrircofre, register,compracofre, inventario, user_logout, compra, farmear, perfil,farmearTower,ranking
from django.conf import settings
from django.contrib.auth import views as auth_views

from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login),
    path('register/', register),
    path('home/', home),
    path('ranking/',ranking),
    path('inventario/', inventario, name='inventario'),
    path('logout/', user_logout),
    path('compra/<int:id>/', compra, name='compra'),
    path('compra/<str:id>/', compra, name='compra'),
    path('abrircofre/<int:id>/', abrircofre, name='abrircofre'),

    path('farmear/<int:id>/', farmear, name='farmear'),
    path('farmearTower/<int:id>/', farmearTower, name='farmearTower'),
    path('compracofre/<int:id>/', compracofre, name='compracofre'),

    path('perfil/', perfil),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),  # Utiliza la vista predeterminada de Django para la confirmación del envío del correo electrónico de recuperación
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),  # Utiliza la vista predeterminada de Django para confirmar la recuperación de contraseña
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),  # Utiliza la vista predeterminada de Django para la confirmación de la recuperación de contraseña completa
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
