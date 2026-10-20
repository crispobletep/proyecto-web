from django.db import migrations


PRODUCTS = (
    {
        "slug": "catalogo-staford-enchufesstf-ed-10a-horizontal",
        "white_code": "STF-ED-10A-BL-H",
        "champagne_code": "STF-ED-10A-CH-H",
        "cafe_code": "STF-ED-10A-CA-H",
        "white_old": "productos/catalogo/enchufes/enchufe-10a-doble-blanco.png",
        "white_new": "productos/catalogo/enchufes/enchufe-10a-doble-blanco-alternativa.png",
        "champagne_old": "productos/catalogo/enchufes/enchufe-10a-doble-champagne.png",
        "champagne_old_available": True,
        "champagne_new": "productos/catalogo/enchufes/enchufe-10a-doble-champagne-placa.png",
        "cafe_old": "",
        "cafe_old_available": False,
        "cafe_new": "productos/catalogo/enchufes/enchufe-10a-doble-cafe.png",
        "white_extra_key": "enchufe-10a-doble-blanco-alternativa",
    },
    {
        "slug": "catalogo-staford-enchufesstf-et-10a-horizontal",
        "white_code": "STF-ET-10A-BL-H",
        "champagne_code": "STF-ET-10A-CH-H",
        "cafe_code": "STF-ET-10A-CA-H",
        "white_old": "productos/catalogo/enchufes/enchufe-10a-triple-blanco.png",
        "white_new": "productos/catalogo/enchufes/enchufe-10a-triple-blanco-alternativa.png",
        "champagne_old": "",
        "champagne_old_available": False,
        "champagne_new": "productos/catalogo/enchufes/enchufe-10a-triple-champagne-placa.png",
        "cafe_old": "productos/catalogo/enchufes/enchufe-triple-cafe.png",
        "cafe_old_available": True,
        "cafe_new": "productos/catalogo/enchufes/enchufe-triple-cafe.png",
        "white_extra_key": "enchufe-10a-triple-blanco-alternativa",
    },
)


def guardar_foto(Imagen, alias, producto, variante, clave, ruta, orden=None):
    orden = variante.orden if orden is None else orden
    imagen, _ = Imagen.objects.using(alias).get_or_create(
        clave=clave,
        defaults={
            "producto_id": producto.pk,
            "imagen": ruta,
            "texto_alternativo": f"{producto.nombre}, color {variante.nombre}",
            "orden": orden,
        },
    )
    imagen.producto_id = producto.pk
    imagen.imagen = ruta
    imagen.texto_alternativo = f"{producto.nombre}, color {variante.nombre}"
    imagen.orden = orden
    imagen.save(
        using=alias,
        update_fields=("producto", "imagen", "texto_alternativo", "orden"),
    )
    imagen.variantes.set([variante.pk])


def actualizar_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    for datos in PRODUCTS:
        producto = Producto.objects.using(alias).filter(slug=datos["slug"]).first()
        if not producto:
            continue

        variantes = {
            codigo: Variante.objects.using(alias).filter(
                producto_id=producto.pk,
                codigo=codigo,
            ).first()
            for codigo in (
                datos["white_code"],
                datos["champagne_code"],
                datos["cafe_code"],
            )
        }

        blanco = variantes[datos["white_code"]]
        if blanco:
            blanco.imagen = datos["white_new"]
            blanco.save(using=alias, update_fields=("imagen",))
            producto.imagen = datos["white_new"]
            producto.save(using=alias, update_fields=("imagen",))
            guardar_foto(
                Imagen,
                alias,
                producto,
                blanco,
                f"catalogo-placa-{producto.pk}-bl",
                datos["white_new"],
            )
            Imagen.objects.using(alias).filter(
                clave=datos["white_extra_key"],
            ).delete()

        champagne = variantes[datos["champagne_code"]]
        if champagne:
            champagne.imagen = datos["champagne_new"]
            champagne.disponible = True
            champagne.save(using=alias, update_fields=("imagen", "disponible"))
            guardar_foto(
                Imagen,
                alias,
                producto,
                champagne,
                f"catalogo-placa-{producto.pk}-ch",
                datos["champagne_new"],
            )

        cafe = variantes[datos["cafe_code"]]
        if cafe:
            cafe.imagen = datos["cafe_new"]
            cafe.disponible = True
            cafe.save(using=alias, update_fields=("imagen", "disponible"))
            guardar_foto(
                Imagen,
                alias,
                producto,
                cafe,
                f"catalogo-placa-{producto.pk}-ca",
                datos["cafe_new"],
            )


def revertir_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    for datos in PRODUCTS:
        producto = Producto.objects.using(alias).filter(slug=datos["slug"]).first()
        if not producto:
            continue

        blanco = Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            codigo=datos["white_code"],
        ).first()
        if blanco:
            blanco.imagen = datos["white_old"]
            blanco.save(using=alias, update_fields=("imagen",))
            producto.imagen = datos["white_old"]
            producto.save(using=alias, update_fields=("imagen",))
            guardar_foto(
                Imagen,
                alias,
                producto,
                blanco,
                f"catalogo-placa-{producto.pk}-bl",
                datos["white_old"],
            )
            guardar_foto(
                Imagen,
                alias,
                producto,
                blanco,
                datos["white_extra_key"],
                datos["white_new"],
                orden=10 + blanco.orden,
            )

        champagne = Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            codigo=datos["champagne_code"],
        ).first()
        if champagne:
            champagne.imagen = datos["champagne_old"]
            champagne.disponible = datos["champagne_old_available"]
            champagne.save(using=alias, update_fields=("imagen", "disponible"))
            if datos["champagne_old_available"]:
                guardar_foto(
                    Imagen,
                    alias,
                    producto,
                    champagne,
                    f"catalogo-placa-{producto.pk}-ch",
                    datos["champagne_old"],
                )
            else:
                Imagen.objects.using(alias).filter(
                    clave=f"catalogo-placa-{producto.pk}-ch",
                ).delete()

        cafe = Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            codigo=datos["cafe_code"],
        ).first()
        if cafe:
            cafe.imagen = datos["cafe_old"]
            cafe.disponible = datos["cafe_old_available"]
            cafe.save(using=alias, update_fields=("imagen", "disponible"))
            if datos["cafe_old_available"]:
                guardar_foto(
                    Imagen,
                    alias,
                    producto,
                    cafe,
                    f"catalogo-placa-{producto.pk}-ca",
                    datos["cafe_old"],
                )
            else:
                Imagen.objects.using(alias).filter(
                    clave=f"catalogo-placa-{producto.pk}-ca",
                ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0032_corregir_colores_enchufe_doble_1016")]

    operations = [
        migrations.RunPython(actualizar_imagenes, revertir_imagenes),
    ]
