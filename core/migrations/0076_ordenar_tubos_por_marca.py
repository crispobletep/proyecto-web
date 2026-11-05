from django.db import migrations


ORDEN_POR_MARCA = (
    ("tubo-led-9w-3000k-forceman", 720),
    ("tubo-led-9w-6500k-forceman", 721),
    ("tubo-led-18w-3000k-forceman", 722),
    ("tubo-led-18w-6500k-forceman", 723),
    ("tubo-led-9w-3000k-fsl", 724),
    ("tubo-led-9w-6500k-fsl", 725),
    ("tubo-led-18w-3000k-fsl", 726),
    ("tubo-led-18w-6500k-fsl", 727),
)

ORDEN_ANTERIOR = (
    ("tubo-led-9w-3000k-forceman", 720),
    ("tubo-led-9w-3000k-fsl", 721),
    ("tubo-led-9w-6500k-forceman", 722),
    ("tubo-led-9w-6500k-fsl", 723),
    ("tubo-led-18w-3000k-forceman", 724),
    ("tubo-led-18w-3000k-fsl", 725),
    ("tubo-led-18w-6500k-forceman", 726),
    ("tubo-led-18w-6500k-fsl", 727),
)


def actualizar_orden(apps, schema_editor, ordenes):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for slug, orden in ordenes:
        Producto.objects.using(alias).filter(slug=slug).update(orden=orden)


def ordenar_por_marca(apps, schema_editor):
    actualizar_orden(apps, schema_editor, ORDEN_POR_MARCA)


def restaurar_orden_anterior(apps, schema_editor):
    actualizar_orden(apps, schema_editor, ORDEN_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0075_unificar_imagenes_tubos_led"),
    ]

    operations = [
        migrations.RunPython(ordenar_por_marca, restaurar_orden_anterior),
    ]
