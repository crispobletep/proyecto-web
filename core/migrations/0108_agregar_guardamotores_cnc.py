from django.db import migrations


RANGOS_CORRIENTE = (
    ("1-1-6", "1–1,6"),
    ("1-6-2-5", "1,6–2,5"),
    ("4-6-3", "4–6,3"),
    ("6-10", "6–10"),
    ("9-14", "9–14"),
    ("13-18", "13–18"),
    ("20-23", "20–23"),
)


def agregar_guardamotores(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    proteccion = Categoria.objects.using(alias).get(slug="proteccion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="guarda-motores",
        defaults={
            "nombre": "Guarda-motores",
            "padre_id": proteccion.pk,
            "orden": 3,
            "activa": True,
        },
    )

    for orden, (slug_rango, rango) in enumerate(RANGOS_CORRIENTE, start=1):
        slug = f"guardamotor-cnc-{slug_rango}-a"
        nombre = f"Guardamotor CNC {rango} A"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": nombre,
                "marca": "CNC",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Protección de motores",
                "descripcion": (
                    "Guardamotor CNC para protección de motores eléctricos. "
                    f"Cuenta con un rango de corriente regulable de {rango} A."
                ),
                "imagen": (
                    "productos/catalogo/protecciones/guarda-motores/"
                    "guardamotor-cnc.png"
                ),
                "texto_alternativo": (
                    f"Guardamotor CNC con rango de corriente de {rango} A"
                ),
                "etiqueta_visual": "GUARDA-MOTORES",
                "orden": orden,
                "publicado": True,
            },
        )
        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=f"Rango de corriente regulable: {rango} A.",
            orden=1,
        )
        Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre="Rango de corriente",
            valor=rango,
            unidad="A",
            orden=1,
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0107_marcar_base_panel_led_por_confirmar")]

    operations = [migrations.RunPython(agregar_guardamotores, migrations.RunPython.noop)]
