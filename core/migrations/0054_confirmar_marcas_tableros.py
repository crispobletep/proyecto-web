from django.db import migrations


MARCAS_ANTERIORES = {
    "tablero-plastico-forceman": "forceman",
    "tablero-plastico-forceman-4-modulos": "forceman",
    "tablero-sobrepuesto-lexo-12-polos": "lexo",
    "tablero-sobrepuesto-lexo-18-polos": "lexo",
}


def marcar_sin_confirmar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(alias).filter(
        categoria__slug="tableros-plasticos"
    ).update(marca="", marca_nueva_id=None)


def restaurar_marcas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    for slug, marca_slug in MARCAS_ANTERIORES.items():
        marca = Marca.objects.using(alias).get(slug=marca_slug)
        Producto.objects.using(alias).filter(slug=slug).update(
            marca="", marca_nueva_id=marca.pk
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0053_renombrar_familia_enchufes_placas"),
    ]

    operations = [
        migrations.RunPython(marcar_sin_confirmar, restaurar_marcas),
    ]
