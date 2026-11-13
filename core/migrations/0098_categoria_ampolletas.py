from django.db import migrations


PRODUCT_SLUGS = (
    "ampolleta-led-megabright-a60-e27",
    "ampolleta-led-wellmax-e27-alta-potencia",
)


def organizar_ampolletas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="ampolletas",
        defaults={
            "nombre": "Ampolletas",
            "padre_id": iluminacion.pk,
            "orden": 3,
            "activa": True,
        },
    )

    Producto.objects.using(alias).filter(slug__in=PRODUCT_SLUGS).update(
        categoria_id=categoria.pk,
        publicado=True,
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0097_focos_color_como_variante")]

    operations = [migrations.RunPython(organizar_ampolletas, migrations.RunPython.noop)]
