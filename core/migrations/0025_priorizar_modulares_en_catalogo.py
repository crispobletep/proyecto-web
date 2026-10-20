from django.db import migrations


PARES = (
    ("catalogo-staford-enchufesstf-es-10a", "catalogo-staford-enchufesstf-es-10a-horizontal"),
    ("catalogo-staford-enchufesstf-ed-10a", "catalogo-staford-enchufesstf-ed-10a-horizontal"),
    ("catalogo-staford-enchufesstf-et-10a", "catalogo-staford-enchufesstf-et-10a-horizontal"),
    ("catalogo-staford-enchufesstf-es-1016", "catalogo-staford-enchufesstf-es-1016-horizontal"),
    ("catalogo-staford-enchufesstf-ed-1016", "catalogo-staford-enchufesstf-ed-1016-horizontal"),
    ("enchufe-triple-vertical-1016-a-stanford", "catalogo-staford-enchufesstf-et-1016-horizontal"),
)


def priorizar_modulares(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for slug_modular, slug_placa in PARES:
        modular = Producto.objects.using(alias).filter(slug=slug_modular).first()
        placa = Producto.objects.using(alias).filter(slug=slug_placa).first()
        if not modular or not placa:
            continue
        modular.orden = max(placa.orden - 1, 0)
        modular.save(using=alias, update_fields=["orden"])


class Migration(migrations.Migration):
    dependencies = [("core", "0024_retirar_colores_modulares_sin_imagen")]

    operations = [
        migrations.RunPython(priorizar_modulares, migrations.RunPython.noop),
    ]
