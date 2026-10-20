from django.db import migrations


def corregir_imagen_10mm2(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    alias = schema_editor.connection.alias
    producto = Producto.objects.using(alias).filter(
        slug="cable-flexible-libre-halogenos-10mm2"
    ).first()
    if producto:
        producto.imagen = (
            "productos/catalogo/conductores-conexiones/cables/"
            "cable-libre-halogeno-6-negro.png"
        )
        producto.texto_alternativo = "Cable flexible libre de halógenos de 10 mm²"
        producto.save(using=alias, update_fields=["imagen", "texto_alternativo"])


class Migration(migrations.Migration):
    dependencies = [("core", "0019_identificadores_enchufes_horizontales")]

    operations = [migrations.RunPython(corregir_imagen_10mm2, migrations.RunPython.noop)]
