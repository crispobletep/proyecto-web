from django.db import migrations


PRODUCTOS = (
    (10, "proyector-led-sensor-logic-10w-6500k"),
    (20, "proyector-led-sensor-logic-20w-6500k"),
    (30, "proyector-led-sensor-logic-30w-6500k"),
    (50, "proyector-led-sensor-logic-50w-6500k"),
    (100, "proyector-led-sensor-logic-100w-6500k"),
)
IMAGEN = "productos/catalogo/iluminacion/proyector-led-sensor-movimiento.png"


def separar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Marca = apps.get_model("core", "Marca")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    ImagenProducto = apps.get_model("core", "ImagenProducto")

    original = Producto.objects.using(alias).get(
        slug="proyector-led-sensor-movimiento-6500k"
    )
    marca_logic = Marca.objects.using(alias).get(nombre__iexact="Logic")

    # Conserva la ficha agrupada en administración, fuera del catálogo público.
    original.publicado = False
    original.save(using=alias, update_fields=["publicado"])
    original.variantes.all().using(alias).update(disponible=False)

    for posicion, (potencia, slug) in enumerate(PRODUCTOS, start=1):
        nombre = f"Proyector LED con sensor de movimiento {potencia} W 6500 K"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": original.categoria_id,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": marca_logic.pk,
                "modelo": "",
                "codigo": None,
                "subtitulo": original.categoria.nombre,
                "descripcion": (
                    f"Proyector LED Logic con sensor de movimiento. "
                    f"Potencia de {potencia} W y luz de 6500 K."
                ),
                "imagen": IMAGEN,
                "texto_alternativo": (
                    f"Proyector LED Logic con sensor de movimiento de {potencia} W"
                ),
                "etiqueta_visual": original.etiqueta_visual,
                "orden": original.orden + posicion,
                "publicado": True,
            },
        )

        for orden, texto in enumerate(
            ("Sensor de movimiento integrado.", "Iluminación LED con luz blanca fría."),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )

        for orden, nombre_spec, valor, unidad in (
            (1, "Potencia", str(potencia), "W"),
            (2, "Temperatura de color", "6500", "K"),
        ):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre_spec,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

        ImagenProducto.objects.using(alias).update_or_create(
            clave=f"{slug}-imagen-principal",
            defaults={
                "producto_id": producto.pk,
                "imagen": IMAGEN,
                "texto_alternativo": producto.texto_alternativo,
                "orden": 1,
            },
        )


def revertir_separacion(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    original = Producto.objects.using(alias).get(
        slug="proyector-led-sensor-movimiento-6500k"
    )
    original.publicado = True
    original.save(using=alias, update_fields=["publicado"])
    original.variantes.all().using(alias).update(disponible=True)

    Producto.objects.using(alias).filter(
        slug__in=[slug for _, slug in PRODUCTOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0050_ocultar_tubos_led_fsl_temporalmente"),
    ]

    operations = [
        migrations.RunPython(separar_productos, revertir_separacion),
    ]
