# Estructura propuesta del proyecto TemucoSoft

> Resumen inicial para orientar el desarrollo modular del backend (Django + DRF) y los templates (Bootstrap 5).

## Árbol lógico de apps

```
temucosoft/              # Configuración global del proyecto
    settings.py          # Variables de entorno, DB PostgreSQL, DRF, JWT y templates
    urls.py              # Enrutamiento principal y registro de APIs/plantillas

core/                    # Implementación actual (modelos y vistas unificados)
    models.py
    serializers.py
    views.py
    permissions.py
    validators.py

# Próxima modularización (apps separadas)
accounts/                # Usuario personalizado (AUTH_USER_MODEL), auth web y JWT
companies/               # Tenants (Company) y suscripciones (Subscription)
catalog/                 # Productos y categorías
branches/                # Sucursales y capas de restricción por plan
inventory/               # Stock por sucursal, ajustes y movimientos
suppliers/               # Proveedores y compras
sales/                   # POS: Sale y SaleItem
shop/                    # E-commerce, carrito y órdenes
reports/                 # Endpoints de reportes (stock, ventas)
common/                  # Utilidades compartidas: validadores, mixins, paginación
```

## Templates principales (Bootstrap 5)
- `templates/login.html`: autenticación web + obtención de JWT con fetch.
- `templates/dashboard.html`: menú dinámico por rol/plan.
- Catálogo, detalle de producto, carrito y checkout se ubicarán en `templates/shop/`.
- Vistas de gestión (inventario, proveedores, compras, reportes) se ubicarán en `templates/panel/` agrupadas por módulo.

## Enrutamiento esperado
- Prefijo API: `/api/` usando `DefaultRouter` de DRF.
- Autenticación JWT: `/api/token/` y `/api/token/refresh/` (SimpleJWT).
- Rutas web: `/login/`, `/dashboard/` y páginas públicas de catálogo en `/shop/`.

## Configuración local
- Base de datos PostgreSQL obligatoria (variables de entorno `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`).
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS` se leen desde el entorno con valores por defecto de desarrollo.
- Comandos habituales: `python manage.py makemigrations`, `python manage.py migrate`, `python manage.py createsuperuser`, `python manage.py runserver`.

## Próximos pasos sugeridos
1. Crear las apps modulares (`accounts`, `companies`, etc.) y mover modelos/serializers por dominio.
2. Definir permisos por rol en cada ViewSet y mixins de tenant para filtrar por compañía.
3. Implementar endpoints mínimos descritos en el requerimiento y plantillas faltantes.
4. Añadir pruebas unitarias para validadores de RUT, flujos de inventario y ventas.
