from django.db import migrations


def identificar_horizontales(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    productos = Producto.objects.using(alias).filter(
        categoria__slug="enchufes-horizontales",
        marca_nueva__slug="stanford",
    )
    for producto in productos:
        if not producto.slug.endswith("-horizontal"):
            producto.slug = f"{producto.slug}-horizontal"
            producto.save(using=alias, update_fields=["slug"])
        for variante in Variante.objects.using(alias).filter(producto_id=producto.pk):
            if variante.codigo and not variante.codigo.endswith("-H"):
                variante.codigo = f"{variante.codigo}-H"
                variante.save(using=alias, update_fields=["codigo"])


class Migration(migrations.Migration):
    dependencies = [("core", "0018_separar_orientaciones_y_secciones_cable")]

    operations = [
        migrations.RunPython(identificar_horizontales, migrations.RunPython.noop),
    ]
