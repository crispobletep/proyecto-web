from django.db import migrations


def corregir_nombre(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(
        slug="tablero-plastico-forceman-4-modulos"
    ).update(
        nombre="Tablero plástico 4 módulos",
        descripcion="Tablero plástico de 4 módulos. Imagen de referencia tomada de su embalaje.",
        texto_alternativo="Tablero plástico de 4 módulos",
        etiqueta_visual="",
    )


def restaurar_nombre(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(
        slug="tablero-plastico-forceman-4-modulos"
    ).update(
        nombre="Tablero plástico Forceman 4 módulos",
        descripcion="Tablero plástico Forceman 4 módulos. Imagen de referencia tomada de su embalaje.",
        texto_alternativo="Tablero plástico Forceman 4 módulos",
        etiqueta_visual="Forceman",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0054_confirmar_marcas_tableros"),
    ]

    operations = [
        migrations.RunPython(corregir_nombre, restaurar_nombre),
    ]
