from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Movimiento, Farmacia, Motorista, Motocicleta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MovimientoSerializer
import random

# --- VISTAS PROTEGIDAS CON LOGIN ---

@login_required(login_url='login')
def listado_general(request):
    movimientos_db = Movimiento.objects.all().order_by('-id')
    return render(request, 'listado_general.html', {'movimientos': movimientos_db})

@login_required(login_url='login')
def registrar_movimiento(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipoMov')
        id_origen = request.POST.get('origen')
        id_motorista = request.POST.get('motorista')
        direccion = request.POST.get('mov_direccion')
        comuna = request.POST.get('mov_comuna')

        farmacia_origen = Farmacia.objects.get(id=id_origen)
        motorista_asignado = Motorista.objects.get(id=id_motorista)

        numero_pedido = f"#{random.randint(1000, 9999)}"

        Movimiento.objects.create(
            numero_pedido=numero_pedido,
            tipo=tipo,
            origen=farmacia_origen,
            motorista=motorista_asignado,
            direccion_destino=direccion,
            comuna_destino=comuna,
            estado='En ruta'
        )
        return redirect('listado_general')

    farmacias = Farmacia.objects.filter(estado='Activa')
    motoristas = Motorista.objects.filter(estado='Activo')
    
    return render(request, 'registrar_movimientos.html', {
        'farmacias': farmacias,
        'motoristas': motoristas
    })

@login_required(login_url='login')
def gestor_farmacias(request):
    if request.method == 'POST':
        f_id = request.POST.get('f_id_edit') 
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        region = request.POST.get('region')
        provincia = request.POST.get('provincia')
        comuna = request.POST.get('comuna')  # 👈 Captura Comuna
        telefono = request.POST.get('telefono')  # 👈 Captura Teléfono
        estado = request.POST.get('estado')

        if f_id:
            farmacia = Farmacia.objects.get(id=f_id)
            farmacia.codigo = codigo
            farmacia.nombre = nombre
            farmacia.direccion = direccion
            farmacia.region = region
            farmacia.provincia = provincia
            farmacia.comuna = comuna  # 👈 Actualiza Comuna
            farmacia.telefono = telefono  # 👈 Actualiza Teléfono
            farmacia.estado = estado
            farmacia.save()
        else:
            Farmacia.objects.create(
                codigo=codigo,
                nombre=nombre,
                direccion=direccion,
                region=region,
                provincia=provincia,
                comuna=comuna,  # 👈 Crea con Comuna
                telefono=telefono,  # 👈 Crea con Teléfono
                estado=estado
            )
        return redirect('farmacias')

    farmacias_db = Farmacia.objects.all().order_by('id')
    return render(request, 'farmacias.html', {'farmacias': farmacias_db})

@login_required(login_url='login')
def eliminar_farmacia(request, id):
    farmacia = Farmacia.objects.get(id=id)
    farmacia.delete()
    return redirect('farmacias')

@login_required(login_url='login')
def gestor_motoristas(request):
    if request.method == 'POST':
        m_id = request.POST.get('m_id_edit') 
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        region = request.POST.get('region')
        provincia = request.POST.get('provincia')
        estado = request.POST.get('estado')

        if m_id:
            motorista = Motorista.objects.get(id=m_id)
            motorista.rut = rut
            motorista.nombre_completo = nombre
            motorista.region = region
            motorista.provincia = provincia
            motorista.estado = estado
            motorista.save()
        else:
            Motorista.objects.create(
                rut=rut,
                nombre_completo=nombre,
                region=region,
                provincia=provincia,
                estado=estado
            )
        return redirect('motoristas')

    motoristas_db = Motorista.objects.all().order_by('id')
    return render(request, 'motoristas.html', {'motoristas': motoristas_db})

@login_required(login_url='login')
def eliminar_motorista(request, id):
    motorista = Motorista.objects.get(id=id)
    motorista.delete()
    return redirect('motoristas')

@login_required(login_url='login')
def gestor_motos(request):
    if request.method == 'POST':
        moto_id = request.POST.get('moto_id_edit')
        patente = request.POST.get('patente')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        anio = request.POST.get('anio')

        if moto_id:
            moto = Motocicleta.objects.get(id=moto_id)
            moto.patente = patente
            moto.marca = marca
            moto.modelo = modelo
            moto.anio = anio
            moto.save()
        else:
            Motocicleta.objects.create(
                patente=patente,
                marca=marca,
                modelo=modelo,
                anio=anio
            )
        return redirect('registro_motos')

    motos_db = Motocicleta.objects.all().order_by('id')
    return render(request, 'registro_motos.html', {'motos': motos_db})

@login_required(login_url='login')
def eliminar_moto(request, id):
    moto = Motocicleta.objects.get(id=id)
    moto.delete()
    return redirect('registro_motos')

@login_required(login_url='login')
def asignar_motos(request):
    if request.method == 'POST':
        motorista_id = request.POST.get('motorista')
        moto_id = request.POST.get('moto')

        if motorista_id:
            motorista = Motorista.objects.get(id=motorista_id)
            
            if moto_id:
                moto = Motocicleta.objects.get(id=moto_id)
                
                dueno_actual = Motorista.objects.filter(motocicleta=moto).exclude(id=motorista.id).first()
                
                if dueno_actual:
                    messages.error(request, f'Error: La moto patente {moto.patente} ya está siendo utilizada por {dueno_actual.nombre_completo}.')
                    return redirect('asignar_motos')
                
                motorista.motocicleta = moto
                messages.success(request, f'Moto {moto.patente} asignada correctamente a {motorista.nombre_completo}.')
            else:
                motorista.motocicleta = None
                messages.success(request, f'Se ha quitado la moto a {motorista.nombre_completo}.')
                
            motorista.save()
            
        return redirect('asignar_motos')

    motoristas_db = Motorista.objects.all().order_by('nombre_completo')
    motos_db = Motocicleta.objects.all().order_by('patente')
    
    return render(request, 'motos.html', {
        'motoristas': motoristas_db,
        'motos': motos_db
    })

@login_required(login_url='login')
def eliminar_movimiento(request, id):
    movimiento = Movimiento.objects.get(id=id)
    movimiento.delete()
    return redirect('listado_general')

# --- VISTAS LIBRES (No requieren estar logueado para verlas) ---

def iniciar_sesion(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=contrasena)
        
        if user is not None:
            login(request, user) 
            return redirect('listado_general') 
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    return render(request, 'index.html')

def cerrar_sesion(request):
    logout(request) 
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    # Contamos los movimientos según su estado
    total_pedidos = Movimiento.objects.count()
    en_ruta = Movimiento.objects.filter(estado='En ruta').count()
    entregados = Movimiento.objects.filter(estado='Entregado').count()
    
    # Contamos los recursos de los mantenedores
    total_farmacias = Farmacia.objects.filter(estado='Activa').count()
    total_motoristas = Motorista.objects.filter(estado='Activo').count()
    total_motos = Motocicleta.objects.count()
    
    # Traemos solo los últimos 5 movimientos para mostrar una sección de "Actividad Reciente"
    movimientos_recientes = Movimiento.objects.all().order_by('-id')[:5]
    
    contexto = {
        'total_pedidos': total_pedidos,
        'en_ruta': en_ruta,
        'entregados': entregados,
        'total_farmacias': total_farmacias,
        'total_motoristas': total_motoristas,
        'total_motos': total_motos,
        'recientes': movimientos_recientes,
    }
    return render(request, 'dashboard.html', contexto)
# --- API PARA LA APLICACIÓN MÓVIL ---

@api_view(['GET'])
def api_pedidos_motorista(request, motorista_id):
    # Buscamos los pedidos asignados a este motorista que NO estén "Entregados"
    movimientos = Movimiento.objects.filter(motorista_id=motorista_id).exclude(estado='Entregado')
    
    # Pasamos los datos por el "traductor" que creamos
    serializer = MovimientoSerializer(movimientos, many=True)
    
    # Devolvemos un JSON puro
    return Response(serializer.data)