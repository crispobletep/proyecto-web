from django.db import migrations


IMAGEN = (
    "productos/catalogo/control-senalizacion/conmutadores/"
    "conmutador-3-posiciones.png"
)
AMPERAJES = (20, 25, 32, 40, 50, 63)


def agregar_selector_pacco(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    categoria = Categoria.objects.using(alias).get(slug="conmutadores")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="selector-tipo-pacco-3-posiciones-3-polos",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Selector tipo Pacco de 3 posiciones (1-0-2), 3 polos",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Selectores tipo Pacco",
            "descripcion": (
                "Selector tipo Pacco de 3 polos y tres posiciones (1-0-2). "
                "Disponible en corrientes nominales de 20, 25, 32, 40, 50 y 63 A."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Selector tipo Pacco rotativo de 3 polos y 3 posiciones"
            ),
            "etiqueta_visual": "SELECTORES PACCO",
            "orden": 900,
            "publicado": True,
        },
    )

    caracteristicas = (
        "Selector tipo Pacco de 3 polos.",
        "Tres posiciones: 1-0-2.",
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
    for orden, (nombre, valor) in enumerate(
        (("Posiciones", "3 (1-0-2)"), ("Polos", "3")),
        start=1,
    ):
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre=nombre,
            valor=valor,
            unidad="",
            orden=orden,
        )

    for orden, amperaje in enumerate(AMPERAJES, start=1):
        nombre = f"{amperaje} A · 3 polos"
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
            nombre="Polos",
            defaults={"valor": "3", "unidad": "", "orden": 2},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0114_agregar_conmutador_tres_posiciones")]

    operations = [migrations.RunPython(agregar_selector_pacco, migrations.RunPython.noop)]
