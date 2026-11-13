from django.db import migrations


TABLEROS = (18, 28, 36, 45, 54, 72, 100)


def corregir_categorias_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    ampolletas = Categoria.objects.using(alias).get(slug="ampolletas")
    Producto.objects.using(alias).filter(
        slug="ampolleta-led-fsl-gu10-6w"
    ).update(categoria_id=ampolletas.pk, publicado=True)

    tableros_electricos = Categoria.objects.using(alias).get(
        slug="tableros-electricos"
    )
    categoria_tableros, _ = Categoria.objects.using(alias).update_or_create(
        slug="tableros-metalicos",
        defaults={
            "nombre": "Tableros metálicos",
            "padre_id": tableros_electricos.pk,
            "orden": 1,
            "activa": True,
        },
    )

    for orden, polos in enumerate(TABLEROS, start=1):
        Producto.objects.using(alias).filter(
            slug=f"tablero-metalico-{polos}-polos"
        ).update(
            categoria_id=categoria_tableros.pk,
            publicado=True,
            orden=orden,
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0103_mejorar_imagenes_kalop_chint_fsl")]

    operations = [
        migrations.RunPython(corregir_categorias_catalogo, migrations.RunPython.noop),
    ]
