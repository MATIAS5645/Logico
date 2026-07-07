from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Incidencia, Movimiento
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import datetime
from .models import Incidencia 
from django.http import HttpResponse
from .forms import IncidenciaForm, IncidenciaMovilForm
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

def api_listar_pedidos_activos(request):
    if request.method == 'GET':
        # Filtramos los pedidos que están en proceso de entrega
        pedidos = Movimiento.objects.filter(estado__iexact='En Ruta')
        
        data = []
        for p in pedidos:
            data.append({
                'id': p.id,
                'numero_pedido': p.numero_pedido,
                'destino': p.direccion_destino,
                'tipo': p.tipo
            })
            
        return JsonResponse({'status': 'success', 'pedidos': data}, safe=False)

@login_required
def panel_incidencias(request):
    # El despachador ve todas las incidencias, las más recientes primero
    incidencias = Incidencia.objects.all().order_by('-fecha_reporte')
    
    if request.method == 'POST':
        # Lógica por si se reporta una incidencia desde la web (o testing)
        movimiento_id = request.POST.get('movimiento_id')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        
        movimiento = get_object_or_404(Movimiento, id=movimiento_id)
        
        Incidencia.objects.create(
            movimiento=movimiento,
            motorista=request.user,
            tipo=tipo,
            descripcion=descripcion
        )
        # Opcional: Cambiar el estado del pedido a 'RETRASADO' o 'CON_PROBLEMAS'
        movimiento.estado = 'CON_PROBLEMAS' 
        movimiento.save()
        
        messages.success(request, "Incidencia reportada con éxito.")
        return redirect('panel_incidencias')

    return render(request, 'incidencias.html', {'incidencias': incidencias})

@login_required
def cambiar_estado_incidencia(request, incidencia_id, nuevo_estado):
    # Permite al despachador gestionar y solucionar el problema
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    incidencia.estado = nuevo_estado
    incidencia.save()
    messages.info(request, f"Incidencia #{incidencia_id} actualizada a {nuevo_estado}.")
    return redirect('panel_incidencias')
@csrf_exempt  # Evita el bloqueo de seguridad 403 en apps móviles
@api_view(['POST'])
def confirmar_entrega(request, pk):
    try:
        # Django busca automáticamente en la columna 'id' (bigint)
        pedido = Movimiento.objects.get(pk=pk)
        pedido.estado = 'ENTREGADO'
        pedido.save()
        
        # Enviamos un diccionario plano para asegurar compatibilidad total
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        
    except Movimiento.DoesNotExist:
        return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
@login_required
def generar_reporte_mensual_pdf(request):
    # 1. Obtener el mes y año actual de forma automática
    hoy = datetime.date.today()
    primer_dia_mes = hoy.replace(day=1)
    
    # 2. Filtrar los datos en PostgreSQL
    pedidos_del_mes = Movimiento.objects.filter(fecha__gte=primer_dia_mes)    
    totales = pedidos_del_mes.count()
    entregados = pedidos_del_mes.filter(estado__iexact='ENTREGADO').count()
    en_ruta = pedidos_del_mes.filter(estado__iexact='En ruta').count()
    
    # Contar incidencias ocurridas en el mes
    incidencias_del_mes = Incidencia.objects.filter(fecha_reporte__gte=primer_dia_mes).count()

    # 3. Configurar la respuesta HTTP para forzar la descarga del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Reporte_Logistico_{hoy.strftime("%m_%Y")}.pdf"'

    # 4. Construir el documento PDF con ReportLab
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Estilos de texto
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E1E1E'),
        spaceAfter=12
    )
    style_normal = styles['Normal']

    # Encabezado del PDF
    story.append(Paragraph(f"📊 Reporte Mensual de Operaciones - {hoy.strftime('%B %Y')}", style_titulo))
    story.append(Paragraph(f"Generado el: {hoy.strftime('%d/%m/%Y a las %H:%M')}", style_normal))
    story.append(Spacer(1, 20))

    # Tabla de Métricas de Rendimiento Clave (KPIs)
    datos_kpi = [
        ['Métrica Logística', 'Cantidad'],
        ['Total Pedidos Procesados', str(totales)],
        ['Entregas Confirmadas (App)', str(entregados)],
        ['Pedidos en Ruta Activa', str(en_ruta)],
        ['Alertas / Incidencias Reportadas', str(incidencias_del_mes)]
    ]
    
    tabla_kpi = Table(datos_kpi, colWidths=[250, 150])
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0D6EFD')), # Azul corporativo LÓGICO
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(Paragraph("<b>Resumen de Rendimiento del Mes</b>", styles['Heading2']))
    story.append(Spacer(1, 8))
    story.append(tabla_kpi)
    
    # Generar el PDF final
    doc.build(story)
    return response

@login_required
def listado_incidencias(request):
    # 1. Obtener todas las incidencias ordenadas por la más reciente
    # (Si tu campo no se llama 'fecha_reporte', cámbialo por 'fecha')
    incidencias = Incidencia.objects.all().order_by('-fecha_reporte')
    
    # 2. Calcular métricas rápidas para los KPIs superiores
    total_incidencias = incidencias.count()
    criticas = incidencias.filter(tipo__iexact='Critica').count()
    pendientes = incidencias.filter(estado__iexact='Pendiente').count()
    resueltas = incidencias.filter(estado__iexact='Resuelta').count()

    context = {
        'incidencias': incidencias,
        'total_incidencias': total_incidencias,
        'criticas': criticas,
        'pendientes': pendientes,
        'resueltas': resueltas,
    }
    return render(request, 'incidencias.html', context)

@login_required
def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_incidencias') # Redirige al historial tras guardar
    else:
        form = IncidenciaForm()
    
    return render(request, 'crear_incidencia.html', {'form': form})
@csrf_exempt
def crear_incidencia_movil(request):
    if request.method == 'POST':
        form = IncidenciaMovilForm(request.POST)
        if form.is_valid():
            # 1. Guardamos la incidencia en la base de datos
            incidencia = form.save(commit=False)
            
            # Detectamos si marcó la opción móvil de cliente ausente
            accion = form.cleaned_data.get('causa_reenvio')
            if accion == 'cliente_ausente':
                incidencia.tipo = 'Media' # O la gravedad que definas
                if not incidencia.descripcion:
                    incidencia.descripcion = "El cliente no estaba en su casa. Pedido programado para reenvío."
                
                # 2. Modificamos el estado del pedido relacionado (Movimiento)
                pedido = incidencia.movimiento
                pedido.estado = 'Reenviado' # O 'En Retorno' según tus Choices de Movimiento
                pedido.save()
            
            incidencia.save()
            return redirect('listado_incidencias')
    else:
        form = IncidenciaMovilForm()
        
    return JsonResponse({'status': 'success', 'message': 'Guardado'})