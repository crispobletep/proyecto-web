from django.db import migrations


def nombrar_modulos_stanford(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for producto in Producto.objects.using(alias).filter(
        categoria__slug="modulos-electricos",
        marca_nueva__slug="stanford",
    ):
        nombre = producto.nombre
        if "stanford" not in nombre.casefold():
            producto.nombre = f"{nombre} Stanford"
            producto.save(using=alias, update_fields=["nombre"])


class Migration(migrations.Migration):
    dependencies = [("core", "0021_corregir_galerias_cable_10_mm2")]

    operations = [migrations.RunPython(nombrar_modulos_stanford, migrations.RunPython.noop)]
