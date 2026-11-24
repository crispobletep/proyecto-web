from django.db import migrations


IMAGEN = (
    "productos/catalogo/herramientas/"
    "prensa-terminal-hidraulica.png"
)


def agregar_prensa_terminal_hidraulica(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    categoria = Categoria.objects.using(alias).get(
        slug="herramientas-manuales"
    )
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="prensa-terminal-hidraulica",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Prensa terminal hidráulica",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Herramientas manuales",
            "descripcion": (
                "Prensa terminal hidráulica manual para crimpar terminales. "
                "Se presenta en un estuche con un juego de matrices."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Prensa terminal hidráulica manual con matrices en estuche amarillo"
            ),
            "etiqueta_visual": "HERRAMIENTAS MANUALES",
            "orden": 9,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    Caracteristica.objects.using(alias).create(
        producto_id=producto.pk,
        texto="Incluye un juego de matrices y estuche de transporte.",
        orden=1,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0124_mejorar_imagenes_lauchas"),
    ]

    operations = [
        migrations.RunPython(
            agregar_prensa_terminal_hidraulica,
            migrations.RunPython.noop,
        ),
    ]
