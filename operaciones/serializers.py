from rest_framework import serializers
from .models import Movimiento, Farmacia, Motorista

class FarmaciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmacia
        # Traemos los datos clave de la sucursal de origen
        fields = ['codigo', 'nombre', 'direccion', 'region', 'provincia', 'comuna', 'telefono', 'estado']

class MotoristaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorista
        fields = ['rut', 'nombre_completo', 'estado']

class MovimientoSerializer(serializers.ModelSerializer):
    # Anidamos la farmacia para obtener el objeto completo en lugar de solo el ID
    origen = FarmaciaSerializer(read_only=True)
    motorista = MotoristaSerializer(read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            'id', 
            'numero_pedido', 
            'tipo', 
            'origen', 
            'direccion_destino', 
            'comuna_destino', 
            'motorista', 
            'fecha', 
            'estado'
        ]