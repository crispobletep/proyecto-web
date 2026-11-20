from django.db import migrations


RANGOS_CORRIENTE = (
    ("1-6-2-5", "1,6–2,5"),
    ("2-5-4", "2,5–4"),
    ("4-6", "4–6"),
    ("5-5-8", "5,5–8"),
    ("7-10", "7–10"),
    ("9-15", "9–15"),
    ("12-18", "12–18"),
    ("17-25", "17–25"),
)


def agregar_reles_termicos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    proteccion = Categoria.objects.using(alias).get(slug="proteccion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="rele-termico",
        defaults={
            "nombre": "Relé térmico",
            "padre_id": proteccion.pk,
            "orden": 4,
            "activa": True,
        },
    )

    for orden, (slug_rango, rango) in enumerate(RANGOS_CORRIENTE, start=1):
        slug = f"rele-termico-{slug_rango}-a"
        nombre = f"Relé térmico {rango} A"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Protección de motores",
                "descripcion": (
                    "Relé térmico para protección de motores eléctricos. "
                    f"Su rango de corriente regulable es de {rango} A."
                ),
                "imagen": (
                    "productos/catalogo/protecciones/rele-termico/"
                    "rele-termico.png"
                ),
                "texto_alternativo": (
                    f"Relé térmico con rango de corriente de {rango} A"
                ),
                "etiqueta_visual": "RELÉ TÉRMICO",
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
    dependencies = [("core", "0108_agregar_guardamotores_cnc")]

    operations = [
        migrations.RunPython(agregar_reles_termicos, migrations.RunPython.noop)
    ]
