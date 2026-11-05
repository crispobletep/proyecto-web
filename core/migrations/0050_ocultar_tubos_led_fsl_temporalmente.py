from django.db import migrations


SLUGS_TUBOS_FSL = (
    "tubo-led-9w-3000k-fsl",
    "tubo-led-9w-6500k-fsl",
    "tubo-led-18w-3000k-fsl",
    "tubo-led-18w-6500k-fsl",
)


def ocultar_tubos_fsl(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.filter(slug__in=SLUGS_TUBOS_FSL).update(publicado=False)


def volver_a_publicar_tubos_fsl(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.filter(slug__in=SLUGS_TUBOS_FSL).update(publicado=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0049_completar_fichas_uni_t"),
    ]

    operations = [
        migrations.RunPython(ocultar_tubos_fsl, volver_a_publicar_tubos_fsl),
    ]
