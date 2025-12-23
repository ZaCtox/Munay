from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Snack)
admin.site.register(Torta)
admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Gasto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(CostoSector)

