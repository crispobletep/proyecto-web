from django.db import migrations


IMAGEN = "productos/catalogo/herramientas/cinta-pasacable-kalop.jpeg"
LARGOS_METROS = (10, 20, 30)


def agregar_cinta_pasacable_kalop(apps, schema_editor):
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
        slug="herramientas-manuales"
    )
    marca = Marca.objects.using(alias).get(slug="kalop")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="cinta-pasacable-kalop-profesional",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Cinta pasacable profesional Kalop",
            "marca": "",
            "marca_nueva_id": marca.pk,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Herramientas manuales",
            "descripcion": (
                "Cinta pasacable profesional Kalop con alma de acero, "
                "para cableado en instalaciones comerciales. Disponible "
                "en largos de 10, 20 y 30 metros."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Cinta pasacable profesional Kalop con alma de acero"
            ),
            "etiqueta_visual": "HERRAMIENTAS MANUALES",
            "orden": 8,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Cinta pasacable profesional con alma de acero.",
            "Resistencia a la tracción indicada en el envase: 100 kg.",
            "Largos disponibles: 10, 20 y 30 m.",
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
            ("Material del alma", "Acero", ""),
            ("Resistencia a la tracción", "100", "kg"),
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

    for orden, largo in enumerate(LARGOS_METROS, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"{largo} m",
            defaults={
                "modelo": "",
                "codigo": "KL29110N" if largo == 10 else None,
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
        ("core", "0120_agregar_laucha_electrica"),
    ]

    operations = [
        migrations.RunPython(
            agregar_cinta_pasacable_kalop,
            migrations.RunPython.noop,
        ),
    ]
