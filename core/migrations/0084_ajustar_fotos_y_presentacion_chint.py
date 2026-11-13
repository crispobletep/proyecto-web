from django.db import migrations


SHUNT_IMAGE = "productos/catalogo/protecciones/nuevos/chint-shunt-x1-blanco.png"


def ajustar_presentacion_chint(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    shunt = Producto.objects.using(alias).get(slug="disparador-shunt-chint-sht-x1")
    shunt.imagen = SHUNT_IMAGE
    shunt.texto_alternativo = "Bobina de disparo CHINT SHT-X1 aislada sobre fondo blanco"
    shunt.save(using=alias, update_fields=("imagen", "texto_alternativo"))

    diferencial = Producto.objects.using(alias).get(
        slug="diferencial-magnetotermico-chint-nb2le-1pn"
    )
    diferencial.nombre = "Interruptor diferencial CHINT NB2LE 1P+N"
    diferencial.save(using=alias, update_fields=("nombre",))

    ordenes = {
        "Curva C · 10 A": 1,
        "Curva C · 16 A": 2,
        "Curva C · 20 A": 3,
        "Curva C · 25 A": 4,
        "Curva C · 32 A": 5,
        "Curva C · 40 A": 6,
    }
    for nombre, orden in ordenes.items():
        Variante.objects.using(alias).filter(
            producto_id=diferencial.pk,
            nombre=nombre,
        ).update(orden=orden)


class Migration(migrations.Migration):
    dependencies = [("core", "0083_nuevos_productos_catalogo_noviembre")]
    operations = [migrations.RunPython(ajustar_presentacion_chint, migrations.RunPython.noop)]
