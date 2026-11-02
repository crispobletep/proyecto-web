import re

from django.db import migrations


def quitar_marca_del_nombre(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    alias = schema_editor.connection.alias

    for producto in Producto.objects.using(alias).select_related("marca_nueva").iterator():
        marca = producto.marca_nueva.nombre if producto.marca_nueva_id else producto.marca
        if not marca or not re.search(rf"\b{re.escape(marca)}\b", producto.nombre, flags=re.IGNORECASE):
            continue

        nombre = re.sub(rf"\s*\b{re.escape(marca)}\b\s*", " ", producto.nombre, flags=re.IGNORECASE)
        nombre = re.sub(r"\s+", " ", nombre).strip(" -–—,.")
        producto.nombre = nombre
        producto.texto_alternativo = nombre
        producto.save(using=alias, update_fields=("nombre", "texto_alternativo"))


class Migration(migrations.Migration):
    dependencies = [("core", "0039_ajustar_automaticos_y_diferenciales")]
    operations = [migrations.RunPython(quitar_marca_del_nombre, migrations.RunPython.noop)]
