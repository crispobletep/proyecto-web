from django.contrib import admin

from .models import (
    Categoria,
    CaracteristicaProducto,
    Cotizacion,
    EspecificacionProducto,
    EspecificacionVariante,
    Marca,
    Producto,
    VarianteProducto,
)


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "empresa",
        "servicio",
        "producto",
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
        "variante__nombre",
    )

    list_filter = (
        "servicio",
        "producto",
        "fecha",
    )

    readonly_fields = (
        "fecha",
    )

    autocomplete_fields = (
        "producto",
        "variante",
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
        "disponible",
        "orden",
    )

    ordering = (
        "orden",
        "nombre",
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

    inlines = (
        CaracteristicaProductoInline,
        EspecificacionProductoInline,
        VarianteProductoInline,
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


@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "producto",
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
    )

    inlines = (
        EspecificacionVarianteInline,
    )