from django.db import migrations


SLUGS_TUBOS = (
    "tubo-led-9w-3000k-forceman",
    "tubo-led-9w-3000k-fsl",
    "tubo-led-9w-6500k-forceman",
    "tubo-led-9w-6500k-fsl",
    "tubo-led-18w-3000k-forceman",
    "tubo-led-18w-3000k-fsl",
    "tubo-led-18w-6500k-forceman",
    "tubo-led-18w-6500k-fsl",
)
IMAGEN_FORCEMAN = "productos/catalogo/iluminacion/nuevos/tubo-forceman.png"
IMAGEN_FSL = "productos/catalogo/iluminacion/nuevos/tubo-fsl.png"
SLUGS_FSL = tuple(slug for slug in SLUGS_TUBOS if slug.endswith("-fsl"))


def unificar_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(alias).filter(slug__in=SLUGS_TUBOS).update(
        imagen=IMAGEN_FORCEMAN
    )


def restaurar_imagenes_fsl(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(alias).filter(slug__in=SLUGS_FSL).update(
        imagen=IMAGEN_FSL
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0074_publicar_tubos_fsl_y_forceman"),
    ]

    operations = [
        migrations.RunPython(unificar_imagenes, restaurar_imagenes_fsl),
    ]
