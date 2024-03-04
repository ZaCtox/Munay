from django.db import models
from django.db.models.fields import CharField,IntegerField, URLField
from django.db.models.fields.files import ImageField
from django.utils import timezone
import pytz
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Snack(models.Model):
    TIPO_CHOICES = (('Torta', 'Torta'),
                    ('Snack', 'Snack'),)
    id = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to='')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    descripcion = models.TextField(default='', verbose_name='Descripción')
    precio = models.PositiveIntegerField(verbose_name='Precio')
    descuento_2da_unidad = models.IntegerField(verbose_name='Descuento en Segunda Unidad', default=0)
    stock = models.IntegerField(verbose_name='Cantidad')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo', default='')


    def InfoSnack(self):
         return "id: {} - imagen: {} - nombre: {} - descripcion: {} - precio: {} - descuento_2da_unidad: {} - stock: {}".format(
             self.id, self.imagen, self.nombre, self.precio, self.descuento_2da_unidad, self.stock)

    def __str__(self):
        return self.InfoSnack


class Torta(models.Model):
    TIPO_CHOICES = (('Torta', 'Torta'),
                    ('Snack', 'Snack'),)
    id = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to='')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    descripcion = models.TextField(default='', verbose_name='Descripción')
    precio = models.IntegerField(verbose_name='Precio')
    precio_15p = models.PositiveIntegerField(verbose_name='Precio_15p', default=0)
    precio_24p = models.PositiveIntegerField(verbose_name='Precio_24p', default=0)
    stock = models.IntegerField(verbose_name='Cantidad')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo', default='')

    
    def InfoTorta(self):
         return "id: {} - imagen: {} - nombre: {} - descripcion: {} - precio: {} - precio_15p: {} - stock: {}".format(
             self.id, self.imagen, self.nombre, self.precio, self.precio_15p, self.precio_24p, self.stock)

    def __str__(self):
        return self.InfoTorta



class Cliente(models.Model):
    opcion = [('Norte','Norte'),('Sur','Sur'),('Poniente','Poniente'),('Oriente','Oriente')]
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=10, blank=True, null=True, verbose_name="Rut")
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    telefono = models.CharField(max_length=9, verbose_name="Teléfono")
    direccion = models.CharField(max_length=100, verbose_name="Dirección")
    numero_casa = models.IntegerField(verbose_name= "Número")
    barrio = models.CharField(max_length=50, choices=opcion, verbose_name="Barrio")

    def InfoCliente(self):
        return "rut: {} - nombre: {} - telefono: {} - direccion: {} -  numero_casa {} - barrio: {}".format(self.rut, self.nombre, self.telefono, self.direccion, self.numero_casa, self.barrio)

    def __str__(self):
        return self.opcion  # Asegúrate de que esto sea una cadena

class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=10, verbose_name="Rut")
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    telefono = models.CharField(max_length=9, verbose_name="Teléfono")

    def InfoProveedor(self):
        return "rut: {} - nombre: {} - telefono: {}".format(self.rut, self.nombre, self.telefono)

    def __str__(self):
        return self.InfoProveedor()  # Llama al método InfoProveedor y devuelve su resultado como una cadena

class Gasto(models.Model):
    pago =[('Efectivo','Efectivo'),('Trasferencia Bancaria','Trasferencia Bancaria'),('Tarjeta Crédito/Débito','Tarjeta Crédito/Débito')]
    opcion = [('Gasto','Gasto'),('Productos comprado y/o elaborados para la venta','Productos comprado y/o elaborados para la venta')]
    id = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    tipo = models.CharField(max_length=60, choices=opcion, verbose_name="Selecciona un tipo")
    forma_de_pago = models.CharField(max_length=60, choices=pago, verbose_name="Forma de pago")
    monto = models.PositiveIntegerField(verbose_name="Costo Total")
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")

    def InfoGasto(self):
        return "id: {} - proveedor: {} - descripcion: {} - tipo: {} - forma_de_pago: {}- monto: {} - fecha: {}".format(self.id, self.proveedor, self.descripcion,self.tipo, self.forma_de_pago, self.monto, self.fecha.astimezone(pytz.timezone('America/Santiago')))

    def __str__(self):
        return self.InfoGasto()  # Llama al método InfoGasto y devuelve su resultado como una cadena
    
class Venta(models.Model):
    pago = [
        ('Efectivo', 'Efectivo'),
        ('Trasferencia Bancaria', 'Trasferencia Bancaria'),
        ('Tarjeta Crédito/Débito', 'Tarjeta Crédito/Débito')
    ]
    id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    forma_de_pago = models.CharField(max_length=60, choices=pago, verbose_name="Forma de pago")
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    monto_total = models.IntegerField(verbose_name="Monto Total")  # Este es el campo que necesitas agregar

    def InfoVenta(self):
        return f"id: {self.id} - cliente: {self.cliente} - forma_de_pago: {self.forma_de_pago} - fecha: {self.fecha} - monto_total: {self.monto_total}"

    def __str__(self):
        return f"Venta - ID: {self.id}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    cantidad = models.PositiveIntegerField()
    tamaño = models.CharField(max_length=10, blank=True, null=True)  # Campo para almacenar el tamaño de la torta

    def __str__(self):
        return f"Detalle de Venta - Venta: {self.venta.id}, Producto: {self.producto.nombre}, Cantidad: {self.cantidad}"
