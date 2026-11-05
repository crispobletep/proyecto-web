from django.db import migrations


ORDENES = (
    ("catalogo-staford-enchufesstf-es-10a-horizontal", 1810),
    ("catalogo-staford-enchufesstf-es-1016-horizontal", 1820),
    ("catalogo-staford-enchufesstf-ed-10a-horizontal", 1830),
    ("catalogo-staford-enchufesstf-ed-1016-horizontal", 1840),
    ("catalogo-staford-enchufesstf-et-10a-horizontal", 1850),
    ("catalogo-staford-enchufesstf-et-1016-horizontal", 1860),
)


def ordenar_productos(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    alias = schema_editor.connection.alias
    for slug, orden in ORDENES:
        Producto.objects.using(alias).filter(slug=slug).update(orden=orden)


def restaurar_orden(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    alias = schema_editor.connection.alias
    for posicion, (slug, _) in enumerate(
        sorted(ORDENES, key=lambda item: item[1], reverse=True)
    ):
        Producto.objects.using(alias).filter(slug=slug).update(
            orden=1810 + (len(ORDENES) - 1 - posicion) * 10
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0067_renombrar_tablero_plastico_generico"),
    ]

    operations = [
        migrations.RunPython(ordenar_productos, restaurar_orden),
    ]
