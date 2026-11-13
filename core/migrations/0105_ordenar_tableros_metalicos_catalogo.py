from django.db import migrations


TABLEROS = (18, 28, 36, 45, 54, 72, 100)


def ordenar_tableros(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")

    for orden, polos in enumerate(TABLEROS, start=1540):
        Producto.objects.using(alias).filter(
            slug=f"tablero-metalico-{polos}-polos"
        ).update(orden=orden)


class Migration(migrations.Migration):
    dependencies = [("core", "0104_hacer_visibles_ampolletas_fsl_y_tableros_metalicos")]

    operations = [
        migrations.RunPython(ordenar_tableros, migrations.RunPython.noop),
    ]
