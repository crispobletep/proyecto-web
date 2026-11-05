from django.db import migrations


PARES = (
    (
        "gabinete-metalico-500x400x200-ip65-estandar",
        "gabinete-metalico-500x400x200-ip65-con-chasis",
    ),
    (
        "gabinete-metalico-600x400x200-ip65-estandar",
        "gabinete-metalico-600x400x200-ip65-con-chasis",
    ),
)


def intercambiar_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Imagen = apps.get_model("core", "ImagenProducto")

    for slug_sin_chasis, slug_con_chasis in PARES:
        sin_chasis = Producto.objects.using(alias).get(slug=slug_sin_chasis)
        con_chasis = Producto.objects.using(alias).get(slug=slug_con_chasis)
        imagen_sin_chasis = sin_chasis.imagen
        imagen_con_chasis = con_chasis.imagen

        sin_chasis.imagen = imagen_con_chasis
        con_chasis.imagen = imagen_sin_chasis
        sin_chasis.save(using=alias, update_fields=["imagen"])
        con_chasis.save(using=alias, update_fields=["imagen"])

        Imagen.objects.using(alias).filter(producto_id=sin_chasis.pk).update(
            imagen=imagen_con_chasis
        )
        Imagen.objects.using(alias).filter(producto_id=con_chasis.pk).update(
            imagen=imagen_sin_chasis
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0077_unificar_tableros_18_polos"),
    ]

    operations = [
        migrations.RunPython(intercambiar_imagenes, intercambiar_imagenes),
    ]
