from django.db import migrations


IMAGEN = "productos/catalogo/herramientas/broca-paleta.png"
MEDIDAS = (
    ("7-8", "7/8", 75),
    ("3-4", "3/4", 76),
)


def agregar_medidas_broca_paleta(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    categoria = Categoria.objects.using(alias).get(slug="brocas-perforacion")

    for slug_medida, medida, orden in MEDIDAS:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=f"broca-paleta-{slug_medida}-pulg",
            defaults={
                "categoria_id": categoria.pk,
                "nombre": f"Broca paleta {medida}″",
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Brocas y perforación",
                "descripcion": (
                    "Broca paleta para perforación en madera, "
                    f"de {medida} pulgadas."
                ),
                "imagen": IMAGEN,
                "texto_alternativo": (
                    "Broca paleta para madera de "
                    f"{medida} pulgadas"
                ),
                "etiqueta_visual": "BROCAS Y PERFORACIÓN",
                "orden": orden,
                "publicado": True,
            },
        )

        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto="Tipo paleta para perforación en madera.",
            orden=1,
        )
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=f"Diámetro: {medida}″.",
            orden=2,
        )

        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre="Diámetro",
            valor=medida,
            unidad="pulg",
            orden=1,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0117_galeria_hospital_trabajador_achs"),
    ]

    operations = [
        migrations.RunPython(
            agregar_medidas_broca_paleta,
            migrations.RunPython.noop,
        ),
    ]
