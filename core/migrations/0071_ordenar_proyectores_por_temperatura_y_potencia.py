from django.db import migrations


ORDEN_ANTERIOR = (
    ("proyector-area-led-10w-3000k", 1010),
    ("proyector-area-led-20w-3000k", 1020),
    ("proyector-area-led-20w-6500k", 1030),
    ("proyector-area-led-30w-3000k", 1040),
    ("proyector-area-led-30w-6500k", 1050),
    ("proyector-area-led-50w-3000k", 1060),
    ("proyector-area-led-50w-6500k", 1070),
    ("proyector-area-led-100w-3000k", 1080),
    ("proyector-area-led-100w-6500k", 1090),
    ("proyector-area-led-150w-3000k", 1100),
    ("proyector-area-led-150w-6500k", 1110),
    ("proyector-area-led-200w-3000k", 1120),
    ("proyector-area-led-200w-6500k", 1130),
)

ORDEN_NUEVO = (
    ("proyector-area-led-10w-3000k", 1010),
    ("proyector-area-led-20w-3000k", 1020),
    ("proyector-area-led-30w-3000k", 1030),
    ("proyector-area-led-50w-3000k", 1040),
    ("proyector-area-led-100w-3000k", 1050),
    ("proyector-area-led-150w-3000k", 1060),
    ("proyector-area-led-200w-3000k", 1070),
    ("proyector-area-led-20w-6500k", 1080),
    ("proyector-area-led-30w-6500k", 1090),
    ("proyector-area-led-50w-6500k", 1100),
    ("proyector-area-led-100w-6500k", 1110),
    ("proyector-area-led-150w-6500k", 1120),
    ("proyector-area-led-200w-6500k", 1130),
)


def actualizar_orden(apps, schema_editor, ordenes):
    Producto = apps.get_model("core", "Producto")
    alias = schema_editor.connection.alias
    for slug, orden in ordenes:
        Producto.objects.using(alias).filter(slug=slug).update(orden=orden)


def ordenar_proyectores(apps, schema_editor):
    actualizar_orden(apps, schema_editor, ORDEN_NUEVO)


def restaurar_orden(apps, schema_editor):
    actualizar_orden(apps, schema_editor, ORDEN_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0070_asignar_megabright_a_proyectores"),
    ]

    operations = [
        migrations.RunPython(ordenar_proyectores, restaurar_orden),
    ]
