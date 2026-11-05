from django.db import migrations


SLUG_EMBUTIDO = "tablero-embutido-dex-18-polos"
SLUG_SOBREPUESTO = "tablero-sobrepuesto-lexo-18-polos"
SLUG_COMBINADO = "tablero-18-polos"
IMAGEN_EMBUTIDO = "productos/catalogo/tableros-cnc/tablero-dex-18-polos.png"
IMAGEN_SOBREPUESTO = "productos/catalogo/tableros-cnc/tablero-lexo-18-polos.png"


def unificar_tableros(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    combinado = Producto.objects.using(alias).get(slug=SLUG_SOBREPUESTO)
    Producto.objects.using(alias).filter(slug=SLUG_EMBUTIDO).update(
        publicado=False
    )
    combinado.slug = SLUG_COMBINADO
    combinado.nombre = "Tablero de 18 polos"
    combinado.descripcion = (
        "Tablero plástico de distribución de 18 polos, disponible para "
        "montaje embutido o sobrepuesto."
    )
    combinado.imagen = IMAGEN_EMBUTIDO
    combinado.texto_alternativo = (
        "Tablero plástico de 18 polos para montaje embutido o sobrepuesto"
    )
    combinado.orden = 1410
    combinado.publicado = True
    combinado.save(
        using=alias,
        update_fields=(
            "slug", "nombre", "descripcion", "imagen", "texto_alternativo",
            "orden", "publicado",
        ),
    )

    Especificacion.objects.using(alias).update_or_create(
        producto_id=combinado.pk,
        nombre="Polos",
        defaults={"valor": "18", "unidad": "polos", "orden": 1},
    )
    Caracteristica.objects.using(alias).update_or_create(
        producto_id=combinado.pk,
        orden=1,
        defaults={"texto": "Disponible para montaje embutido o sobrepuesto."},
    )

    for orden, (nombre, montaje, imagen) in enumerate(
        (
            ("Embutido", "Embutido", IMAGEN_EMBUTIDO),
            ("Sobrepuesto", "Sobrepuesto", IMAGEN_SOBREPUESTO),
        ),
        start=1,
    ):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=combinado.pk,
            nombre=nombre,
            defaults={
                "codigo": None,
                "modelo": "",
                "imagen": imagen,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Montaje",
            defaults={"valor": montaje, "unidad": "", "orden": 1},
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Polos",
            defaults={"valor": "18", "unidad": "polos", "orden": 2},
        )


def separar_tableros(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    combinado = Producto.objects.using(alias).filter(slug=SLUG_COMBINADO).first()
    if combinado:
        combinado.slug = SLUG_SOBREPUESTO
        combinado.nombre = "Tablero sobrepuesto 18 polos"
        combinado.descripcion = (
            "Tablero sobrepuesto 18 polos. Imagen de referencia tomada de su embalaje."
        )
        combinado.imagen = IMAGEN_SOBREPUESTO
        combinado.texto_alternativo = "Tablero sobrepuesto 18 polos"
        combinado.orden = 1420
        combinado.save(
            using=alias,
            update_fields=(
                "slug", "nombre", "descripcion", "imagen", "texto_alternativo",
                "orden",
            ),
        )
        Variante.objects.using(alias).filter(producto_id=combinado.pk).update(
            disponible=False
        )
        Especificacion.objects.using(alias).filter(
            producto_id=combinado.pk, nombre="Polos"
        ).delete()
        Caracteristica.objects.using(alias).filter(
            producto_id=combinado.pk,
            texto="Disponible para montaje embutido o sobrepuesto.",
        ).delete()

    Producto.objects.using(alias).filter(slug=SLUG_EMBUTIDO).update(
        publicado=True,
        orden=1410,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0076_ordenar_tubos_por_marca"),
    ]

    operations = [
        migrations.RunPython(unificar_tableros, separar_tableros),
    ]
