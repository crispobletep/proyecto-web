from django.db import migrations


SLUG_PREFIX = "proyector-area-led-"


def asignar_megabright(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")

    categoria = Categoria.objects.using(alias).get(slug="proyectores-area-led")
    marca = Marca.objects.using(alias).get(slug="megabright")
    Producto.objects.using(alias).filter(
        categoria_id=categoria.pk,
        slug__startswith=SLUG_PREFIX,
    ).update(marca="", marca_nueva_id=marca.pk)


def revertir_megabright(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categoria = Categoria.objects.using(alias).get(slug="proyectores-area-led")
    Producto.objects.using(alias).filter(
        categoria_id=categoria.pk,
        slug__startswith=SLUG_PREFIX,
    ).update(marca="", marca_nueva_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0069_agregar_instrumentos_uni_t"),
    ]

    operations = [
        migrations.RunPython(asignar_megabright, revertir_megabright),
    ]
