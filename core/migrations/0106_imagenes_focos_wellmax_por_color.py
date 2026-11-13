from django.db import migrations


ROOT = "productos/catalogo/iluminacion/focos-superficie/variantes/"
IMAGENES = {
    "Blanco": ROOT + "wellmax-eagle-eye-blanco.png",
    "Negro": ROOT + "wellmax-eagle-eye-negro.png",
}
SLUGS = (
    "foco-led-superficie-wellmax-eagle-eye",
    "foco-led-superficie-wellmax-eagle-eye-20w",
    "foco-led-superficie-wellmax-eagle-eye-30w",
)
IMAGENES_ORIGINALES = {
    "foco-led-superficie-wellmax-eagle-eye": (
        "productos/catalogo/iluminacion/focos-superficie/wellmax-eagle-eye-10w.png"
    ),
    "foco-led-superficie-wellmax-eagle-eye-20w": (
        "productos/catalogo/iluminacion/focos-superficie/wellmax-eagle-eye-20w.png"
    ),
    "foco-led-superficie-wellmax-eagle-eye-30w": (
        "productos/catalogo/iluminacion/focos-superficie/wellmax-eagle-eye-30w.png"
    ),
}


def separar_imagenes_por_color(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    for producto in Producto.objects.using(alias).filter(slug__in=SLUGS):
        imagen_blanca = IMAGENES["Blanco"]
        producto.imagen = imagen_blanca
        producto.texto_alternativo = (
            f"Foco LED Wellmax Eagle Eye {producto.nombre.rsplit(' ', 2)[-2]} W, color blanco"
        )
        producto.save(update_fields=["imagen", "texto_alternativo"])

        for color, imagen in IMAGENES.items():
            Variante.objects.using(alias).filter(
                producto_id=producto.pk,
                nombre=color,
            ).update(imagen=imagen)


def restaurar_imagenes_compuestas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    for slug, imagen in IMAGENES_ORIGINALES.items():
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        producto.imagen = imagen
        producto.save(update_fields=["imagen"])
        Variante.objects.using(alias).filter(producto_id=producto.pk).update(imagen=imagen)


class Migration(migrations.Migration):
    dependencies = [("core", "0105_ordenar_tableros_metalicos_catalogo")]

    operations = [migrations.RunPython(separar_imagenes_por_color, restaurar_imagenes_compuestas)]
