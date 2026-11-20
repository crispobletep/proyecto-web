from django.db import migrations


IMAGEN = (
    "productos/catalogo/iluminacion/luminarias-publicas/"
    "luminaria-publica-street-light.png"
)
POTENCIAS = (50, 100, 150)


def agregar_luminaria_publica(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="luminarias-publicas",
        defaults={
            "nombre": "Luminarias públicas",
            "padre_id": iluminacion.pk,
            "orden": 10,
            "activa": True,
        },
    )

    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="luminaria-publica-led-street-light",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Luminaria pública LED Street Light",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "Street Light",
            "codigo": None,
            "subtitulo": "Alumbrado público LED",
            "descripcion": (
                "Luminaria pública LED tipo Street Light para iluminación "
                "exterior. Disponible en 50, 100 y 150 W, con alimentación "
                "de 220 V y flujo luminoso indicado de 6.000 lm."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Luminaria pública LED tipo Street Light, vista frontal"
            ),
            "etiqueta_visual": "STREET LIGHT",
            "orden": 950,
            "publicado": True,
        },
    )

    caracteristicas = (
        "Luminaria pública LED para alumbrado exterior.",
        "Potencias disponibles de 50, 100 y 150 W.",
        "Alimentación de 220 V y flujo luminoso indicado de 6.000 lm.",
    )
    Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
    for orden, texto in enumerate(caracteristicas, start=1):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )

    Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
    for orden, (nombre, valor, unidad) in enumerate(
        (
            ("Tipo", "Street Light", ""),
            ("Tensión de alimentación", "220", "V"),
            ("Flujo luminoso", "6.000", "lm"),
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

    for orden, potencia in enumerate(POTENCIAS, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"{potencia} W",
            defaults={
                "modelo": "Street Light",
                "codigo": None,
                "imagen": IMAGEN,
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
            nombre="Tensión de alimentación",
            defaults={"valor": "220", "unidad": "V", "orden": 2},
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Flujo luminoso",
            defaults={"valor": "6.000", "unidad": "lm", "orden": 3},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0115_agregar_selector_tipo_pacco")]

    operations = [migrations.RunPython(agregar_luminaria_publica, migrations.RunPython.noop)]
