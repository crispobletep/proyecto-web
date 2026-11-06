from django.db import migrations


EQUIPO_ESTANCO_IMAGEN = (
    "productos/catalogo/iluminacion/nuevos/estanco-1x18w.png"
)
TABLERO_18_EMBUTIDO = "productos/catalogo/tableros-cnc/tablero-dex-18-polos.png"
TABLERO_18_SOBREPUESTO = "productos/catalogo/tableros-cnc/tablero-lexo-18-polos.png"


def actualizar_imagenes_referenciales(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    equipo = Producto.objects.using(alias).get(
        slug="equipo-estanco-led-2x18w"
    )
    equipo.imagen = EQUIPO_ESTANCO_IMAGEN
    equipo.texto_alternativo = (
        "Imagen referencial del equipo estanco LED 1 × 18 W para el modelo 2 × 18 W"
    )
    equipo.save(
        using=alias,
        update_fields=("imagen", "texto_alternativo"),
    )
    Variante.objects.using(alias).filter(
        producto_id=equipo.pk,
        nombre="2 × 18 W",
    ).update(imagen=EQUIPO_ESTANCO_IMAGEN)

    tablero = Producto.objects.using(alias).get(
        slug="tablero-plastico-24-polos"
    )
    tablero.imagen = TABLERO_18_EMBUTIDO
    tablero.texto_alternativo = (
        "Imagen referencial de un tablero embutido de 18 polos para el modelo de 24 polos"
    )
    tablero.descripcion = (
        "Tablero plástico de distribución de 24 polos, disponible para "
        "montaje embutido o sobrepuesto. Imagen referencial de un tablero de 18 polos."
    )
    tablero.save(
        using=alias,
        update_fields=("imagen", "texto_alternativo", "descripcion"),
    )
    Variante.objects.using(alias).filter(
        producto_id=tablero.pk,
        nombre="Embutido",
    ).update(imagen=TABLERO_18_EMBUTIDO)
    Variante.objects.using(alias).filter(
        producto_id=tablero.pk,
        nombre="Sobrepuesto",
    ).update(imagen=TABLERO_18_SOBREPUESTO)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0079_tableros_variantes_y_marcas_lexo"),
    ]

    operations = [
        migrations.RunPython(actualizar_imagenes_referenciales),
    ]
