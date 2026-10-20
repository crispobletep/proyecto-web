from django.db import migrations


PRODUCT_SLUG = "catalogo-staford-enchufesstf-ed-1016-horizontal"
VARIANT_WHITE = "STF-ED-10/16-BL-H"
VARIANT_CHAMPAGNE = "STF-ED-10/16-CH-H"

WHITE_IMAGE = (
    "productos/catalogo/enchufes/"
    "enchufe-1016-doble-blanco-alternativa.png"
)
CHAMPAGNE_IMAGE = (
    "productos/catalogo/enchufes/enchufe-1016-doble-champagne.png"
)
OLD_WHITE_IMAGE = "productos/catalogo/enchufes/enchufe-1016-doble-blanco.png"
OLD_WHITE_GALLERY_KEY = "enchufe-1016-doble-blanco-alternativa"


def set_gallery_image(Imagen, alias, producto, variante, key, path, order=None):
    order = variante.orden if order is None else order
    image, _ = Imagen.objects.using(alias).get_or_create(
        clave=key,
        defaults={
            "producto_id": producto.pk,
            "imagen": path,
            "texto_alternativo": f"{producto.nombre}, color {variante.nombre}",
            "orden": order,
        },
    )
    image.producto_id = producto.pk
    image.imagen = path
    image.texto_alternativo = f"{producto.nombre}, color {variante.nombre}"
    image.orden = order
    image.save(
        using=alias,
        update_fields=("producto", "imagen", "texto_alternativo", "orden"),
    )
    image.variantes.set([variante.pk])


def corregir_colores(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    producto = Producto.objects.using(alias).filter(slug=PRODUCT_SLUG).first()
    if not producto:
        return

    blanco = Variante.objects.using(alias).filter(
        producto_id=producto.pk,
        codigo=VARIANT_WHITE,
    ).first()
    champagne = Variante.objects.using(alias).filter(
        producto_id=producto.pk,
        codigo=VARIANT_CHAMPAGNE,
    ).first()

    if blanco:
        blanco.imagen = WHITE_IMAGE
        blanco.save(using=alias, update_fields=("imagen",))
        producto.imagen = WHITE_IMAGE
        producto.save(using=alias, update_fields=("imagen",))
        set_gallery_image(
            Imagen,
            alias,
            producto,
            blanco,
            f"catalogo-placa-{producto.pk}-bl",
            WHITE_IMAGE,
        )
        Imagen.objects.using(alias).filter(clave=OLD_WHITE_GALLERY_KEY).delete()

    if champagne:
        champagne.imagen = CHAMPAGNE_IMAGE
        champagne.disponible = True
        champagne.save(using=alias, update_fields=("imagen", "disponible"))
        set_gallery_image(
            Imagen,
            alias,
            producto,
            champagne,
            f"catalogo-placa-{producto.pk}-ch",
            CHAMPAGNE_IMAGE,
        )


def revertir_colores(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    producto = Producto.objects.using(alias).filter(slug=PRODUCT_SLUG).first()
    if not producto:
        return

    blanco = Variante.objects.using(alias).filter(
        producto_id=producto.pk,
        codigo=VARIANT_WHITE,
    ).first()
    champagne = Variante.objects.using(alias).filter(
        producto_id=producto.pk,
        codigo=VARIANT_CHAMPAGNE,
    ).first()

    if blanco:
        blanco.imagen = OLD_WHITE_IMAGE
        blanco.save(using=alias, update_fields=("imagen",))
        producto.imagen = OLD_WHITE_IMAGE
        producto.save(using=alias, update_fields=("imagen",))
        set_gallery_image(
            Imagen,
            alias,
            producto,
            blanco,
            f"catalogo-placa-{producto.pk}-bl",
            OLD_WHITE_IMAGE,
        )
        set_gallery_image(
            Imagen,
            alias,
            producto,
            blanco,
            OLD_WHITE_GALLERY_KEY,
            WHITE_IMAGE,
            order=10 + blanco.orden,
        )

    if champagne:
        champagne.imagen = ""
        champagne.disponible = False
        champagne.save(using=alias, update_fields=("imagen", "disponible"))
        Imagen.objects.using(alias).filter(
            clave=f"catalogo-placa-{producto.pk}-ch",
        ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0031_catalogo_modulos_tomacorriente_stanford")]

    operations = [
        migrations.RunPython(corregir_colores, revertir_colores),
    ]
