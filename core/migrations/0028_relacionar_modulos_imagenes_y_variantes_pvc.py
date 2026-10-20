from django.db import migrations


PVC_SLUG = "catalogo-canalizacion-electricacanalizacion-electricasalida-caja-pvcpng"
PVC_IMAGE = (
    "productos/catalogo/canalizacion-electrica/"
    "salida-caja-pvc-referencia-recortada.png"
)
PVC_OLD_VARIANT_IMAGE = "productos/catalogo/canalizacion-electrica/salida-caja-pvc.png"

TRIPLE_10A_SLUG = "catalogo-staford-enchufesstf-et-10a-horizontal"
TRIPLE_10A_CAFE = "STF-ET-10A-CA-H"
TRIPLE_10A_CHAMPAGNE = "STF-ET-10A-CH-H"
TRIPLE_CAFE_IMAGE = "productos/catalogo/enchufes/enchufe-triple-cafe.png"
TRIPLE_OLD_CHAMPAGNE_IMAGE = "productos/catalogo/enchufes/enchufe-10a-triple-champagne.png"

MODULO_ENCHUFE_IMAGENES = (
    (
        "catalogo-staford-enchufesstf-es-10a",
        "STF-ES-10A-BL",
        "STF-ES-10A-NE",
        "productos/catalogo/staford-enchufes/staford-simple-10a-blanco.png",
        "productos/catalogo/staford-enchufes/staford-simple-10a-negro.png",
        "productos/catalogo/staford-enchufes/staford-modulo-simple-10a-blanco.png",
        "productos/catalogo/staford-enchufes/staford-modulo-simple-10a-negro.png",
    ),
    (
        "catalogo-staford-enchufesstf-es-1016",
        "STF-ES-10/16-BL",
        "STF-ES-10/16-NE",
        "productos/catalogo/staford-enchufes/staford-simple-10-16a-blanco.png",
        "productos/catalogo/staford-enchufes/staford-simple-10-16a-negro.png",
        "productos/catalogo/staford-enchufes/staford-modulo-simple-10-16a-blanco.png",
        "productos/catalogo/staford-enchufes/staford-modulo-simple-10-16a-negro.png",
    ),
)

FOTOS_ADICIONALES_PLACA = (
    (
        "catalogo-staford-enchufesstf-ed-10a-horizontal",
        "STF-ED-10A-BL-H",
        "enchufe-10a-doble-blanco-alternativa",
        "productos/catalogo/enchufes/enchufe-10a-doble-blanco-alternativa.png",
    ),
    (
        TRIPLE_10A_SLUG,
        "STF-ET-10A-BL-H",
        "enchufe-10a-triple-blanco-alternativa",
        "productos/catalogo/enchufes/enchufe-10a-triple-blanco-alternativa.png",
    ),
    (
        "catalogo-staford-enchufesstf-ed-1016-horizontal",
        "STF-ED-10/16-BL-H",
        "enchufe-1016-doble-blanco-alternativa",
        "productos/catalogo/enchufes/enchufe-1016-doble-blanco-alternativa.png",
    ),
)

INTERRUPTORES_MODULARES = (
    {
        "slug": "modulo-interruptor-stanford-9-12",
        "modelo": "9/12",
        "nombre": "Módulo interruptor Stanford 9/12",
        "clave": "stanford-modulo-interruptor-9-12",
        "imagenes": {
            "Blanco": "productos/catalogo/staford-modulos/staford-interruptor-9-12-blanco.png",
            "Negro": "productos/catalogo/staford-modulos/staford-interruptor-9-12-negro.png",
        },
    },
    {
        "slug": "modulo-interruptor-stanford-9-24",
        "modelo": "9/24",
        "nombre": "Módulo interruptor Stanford 9/24",
        "clave": "stanford-modulo-interruptor-9-24",
        "imagenes": {
            "Blanco": "productos/catalogo/staford-modulos/staford-interruptor-9-24-blanco.png",
            "Negro": "productos/catalogo/staford-modulos/staford-interruptor-9-24-negro.png",
        },
    },
)


def guardar_imagen(Imagen, alias, clave, producto, variante, ruta, alt, orden):
    imagen, _ = Imagen.objects.using(alias).get_or_create(
        clave=clave,
        defaults={
            "producto_id": producto.pk,
            "imagen": ruta,
            "texto_alternativo": alt,
            "orden": orden,
        },
    )
    imagen.producto_id = producto.pk
    imagen.imagen = ruta
    imagen.texto_alternativo = alt
    imagen.orden = orden
    imagen.save(
        using=alias,
        update_fields=("producto", "imagen", "texto_alternativo", "orden"),
    )
    imagen.variantes.set([variante.pk])
    return imagen


def actualizar_imagenes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    # Los seis diámetros son presentaciones del mismo artículo y usan la foto
    # principal ya recortada, tanto en las variantes como en la galería.
    pvc = Producto.objects.using(alias).filter(slug=PVC_SLUG).first()
    if pvc:
        Variante.objects.using(alias).filter(producto_id=pvc.pk).update(imagen=PVC_IMAGE)
        Imagen.objects.using(alias).filter(producto_id=pvc.pk).update(imagen=PVC_IMAGE)

    # La foto recibida como “cafe triple” confirma que el archivo asignado a
    # Champagne era Café. Se cambia el color asociado y se retira el duplicado
    # blanco que se había etiquetado como Champagne.
    triple = Producto.objects.using(alias).filter(slug=TRIPLE_10A_SLUG).first()
    if triple:
        cafe = Variante.objects.using(alias).filter(
            producto_id=triple.pk,
            codigo=TRIPLE_10A_CAFE,
        ).first()
        champagne = Variante.objects.using(alias).filter(
            producto_id=triple.pk,
            codigo=TRIPLE_10A_CHAMPAGNE,
        ).first()
        if cafe:
            cafe.disponible = True
            cafe.imagen = TRIPLE_CAFE_IMAGE
            cafe.save(using=alias, update_fields=("disponible", "imagen"))
            guardar_imagen(
                Imagen,
                alias,
                f"catalogo-placa-{triple.pk}-ca",
                triple,
                cafe,
                TRIPLE_CAFE_IMAGE,
                f"{triple.nombre}, color Café",
                cafe.orden,
            )
        if champagne:
            champagne.disponible = False
            champagne.imagen = ""
            champagne.save(using=alias, update_fields=("disponible", "imagen"))
        Imagen.objects.using(alias).filter(
            producto_id=triple.pk,
            clave=f"catalogo-placa-{triple.pk}-ch",
        ).delete()

    # Sustituye las fotos de las variantes modulares simples con las imágenes
    # nuevas proporcionadas para 10 A y 10/16 A, sin publicar estas fichas.
    for (slug, code_white, code_black, old_white, old_black, new_white, new_black) in MODULO_ENCHUFE_IMAGENES:
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        for codigo, ruta_vieja, ruta_nueva in (
            (code_white, old_white, new_white),
            (code_black, old_black, new_black),
        ):
            variante = Variante.objects.using(alias).filter(
                producto_id=producto.pk,
                codigo=codigo,
            ).first()
            if not variante:
                continue
            variante.imagen = ruta_nueva
            variante.save(using=alias, update_fields=("imagen",))
            galerias = Imagen.objects.using(alias).filter(
                producto_id=producto.pk,
                variantes__pk=variante.pk,
            ).distinct()
            for imagen in galerias:
                imagen.imagen = ruta_nueva
                imagen.texto_alternativo = f"{producto.nombre}, color {variante.nombre}"
                imagen.save(using=alias, update_fields=("imagen", "texto_alternativo"))
        blanco = Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            codigo=code_white,
        ).first()
        if blanco:
            producto.imagen = new_white
            producto.save(using=alias, update_fields=("imagen",))

    # Conserva las nuevas fotografías blancas como vistas adicionales de su
    # variante, sin duplicar los archivos que ya estaban correctamente ligados.
    for slug, codigo, clave, ruta in FOTOS_ADICIONALES_PLACA:
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        variante = Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            codigo=codigo,
            disponible=True,
        ).first()
        if variante:
            guardar_imagen(
                Imagen,
                alias,
                clave,
                producto,
                variante,
                ruta,
                f"{producto.nombre}, color {variante.nombre}",
                10 + variante.orden,
            )

    # Los módulos de interruptor 9/12 y 9/24 no existían como fichas Stanford.
    categoria = Categoria.objects.using(alias).filter(slug="modulos-electricos").first()
    marca = Marca.objects.using(alias).filter(slug="stanford").first()
    if not categoria or not marca:
        raise RuntimeError("Se necesita la categoría Módulos eléctricos y la marca Stanford.")

    ultimo_orden = max(
        Producto.objects.using(alias).filter(categoria_id=categoria.pk).values_list("orden", flat=True),
        default=0,
    )
    for offset, modelo in enumerate(INTERRUPTORES_MODULARES, start=1):
        imagen_blanca = modelo["imagenes"]["Blanco"]
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=modelo["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": modelo["nombre"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": modelo["modelo"],
                "codigo": None,
                "subtitulo": categoria.nombre,
                "descripcion": (
                    f"{modelo['nombre']}. Módulo para el sistema modular Stanford. "
                    "Seleccione el color disponible para solicitar cotización."
                ),
                "imagen": imagen_blanca,
                "texto_alternativo": modelo["nombre"],
                "etiqueta_visual": "MÓDULOS STANFORD",
                "orden": ultimo_orden + offset,
                "publicado": True,
            },
        )
        for orden, (color, ruta) in enumerate(modelo["imagenes"].items(), start=1):
            variante, _ = Variante.objects.using(alias).get_or_create(
                producto_id=producto.pk,
                nombre=color,
                defaults={
                    "codigo": None,
                    "modelo": "",
                    "imagen": ruta,
                    "disponible": True,
                    "orden": orden,
                },
            )
            variante.codigo = None
            variante.imagen = ruta
            variante.disponible = True
            variante.orden = orden
            variante.save(
                using=alias,
                update_fields=("codigo", "imagen", "disponible", "orden"),
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Color",
                defaults={"valor": color, "unidad": "", "orden": 1},
            )
            guardar_imagen(
                Imagen,
                alias,
                f"{modelo['clave']}-{color.casefold()}",
                producto,
                variante,
                ruta,
                f"{modelo['nombre']}, color {color}",
                orden,
            )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Tipo de módulo",
            defaults={"valor": modelo["modelo"], "unidad": "", "orden": 1},
        )
        for orden, texto in enumerate(
            (
                "Módulo interruptor de la línea Stanford",
                "Disponible en blanco y negro",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                texto=texto,
                defaults={"orden": orden},
            )


def revertir_actualizacion(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    pvc = Producto.objects.using(alias).filter(slug=PVC_SLUG).first()
    if pvc:
        Variante.objects.using(alias).filter(producto_id=pvc.pk).update(imagen=PVC_OLD_VARIANT_IMAGE)
        Imagen.objects.using(alias).filter(producto_id=pvc.pk).update(imagen=PVC_OLD_VARIANT_IMAGE)

    triple = Producto.objects.using(alias).filter(slug=TRIPLE_10A_SLUG).first()
    if triple:
        cafe = Variante.objects.using(alias).filter(producto_id=triple.pk, codigo=TRIPLE_10A_CAFE).first()
        champagne = Variante.objects.using(alias).filter(producto_id=triple.pk, codigo=TRIPLE_10A_CHAMPAGNE).first()
        if cafe:
            cafe.disponible = False
            cafe.imagen = ""
            cafe.save(using=alias, update_fields=("disponible", "imagen"))
        if champagne:
            champagne.disponible = True
            champagne.imagen = TRIPLE_OLD_CHAMPAGNE_IMAGE
            champagne.save(using=alias, update_fields=("disponible", "imagen"))
            guardar_imagen(
                Imagen,
                alias,
                f"catalogo-placa-{triple.pk}-ch",
                triple,
                champagne,
                TRIPLE_OLD_CHAMPAGNE_IMAGE,
                f"{triple.nombre}, color Champagne",
                champagne.orden,
            )
        Imagen.objects.using(alias).filter(
            producto_id=triple.pk,
            clave=f"catalogo-placa-{triple.pk}-ca",
        ).delete()

    for slug, code_white, code_black, old_white, old_black, new_white, new_black in MODULO_ENCHUFE_IMAGENES:
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        for codigo, ruta_vieja in ((code_white, old_white), (code_black, old_black)):
            variante = Variante.objects.using(alias).filter(producto_id=producto.pk, codigo=codigo).first()
            if variante:
                variante.imagen = ruta_vieja
                variante.save(using=alias, update_fields=("imagen",))
                Imagen.objects.using(alias).filter(
                    producto_id=producto.pk,
                    variantes__pk=variante.pk,
                ).update(imagen=ruta_vieja)
        producto.imagen = old_white
        producto.save(using=alias, update_fields=("imagen",))

    for _, _, clave, _ in FOTOS_ADICIONALES_PLACA:
        Imagen.objects.using(alias).filter(clave=clave).delete()

    slugs = [modelo["slug"] for modelo in INTERRUPTORES_MODULARES]
    Producto.objects.using(alias).filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0027_corregir_colores_triple_y_foto_pvc")]

    operations = [
        migrations.RunPython(actualizar_imagenes, revertir_actualizacion),
    ]
