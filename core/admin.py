from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Categoria,
    CaracteristicaProducto,
    Cotizacion,
    EspecificacionProducto,
    EspecificacionVariante,
    ImagenProducto,
    Marca,
    Producto,
    Proyecto,
    VarianteProducto,
)


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = (
        "identificador",
        "nombre",
        "empresa",
        "servicio",
        "producto",
        "proyecto",
        "variante",
        "email",
        "telefono",
        "fecha",
    )

    search_fields = (
        "nombre",
        "empresa",
        "email",
        "telefono",
        "servicio",
        "producto__nombre",
        "proyecto__nombre",
        "variante__nombre",
    )

    list_filter = (
        "servicio",
        "producto",
        "proyecto",
        "fecha",
    )

    readonly_fields = (
        "identificador",
        "fecha",
    )

    autocomplete_fields = (
        "producto",
        "proyecto",
        "variante",
    )

    fieldsets = (
        (
            "Solicitud",
            {
                "fields": (
                    "identificador",
                    "fecha",
                    "servicio",
                    "producto",
                    "proyecto",
                    "variante",
                    "mensaje",
                ),
            },
        ),
        (
            "Datos del cliente",
            {
                "fields": (
                    "nombre",
                    "empresa",
                    "email",
                    "telefono",
                ),
            },
        ),
    )

    @admin.display(description="ID de cotización", ordering="id")
    def identificador(self, cotizacion):
        if not cotizacion.pk:
            return "Se asigna al guardar"

        return f"COT-{cotizacion.pk:06d}"


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura",
        "nombre",
        "sector",
        "estado",
        "periodo",
        "orden",
        "destacado",
        "publicado",
    )
    list_display_links = ("miniatura", "nombre")
    list_editable = ("orden", "destacado", "publicado")
    list_filter = ("sector", "estado", "destacado", "publicado")
    search_fields = (
        "nombre",
        "descripcion",
        "constructora",
        "mandante",
        "direccion",
    )
    prepopulated_fields = {"slug": ("nombre",)}
    readonly_fields = ("vista_previa", "creado", "actualizado")
    save_on_top = True
    fieldsets = (
        (
            "Información principal",
            {
                "fields": (
                    "nombre",
                    "slug",
                    "sector",
                    "descripcion",
                    "estado",
                    "periodo",
                ),
            },
        ),
        (
            "Participantes",
            {"fields": ("constructora", "mandante")},
        ),
        (
            "Imagen",
            {"fields": ("imagen", "texto_alternativo", "vista_previa")},
        ),
        (
            "Ubicación y enlaces",
            {
                "fields": (
                    "direccion",
                    "url_mapa",
                    "url_referencia",
                ),
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "orden",
                    "destacado",
                    "publicado",
                    "creado",
                    "actualizado",
                ),
            },
        ),
    )

    @admin.display(description="Imagen")
    def miniatura(self, proyecto):
        if not proyecto.imagen:
            return "Sin imagen"
        return format_html(
            '<img src="{}" alt="" style="width:70px;height:46px;'
            'object-fit:cover;border-radius:4px;">',
            proyecto.imagen.url,
        )

    @admin.display(description="Vista previa")
    def vista_previa(self, proyecto):
        if not proyecto.imagen:
            return "La imagen aparecerá aquí después de guardarla."
        return format_html(
            '<img src="{}" alt="{}" style="max-width:520px;'
            'max-height:320px;object-fit:contain;border-radius:6px;">',
            proyecto.imagen.url,
            proyecto.alt_imagen,
        )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo_clasificacion",
        "padre",
        "orden",
        "activa",
    )

    list_editable = (
        "orden",
        "activa",
    )

    list_filter = (
        "padre",
        "activa",
    )

    search_fields = (
        "nombre",
        "padre__nombre",
    )

    prepopulated_fields = {
        "slug": ("nombre",),
    }

    ordering = (
        "padre__nombre",
        "orden",
        "nombre",
    )

    fieldsets = (
        (
            "Clasificación del catálogo",
            {
                "fields": (
                    "nombre",
                    "slug",
                    "padre",
                ),
                "description": (
                    "Registre una familia principal o una "
                    "subcategoría perteneciente a una familia."
                ),
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "orden",
                    "activa",
                ),
            },
        ),
    )

    @admin.display(
        description="Nivel de clasificación",
        ordering="padre",
    )
    def tipo_clasificacion(self, categoria):
        if categoria.padre_id:
            return "Subcategoría"

        return "Familia principal"


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "slug",
        "activa",
    )

    list_editable = (
        "activa",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "activa",
    )

    prepopulated_fields = {
        "slug": ("nombre",),
    }


class CaracteristicaProductoInline(admin.TabularInline):
    model = CaracteristicaProducto
    extra = 2

    fields = (
        "texto",
        "orden",
    )

    ordering = (
        "orden",
        "id",
    )


class EspecificacionProductoInline(admin.TabularInline):
    model = EspecificacionProducto
    extra = 2

    fields = (
        "nombre",
        "valor",
        "unidad",
        "orden",
    )

    ordering = (
        "orden",
        "nombre",
    )


class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1
    show_change_link = True

    fields = (
        "nombre",
        "modelo",
        "codigo",
        "imagen",
        "disponible",
        "orden",
    )

    ordering = (
        "orden",
        "nombre",
    )


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 0
    autocomplete_fields = (
        "variantes",
    )

    fields = (
        "vista_previa",
        "imagen",
        "texto_alternativo",
        "variantes",
        "orden",
    )

    readonly_fields = (
        "vista_previa",
    )

    ordering = (
        "orden",
        "id",
    )

    @admin.display(description="Vista previa")
    def vista_previa(self, imagen):
        if not imagen.pk or not imagen.imagen:
            return "Se mostrará al guardar"

        return format_html(
            '<img src="{}" alt="" style="height: 72px; width: 72px; '
            'object-fit: contain; background: #fff;" />',
            imagen.imagen.url,
        )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "marca_catalogo",
        "modelo",
        "codigo",
        "categoria",
        "orden",
        "publicado",
    )

    list_editable = (
        "orden",
        "publicado",
    )

    list_filter = (
        "categoria__padre",
        "categoria",
        "marca_nueva",
        "publicado",
    )

    search_fields = (
        "nombre",
        "marca_nueva__nombre",
        "marca",
        "modelo",
        "codigo",
        "descripcion",
    )

    prepopulated_fields = {
        "slug": ("nombre",),
    }

    list_select_related = (
        "categoria",
        "marca_nueva",
    )

    autocomplete_fields = (
        "categoria",
        "marca_nueva",
    )

    save_on_top = True

    readonly_fields = (
        "creado",
        "actualizado",
    )

    fieldsets = (
        (
            "Clasificación",
            {
                "fields": (
                    "categoria",
                    "marca_nueva",
                    "marca",
                ),
                "description": (
                    "Use Marca para los registros nuevos. Marca anterior "
                    "se conserva únicamente por compatibilidad."
                ),
            },
        ),
        (
            "Identificación del producto",
            {
                "fields": (
                    "nombre",
                    "slug",
                    "modelo",
                    "codigo",
                    "subtitulo",
                ),
            },
        ),
        (
            "Contenido del catálogo",
            {
                "fields": (
                    "descripcion",
                    "imagen",
                    "texto_alternativo",
                    "etiqueta_visual",
                ),
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "orden",
                    "publicado",
                    "creado",
                    "actualizado",
                ),
            },
        ),
    )

    inlines = (
        CaracteristicaProductoInline,
        EspecificacionProductoInline,
        VarianteProductoInline,
        ImagenProductoInline,
    )

    @admin.display(
        description="Marca",
        ordering="marca_nueva__nombre",
    )
    def marca_catalogo(self, producto):
        if producto.marca_nueva:
            return producto.marca_nueva.nombre

        if producto.marca:
            return f"{producto.marca} (anterior)"

        return "Sin marca"


class EspecificacionVarianteInline(admin.TabularInline):
    model = EspecificacionVariante
    extra = 2

    fields = (
        "nombre",
        "valor",
        "unidad",
        "orden",
    )

    ordering = (
        "orden",
        "id",
    )


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = (
        "vista_previa",
        "texto_alternativo",
        "producto",
        "cantidad_variantes",
        "orden",
    )

    search_fields = (
        "texto_alternativo",
        "clave",
        "producto__nombre",
        "variantes__codigo",
    )

    list_filter = (
        "producto__categoria",
        "producto__marca_nueva",
    )

    autocomplete_fields = (
        "producto",
        "variantes",
    )

    list_select_related = (
        "producto",
    )

    readonly_fields = (
        "clave",
        "vista_previa",
    )

    fields = (
        "producto",
        "imagen",
        "vista_previa",
        "texto_alternativo",
        "variantes",
        "orden",
        "clave",
    )

    @admin.display(description="Imagen")
    def vista_previa(self, imagen):
        if not imagen.pk or not imagen.imagen:
            return "Se mostrará al guardar"

        return format_html(
            '<img src="{}" alt="" style="height: 64px; width: 64px; '
            'object-fit: contain; background: #fff;" />',
            imagen.imagen.url,
        )

    @admin.display(description="Variantes")
    def cantidad_variantes(self, imagen):
        return imagen.variantes.count()


@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "producto",
        "categoria_catalogo",
        "marca_catalogo",
        "modelo",
        "codigo",
        "disponible",
        "orden",
    )

    list_editable = (
        "disponible",
        "orden",
    )

    list_filter = (
        "disponible",
        "producto__categoria",
        "producto__marca_nueva",
    )

    search_fields = (
        "nombre",
        "modelo",
        "codigo",
        "producto__nombre",
        "producto__marca_nueva__nombre",
    )

    autocomplete_fields = (
        "producto",
    )

    list_select_related = (
        "producto",
        "producto__categoria",
        "producto__marca_nueva",
    )

    inlines = (
        EspecificacionVarianteInline,
    )

    save_on_top = True

    @admin.display(
        description="Subcategoría",
        ordering="producto__categoria__nombre",
    )
    def categoria_catalogo(self, variante):
        return variante.producto.categoria

    @admin.display(
        description="Marca",
        ordering="producto__marca_nueva__nombre",
    )
    def marca_catalogo(self, variante):
        return variante.producto.marca_nueva or variante.producto.marca or "—"
