from django.db import migrations


PRODUCTOS_LISOS = (
    "caja-estanca-80x80x40-lisa",
    "caja-estanca-100x100x70-lisa-ip65",
    "caja-estanca-170x140x85-lisa",
    "caja-estanca-220x170x95-lisa-ip55",
)


def corregir_texto(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    alias = schema_editor.connection.alias
    ids = Producto.objects.using(alias).filter(slug__in=PRODUCTOS_LISOS).values_list("pk", flat=True)
    Caracteristica.objects.using(alias).filter(
        producto_id__in=ids,
        orden=2,
        texto="Entradas laterales lisa.",
    ).update(texto="Entradas laterales lisas.")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0058_cajas_estancas_una_tarjeta_por_medida"),
    ]

    operations = [
        migrations.RunPython(corregir_texto, migrations.RunPython.noop),
    ]
