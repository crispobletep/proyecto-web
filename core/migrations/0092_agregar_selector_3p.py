from django.db import migrations


IMAGE = "productos/catalogo/control-senalizacion/pulsadores/selector-2-posiciones.webp"


def agregar_selector_3p(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categoria = Categoria.objects.using(alias).get(slug="pulsadores")
    Producto.objects.using(alias).update_or_create(
        slug="selector-3p-dex-electric",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Selector 3P DEX Electric",
            "marca": "DEX Electric",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Pulsadores y selectores DEX Electric",
            "descripcion": "Selector DEX Electric, referencia 3P.",
            "imagen": IMAGE,
            "texto_alternativo": "Selector DEX Electric 3P",
            "etiqueta_visual": "DEX ELECTRIC",
            "orden": 855,
            "publicado": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0091_agregar_pulsadores_dex")]

    operations = [migrations.RunPython(agregar_selector_3p, migrations.RunPython.noop)]
