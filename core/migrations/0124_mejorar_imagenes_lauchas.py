from django.db import migrations


IMAGENES = {
    "laucha-electrica-150-mm": (
        "productos/catalogo/herramientas/laucha-electrica-150mm.jpg"
    ),
    "cinta-pasacable-kalop-profesional": (
        "productos/catalogo/herramientas/"
        "cinta-pasacable-kalop-profesional.jpg"
    ),
}


def mejorar_imagenes_lauchas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")

    for slug, imagen in IMAGENES.items():
        Producto.objects.using(alias).filter(slug=slug).update(
            imagen=imagen
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0123_agregar_baliza_giratoria_lexo"),
    ]

    operations = [
        migrations.RunPython(
            mejorar_imagenes_lauchas,
            migrations.RunPython.noop,
        ),
    ]
