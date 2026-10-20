from django.db import migrations


def ocultar_modulares(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categoria = Categoria.objects.using(alias).filter(slug="enchufes-verticales").first()
    if not categoria:
        return

    Producto.objects.using(alias).filter(categoria_id=categoria.pk).update(publicado=False)
    categoria.activa = False
    categoria.save(using=alias, update_fields=["activa"])


class Migration(migrations.Migration):
    dependencies = [("core", "0025_priorizar_modulares_en_catalogo")]

    operations = [
        migrations.RunPython(ocultar_modulares, migrations.RunPython.noop),
    ]
