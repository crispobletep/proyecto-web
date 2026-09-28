from django.db import migrations


def eliminar_variantes_plafones(apps, schema_editor):
    alias = schema_editor.connection.alias
    Cotizacion = apps.get_model("core", "Cotizacion")
    Producto = apps.get_model("core", "Producto")
    VarianteProducto = apps.get_model("core", "VarianteProducto")

    productos = Producto.objects.using(alias).filter(
        categoria__slug="plafones-led"
    ).values_list("pk", flat=True)
    variantes = VarianteProducto.objects.using(alias).filter(
        producto_id__in=productos
    )

    Cotizacion.objects.using(alias).filter(
        variante__in=variantes
    ).update(variante=None)
    variantes.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_proyecto"),
    ]

    operations = [
        migrations.RunPython(
            eliminar_variantes_plafones,
            migrations.RunPython.noop,
        ),
    ]
