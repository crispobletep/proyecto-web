from django.db import migrations


ORDEN_TUBOS = (
    ("tubo-led-9w-3000k-forceman", 720),
    ("tubo-led-9w-3000k-fsl", 721),
    ("tubo-led-9w-6500k-forceman", 722),
    ("tubo-led-9w-6500k-fsl", 723),
    ("tubo-led-18w-3000k-forceman", 724),
    ("tubo-led-18w-3000k-fsl", 725),
    ("tubo-led-18w-6500k-forceman", 726),
    ("tubo-led-18w-6500k-fsl", 727),
)

ORDEN_ANTERIOR = {
    "tubo-led-9w-3000k-fsl": 720,
    "tubo-led-9w-6500k-forceman": 730,
    "tubo-led-9w-6500k-fsl": 740,
    "tubo-led-18w-3000k-forceman": 750,
    "tubo-led-18w-3000k-fsl": 760,
    "tubo-led-18w-6500k-forceman": 770,
    "tubo-led-18w-6500k-fsl": 780,
}

IMAGEN_FSL = "productos/catalogo/iluminacion/nuevos/tubo-fsl.png"
IMAGEN_FORCEMAN = "productos/catalogo/iluminacion/nuevos/tubo-forceman.png"


def publicar_y_ordenar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    categoria = Categoria.objects.using(alias).get(slug="tubos-led")
    marca_forceman = Marca.objects.using(alias).get(slug="forceman")
    nuevo, _ = Producto.objects.using(alias).update_or_create(
        slug="tubo-led-9w-3000k-forceman",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Tubo LED 9 W 3000 K",
            "marca": "",
            "marca_nueva_id": marca_forceman.pk,
            "subtitulo": "Tubos LED",
            "descripcion": (
                "Tubo LED Forceman de luz cálida 3000 K y 9 W, "
                "largo 60 cm. Imagen referencial del tubo LED."
            ),
            "imagen": IMAGEN_FORCEMAN,
            "texto_alternativo": "Tubo LED Forceman 9 W 3000 K",
            "etiqueta_visual": "FORCEMAN",
            "publicado": True,
        },
    )
    Variante.objects.using(alias).update_or_create(
        producto_id=nuevo.pk,
        nombre="9 W · 3000 K · 60 cm",
        defaults={"disponible": True, "orden": 10},
    )

    slugs_fsl = tuple(
        slug for slug in ORDEN_ANTERIOR if slug.endswith("-fsl")
    )
    Producto.objects.using(alias).filter(slug__in=slugs_fsl).update(
        publicado=True,
        imagen=IMAGEN_FSL,
    )
    for slug, orden in ORDEN_TUBOS:
        Producto.objects.using(alias).filter(slug=slug).update(
            publicado=True,
            orden=orden,
        )


def ocultar_y_restaurar_orden(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(alias).filter(
        slug="tubo-led-9w-3000k-forceman"
    ).update(publicado=False, orden=0)
    for slug, orden in ORDEN_ANTERIOR.items():
        Producto.objects.using(alias).filter(slug=slug).update(
            publicado=slug not in {
                "tubo-led-9w-3000k-fsl",
                "tubo-led-9w-6500k-fsl",
                "tubo-led-18w-3000k-fsl",
                "tubo-led-18w-6500k-fsl",
            },
            orden=orden,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0073_panel_cuadrado_avc_48w"),
    ]

    operations = [
        migrations.RunPython(publicar_y_ordenar, ocultar_y_restaurar_orden),
    ]
