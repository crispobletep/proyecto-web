from django.db import migrations


def actualizar_nombre(apps, schema_editor):
    Proyecto = apps.get_model("core", "Proyecto")
    for proyecto in Proyecto.objects.filter(
        descripcion__contains="PH Servicios Electrónicos"
    ):
        proyecto.descripcion = proyecto.descripcion.replace(
            "PH Servicios Electrónicos", "PH Servicios Eléctricos"
        )
        proyecto.save(update_fields=["descripcion"])


def restaurar_nombre(apps, schema_editor):
    Proyecto = apps.get_model("core", "Proyecto")
    for proyecto in Proyecto.objects.filter(
        descripcion__contains="PH Servicios Eléctricos"
    ):
        proyecto.descripcion = proyecto.descripcion.replace(
            "PH Servicios Eléctricos", "PH Servicios Electrónicos"
        )
        proyecto.save(update_fields=["descripcion"])


class Migration(migrations.Migration):
    dependencies = [("core", "0013_renombrar_mecanismos_electricos")]

    operations = [migrations.RunPython(actualizar_nombre, restaurar_nombre)]
