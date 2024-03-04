from django.http import HttpResponseBadRequest, JsonResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
import logging, pytz
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db import transaction
from django.db.models import Q #filtra textos ignorando mayusculas y minisculas
import logging, json
import matplotlib.pyplot as plt
import base64, io
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from administracion.Carrito import Carrito
from django.views.decorators.http import require_POST
from urllib.parse import urlencode




# Create your views here.

def index(request):
    return render(request, 'index.html', {})


def productos(request):
    category = request.GET.get('category')
    snacks = Snack.objects.all()
    tortas = Torta.objects.all()
    
    if category:
        if category == 'Snack':
            snacks = Snack.objects.all()
            tortas = []
        elif category == 'Torta':
            snacks = []
            tortas = Torta.objects.all()

    return render(request, 'productos.html', {'snacks': snacks, 'tortas': tortas})

def buscar_producto(request):
    if 'search' in request.GET:
        query = request.GET['search']
        # Filtrar snacks y tortas que contengan el término de búsqueda en su nombre
        snacks = Snack.objects.filter(nombre__icontains=query)
        tortas = Torta.objects.filter(nombre__icontains=query)
    else:
        snacks = Snack.objects.all()
        tortas = Torta.objects.all()

    return render(request, 'productos.html', {'snacks': snacks, 'tortas': tortas})

def detalles_snack(request, producto_id):
    producto = Snack.objects.get(pk=producto_id)
    precio_doble = producto.precio * 2
    precio_2da_unidad = producto.precio + (producto.precio - producto.descuento_2da_unidad)
    return render(request, 'detalles_snack.html', {'producto': producto, 'precio_doble': precio_doble, 'precio_2da_unidad': precio_2da_unidad})

def detalles_torta(request, producto_id):
    producto = Torta.objects.get(pk=producto_id)
    return render(request, 'detalles_torta.html', {'producto': producto})


# estamos trabajando con el carritooooooooooooooooooooooooooooooooooooooooooooooooooooooo

@require_POST
def agregar_al_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad_str = request.POST.get('cantidad')
        tipo_producto = request.POST.get('tipo')  # Agregar el tipo de producto (Snack o Torta)

        try:
            cantidad = int(cantidad_str)
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

        if 'carrito' not in request.session:
            request.session['carrito'] = {}
        
        carrito = request.session['carrito']
        if producto_id in carrito:
            carrito[producto_id]['cantidad'] += cantidad
        else:
            carrito[producto_id] = {
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': cantidad,
                'imagen': producto.imagen.url
            }


        request.session.modified = True

        return redirect('productos')

    return redirect('productos')


def limpiar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect('pedido')


def obtener_carrito(request):
    carrito = request.session.get('carrito', {})
    total_carrito = 0

    for producto_id, producto_info in carrito.items():
        producto_info['precio_total'] = producto_info['precio'] * producto_info['cantidad']
        total_carrito += producto_info['precio_total']

    total_carrito = int(total_carrito)
    
    return carrito, total_carrito


def pedido(request):
    if request.method == 'POST':
        # Procesar el formulario cuando se envíe
        nombre_apellido = request.POST.get('nombre_apellido', '')
        telefono = request.POST.get('telefono', '')
        forma_entrega = request.POST.get('forma_entrega', '')
        
        # Verificar que se haya ingresado nombre y apellido
        if not nombre_apellido:
            # Aquí puedes manejar el caso de que no se haya ingresado el nombre y apellido
            pass
        
        # Obtener el carrito y el total del carrito
        carrito, total_carrito = obtener_carrito(request)
        
        # Formatear el mensaje de WhatsApp con todos los datos del carrito y la información del usuario
        mensaje_whatsapp = f"¡Hola! Te envío el resumen de mi pedido:\n\n"
        for producto_id, producto_info in carrito.items():
            mensaje_whatsapp += f"Producto: {producto_info['nombre']}\n"
            mensaje_whatsapp += f"Cantidad: {producto_info['cantidad']}\n"
            mensaje_whatsapp += f"Precio total: {producto_info['precio_total']}\n\n"
        
        # Agregar nombre, teléfono y forma de entrega al mensaje de WhatsApp
        mensaje_whatsapp += f"Nombre: {nombre_apellido}\n"
        mensaje_whatsapp += f"Teléfono: {telefono}\n"
        mensaje_whatsapp += f"Forma de entrega: {forma_entrega}"
        
        # Construir el enlace de WhatsApp con el mensaje por defecto
        whatsapp_params = {
            'text': mensaje_whatsapp
        }
        whatsapp_link = 'https://wa.me/56972023761?' + urlencode(whatsapp_params)
        
        # Redirigir al enlace de WhatsApp
        return redirect(whatsapp_link)

    # Obtener el carrito y el total del carrito
    carrito, total_carrito = obtener_carrito(request)

    return render(request, 'pedido.html', {'total_carrito': total_carrito}) 





# terminamos de trabajar con el carritooooooooooooooooooooooooooooooooooooooooooooooooooo

def quienes_somos(request):
    return render(request, 'quienes_somos.html', {})


def contactanos(request):
    return render(request, 'contactanos.html', {})


def administracion(request):
    return render(request, 'administracion.html', {})





def admin_producto(request):
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

def aumentar_stock_snack(request, producto_id):
    if request.method == 'POST':
        producto = Snack.objects.get(pk=producto_id)
        producto.stock += 1
        producto.save()
        return redirect('admin_producto')
    
def aumentar_stock_torta(request, producto_id):
    if request.method == 'POST':
        producto = Torta.objects.get(pk=producto_id)
        producto.stock += 1
        producto.save()
        return redirect('admin_producto')
    
def disminuir_stock_snack(request, producto_id):
    if request.method == 'POST':
        producto = Snack.objects.get(pk=producto_id)
        if producto.stock > 0:
            producto.stock -= 1
            producto.save()
        return redirect('admin_producto')

def disminuir_stock_torta(request, producto_id):
    if request.method == 'POST':
        producto = Torta.objects.get(pk=producto_id)
        if producto.stock > 0:
            producto.stock -= 1
            producto.save()
        return redirect('admin_producto')

def eliminar_snack(request, producto_id):
    if request.method == 'POST':
        producto = Snack.objects.get(id=producto_id)
        producto.delete()
        return redirect('admin_producto')
    return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

def eliminar_torta(request, producto_id):
    if request.method == 'POST':
        producto = Torta.objects.get(id=producto_id)
        producto.delete()
        return redirect('admin_producto')
    return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

def editar_snack(request, producto_id):
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

def editar_torta(request, producto_id):
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


def admin_info_inicio(request):
    return render(request, 'admin_info_inicio.html', {})



#aqui empieza todo lo de contabilidad
def clientes(request):
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
                barrio=form.get('barrioR'),
            )
            cliente.save()
            messages.success(request, "Cliente agregado exitosamente!")  # Mostrar mensaje de éxito después de guardar el cliente
    clientes = Cliente.objects.all()
    return render(request, 'contabilidad/clientes.html', {'clientes': clientes})

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        # Eliminar al cliente de la base de datos
        cliente.delete()
        # Redirigir a la página de clientes después de la eliminación
        return redirect('clientes')
    # Si no se recibe una solicitud POST, mostrar una página de confirmación de eliminación
    return render(request, 'confirmar_eliminar_cliente.html', {'cliente': cliente})


def proveedores(request):
    if request.method == "POST":
        form = request.POST
        rut = form.get('rutR')
        nombre = form.get('nombreR')
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
    proveedores = Proveedor.objects.all()
    return render(request, 'contabilidad/proveedores.html', {'proveedores': proveedores})


def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)

    if request.method == 'POST':
        # Eliminar al proveedor de la base de datos
        proveedor.delete()
        # Redirigir a la página de proveedores después de la eliminación
        return redirect('proveedores')
    return render(request, 'confirmar_eliminar_proveedor.html', {'proveedor': proveedor})





def ventas(request):
    logger = logging.getLogger(__name__)

    if request.method == "POST":
        cliente_id = request.POST.get('clienteR')
        forma_de_pago = request.POST.get('forma_de_pagoR')
        productos_ids = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        tamanios = request.POST.getlist('tamanios')  # Obtener los tamaños seleccionados para las tortas
        monto_total_str = request.POST.get('montoR')

        if not all([cliente_id, forma_de_pago, monto_total_str, productos_ids, cantidades]):
            logger.error("Datos incompletos en el formulario de venta.")
            messages.error(request, "Por favor, complete todos los campos.")
            return redirect('ventas')

        try:
            monto_total = int(monto_total_str)
        except ValueError:
            logger.error("Error al convertir el monto total a número: %s", monto_total_str)
            messages.error(request, "El monto total ingresado no es válido.")
            return redirect('ventas')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        try:
            with transaction.atomic():
                venta = Venta(cliente=cliente, forma_de_pago=forma_de_pago, monto_total=monto_total)
                venta.save()

                for producto_id, cantidad in zip(productos_ids, cantidades):
                    print(producto_id, cantidad)
                    tipo_producto, id_real = producto_id.split('_', 1)  # Separar el prefijo del ID real

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

                # Impresión de detalles de venta
                detalles_venta = DetalleVenta.objects.filter(venta=venta)
                for detalle in detalles_venta:
                    print("ID de Venta:", detalle.venta.id)
                    print("ID del Producto:", detalle.producto.id)
                    print("Nombre del Producto:", detalle.producto.nombre)
                    print("Cantidad:", detalle.cantidad)
                    # Imprimir otros campos según sea necesario

                return redirect('ventas')
        except Exception as e:
            logger.error("Error al agregar la venta: %s", str(e))
            messages.error(request, "Ocurrió un error al procesar la venta.")
            return redirect('ventas')
    else:
        ventas = Venta.objects.all()
        clientes = Cliente.objects.all()
        snacks = Snack.objects.all()
        tortas = Torta.objects.all()

        return render(request, 'contabilidad/ventas.html', {'ventas': ventas, 'clientes': clientes, 'snacks': snacks, 'tortas': tortas})
    
def grafico_ventas_gastos(request):
    # Obtener el filtro seleccionado del formulario (predeterminado: diario)
    filtro = request.GET.get('filtro', 'diario')

    # Obtener la fecha actual en la zona horaria de Chile
    fecha_actual_chile = timezone.now().astimezone(pytz.timezone('America/Santiago'))

    # Definir los límites de fechas según el filtro seleccionado
    if filtro == 'diario':
        fecha_inicio = fecha_actual_chile.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_actual_chile.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif filtro == 'semanal':
        fecha_inicio = fecha_actual_chile - timedelta(days=fecha_actual_chile.weekday())
        fecha_fin = fecha_inicio + timedelta(days=6)
    elif filtro == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=31)

    # Obtener los datos de los gastos y las ventas según el filtro seleccionado
    gastos = Gasto.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
    ventas = Venta.objects.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Calcular los totales de gastos y ventas
    total_gastos = sum(gasto.monto for gasto in gastos)
    total_ventas = sum(venta.monto_total for venta in ventas)

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
    return render(request, 'contabilidad/estadisticas.html', {'graph_html': graph_html, 'filtro': filtro})



def editar_producto(request, producto_id):#dudoso
    # Lógica para editar el producto con el ID dado
    return HttpResponse(f"Editando el producto con ID: {producto_id}")


def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)
    
    if request.method == "POST":
        venta.delete()
        return redirect('ventas')
    else:
        # Handle GET request if needed
        pass

def gastos(request):
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
    ganancias_diarias = Gasto.objects.values('fecha__date').annotate(total_ganancias=Sum('monto'))
    # Convertir la fecha a la zona horaria de Chile antes de pasarla al contexto
    for gasto in gastos:
        gasto.fecha = gasto.fecha.astimezone(pytz.timezone('America/Santiago'))

    proveedores = Proveedor.objects.all()  # Obtener todos los proveedores
    return render(request, 'contabilidad/gastos.html', {'gastos': gastos, 'proveedores': proveedores, 'ganancias_diarias': ganancias_diarias})


def sumar_gastos_por_granularidad(granularidad='diario'):
    # Obtener la fecha actual en la zona horaria de Chile
    fecha_actual_chile = timezone.now()

    # Definir el rango de fechas según la granularidad
    if granularidad == 'diario':
        fecha_inicio = fecha_actual_chile
        fecha_fin = fecha_actual_chile
    elif granularidad == 'semanal':
        fecha_inicio = fecha_actual_chile - timedelta(days=fecha_actual_chile.weekday())
        fecha_fin = fecha_inicio + timedelta(days=6)
    elif granularidad == 'mensual':
        fecha_inicio = fecha_actual_chile.replace(day=1)
        fecha_fin = fecha_inicio + relativedelta(months=1, days=-1)

    # Obtener los gastos según la granularidad
    gastos = (
        Gasto.objects
        .filter(fecha__date__range=[fecha_inicio, fecha_fin])  
        .values('fecha__date')  
        .annotate(total_gastos=Sum('monto'))  
        .order_by('fecha__date')  
    )
    return gastos




def admin_contabilidad(request):
    return render(request, 'admin_contabilidad.html',{})
 

def cliente_agregado(request):
    messages.success(request, 'Cliente agregado exitosamente.')
    return redirect('admin_contabilidad')


def proveedor_agregado(request):
    messages.success(request, 'Proveedor agregado exitosamente.')
    return redirect('admin_contabilidad')

#aqui termina todo lo de contabilidad

#aqui empieza la administracion del inicio

