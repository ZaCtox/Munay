from http.client import HTTPResponse
from django.http import HttpResponseBadRequest, JsonResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
import logging, pytz
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Case, When, Value, BooleanField #para ordenar de forma ascendente
from django.db import transaction
from django.db.models import Q #filtra textos ignorando mayusculas y minisculas
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import  timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from administracion.Carrito import Carrito
from django.views.decorators.http import require_POST
from urllib.parse import urlencode
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout  





# Create your views here.

def index(request):#está listo
    # Obtener todos los slides existentes
    slides = Slide.objects.all()
    return render(request, 'index.html', {'slides': slides})

def productos(request):#está listo
    category = request.GET.get('category')
    
    # Obtener todos los snacks y tortas ordenados por stock (ascendente)
    snacks = Snack.objects.annotate(
        has_stock=Case(
            When(stock__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('-has_stock', 'nombre')
    
    tortas = Torta.objects.annotate(
        has_stock=Case(
            When(stock__gt=0, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('-has_stock', 'nombre')
    
    if category:
        if category == 'Snack':
            snacks = snacks.filter(tipo='Snack')
            tortas = []
        elif category == 'Torta':
            snacks = []
            tortas = tortas.filter(tipo='Torta')

    return render(request, 'productos.html', {'snacks': snacks, 'tortas': tortas})

def buscar_producto(request):#está listo
    if 'search' in request.GET:
        query = request.GET['search']
        # Filtrar snacks y tortas que contengan el término de búsqueda en su nombre
        snacks = Snack.objects.filter(nombre__icontains=query)
        tortas = Torta.objects.filter(nombre__icontains=query)
    else:
        snacks = Snack.objects.all()
        tortas = Torta.objects.all()

    return render(request, 'productos.html', {'snacks': snacks, 'tortas': tortas})

def detalles_snack(request, producto_id):#está listo
    producto = Snack.objects.get(pk=producto_id)

    sin_stock = producto.stock <= 0
    
    return render(request, 'detalles_snack.html', {'producto': producto, 'sin_stock': sin_stock})

def detalles_torta(request, producto_id):#está listo
    producto = Torta.objects.get(pk=producto_id)

    sin_stock = producto.stock <= 0

    return render(request, 'detalles_torta.html', {'producto': producto, 'sin_stock': sin_stock})

@require_POST
def agregar_al_carrito(request):#está listo
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad_str = request.POST.get('cantidad')
        tipo_producto = request.POST.get('tipo')  # Agregar el tipo de producto (Snack o Torta)
        opcion_str = request.POST.get('opcion')  # cambio de precio

        try:
            cantidad = int(cantidad_str)
            opcion = float(opcion_str)  # Convertir el precio a un número flotante
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser un número positivo.")
        except (ValueError, TypeError):
            return JsonResponse({'mensaje': 'Error: La cantidad seleccionada no es válida.'}, status=400)

        # Obtener el producto según su tipo
        if tipo_producto == 'Snack':
            producto_model = Snack
        elif tipo_producto == 'Torta':
            producto_model = Torta
        else:
            return JsonResponse({'mensaje': 'Error: Tipo de producto no válido.'}, status=400)

        producto = get_object_or_404(producto_model, pk=producto_id)

        if tipo_producto == 'Snack':
            if producto.precio != opcion:
                producto.nombre += " (Promo por 2 Unidades)"

        # Asignar el precio al producto antes de almacenarlo en el carrito
        producto.precio = opcion

        if tipo_producto == 'Torta':
             if producto.precio < 20000:
                 producto.nombre += " (7 Personas)"
             elif producto.precio >= 20000 and producto.precio < 30000:
                 producto.nombre += " (14 Personas)"
             elif producto.precio >= 30000:
                 producto.nombre += " (24 Personas)"

        # Crear un identificador único para el producto en el carrito
        producto_carrito_id = f"{producto_id}-{opcion}"  # Utiliza una combinación de id y precio

        if 'carrito' not in request.session:
            request.session['carrito'] = {}

        carrito = request.session['carrito']
        if producto_carrito_id in carrito:
            carrito[producto_carrito_id]['cantidad'] += cantidad
        else:
            carrito[producto_carrito_id] = {
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': cantidad,
                'imagen': producto.imagen.url
            }

        request.session.modified = True

        return redirect('productos')

    return redirect('productos')

def limpiar_carrito(request):#está listo
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect('pedido')

def obtener_carrito(request):#está listo
    carrito = request.session.get('carrito', {})
    total_carrito = 0

    for producto_id, producto_info in carrito.items():
        producto_info['precio_total'] = producto_info['precio'] * producto_info['cantidad']
        total_carrito += producto_info['precio_total']

    total_carrito = int(total_carrito)
    
    return carrito, total_carrito

@require_POST
def sumar_stock_carrito(request, producto_id):#está listo
    carrito = Carrito(request)
    try:
        producto = Snack.objects.get(pk=producto_id)
    except Snack.DoesNotExist:
        try:
            producto = Torta.objects.get(pk=producto_id)
        except Torta.DoesNotExist:
            return redirect('pedido')  # O redirige a una página de error

    carrito.agregar(producto)
    return redirect('pedido')

@require_POST
def restar_stock_carrito(request, producto_id):#está listo
    carrito = Carrito(request)
    try:
        producto = Snack.objects.get(pk=producto_id)
    except Snack.DoesNotExist:
        try:
            producto = Torta.objects.get(pk=producto_id)
        except Torta.DoesNotExist:
            return redirect('pedido')  # O redirige a una página de error

    carrito.restar(producto)
    return redirect('pedido')

@require_POST
def eliminar_producto_carrito(request, producto_id):#está listo
    carrito = Carrito(request)
    
    try:
        producto_snack = Snack.objects.get(pk=producto_id)
        carrito.eliminar(producto_snack)
        return redirect('pedido')
    except Snack.DoesNotExist:
        pass
    
    try:
        producto_torta = Torta.objects.get(pk=producto_id)
        carrito.eliminar(producto_torta)
        return redirect('pedido')
    except Torta.DoesNotExist:
        pass
    
    return redirect('pedido')

def pedido(request):#está listo
    costos_sectores = CostoSector.objects.all()

    if request.method == 'POST':
        # Procesar el formulario cuando se envíe
        nombre_apellido = request.POST.get('nombre_apellido', '')
        telefono = request.POST.get('telefono', '')
        forma_entrega = request.POST.get('forma_entrega', '')
        forma_pago = request.POST.get('forma_pago', '')
        
        # Verificar que se haya ingresado nombre y apellido
        if not nombre_apellido:
            return HTTPResponse('Por favor, ingresa tu nombre y apellido.')

        # Obtener el carrito y el total del carrito
        carrito, total_carrito = obtener_carrito(request)
        
        # Obtener el nombre del sector seleccionado del formulario
        nombre_sector = request.POST.get('sector', '')
        # Obtener el costo del sector seleccionado si existe
        costo_sector_seleccionado = CostoSector.objects.filter(nombre=nombre_sector).values_list('costo', flat=True).first()
        
        if costo_sector_seleccionado is not None:
            # Calcular el precio final del pedido
            if forma_entrega == 'Lo retiro personalmente':
                precio_final = total_carrito
            else:
                precio_final = total_carrito + costo_sector_seleccionado
            
            # Resto del código para generar el mensaje de WhatsApp y el enlace de redireccionamiento

            
            # Formatear el mensaje de WhatsApp con todos los datos del carrito, la información del usuario y el precio final
            mensaje_whatsapp = f"¡Hola! Te envío el resumen de mi pedido:\n\n"
            for producto_id, producto_info in carrito.items():
                mensaje_whatsapp += f"*Producto: {producto_info['nombre']}\n*"
                mensaje_whatsapp += f"Cantidad: {producto_info['cantidad']}\n"
                mensaje_whatsapp += f"Precio: {producto_info['precio_total']}\n\n"
            
            mensaje_whatsapp += f"Nombre: {nombre_apellido}\n"
            mensaje_whatsapp += f"Teléfono: {telefono}\n"
            mensaje_whatsapp += f"Forma de entrega: {forma_entrega}\n"
            mensaje_whatsapp += f"Forma de Pago: {forma_pago}\n\n"
            mensaje_whatsapp += f"*Precio Total: {precio_final}*"

            if forma_entrega == 'Necesito que me lo envíen':
                direccion = request.POST.get('direccion', '')
                es_departamento = request.POST.get('es_departamento', '')
                numero_departamento = request.POST.get('numero_departamento', '') if es_departamento else ''
                
                mensaje_whatsapp += f"\nDirección: {direccion}\n"
                mensaje_whatsapp += f"\nSector: {nombre_sector}\n"
                if es_departamento:
                    mensaje_whatsapp += f"Es un departamento con número: {numero_departamento}\n"
                else:
                    mensaje_whatsapp += "\n"

            whatsapp_params = {'text': mensaje_whatsapp}
            whatsapp_link = 'https://wa.me/56972023761?' + urlencode(whatsapp_params)
            
            return redirect(whatsapp_link)
        else:
            return HTTPResponse('El sector seleccionado no tiene un costo asociado.')

    # Obtener el carrito y el total del carrito
    carrito, total_carrito = obtener_carrito(request)

    return render(request, 'pedido.html', {'total_carrito': total_carrito, 'costos_sectores': costos_sectores})

# terminamos de trabajar con funciones del carrito

def quienes_somos(request):#está listo
    return render(request, 'quienes_somos.html', {})

def contactanos(request):#está listo
    return render(request, 'contactanos.html', {})

@login_required#está listo
def administracion(request):
    return render(request, 'administracion.html', {})

@login_required
def admin_producto(request):#está listo
    snacks = Snack.objects.all()
    tortas = Torta.objects.all()

    if request.method == 'POST':
        # Recibir los datos del formulario
        imagen = request.FILES.get('imagen')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        tipo = request.POST.get('tipo')


        # Validar los campos y guardar el producto correspondiente
        if tipo == 'Snack':
            if nombre and descripcion and precio and stock and imagen:
                descuento_2da_unidad = request.POST.get('descuento_2da_unidad')
                nuevo_snack = Snack(nombre=nombre, descripcion=descripcion, precio=precio,
                                    descuento_2da_unidad=descuento_2da_unidad, stock=stock, imagen=imagen)
                nuevo_snack.save()
                return redirect('admin_producto')
            else:
                return render(request, 'admin_producto.html', {'error': 'Todos los campos son obligatorios'})
        elif tipo == 'Torta':
            precio_15p = request.POST.get('precio_15p')
            precio_24p = request.POST.get('precio_24p')
            if nombre and descripcion and precio and stock and imagen:
                nueva_torta = Torta(nombre=nombre, descripcion=descripcion, precio=precio,
                                    precio_15p=precio_15p, precio_24p=precio_24p, stock=stock, imagen=imagen)
                nueva_torta.save()
                return redirect('admin_producto')
            else:
                return render(request, 'admin_producto.html', {'error': 'Todos los campos son obligatorios'})
        else:
            return render(request, 'admin_producto.html', {'error': 'Tipo de producto no válido'})

    return render(request, 'admin_producto.html', {'snacks': snacks, 'tortas': tortas})

@login_required
def aumentar_stock_snack(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Snack.objects.get(pk=producto_id)
        producto.stock += 1
        producto.save()
        return redirect('admin_producto')

@login_required
def aumentar_stock_torta(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Torta.objects.get(pk=producto_id)
        producto.stock += 1
        producto.save()
        return redirect('admin_producto')

@login_required
def disminuir_stock_snack(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Snack.objects.get(pk=producto_id)
        if producto.stock > 0:
            producto.stock -= 1
            producto.save()
        return redirect('admin_producto')

@login_required
def disminuir_stock_torta(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Torta.objects.get(pk=producto_id)
        if producto.stock > 0:
            producto.stock -= 1
            producto.save()
        return redirect('admin_producto')

@login_required
def eliminar_snack(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Snack.objects.get(id=producto_id)
        producto.delete()
        return redirect('admin_producto')
    return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

@login_required
def eliminar_torta(request, producto_id):#está listo
    if request.method == 'POST':
        producto = Torta.objects.get(id=producto_id)
        producto.delete()
        return redirect('admin_producto')
    return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

@login_required
def editar_snack(request, producto_id):#está listo
    if request.method == 'POST':
        # Obtener el producto a editar
        producto = Snack.objects.get(id=producto_id)
        
        # Actualizar los campos con los datos enviados por el formulario
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.stock = request.POST.get('stock')
        producto.precio = request.POST.get('precio')
        producto.descuento_2da_unidad = request.POST.get('descuento_2da_unidad')
        
        # Guardar los cambios en la base de datos
        producto.save()
        
        # Redirigir a alguna vista de éxito
        messages.success(request, 'Producto editado exitosamente', extra_tags='message-success')
        return redirect('admin_producto')

    # En caso de que el método de solicitud no sea POST, redirigir a alguna vista de error o a donde corresponda
    return redirect('index')

@login_required
def editar_torta(request, producto_id):#está listo
    if request.method == 'POST':
        # Obtener el producto a editar
        producto = Torta.objects.get(id=producto_id)
        
        # Actualizar los campos con los datos enviados por el formulario
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.stock = request.POST.get('stock')
        producto.precio = request.POST.get('precio')
        producto.precio_15p = request.POST.get('precio_15p')
        producto.precio_24p = request.POST.get('precio_24p')
        
        # Guardar los cambios en la base de datos
        producto.save()
        
        # Redirigir a alguna vista de éxito
        messages.success(request, 'Producto editado exitosamente', extra_tags='message-success')
        return redirect('admin_producto')

    # En caso de que el método de solicitud no sea POST, redirigir a alguna vista de error o a donde corresponda
    return redirect('index')

# aqui termina admin productos

@login_required
def clientes(request):#está listo
    costos_sectores = CostoSector.objects.all()
    filtro_nombre = request.GET.get('filtro_nombre', '')

    if filtro_nombre:
        # Filtra los clientes por nombre usando el operador OR en caso de que el nombre contenga varios términos separados por espacios
        terminos_busqueda = filtro_nombre.split()  # Dividir los términos de búsqueda
        condiciones = Q()  # Inicializar una condición vacía

        for termino in terminos_busqueda:
            # Agregar cada término como una condición OR para buscar coincidencias parciales en el nombre del cliente
            condiciones |= Q(nombre__icontains=termino)

        # Aplicar las condiciones de búsqueda
        clientes = Cliente.objects.filter(condiciones)
    else:
        # Si no se proporciona un filtro, muestra todos los clientes
        clientes = Cliente.objects.all()

    if request.method == "POST":
        form = request.POST
        rut = form.get('rutR')
        telefono = form.get('telefonoR')

        # Verificar si el campo rut no está en blanco y si ya existe un cliente con el mismo Rut
        if rut and Cliente.objects.filter(rut=rut).exists():
            messages.error(request, f"El Rut {rut} ya está registrado.")
        elif telefono and Cliente.objects.filter(telefono=telefono).exists():
            messages.error(request, f"El número de teléfono {telefono} ya está registrado.")
        else:
            # Si no existe o el campo rut está en blanco, guardar el nuevo cliente en la base de datos
            cliente = Cliente(
                rut=rut,
                nombre=form.get('nombreR'),
                telefono=telefono,
                direccion=form.get('direccionR'),
                numero_casa=form.get('numeroR'),
                sector=form.get('sectorR'),
            )
            cliente.save()
            messages.success(request, "Cliente agregado exitosamente!")  # Mostrar mensaje de éxito después de guardar el cliente

    return render(request, 'contabilidad/clientes.html', {'clientes': clientes, 'filtro_nombre': filtro_nombre, 'costos_sectores':costos_sectores})

@login_required
def eliminar_cliente(request, cliente_id):#está listo
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        # Eliminar al cliente de la base de datos
        cliente.delete()
        # Redirigir a la página de clientes después de la eliminación
        return redirect('clientes')
    # Si no se recibe una solicitud POST, mostrar una página de confirmación de eliminación
    return render(request, 'confirmar_eliminar_cliente.html', {'cliente': cliente})

@login_required
def proveedores(request):#está listo
    filtro_nombre = request.GET.get('filtro_nombre', '')

    if filtro_nombre:
        # Filtra los proveedores por nombre usando el operador OR en caso de que el nombre contenga varios términos separados por espacios
        terminos_busqueda = filtro_nombre.split()  # Dividir los términos de búsqueda
        condiciones = Q()  # Inicializar una condición vacía

        for termino in terminos_busqueda:
            # Agregar cada término como una condición OR para buscar coincidencias parciales en el nombre del cliente
            condiciones |= Q(nombre__icontains=termino)

        # Aplicar las condiciones de búsqueda
        proveedores = Proveedor.objects.filter(condiciones)
    else:
        # Si no se proporciona un filtro, muestra todos los proveedores
        proveedores = Proveedor.objects.all()

    if request.method == "POST":
        form = request.POST
        rut = form.get('rutR')
        telefono = form.get('telefonoR')
        
        # Verificar si algún campo está vacío
        if rut and Proveedor.objects.filter(rut=rut).exists():
            messages.error(request, f"El Rut {rut} ya está registrado.")
        elif telefono and Proveedor.objects.filter(telefono=telefono).exists():
            messages.error(request, f"El número de teléfono {telefono} ya está registrado.")
        else:
            # Crear el proveedor si los campos no están vacíos
            proveedor = Proveedor(
                rut=rut,
                nombre=form.get('nombreR'),
                telefono=telefono,
            )
            proveedor.save()
            messages.success(request, "Proveedor agregado exitosamente!")  # Mostrar mensaje de éxito después de guardar el proveedor
    
    return render(request, 'contabilidad/proveedores.html', {'proveedores': proveedores, 'filtro_nombre': filtro_nombre})

@login_required
def eliminar_proveedor(request, proveedor_id):#está listo
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    if request.method == 'POST':
        # Eliminar al proveedor de la base de datos
        proveedor.delete()
        # Redirigir a la página de proveedores después de la eliminación
        return redirect('proveedores')
    return render(request, 'confirmar_eliminar_proveedor.html', {'proveedor': proveedor})

@login_required
def ventas(request):#está listo
    costos_sectores = CostoSector.objects.all()

    filtro = request.GET.get('filtro', 'diario')

    fecha_actual_chile = timezone.now().astimezone(pytz.timezone('America/Santiago'))

    if filtro == 'diario':
        fecha_inicio = fecha_actual_chile.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_actual_chile.replace(hour=23, minute=59, second=59, microsecond=999999)

    elif filtro == 'semanal':
        dia_semana = fecha_actual_chile.weekday()
        fecha_inicio = fecha_actual_chile - timedelta(days=dia_semana)
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    elif filtro == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=31)

    if request.method == "POST":
        cliente_id = request.POST.get('clienteR')
        forma_de_pago = request.POST.get('forma_de_pagoR')
        productos_ids = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        tamanios = request.POST.getlist('tamanios')  # Obtener los tamaños seleccionados para las tortas
        costo_sector = request.POST.get('costo_sectorR')
        monto_total_str = request.POST.get('montoR')


        if not all([cliente_id, forma_de_pago, monto_total_str, productos_ids, cantidades]):
            messages.error(request, "Por favor, complete todos los campos.")
            return redirect('ventas')

        try:
            monto_total = int(monto_total_str)
        except ValueError:
            messages.error(request, "El monto total ingresado no es válido.")
            return redirect('ventas')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        try:
            with transaction.atomic():
                venta = Venta(cliente=cliente, forma_de_pago=forma_de_pago, costo_sector=costo_sector, monto_total=monto_total)
                venta.save()

                for producto_id, cantidad in zip(productos_ids, cantidades):
                    tipo_producto, id_real = producto_id.split('_', 1)

                    if tipo_producto == 'snack':
                        producto = get_object_or_404(Snack, pk=id_real)
                    elif tipo_producto == 'torta':
                        producto = get_object_or_404(Torta, pk=id_real)
                        cantidad_por_producto = 1  # Cantidad fija para tortas
                    else:
                        logger.error("Tipo de producto no válido para el ID: %s", producto_id)
                        messages.error(request, "Tipo de producto no válido.")
                        return redirect('ventas')

                    cantidad_por_producto = int(cantidad)

                    if tipo_producto == 'snack':
                        detalle_venta = DetalleVenta(venta=venta, producto=producto, cantidad=cantidad_por_producto)
                        detalle_venta.save()

                    elif tipo_producto == 'torta':
                        persona= tamanios[0]
                        detalle_venta = DetalleVenta(venta=venta, producto=producto, cantidad=cantidad_por_producto,tamaño=persona)
                        detalle_venta.save()

                    producto.stock -= cantidad_por_producto
                    producto.save()

                messages.success(request, "Venta agregada exitosamente.")
                return redirect('ventas')
        except Exception as e:
            messages.error(request, "Ocurrió un error al procesar la venta.")
            return redirect('ventas')
    else:
        ventas = Venta.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
        clientes = Cliente.objects.all()
        snacks = Snack.objects.all()
        tortas = Torta.objects.all()

        return render(request, 'contabilidad/ventas.html', {'ventas': ventas, 'clientes': clientes, 'snacks': snacks, 'tortas': tortas, 'filtro': filtro, 'costos_sectores': costos_sectores})

@login_required    
def grafico_ventas_gastos(request): #está listo
    # Obtener el filtro seleccionado del formulario (predeterminado: diario)
    filtro = request.GET.get('filtro', 'diario')

    # Obtener la fecha actual en la zona horaria de Chile
    fecha_actual_chile = timezone.now().astimezone(pytz.timezone('America/Santiago'))

    # Definir los límites de fechas según el filtro seleccionado
    if filtro == 'diario':
        fecha_inicio = fecha_actual_chile.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_actual_chile.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif filtro == 'semanal':
        # Obtener el día de la semana (0 para lunes, 6 para domingo)
        dia_semana = fecha_actual_chile.weekday()

        # Restar los días necesarios para llegar al lunes y ajustar la hora a las 00:00
        fecha_inicio = fecha_actual_chile - timedelta(days=dia_semana)
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)

        # Sumar los días restantes de la semana y ajustar la hora a las 23:59
        fecha_fin = fecha_inicio + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    elif filtro == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=31)

    # Obtener los datos de los gastos y las ventas según el filtro seleccionado
    gastos = Gasto.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
    ventas = Venta.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Calcular los totales de gastos y ventas
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_ventas = ventas.aggregate(Sum('monto_total'))['monto_total__sum'] or 0

    # Calcular la diferencia entre ventas y gastos
    diferencia = total_ventas - total_gastos

    # Crear etiquetas y datos para el gráfico
    labels = ['Gastos', 'Ventas']
    sizes = [total_gastos, total_ventas]
    colors = ['#ff0000', '#008000']  # Rojo para gastos, verde para ventas

    # Crear el gráfico de torta con Plotly
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, marker=dict(colors=colors))])

    # Configurar el tamaño del gráfico
    fig.update_layout(
        autosize=True,  # Habilita el ajuste automático del tamaño
        margin=dict(l=0, r=0, t=0, b=0),  # Configura los márgenes del gráfico
        width=None,  # Ancho del gráfico
        height=None,  # Alto del gráfico
    )

    graph_html = plot(fig, output_type='div')

    # Renderizar la plantilla con el gráfico incrustado y el formulario de filtro
    return render(request, 'contabilidad/estadisticas.html', {'graph_html': graph_html, 'filtro': filtro, 'total_ganancias': total_ventas, 'total_gastos': total_gastos, 'diferencia': diferencia})

@login_required
def editar_producto(request, producto_id):#dudoso
    # Lógica para editar el producto con el ID dado
    return HttpResponse(f"Editando el producto con ID: {producto_id}")

@login_required
def eliminar_venta(request, venta_id):#está listo
    venta = get_object_or_404(Venta, pk=venta_id)
    
    if request.method == "POST":
        venta.delete()
        return redirect('ventas')
    else:
        # Handle GET request if needed
        pass

@login_required
def gastos(request):#está listo
    if request.method == "POST":
        form = request.POST
        gasto = Gasto(
            proveedor = Proveedor.objects.get(pk=form.get('proveedorR')),
            descripcion = form.get('descripcionR'),
            tipo = form.get('tipoR'),
            forma_de_pago = form.get('forma_de_pagoR'),
            monto = form.get('montoR'),
        )
        gasto.save()
        gastos = Gasto.objects.all()  # Obtener todos los gastos después de guardar el nuevo gasto
    else:
        gastos = Gasto.objects.all()  # Obtener todos los gastos en caso de una solicitud GET

    # Filtrar los gastos por fechas
    filtro = request.GET.get('filtro', 'diario')

    # Obtener la fecha actual en la zona horaria de Chile
    fecha_actual_chile = timezone.now().astimezone(pytz.timezone('America/Santiago'))

    # Definir los límites de fechas según el filtro seleccionado
    if filtro == 'diario':
        fecha_inicio = fecha_actual_chile.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_actual_chile.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif filtro == 'semanal':
        # Obtener el día de la semana (0 para lunes, 6 para domingo)
        dia_semana = fecha_actual_chile.weekday()

        # Restar los días necesarios para llegar al lunes y ajustar la hora a las 00:00
        fecha_inicio = fecha_actual_chile - timedelta(days=dia_semana)
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)

        # Sumar los días restantes de la semana y ajustar la hora a las 23:59
        fecha_fin = fecha_inicio + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    elif filtro == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=31)

    # Filtrar los gastos por las fechas definidas
    gastos = gastos.filter(fecha__range=[fecha_inicio, fecha_fin])

    ganancias_diarias = Gasto.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Convertir la fecha a la zona horaria de Chile antes de pasarla al contexto


    proveedores = Proveedor.objects.all()  # Obtener todos los proveedores
    return render(request, 'contabilidad/gastos.html', {'gastos': gastos, 'proveedores': proveedores, 'ganancias_diarias': ganancias_diarias, 'filtro': filtro})

@login_required
def eliminar_gasto(request, gasto_id):#está listo
    gasto = get_object_or_404(Gasto, pk=gasto_id)

    if request.method == "POST":
        gasto.delete()
        return redirect('gastos')
    else:
        # Handle GET request if needed
        pass

@login_required
def productos_vendidos(request):#está listo
    filtro = request.GET.get('filtro', 'diario')

    # Obtener la fecha actual en la zona horaria de Chile
    fecha_actual_chile = timezone.now().astimezone(pytz.timezone('America/Santiago'))

    # Definir los límites de fechas según el filtro seleccionado
    if filtro == 'diario':
        fecha_inicio = fecha_actual_chile.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_actual_chile.replace(hour=23, minute=59, second=59, microsecond=999999)
        
    elif filtro == 'semanal':
        # Obtener el día de la semana (0 para lunes, 6 para domingo)
        dia_semana = fecha_actual_chile.weekday()

        # Restar los días necesarios para llegar al lunes y ajustar la hora a las 00:00
        fecha_inicio = fecha_actual_chile - timedelta(days=dia_semana)
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)

        # Sumar los días restantes de la semana y ajustar la hora a las 23:59
        fecha_fin = fecha_inicio + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    elif filtro == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=31)

    # Obtener los detalles de venta según el filtro seleccionado
    detalles_venta = DetalleVenta.objects.filter(venta__fecha__range=[fecha_inicio, fecha_fin]) 

    # Pasar el filtro y los detalles de la venta al template
    return render(request, 'contabilidad/productos_vendidos.html', {'detalles_venta': detalles_venta, 'filtro': filtro, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})

@login_required
def admin_contabilidad(request):#está listo
    return render(request, 'admin_contabilidad.html',{})
 
@login_required
def cliente_agregado(request):#revisar
    messages.success(request, 'Cliente agregado exitosamente.')
    return redirect('admin_contabilidad')

@login_required
def proveedor_agregado(request):#revisar
    messages.success(request, 'Proveedor agregado exitosamente.')
    return redirect('admin_contabilidad')

@login_required
def agregar_precios(request):#está listo
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        costo = request.POST.get('costo')
        CostoSector.objects.create(nombre=nombre, costo=costo)
        messages.success(request, '¡Sector agregado correctamente!')
        return redirect('precios_sector')  # Redirige al nombre de la URL

    precios_sectores = CostoSector.objects.all()
    return render(request, 'contabilidad/precios_sector.html', {'precios_sectores': precios_sectores})

@login_required
def editar_sector(request, costosector_id): #está listo
    sector = CostoSector.objects.get(id=costosector_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        costo = request.POST.get('costo')

        sector.nombre = nombre
        sector.costo = costo
        sector.save()

        return redirect('precios_sector')

    return render(request, 'contabilidad/precios_sector.html', {'sector': sector})

@login_required
def eliminar_sector(request, id):#está listo
    # Obtener el objeto CostoSector a eliminar
    costo_sector = CostoSector.objects.get(id=id)
    if request.method == 'POST':
        costo_sector.delete()
        messages.error(request, "Sector eliminado correctamente.")
        return redirect('precios_sector')  # Redirige a la página deseada después de eliminar el sector
    else:
        messages.error(request, "Error al eliminar el sector. Método de solicitud no válido.")
        return redirect('contabilidad/precios_sector.html')  # Redirige a la página deseada en caso de error o solicitud incorrecta

#aqui termina todo lo de contabilidad

#aqui empieza la administracion del inicio
    
@login_required
def admin_info_inicio(request):#está listo
    # Obtener todos los slides existentes
    slides = Slide.objects.all()

    # Obtener todos los snacks y tortas
    snacks = Snack.objects.all()
    tortas = Torta.objects.all()

    context = {
        'slides': slides,
        'snacks': snacks,
        'tortas': tortas,
    }

    return render(request, 'admin_info_inicio.html', context)

def salir(request):#está listo
    logout(request)
    return redirect('index')  # Redirigir a la página principal u otra página después de cerrar sesión

@login_required
def guardar_slide(request):#está listo
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        imagen = request.FILES['imagen']
        producto_url = request.POST.get('producto_id')
        boton_texto = request.POST.get('boton_texto')

        # Verifica si el URL es el específico que deseas
        if producto_url == 'https://wa.me/56972023761':
            oferta = request.POST.get('oferta')
        else:
            oferta = None


        slide = Slide.objects.create(
            title=title,
            content=content,
            imagen=imagen,
            urls=producto_url,
            boton_texto=boton_texto,
            oferta=oferta,
        )
        slide.save()
        
        messages.success(request, "Slide agregada exitosamente.")  # Configura el mensaje de éxito   
        return redirect('admin_info_inicio')
    return render(request, 'admin_info_inicio.html')

@login_required
def editar_slide(request, slide_id):#está listo
    slide = Slide.objects.get(id=slide_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        imagen = request.FILES.get('imagen')  # Cambiar a get para evitar errores si no se proporciona la imagen
        
        # Obtener los valores de producto_id y boton_texto desde el formulario
        producto_id = request.POST.get('producto_id')
        boton_texto = request.POST.get('boton_texto')
        
        # Asignar los valores actualizados al objeto Slide
        slide.title = title
        slide.content = content
        if imagen:
            slide.imagen = imagen
        
        # Guardar el valor de producto_id en el campo urls de Slide
        slide.urls = producto_id
        
        # Guardar el valor de boton_texto en el campo boton_texto de Slide
        slide.boton_texto = boton_texto

        # Verificar si el URL es el específico que deseas
        if producto_id == 'https://wa.me/56972023761':
            oferta = request.POST.get('oferta')
        else:
            oferta = None

        slide.oferta = oferta  # Asignar el valor de oferta
        
        slide.save()
        return redirect('admin_info_inicio')
    return render(request, 'admin_info_inicio.html', {'slide': slide})

@login_required
def eliminar_slide(request, slide_id):#está listo
    if request.method == 'POST':
        slide = Slide.objects.get(id=slide_id)
        slide.delete()
        return redirect('admin_info_inicio')