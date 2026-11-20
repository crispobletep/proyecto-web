from django.db import migrations


IMAGEN = (
    "productos/catalogo/control-senalizacion/conmutadores/"
    "conmutador-3-posiciones.png"
)
AMPERAJES = (20, 25, 32, 40, 50, 63)


def agregar_conmutador(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    familia = Categoria.objects.using(alias).get(slug="control-senalizacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="conmutadores",
        defaults={
            "nombre": "Conmutadores",
            "padre_id": familia.pk,
            "orden": 11,
            "activa": True,
        },
    )

    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="conmutador-rotativo-3-posiciones",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Conmutador rotativo de 3 posiciones",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Conmutadores eléctricos",
            "descripcion": (
                "Conmutador rotativo de tres posiciones para selección manual. "
                "Disponible en corrientes nominales de 20, 25, 32, 40, 50 y 63 A."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": "Conmutador rotativo de tres posiciones",
            "etiqueta_visual": "CONMUTADORES",
            "orden": 890,
            "publicado": True,
        },
    )

    caracteristicas = (
        "Conmutador rotativo de tres posiciones.",
        "Variantes de 20, 25, 32, 40, 50 y 63 A.",
    )
    Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
    for orden, texto in enumerate(caracteristicas, start=1):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )

    Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
    Especificacion.objects.using(alias).create(
        producto_id=producto.pk,
        nombre="Posiciones",
        valor="3",
        unidad="",
        orden=1,
    )

    for orden, amperaje in enumerate(AMPERAJES, start=1):
        nombre = f"{amperaje} A · 3 posiciones"
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=nombre,
            defaults={
                "modelo": "",
                "codigo": None,
                "imagen": IMAGEN,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Corriente nominal",
            defaults={"valor": str(amperaje), "unidad": "A", "orden": 1},
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Posiciones",
            defaults={"valor": "3", "unidad": "", "orden": 2},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0113_simplificar_descripciones_adicionales")]

    operations = [migrations.RunPython(agregar_conmutador, migrations.RunPython.noop)]
