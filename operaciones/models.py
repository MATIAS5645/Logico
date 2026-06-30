from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # 💡 Importamos el modelo de usuarios

class Farmacia(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección Física")
    region = models.CharField(max_length=100, verbose_name="Región")
    provincia = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='Activa', choices=[('Activa', 'Activa'), ('Inactiva', 'Inactiva')])
    comuna = models.CharField(max_length=100, default="Santiago") 
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Motocicleta(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField(verbose_name="Año")

    def __str__(self):
        return f"{self.patente} ({self.marca} {self.modelo})"

class Motorista(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='motorista_perfil', null=True, blank=True)
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre_completo = models.CharField(max_length=150)
    region = models.CharField(max_length=100, verbose_name="Región")
    provincia = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, default='Activo', choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')])
    
    # Relación 1 a 1
    motocicleta = models.OneToOneField(Motocicleta, on_delete=models.SET_NULL, null=True, blank=True, related_name='motorista_asignado')

    def __str__(self):
        return self.nombre_completo

class Movimiento(models.Model):
    TIPOS_MOVIMIENTO = [
        ('Directo', 'Directo'),
        ('Con Receta', 'Con Receta'),
        ('Traslado', 'Traslado'),
        ('Reenvío', 'Reenvío'),
    ]
    ESTADOS_MOVIMIENTO = [
        ('Pendiente', 'Pendiente'),
        ('En ruta', 'En ruta'),
        ('Entregado', 'Entregado'),
    ]
    
    numero_pedido = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=50, choices=TIPOS_MOVIMIENTO)
    
    # Origen
    origen = models.ForeignKey(Farmacia, on_delete=models.CASCADE, related_name='movimientos_salida')
    
    # === NUEVOS CAMPOS DE DESTINO ===
    direccion_destino = models.CharField(max_length=250, verbose_name="Dirección de Destino")
    comuna_destino = models.CharField(max_length=100, verbose_name="Comuna de Destino", blank=True, null=True)
    
    # Motorista asignado
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE, related_name='movimientos_asignados')
    
    fecha = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=50, choices=ESTADOS_MOVIMIENTO, default='En ruta')

    def __str__(self):
        return f"{self.numero_pedido} hacia {self.direccion_destino}"