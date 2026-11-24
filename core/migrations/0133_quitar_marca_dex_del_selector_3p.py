from django.db import migrations


def quitar_marca_dex_del_selector(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")

    Producto.objects.using(alias).filter(
        slug="selector-3p-dex-electric"
    ).update(
        nombre="Selector 3P",
        marca="",
        marca_nueva_id=None,
        subtitulo="Pulsadores y selectores",
        descripcion="Selector eléctrico 3P.",
        texto_alternativo="Selector eléctrico 3P",
        etiqueta_visual="SELECTOR 3P",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0132_quitar_emt_de_abrazadera_omega"),
    ]

    operations = [
        migrations.RunPython(
            quitar_marca_dex_del_selector,
            migrations.RunPython.noop,
        ),
    ]
