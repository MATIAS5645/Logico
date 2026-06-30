from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User # 💡 Asegúrate de tener esta importación al principio del archivo
from django.contrib.auth.decorators import user_passes_test

import random


from .models import Movimiento, Farmacia, Motorista, Motocicleta
from .serializers import MovimientoSerializer

def es_admin_absoluto(user):
    # Solo permite la entrada si es el superusuario creador del sistema
    return user.is_authenticated and user.is_superuser

# --- VISTAS PROTEGIDAS CON LOGIN (PLATAFORMA WEB) ---

@login_required(login_url='login')
def listado_general(request):
    movimientos_db = Movimiento.objects.all().order_by('-id')
    return render(request, 'listado_general.html', {'movimientos': movimientos_db})

@login_required(login_url='login')
@user_passes_test(es_admin_absoluto, login_url='asignar_pedidos') # 💡 Si entra el despachador, lo rebota a su pantalla de despacho
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
@user_passes_test(es_admin_absoluto, login_url='asignar_pedidos')
def gestor_farmacias(request):
    if request.method == 'POST':
        f_id = request.POST.get('f_id_edit') 
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        region = request.POST.get('region')
        provincia = request.POST.get('provincia')
        comuna = request.POST.get('comuna')  
        telefono = request.POST.get('telefono')  
        estado = request.POST.get('estado')

        if f_id:
            farmacia = Farmacia.objects.get(id=f_id)
            farmacia.codigo = codigo
            farmacia.nombre = nombre
            farmacia.direccion = direccion
            farmacia.region = region
            farmacia.provincia = provincia
            farmacia.comuna = comuna  
            farmacia.telefono = telefono  
            farmacia.estado = estado
            farmacia.save()
        else:
            Farmacia.objects.create(
                codigo=codigo,
                nombre=nombre,
                direccion=direccion,
                region=region,
                provincia=provincia,
                comuna=comuna,  
                telefono=telefono,  
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
@user_passes_test(es_admin_absoluto, login_url='asignar_pedidos')
def gestor_motoristas(request):
    if request.method == 'POST':
        m_id = request.POST.get('m_id_edit') 
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        region = request.POST.get('region')
        provincia = request.POST.get('provincia')
        estado = request.POST.get('estado')

        if m_id:
            # --- MODO EDICIÓN: Solo actualiza los datos del motorista ---
            motorista = Motorista.objects.get(id=m_id)
            motorista.rut = rut
            motorista.nombre_completo = nombre
            motorista.region = region
            motorista.provincia = provincia
            motorista.estado = estado
            motorista.save()
            messages.success(request, f'Motorista {nombre} actualizado correctamente.')
        else:
            # --- MODO CREACIÓN AUTOMÁTICA ---
            
            # 1. Generar Username limpio (ejemplo: "Thomas Silva" -> "thomassilva")
            username_automatico = "".join(nombre.split()).lower()
            
            # 2. Evitar duplicados de usuario si dos personas se llaman igual
            base_username = username_automatico
            contador = 1
            while User.objects.filter(username=username_automatico).exists():
                username_automatico = f"{base_username}{contador}"
                contador += 1

            # 3. Generar Contraseña (limpia los puntos/guiones del RUT y toma los primeros 6 números)
            rut_limpio = rut.replace(".", "").replace("-", "")
            password_automatica = rut_limpio[:6] if len(rut_limpio) >= 6 else "logico123"

            # 4. Crear el Usuario en el sistema de seguridad de Django
            nuevo_usuario = User.objects.create_user(
                username=username_automatico,
                password=password_automatica
            )

            # 5. Crear el perfil del Motorista y asociarle el usuario recién creado
            Motorista.objects.create(
                user=nuevo_usuario, # 💡 Queda enlazado de inmediato para la App Móvil
                rut=rut,
                nombre_completo=nombre,
                region=region,
                provincia=provincia,
                estado=estado
            )
            
            # Mostramos un mensaje flotante en la web con las credenciales creadas
            messages.success(
                request, 
                f'¡Motorista creado! Usuario de App: {username_automatico} | Contraseña: {password_automatica}'
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
@user_passes_test(es_admin_absoluto, login_url='asignar_pedidos')
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

# --- VISTAS LIBRES (AUTENTICACIÓN WEB) ---

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
    total_pedidos = Movimiento.objects.count()
    en_ruta = Movimiento.objects.filter(estado='En ruta').count()
    entregados = Movimiento.objects.filter(estado='Entregado').count()
    
    total_farmacias = Farmacia.objects.filter(estado='Activa').count()
    total_motoristas = Motorista.objects.filter(estado='Activo').count()
    total_motos = Motocicleta.objects.count()
    
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


# --- API ENDPOINTS PARA LA APLICACIÓN MÓVIL ---

@api_view(['POST'])
@csrf_exempt
def api_login_motorista(request):
    usuario = request.data.get('username')
    contrasena = request.data.get('password')
    
    user = authenticate(username=usuario, password=contrasena)
    
    if user is not None:
        try:
            motorista = user.motorista_perfil
            return Response({
                'success': True,
                'motorista_id': motorista.id,
                'nombre': motorista.nombre_completo
            })
        except Exception:
            return Response({
                'success': False, 
                'error': 'Este usuario no tiene un perfil de motorista asignado en el panel Admin.'
            })
    else:
        return Response({
            'success': False,
            'error': 'Usuario o contraseña incorrectos en el sistema Django.'
        })

@api_view(['GET'])
def api_pedidos_motorista(request, motorista_id):
    movimientos = Movimiento.objects.filter(motorista_id=motorista_id).exclude(estado='Entregado')
    serializer = MovimientoSerializer(movimientos, many=True)
    return Response(serializer.data)
def es_miembro_despacho(user):
    # Permite la entrada si es administrador absoluto O si pertenece al grupo 'Despachadores'
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Despachadores').exists())
def es_despachador(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Despachadores').exists())
@login_required(login_url='login')
@user_passes_test(es_miembro_despacho, login_url='listado_general')
def asignar_pedidos(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        motorista_id = request.POST.get('motorista_id')

        if pedido_id and motorista_id:
            try:
                pedido = Movimiento.objects.get(id=pedido_id)
                motorista = Motorista.objects.get(id=motorista_id)
                
                # Asignamos el motorista al pedido y nos aseguramos de que quede 'En ruta'
                pedido.motorista = motorista
                pedido.estado = 'En ruta'
                pedido.save()
                
                messages.success(request, f'Pedido {pedido.numero_pedido} asignado con éxito a {motorista.nombre_completo}.')
            except Exception as e:
                messages.error(request, f'Error al asignar el pedido: {str(e)}')
        else:
            messages.error(request, 'Faltan datos obligatorios para realizar la asignación.')
            
        return redirect('asignar_pedidos')

    # Filtramos los movimientos que NO tengan un motorista asignado o estén pendientes
    pedidos_pendientes = Movimiento.objects.filter(motorista__isnull=True).order_by('-id')
    
    # Traemos solo los motoristas que estén activos en el sistema para desplegarlos en el select
    motoristas_activos = Motorista.objects.filter(estado='Activo').order_by('nombre_completo')

    return render(request, 'asignar_pedidos.html', {
        'pedidos': pedidos_pendientes,
        'motoristas': motoristas_activos
    })