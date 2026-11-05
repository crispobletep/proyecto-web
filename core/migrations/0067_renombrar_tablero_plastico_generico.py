from django.db import migrations


SLUG = "tablero-plastico-forceman"


def corregir_ficha(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(slug=SLUG).update(
        nombre="Tablero plástico de distribución",
        descripcion=(
            "Tablero plástico para distribución eléctrica. "
            "Imagen de referencia tomada de su embalaje."
        ),
        texto_alternativo="Tablero plástico para distribución eléctrica",
    )


def restaurar_ficha(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(slug=SLUG).update(
        nombre="Tablero plástico Forceman",
        descripcion="Tablero plástico Forceman. Imagen de referencia tomada de su embalaje.",
        texto_alternativo="Tablero plástico Forceman",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0066_agregar_calotas_kalop"),
    ]

    operations = [
        migrations.RunPython(corregir_ficha, restaurar_ficha),
    ]
