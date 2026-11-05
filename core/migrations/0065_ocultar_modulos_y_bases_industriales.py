from django.db import migrations


SLUGS = ("modulos-industriales", "bases-industriales")


def ocultar_categorias(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.using(schema_editor.connection.alias).filter(
        slug__in=SLUGS
    ).update(activa=False)


def restaurar_categorias(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.using(schema_editor.connection.alias).filter(
        slug__in=SLUGS
    ).update(activa=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0064_agregar_hembra_sobrepuesta"),
    ]

    operations = [
        migrations.RunPython(ocultar_categorias, restaurar_categorias),
    ]
