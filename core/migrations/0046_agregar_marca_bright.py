from django.db import migrations


def agregar_bright(apps, schema_editor):
    Marca = apps.get_model("core", "Marca")
    Marca.objects.using(schema_editor.connection.alias).get_or_create(
        slug="bright",
        defaults={"nombre": "Bright", "activa": True},
    )


def retirar_bright_si_vacia(apps, schema_editor):
    Marca = apps.get_model("core", "Marca")
    Marca.objects.using(schema_editor.connection.alias).filter(
        slug="bright",
        productos__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0045_corregir_marca_chint")]

    operations = [migrations.RunPython(agregar_bright, retirar_bright_si_vacia)]
