from django.db import migrations


IMAGE = "productos/catalogo/iluminacion/nuevos/banderola-salida-led-lexo-6-horas.png"


def agregar_banderola_salida(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    categoria = Categoria.objects.using(alias).get(slug="equipos-emergencia")
    lexo = Marca.objects.using(alias).get(slug="lexo")
    product, _ = Producto.objects.using(alias).update_or_create(
        slug="banderola-salida-led-lexo-6-horas",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Banderola de salida LED LEXO 6 horas",
            "marca": "",
            "marca_nueva_id": lexo.pk,
            "modelo": "",
            "codigo": "1810012",
            "subtitulo": "Equipos de emergencia",
            "descripcion": (
                "Banderola LED LEXO con señal de salida y autonomía de "
                "6 horas. SKU 1810012."
            ),
            "imagen": IMAGE,
            "texto_alternativo": "Banderola LED LEXO con señal verde de salida",
            "etiqueta_visual": "LEXO",
            "orden": 610,
            "publicado": True,
        },
    )

    for order, text in enumerate(
        (
            "Señal luminosa LED de salida.",
            "Autonomía indicada: 6 horas.",
            "SKU: 1810012.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=product.pk,
            orden=order,
            defaults={"texto": text},
        )

    for order, (name, value, unit) in enumerate(
        (("Autonomía", "6", "h"), ("Iluminación", "LED", "")),
        start=1,
    ):
        Especificacion.objects.using(alias).update_or_create(
            producto_id=product.pk,
            nombre=name,
            defaults={"valor": value, "unidad": unit, "orden": order},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0084_ajustar_fotos_y_presentacion_chint")]
    operations = [migrations.RunPython(agregar_banderola_salida, migrations.RunPython.noop)]
