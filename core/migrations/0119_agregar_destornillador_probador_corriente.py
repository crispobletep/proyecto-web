from django.db import migrations


IMAGEN = (
    "productos/catalogo/herramientas/"
    "destornillador-probador-corriente.png"
)


def agregar_destornillador_probador(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    categoria = Categoria.objects.using(alias).get(
        slug="herramientas-manuales"
    )
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="destornillador-probador-de-corriente",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Destornillador probador de corriente",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Herramientas manuales",
            "descripcion": (
                "Destornillador probador para verificar la presencia "
                "de tensión eléctrica."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Destornillador probador de corriente con mango transparente"
            ),
            "etiqueta_visual": "HERRAMIENTAS MANUALES",
            "orden": 6,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    Caracteristica.objects.using(alias).create(
        producto_id=producto.pk,
        texto="Formato de destornillador con indicador visual de tensión.",
        orden=1,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0118_agregar_medidas_broca_paleta"),
    ]

    operations = [
        migrations.RunPython(
            agregar_destornillador_probador,
            migrations.RunPython.noop,
        ),
    ]
