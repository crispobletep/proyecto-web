from django.db import migrations


def renombrar(apps, schema_editor):
    Marca = apps.get_model("core", "Marca")
    Marca.objects.using(schema_editor.connection.alias).filter(
        slug="bright"
    ).update(nombre="Megabright", slug="megabright", activa=True)


def revertir(apps, schema_editor):
    Marca = apps.get_model("core", "Marca")
    Marca.objects.using(schema_editor.connection.alias).filter(
        slug="megabright"
    ).update(nombre="Bright", slug="bright", activa=True)


class Migration(migrations.Migration):
    dependencies = [("core", "0047_corregir_poder_corte_chint_2p")]

    operations = [migrations.RunPython(renombrar, revertir)]
