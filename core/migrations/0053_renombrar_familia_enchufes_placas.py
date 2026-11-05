from django.db import migrations


def renombrar_familia(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.using(schema_editor.connection.alias).filter(
        slug="mecanismos-electricos"
    ).update(nombre="Enchufes y placas")


def restaurar_nombre(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.using(schema_editor.connection.alias).filter(
        slug="mecanismos-electricos"
    ).update(nombre="Interruptores, enchufes y accesorios")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0052_simplificar_filtros_iluminacion"),
    ]

    operations = [
        migrations.RunPython(renombrar_familia, restaurar_nombre),
    ]
