from django.db import migrations


ORDENES_ORIGINALES = {
    "catalogo-staford-enchufesstf-es-10a": 379,
    "catalogo-staford-enchufesstf-es-1016": 409,
}


def priorizar_modulos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    productos = Producto.objects.using(alias).filter(
        slug__in=ORDENES_ORIGINALES
    )
    if productos.count() != len(ORDENES_ORIGINALES):
        raise RuntimeError("No se encontraron ambas fichas de enchufes modulares Stanford.")
    productos.update(orden=69)


def restaurar_orden(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for slug, orden in ORDENES_ORIGINALES.items():
        Producto.objects.using(alias).filter(slug=slug).update(orden=orden)


class Migration(migrations.Migration):
    dependencies = [("core", "0029_publicar_modulos_simples_stanford")]

    operations = [
        migrations.RunPython(priorizar_modulos, restaurar_orden),
    ]
