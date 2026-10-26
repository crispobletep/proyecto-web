from django.db import migrations


PRODUCTOS = {
    "plafon-led-sobrepuesto-fsl-6500k": {
        "variantes": (
            ("24 W · 6500 K", "productos/catalogo/iluminacion/fsl-plafon-led-sobrepuesto-24w-6500k.png", 24),
            ("18 W · 6500 K", "productos/catalogo/iluminacion/fsl-plafon-led-sobrepuesto-18w-6500k.png", 18),
        ),
    },
    "panel-led-embutido-fsl": {
        "variantes": (
            ("24 W · 6500 K", "productos/catalogo/iluminacion/fsl-panel-led-embutido-24w-profesional.png", 24),
            ("18 W · 6500 K", "productos/catalogo/iluminacion/fsl-panel-led-embutido-18w-profesional.png", 18),
        ),
    },
    "panel-led-embutido-avc-6500k": {
        "variantes": (
            ("6 W · 6500 K", "productos/catalogo/iluminacion/avc-panel-led-embutido-6w-6500k.png", 6),
            ("12 W · 6500 K", "productos/catalogo/iluminacion/avc-panel-led-embutido-12w-6500k.png", 12),
            ("18 W · 6500 K", "productos/catalogo/iluminacion/avc-panel-led-embutido-18w-6500k.png", 18),
        ),
    },
    "panel-led-sobrepuesto-avc-6500k": {
        "variantes": (
            ("12 W · 6500 K", "productos/catalogo/iluminacion/avc-panel-led-sobrepuesto-12w-profesional.png", 12),
            ("18 W · 6500 K", "productos/catalogo/iluminacion/avc-panel-led-sobrepuesto-18w-profesional.png", 18),
        ),
    },
}


def publicar_y_agregar_potencias(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Imagen = apps.get_model("core", "ImagenProducto")

    for slug, definicion in PRODUCTOS.items():
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        producto.publicado = True
        producto.save(using=alias, update_fields=("publicado",))

        nombres_vigentes = {nombre for nombre, _, _ in definicion["variantes"]}
        variantes_obsoletas = Variante.objects.using(alias).filter(
            producto_id=producto.pk
        ).exclude(nombre__in=nombres_vigentes)
        protegidas = variantes_obsoletas.filter(cotizaciones__isnull=False)
        protegidas.update(disponible=False)
        variantes_obsoletas.exclude(cotizaciones__isnull=False).delete()

        for orden, (nombre, ruta, potencia) in enumerate(
            definicion["variantes"], start=1
        ):
            variante, _ = Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={
                    "codigo": None,
                    "modelo": "",
                    "imagen": ruta,
                    "disponible": True,
                    "orden": orden,
                },
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Potencia",
                defaults={"valor": str(potencia), "unidad": "W", "orden": 1},
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Temperatura de color",
                defaults={"valor": "6500", "unidad": "K", "orden": 2},
            )

        # Las opciones muestran estas imágenes; evita repetirlas en la galería.
        Imagen.objects.using(alias).filter(producto_id=producto.pk).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0036_eliminar_fotoceldas_y_soporte")]

    operations = [
        migrations.RunPython(publicar_y_agregar_potencias, migrations.RunPython.noop)
    ]
