from django.db import migrations


def vincular_marcas(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Marca = apps.get_model("core", "Marca")
    database = schema_editor.connection.alias
    for producto in Producto.objects.using(database).filter(marca_nueva__isnull=True).exclude(marca=""):
        coincidencias = list(Marca.objects.using(database).filter(
            nombre__iexact=producto.marca.strip()
        ).values_list("pk", flat=True)[:2])
        # Solo completar relaciones inequívocas; conservar el texto histórico.
        if len(coincidencias) == 1:
            Producto.objects.using(database).filter(pk=producto.pk).update(
                marca_nueva_id=coincidencias[0]
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0014_normalizar_nombre_comercial")]
    operations = [migrations.RunPython(vincular_marcas, migrations.RunPython.noop)]
