from django.db import migrations


IMAGENES = {
    "Roja": (
        "productos/catalogo/control-senalizacion/"
        "baliza-giratoria-lexo-roja.jpg"
    ),
    "Amarilla": (
        "productos/catalogo/control-senalizacion/"
        "baliza-giratoria-lexo-amarilla.jpg"
    ),
}


def agregar_baliza_giratoria_lexo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model(
        "core", "EspecificacionVariante"
    )

    categoria = Categoria.objects.using(alias).get(
        slug="sirenas-y-alarmas"
    )
    marca = Marca.objects.using(alias).get(slug="lexo")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="baliza-giratoria-led-lexo-220v",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Baliza giratoria LED Lexo 220 V",
            "marca": "",
            "marca_nueva_id": marca.pk,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Sirenas y alarmas",
            "descripcion": (
                "Baliza giratoria LED Lexo para señalización visual. "
                "Alimentación de 220 V, disponible en color rojo o amarillo."
            ),
            "imagen": IMAGENES["Roja"],
            "texto_alternativo": (
                "Baliza giratoria LED roja Lexo de 220 V"
            ),
            "etiqueta_visual": "BALIZAS LED",
            "orden": 2,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Baliza giratoria LED para señalización visual.",
            "Tensión de alimentación: 220 V.",
            "Colores disponibles: rojo y amarillo.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )

    Especificacion.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, (nombre, valor, unidad) in enumerate(
        (
            ("Tensión", "220", "V"),
            ("Tecnología", "LED", ""),
        ),
        start=1,
    ):
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre=nombre,
            valor=valor,
            unidad=unidad,
            orden=orden,
        )

    for orden, (color, imagen) in enumerate(IMAGENES.items(), start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=color,
            defaults={
                "modelo": "",
                "codigo": None,
                "imagen": imagen,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Color",
            defaults={
                "valor": color,
                "unidad": "",
                "orden": 1,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0122_agregar_sirena_roja_lexo"),
    ]

    operations = [
        migrations.RunPython(
            agregar_baliza_giratoria_lexo,
            migrations.RunPython.noop,
        ),
    ]
