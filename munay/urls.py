from django.contrib import admin
from django.urls import path, include
# from .views import *
from administracion import views
from django.conf import settings
from django.contrib.staticfiles.urls import static

# estas de abajo son para cargar imagenes de la base de datos
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path, include


# 1) intentar hacer que los snack en oferta sean productos unicos en el pedido al igual que los diferentes tamaños de tortas
# se hizo a medias, que elija la Maitte con cual se queda



urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),

    #Urls para la vista de los productos
    path('productos', views.productos, name='productos'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('detalles_torta/<int:producto_id>/', views.detalles_torta, name='detalles_torta'),
    path('detalles_snack/<int:producto_id>/', views.detalles_snack, name='detalles_snack'),

    


    #Urls para la vista del carrito/pedido
    path('agregar_al_carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('limpiar_carrito/', views.limpiar_carrito, name='limpiar_carrito'),
    path('sumar_stock_carrito/<int:producto_id>/', views.sumar_stock_carrito, name='sumar_stock_carrito'),
    path('restar_stock_carrito/<int:producto_id>/', views.restar_stock_carrito, name='restar_stock_carrito'),
    path('eliminar_producto_carrito/<int:producto_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('pedido', views.pedido, name="pedido"),
    path('obtener_carrito/', views.obtener_carrito, name='obtener_carrito'),




    #Urls para la vista de las pestañas de los clientes
    path('quienes_somos', views.quienes_somos, name='quienes_somos'),
    path('contactanos', views.contactanos, name='contactanos'),

    #Urls para la vista de las pestañas para admnistración
    path('administracion/',views.administracion, name='administracion'),

    #Urls para la vista de administracion de productos
    path('admin_producto/', views.admin_producto, name='admin_producto'),
    path('aumentar_stock_snack/<int:producto_id>/', views.aumentar_stock_snack, name="aumentar_stock_snack"),
    path('aumentar_stock_torta/<int:producto_id>/', views.aumentar_stock_torta, name="aumentar_stock_torta"),
    path('disminuir_stock_snack/<int:producto_id>/', views.disminuir_stock_snack, name='disminuir_stock_snack'),
    path('disminuir_stock_torta/<int:producto_id>/', views.disminuir_stock_torta, name='disminuir_stock_torta'),
    path('eliminar_snack/<int:producto_id>/', views.eliminar_snack, name='eliminar_snack'),
    path('eliminar_torta/<int:producto_id>/', views.eliminar_torta, name='eliminar_torta'),
    path('editar_snack/<int:producto_id>/', views.editar_snack, name='editar_snack'),
    path('editar_torta/<int:producto_id>/', views.editar_torta, name='editar_torta'),

    #Urls para la vista de administracion de inicio
    path('admin_info_inicio/', views.admin_info_inicio, name='admin_info_inicio'),
    path('guardar-slide/', views.guardar_slide, name='guardar_slide'),
    path('editar-slide/<int:slide_id>/', views.editar_slide, name='editar_slide'),
    path('eliminar-slide/<int:slide_id>/', views.eliminar_slide, name='eliminar_slide'),
    
    #Urls para la vista de administracion contabilidad
    path('admin_contabilidad/', views.admin_contabilidad, name='admin_contabilidad'),
    path('cliente_agregado/',views.cliente_agregado, name='cliente_agregado'),
    path('proveedor_agregado/',views.proveedor_agregado, name='proveedor_agregado'),
    path('admin_contabilidad/clientes.html', views.clientes, name='clientes'),
    path('admin_contabilidad/proveedores.html', views.proveedores, name='proveedores'),
    path('admin_contabilidad/ventas.html', views.ventas, name='ventas'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin_contabilidad/gastos.html', views.gastos, name='gastos'),
    path('eliminar-cliente/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('eliminar-proveedor/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('eliminar-venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('eliminar-gasto/<int:gasto_id>/', views.eliminar_gasto, name='eliminar_gasto'),
    path('admin_contabilidad/estadisticas.html', views.grafico_ventas_gastos, name='estadisticas'),
    path('admin_contabilidad/productos_vendidos.html', views.productos_vendidos, name='productos_vendidos'),
    path('admin_contabilidad/precios_sector.html', views.agregar_precios, name='precios_sector'),
    path('eliminar_sector/<int:id>/', views.eliminar_sector, name='eliminar_sector'),
    path('editar_sector/<int:costosector_id>/', views.editar_sector, name='editar_sector'),

    #Urls logout
    path('salir/', views.salir, name='salir'),

]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

