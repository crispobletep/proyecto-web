from django.db import migrations


IMAGE = "productos/catalogo/canalizacion-electrica/prensaestopas/prensaestopa-blanca.webp"


def actualizar_imagen_prensaestopas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    productos = Producto.objects.using(alias).filter(categoria__slug="prensaestopas")

    for producto in productos.iterator():
        producto.imagen = IMAGE
        producto.texto_alternativo = f"Prensaestopa blanca {producto.nombre.removeprefix('Prensaestopa ')}"
        producto.save(update_fields=["imagen", "texto_alternativo"])


class Migration(migrations.Migration):
    dependencies = [("core", "0089_agregar_prensaestopas_pg")]

    operations = [migrations.RunPython(actualizar_imagen_prensaestopas, migrations.RunPython.noop)]
