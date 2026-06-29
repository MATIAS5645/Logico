from django.contrib import admin
from django.urls import path
from operaciones import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('listado/', views.listado_general, name='listado_general'),
    path('crear-movimiento/', views.registrar_movimiento, name='crear_movimiento'),
    
    # NUEVAS RUTAS PARA FARMACIAS
    path('farmacias/', views.gestor_farmacias, name='farmacias'),
    path('farmacias/eliminar/<int:id>/', views.eliminar_farmacia, name='eliminar_farmacia'),
    path('motoristas/', views.gestor_motoristas, name='motoristas'),
    path('motoristas/eliminar/<int:id>/', views.eliminar_motorista, name='eliminar_motorista'),
    path('motos/registro/', views.gestor_motos, name='registro_motos'),
    path('motos/eliminar/<int:id>/', views.eliminar_moto, name='eliminar_moto'),
    path('motos/asignar/', views.asignar_motos, name='asignar_motos'),
    path('listado/', views.listado_general, name='listado_general'),
    path('listado/eliminar/<int:id>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    path('', views.iniciar_sesion, name='login'), # Esta será tu página principal ahora
    path('logout/', views.cerrar_sesion, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # RUTA DE LA API MÓVIL
    path('api/pedidos/<int:motorista_id>/', views.api_pedidos_motorista, name='api_pedidos_motorista'),
]