from django.db import migrations


def actualizar_texto_alternativo(apps, schema_editor):
    Proyecto = apps.get_model("core", "Proyecto")
    Proyecto.objects.using(schema_editor.connection.alias).filter(
        slug="edificios-mirador-azul"
    ).update(texto_alternativo="Vista exterior de las torres de Edificios Mirador Azul")


class Migration(migrations.Migration):
    dependencies = [("core", "0101_galeria_edificios_mirador_azul")]

    operations = [
        migrations.RunPython(actualizar_texto_alternativo, migrations.RunPython.noop),
    ]
