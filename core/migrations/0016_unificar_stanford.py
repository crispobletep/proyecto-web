import re

from django.db import migrations


def unificar_stanford(apps, schema_editor):
    alias = schema_editor.connection.alias
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    anteriores = Marca.objects.using(alias).filter(nombre__iexact="staford")
    if anteriores.exists():
        marca, _ = Marca.objects.using(alias).get_or_create(
            slug="stanford", defaults={"nombre": "Stanford"}
        )
        for anterior in anteriores:
            Producto.objects.using(alias).filter(marca_nueva_id=anterior.pk).update(marca_nueva_id=marca.pk)
            if anterior.logo and not marca.logo:
                marca.logo = anterior.logo
                marca.save(using=alias, update_fields=["logo"])
            anterior.delete(using=alias)

    # Mantener identificadores, códigos e imágenes; corregir solo textos visibles.
    campos = {
        "Producto": ("nombre", "marca", "descripcion", "subtitulo", "texto_alternativo", "etiqueta_visual"),
        "VarianteProducto": ("nombre",),
        "CaracteristicaProducto": ("texto",),
        "ImagenProducto": ("texto_alternativo",),
    }
    for modelo, nombres in campos.items():
        Model = apps.get_model("core", modelo)
        for objeto in Model.objects.using(alias).all():
            cambios = []
            for nombre in nombres:
                valor = getattr(objeto, nombre)
                corregido = re.sub(r"\bstaford\b", "Stanford", valor, flags=re.IGNORECASE)
                if valor != corregido:
                    setattr(objeto, nombre, corregido)
                    cambios.append(nombre)
            if cambios:
                objeto.save(using=alias, update_fields=cambios)


class Migration(migrations.Migration):
    dependencies = [("core", "0015_vincular_marcas_anteriores")]
    operations = [migrations.RunPython(unificar_stanford, migrations.RunPython.noop)]
