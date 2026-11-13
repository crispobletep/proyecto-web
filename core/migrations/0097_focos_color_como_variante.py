from django.db import migrations


def dejar_color_como_variante(apps, schema_editor):
    alias = schema_editor.connection.alias
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    EspecificacionVariante.objects.using(alias).filter(
        variante__producto__slug__in=(
            "foco-led-superficie-wellmax-eagle-eye",
            "foco-led-superficie-wellmax-eagle-eye-20w",
            "foco-led-superficie-wellmax-eagle-eye-30w",
        ),
        nombre="Potencia",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0096_focos_wellmax_por_potencia")]

    operations = [migrations.RunPython(dejar_color_como_variante, migrations.RunPython.noop)]
