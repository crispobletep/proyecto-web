from django.db import migrations


def marcar_base_por_confirmar(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(
        slug="base-sobrepuesta-panel-led-1203x303-v-plb-5102",
    ).update(marca="Marca por confirmar", marca_nueva_id=None)


def restaurar_marca_yell_max(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Marca = apps.get_model("core", "Marca")
    marca = Marca.objects.using(alias).filter(slug="yell-max").first()
    if marca:
        Producto.objects.using(alias).filter(
            slug="base-sobrepuesta-panel-led-1203x303-v-plb-5102",
        ).update(marca="", marca_nueva_id=marca.pk)


class Migration(migrations.Migration):
    dependencies = [("core", "0106_imagenes_focos_wellmax_por_color")]

    operations = [migrations.RunPython(marcar_base_por_confirmar, restaurar_marca_yell_max)]
