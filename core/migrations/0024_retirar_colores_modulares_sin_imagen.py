from django.db import migrations


def retirar_colores_sin_respaldo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Imagen = apps.get_model("core", "ImagenProducto")

    producto = Producto.objects.using(alias).filter(
        slug="enchufe-triple-vertical-1016-a-stanford"
    ).first()
    if not producto:
        return

    codigos_sin_imagen = (
        "STF-ET-10/16-NE",
        "STF-ET-10/16-CH",
        "STF-ET-10/16-CA",
    )
    for variante in Variante.objects.using(alias).filter(
        producto_id=producto.pk,
        codigo__in=codigos_sin_imagen,
    ):
        for imagen in list(variante.imagenes_catalogo.all()):
            imagen.variantes.remove(variante)
            if not imagen.variantes.exists():
                imagen.delete(using=alias)

        EspecificacionVariante.objects.using(alias).filter(
            variante_id=variante.pk,
        ).delete()
        variante.codigo = None
        variante.imagen = ""
        variante.disponible = False
        variante.save(
            using=alias,
            update_fields=("codigo", "imagen", "disponible"),
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0023_separar_formatos_enchufes_stanford")]

    operations = [
        migrations.RunPython(retirar_colores_sin_respaldo, migrations.RunPython.noop),
    ]
