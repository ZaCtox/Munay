# Munay (Django 4.2)

Proyecto web para la pastelería/snacks Munay. Incluye catálogo público con carrito de compra que envía pedidos por WhatsApp, y un panel administrativo protegido para gestionar productos, slides de inicio y contabilidad (clientes, proveedores, ventas, gastos y costos por sector).

## Requerimientos
- Python 3.10+ y `pip`
- MySQL/MariaDB en ejecución (puerto 3306 por defecto)
- Librerías Python: `Django==4.2.7`, `PyMySQL`, `Pillow`, `matplotlib`, `plotly`, `python-dateutil`, `pytz`

## Instalación rápida
```bash
python -m venv .venv
.venv\Scripts\activate        # en PowerShell
pip install "Django==4.2.7" PyMySQL Pillow matplotlib plotly python-dateutil pytz
```

## Configurar base de datos
1. Crea la base de datos:
   ```sql
   CREATE DATABASE bd_munay CHARACTER SET utf8mb4;
   ```
2. Ajusta credenciales en `munay/settings.py` (sección `DATABASES`). Por defecto usa:
   - ENGINE: `django.db.backends.mysql`
   - NAME: `bd_munay`
   - USER: `root`
   - PASSWORD: *(vacío)*
   - HOST: `127.0.0.1`
3. Aplica migraciones:
   ```bash
   python manage.py migrate
   ```

## Crear superusuario (acceso administrativo)
El panel `/admininistracion` y las vistas internas (`/administracion`,  `/admin_contabilidad`, etc.) requieren autenticación. Crea un usuario con permisos de staff/superusuario:
```bash
python manage.py createsuperuser
```
Luego inicia sesión en `/administracion`

## Ejecutar el servidor
```bash
python manage.py runserver
```
Sitio público: `http://127.0.0.1:8000/`  
Administración Django: `http://127.0.0.1:8000/admin/`

## Funcionalidades principales
- **Catálogo**: listado y búsqueda de snacks y tortas con stock y variaciones de precio.
- **Carrito/Pedido**: agrega productos (incluye promociones y tamaños), calcula total y genera enlace de WhatsApp con el resumen del pedido.
- **Administración de productos**: CRUD de snacks y tortas, control de stock, precios y descuentos.
- **Administración de inicio**: gestión de slides/banner de portada con imagen, texto, botón y oferta opcional.
- **Contabilidad**: registro de clientes, proveedores, ventas, gastos, costos por sector, estadísticas y productos vendidos.

## Archivos y rutas útiles
- Configuración Django: `munay/settings.py`
- URLs principales: `munay/urls.py`
- Lógica de negocio: `administracion/views.py`
- Modelos: `administracion/models.py`
- Plantillas: `templates/`
- Archivos estáticos: `static/` y media de ejemplo en `media/`

## Notas y problemas comunes
- Driver MySQL: si tienes errores de conexión, verifica credenciales y que el servidor esté activo. PyMySQL se instala como drop-in para `MySQLdb` desde `administracion/__init__.py`; si prefieres `mysqlclient`, instálalo y elimina la instalación de PyMySQL.
- Carga de imágenes: en desarrollo se sirven desde `MEDIA_URL` con `DEBUG=True`; en producción configura un servidor de archivos estáticos y media.

