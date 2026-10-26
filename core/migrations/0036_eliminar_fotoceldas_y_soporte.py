from django.db import migrations
from django.db.models import Q


CODIGOS = (
    "CHT-NY01",
    "STF-FC10",
    "LEG-412899",
    "CHT-BY01",
    "STF-BF10",
    "SOP-FC01",
)


def eliminar_fichas_sin_historial(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    ids = list(
        Variante.objects.using(alias)
        .filter(codigo__in=CODIGOS)
        .values_list("producto_id", flat=True)
        .distinct()
    )
    for producto in Producto.objects.using(alias).filter(pk__in=ids):
        tiene_historial = Cotizacion.objects.using(alias).filter(
            Q(producto_id=producto.pk) | Q(variante__producto_id=producto.pk)
        ).exists()
        if tiene_historial:
            producto.publicado = False
            producto.save(using=alias, update_fields=("publicado",))
            Variante.objects.using(alias).filter(
                producto_id=producto.pk
            ).update(disponible=False)
        else:
            producto.delete(using=alias)


class Migration(migrations.Migration):
    dependencies = [("core", "0035_ajustes_catalogo_a_peticion")]

    operations = [migrations.RunPython(eliminar_fichas_sin_historial, migrations.RunPython.noop)]
