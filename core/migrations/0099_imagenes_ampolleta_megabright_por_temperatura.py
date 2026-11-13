from django.db import migrations


def asignar_imagenes_por_temperatura(apps, schema_editor):
    alias = schema_editor.connection.alias
    Variante = apps.get_model("core", "VarianteProducto")
    base = "productos/catalogo/iluminacion/ampolletas-nuevas/megabright-a60-e27-"
    variantes = Variante.objects.using(alias).filter(
        producto__slug="ampolleta-led-megabright-a60-e27",
    )
    variantes.filter(nombre__icontains="cálida").update(imagen=f"{base}calida.png")
    variantes.filter(nombre__icontains="fría").update(imagen=f"{base}fria.png")


class Migration(migrations.Migration):
    dependencies = [("core", "0098_categoria_ampolletas")]

    operations = [
        migrations.RunPython(asignar_imagenes_por_temperatura, migrations.RunPython.noop),
    ]
