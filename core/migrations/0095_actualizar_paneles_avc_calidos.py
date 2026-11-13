from django.db import migrations


EMBUTIDO_IMAGE = "productos/catalogo/iluminacion/avc-panel-embutido-catalogo.png"
SOBREPUESTO_IMAGE = "productos/catalogo/iluminacion/avc-panel-sobrepuesto-catalogo.png"

WARM_VARIANTS = {
    "panel-led-embutido-avc-6500k": (
        ("3 W · 3000 K", 3, 200, EMBUTIDO_IMAGE),
        ("6 W · 3000 K", 6, 480, EMBUTIDO_IMAGE),
        ("18 W · 3000 K", 18, 1440, EMBUTIDO_IMAGE),
    ),
    "panel-led-sobrepuesto-avc-6500k": (
        ("6 W · 3000 K", 6, 480, SOBREPUESTO_IMAGE),
        ("18 W · 3000 K", 18, 1440, SOBREPUESTO_IMAGE),
    ),
}


def actualizar_paneles_avc(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    product_settings = {
        "panel-led-embutido-avc-6500k": {
            "name": "Panel LED AVC embutido redondo",
            "image": EMBUTIDO_IMAGE,
            "alt": "Panel LED redondo AVC para montaje embutido",
            "description": "Panel LED AVC redondo para montaje embutido. Hay variantes de luz cálida 3000 K y fría 6500 K; las potencias y flujos se indican por variante cuando están especificados en el envase.",
            "features": (
                "Formato redondo para montaje embutido.",
                "Variantes disponibles en luz cálida 3000 K y luz fría 6500 K.",
                "Potencias disponibles: 3 W, 6 W, 12 W y 18 W, según variante.",
            ),
        },
        "panel-led-sobrepuesto-avc-6500k": {
            "name": "Panel LED AVC sobrepuesto redondo",
            "image": SOBREPUESTO_IMAGE,
            "alt": "Panel LED redondo AVC para montaje sobrepuesto",
            "description": "Panel LED AVC redondo para montaje sobrepuesto. Hay variantes de luz cálida 3000 K y fría 6500 K; las potencias y flujos se indican por variante cuando están especificados en el envase.",
            "features": (
                "Formato redondo para montaje sobrepuesto.",
                "Variantes disponibles en luz cálida 3000 K y luz fría 6500 K.",
                "Potencias disponibles: 6 W, 12 W y 18 W, según variante.",
            ),
        },
    }

    for slug, settings in product_settings.items():
        producto = Producto.objects.using(alias).get(slug=slug)
        producto.nombre = settings["name"]
        producto.imagen = settings["image"]
        producto.texto_alternativo = settings["alt"]
        producto.descripcion = settings["description"]
        producto.save(update_fields=["nombre", "imagen", "texto_alternativo", "descripcion"])

        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk, nombre="Temperatura de color"
        ).update(valor="3000 / 6500", unidad="K")
        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk, nombre="Color de luz"
        ).update(valor="Cálida y fría", unidad="")

        Caracteristica = apps.get_model("core", "CaracteristicaProducto")
        for orden, texto in enumerate(settings["features"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )

        # Reemplaza las fotos antiguas de caja por una imagen limpia del panel
        # correspondiente al tipo de montaje, conservando las variantes frías.
        for variante in Variante.objects.using(alias).filter(producto_id=producto.pk):
            variante.imagen = settings["image"]
            variante.save(update_fields=["imagen"])

        for orden, (nombre, potencia, flujo, imagen) in enumerate(WARM_VARIANTS[slug], start=10):
            variante, _ = Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"imagen": imagen, "disponible": True, "orden": orden},
            )
            for spec_order, (spec_name, value, unit) in enumerate(
                (
                    ("Potencia", str(potencia), "W"),
                    ("Flujo luminoso", str(flujo), "lm"),
                    ("Temperatura de color", "3000", "K"),
                    ("Color de luz", "Cálida", ""),
                ),
                start=1,
            ):
                EspecificacionVariante.objects.using(alias).update_or_create(
                    variante_id=variante.pk,
                    nombre=spec_name,
                    defaults={"valor": value, "unidad": unit, "orden": spec_order},
                )


class Migration(migrations.Migration):
    dependencies = [("core", "0094_abrazadera_eclipsable")]

    operations = [migrations.RunPython(actualizar_paneles_avc, migrations.RunPython.noop)]
