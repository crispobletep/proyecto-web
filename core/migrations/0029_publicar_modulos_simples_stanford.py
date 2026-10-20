from django.db import migrations


SLUGS_MODULOS_SOLICITADOS = (
    "catalogo-staford-enchufesstf-es-10a",
    "catalogo-staford-enchufesstf-es-1016",
)


def publicar_modulos_simples(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categoria = Categoria.objects.using(alias).filter(
        slug="enchufes-verticales"
    ).first()
    productos = Producto.objects.using(alias).filter(
        slug__in=SLUGS_MODULOS_SOLICITADOS
    )
    if not categoria or productos.count() != len(SLUGS_MODULOS_SOLICITADOS):
        raise RuntimeError("No se encontraron las fichas Stanford de 10 A y 10/16 A.")

    categoria.activa = True
    categoria.save(using=alias, update_fields=("activa",))
    productos.update(publicado=True)


def ocultar_modulos_simples(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    Producto.objects.using(alias).filter(
        slug__in=SLUGS_MODULOS_SOLICITADOS
    ).update(publicado=False)
    categoria = Categoria.objects.using(alias).filter(
        slug="enchufes-verticales"
    ).first()
    if categoria and not Producto.objects.using(alias).filter(
        categoria_id=categoria.pk,
        publicado=True,
    ).exists():
        categoria.activa = False
        categoria.save(using=alias, update_fields=("activa",))


class Migration(migrations.Migration):
    dependencies = [("core", "0028_relacionar_modulos_imagenes_y_variantes_pvc")]

    operations = [
        migrations.RunPython(publicar_modulos_simples, ocultar_modulos_simples),
    ]
