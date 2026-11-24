from django.db import migrations


IMAGEN = "productos/catalogo/herramientas/laucha-electrica.jpeg"
LARGOS_METROS = tuple(range(5, 51, 5))


def agregar_laucha_electrica(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model(
        "core", "EspecificacionVariante"
    )
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    categoria = Categoria.objects.using(alias).get(
        slug="herramientas-manuales"
    )
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="laucha-electrica-150-mm",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Laucha eléctrica 1,50 mm",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Herramientas manuales",
            "descripcion": (
                "Laucha eléctrica de 1,50 mm para facilitar el paso de "
                "conductores por canalizaciones. Disponible en largos de "
                "5 a 50 metros."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Laucha eléctrica metálica en rollo, de 1,50 mm"
            ),
            "etiqueta_visual": "HERRAMIENTAS MANUALES",
            "orden": 7,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Laucha eléctrica metálica para canalizaciones.",
            "Diámetro: 1,50 mm.",
            "Largos disponibles de 5 a 50 m, en intervalos de 5 m.",
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
    Especificacion.objects.using(alias).create(
        producto_id=producto.pk,
        nombre="Diámetro",
        valor="1,50",
        unidad="mm",
        orden=1,
    )

    for orden, largo in enumerate(LARGOS_METROS, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"{largo} m",
            defaults={
                "modelo": "",
                "codigo": None,
                "imagen": "",
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Largo",
            defaults={
                "valor": str(largo),
                "unidad": "m",
                "orden": 1,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0119_agregar_destornillador_probador_corriente"),
    ]

    operations = [
        migrations.RunPython(
            agregar_laucha_electrica,
            migrations.RunPython.noop,
        ),
    ]
