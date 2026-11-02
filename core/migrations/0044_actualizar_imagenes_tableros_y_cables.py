from django.db import migrations


IMAGENES = {
    "tablero-plastico-36-vias": "productos/catalogo/tableros-cnc/tablero-36-vias-producto.png",
    "tablero-plastico-forceman": "productos/catalogo/tableros-cnc/tablero-forceman.png",
    "tablero-sobrepuesto-lexo-18-polos": "productos/catalogo/tableros-cnc/tablero-lexo-18-polos.png",
    "tablero-embutido-dex-18-polos": "productos/catalogo/tableros-cnc/tablero-dex-18-polos.png",
    "tablero-plastico-12-vias": "productos/catalogo/tableros-cnc/tablero-12-vias.png",
    "tablero-sobrepuesto-lexo-12-polos": "productos/catalogo/tableros-cnc/tablero-lexo-12-polos.png",
    "tablero-plastico-8-vias": "productos/catalogo/tableros-cnc/tablero-8-vias.png",
    "tablero-sobrepuesto-dex-6-polos": "productos/catalogo/tableros-cnc/tablero-dex-6-polos.png",
    "tablero-plastico-forceman-4-modulos": "productos/catalogo/tableros-cnc/tablero-forceman-4-modulos.png",
}


def actualizar_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for slug, imagen in IMAGENES.items():
        Producto.objects.using(alias).filter(slug=slug).update(imagen=imagen)
    Producto.objects.using(alias).filter(categoria__slug="cordones-electricos").update(
        imagen="productos/catalogo/tableros-cnc/cordon-electrico-negro-producto.png"
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0043_agregar_tableros_y_cordones")]
    operations = [migrations.RunPython(actualizar_imagenes, migrations.RunPython.noop)]
