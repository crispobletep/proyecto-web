from django.db import migrations


def renombrar_mecanismos(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.filter(slug="mecanismos-electricos").update(
        nombre="Interruptores, enchufes y accesorios"
    )


def restaurar_nombre(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.filter(slug="mecanismos-electricos").update(
        nombre="Mecanismos eléctricos"
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0012_cotizacion_proyecto")]

    operations = [
        migrations.RunPython(renombrar_mecanismos, restaurar_nombre),
    ]
