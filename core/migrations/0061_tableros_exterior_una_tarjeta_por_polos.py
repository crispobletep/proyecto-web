from django.db import migrations


PRODUCTOS = (
    ("CNC-TB-2P", "catalogo-tableros-cnc", 2, 10),
    ("CNC-TB-4P", "tablero-exterior-cnc-ip65-4-polos", 4, 20),
    ("CNC-TB-6P", "tablero-exterior-cnc-ip65-6-polos", 6, 30),
    ("CNC-TB-8P", "tablero-exterior-cnc-ip65-8-polos", 8, 40),
    ("CNC-TB-12P", "tablero-exterior-cnc-ip65-12-polos", 12, 50),
    ("CNC-TB-16P", "tablero-exterior-cnc-ip65-16-polos", 16, 60),
    ("CNC-TB-18P", "tablero-exterior-cnc-ip65-18-polos", 18, 70),
    ("CNC-TB-24P", "tablero-exterior-cnc-ip65-24-polos", 24, 80),
)
IMAGENES_ANTERIORES = (
    (
        "manifiesto-tableros-cnc-tableros-cnccnc-tablero-exterior-cerradopng",
        "productos/catalogo/tableros-cnc/cnc-tablero-exterior-cerrado.png",
        "Tablero exterior CNC IP65 cerrado",
        1,
    ),
    (
        "manifiesto-tableros-cnc-tableros-cnccnc-tablero-exterior-abiertopng",
        "productos/catalogo/tableros-cnc/cnc-tablero-exterior-abierto.png",
        "Tablero exterior CNC IP65 abierto",
        2,
    ),
)


def separar_por_polos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="catalogo-tableros-cnc")
    variantes = {
        variante.codigo: variante
        for variante in Variante.objects.using(alias).filter(producto_id=original.pk)
    }
    especificaciones_comunes = list(
        Especificacion.objects.using(alias).filter(producto_id=original.pk)
    )
    imagenes_base = {
        clave: Imagen.objects.using(alias).get(clave=clave)
        for clave, _, _, _ in IMAGENES_ANTERIORES
    }

    for codigo, product_slug, polos, orden in PRODUCTOS:
        variante = variantes[codigo]
        destino_original = polos == 2
        nombre = f"Tablero exterior CNC IP65 {polos} polos"
        imagen_principal = variante.imagen.name
        if destino_original:
            producto = original
            producto.nombre = nombre
            producto.descripcion = (
                f"Tablero eléctrico CNC para instalaciones exteriores, con protección IP65. "
                f"Capacidad: {polos} polos."
            )
            producto.imagen = imagen_principal
            producto.texto_alternativo = f"Tablero eléctrico CNC IP65 de {polos} polos"
            producto.codigo = codigo
            producto.save(
                using=alias,
                update_fields=["nombre", "descripcion", "imagen", "texto_alternativo", "codigo"],
            )
        else:
            producto, _ = Producto.objects.using(alias).update_or_create(
                slug=product_slug,
                defaults={
                    "categoria_id": original.categoria_id,
                    "nombre": nombre,
                    "marca": original.marca,
                    "marca_nueva_id": original.marca_nueva_id,
                    "modelo": variante.modelo,
                    "codigo": codigo,
                    "subtitulo": original.subtitulo,
                    "descripcion": (
                        f"Tablero eléctrico CNC para instalaciones exteriores, "
                        f"con protección IP65. Capacidad: {polos} polos."
                    ),
                    "imagen": imagen_principal,
                    "texto_alternativo": f"Tablero eléctrico CNC IP65 de {polos} polos",
                    "etiqueta_visual": original.etiqueta_visual,
                    "orden": original.orden + orden,
                    "publicado": True,
                },
            )

        for spec in especificaciones_comunes:
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=spec.nombre,
                defaults={"valor": spec.valor, "unidad": spec.unidad, "orden": spec.orden},
            )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Polos",
            defaults={"valor": str(polos), "unidad": "polos", "orden": 3},
        )

        for posicion, texto in enumerate(
            (
                "Gabinete para instalaciones eléctricas exteriores.",
                "Riel DIN incluido.",
                "Cierre y entradas protegidas.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=posicion,
                defaults={"texto": texto},
            )

        variante.producto_id = producto.pk
        variante.disponible = False
        variante.orden = 10
        variante.save(using=alias, update_fields=["producto", "disponible", "orden"])
        Cotizacion.objects.using(alias).filter(variante_id=variante.pk).update(
            producto_id=producto.pk
        )

        for image_index, (old_key, image_path, _, image_order) in enumerate(IMAGENES_ANTERIORES, start=1):
            if destino_original:
                image = imagenes_base[old_key]
                image.producto_id = producto.pk
                image.imagen = image_path
                image.texto_alternativo = f"Tablero exterior CNC IP65 de {polos} polos"
                image.orden = image_order
                image.save(using=alias, update_fields=["producto", "imagen", "texto_alternativo", "orden"])
                image.variantes.set([variante])
            else:
                image = Imagen.objects.using(alias).create(
                    producto_id=producto.pk,
                    clave=f"{product_slug}-vista-{image_index}",
                    imagen=image_path,
                    texto_alternativo=f"Tablero exterior CNC IP65 de {polos} polos",
                    orden=image_order,
                )
                image.variantes.set([variante])


def restaurar_producto_unico(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="catalogo-tableros-cnc")
    for codigo, product_slug, _, old_order in PRODUCTOS:
        variante = Variante.objects.using(alias).get(codigo=codigo)
        Cotizacion.objects.using(alias).filter(variante_id=variante.pk).update(
            producto_id=original.pk
        )
        variante.producto_id = original.pk
        variante.disponible = True
        variante.orden = old_order // 10
        variante.save(using=alias, update_fields=["producto", "disponible", "orden"])
        if codigo != "CNC-TB-2P":
            Producto.objects.using(alias).filter(slug=product_slug).delete()

    for clave, image_path, alt, orden in IMAGENES_ANTERIORES:
        image = Imagen.objects.using(alias).get(clave=clave)
        image.producto_id = original.pk
        image.imagen = image_path
        image.texto_alternativo = alt
        image.orden = orden
        image.save(using=alias, update_fields=["producto", "imagen", "texto_alternativo", "orden"])
        image.variantes.set(list(Variante.objects.using(alias).filter(producto_id=original.pk)))

    original.nombre = "Tableros eléctricos de exterior IP65"
    original.descripcion = (
        "Tableros eléctricos de exterior CNC IP65. Producto incorporado desde el catálogo técnico; "
        "seleccione la variante correspondiente para solicitar cotización."
    )
    original.imagen = "productos/catalogo/tableros-cnc/cnc-tablero-exterior-cerrado.png"
    original.texto_alternativo = "Tableros eléctricos de exterior IP65"
    original.codigo = None
    original.save(
        using=alias,
        update_fields=["nombre", "descripcion", "imagen", "texto_alternativo", "codigo"],
    )
    Especificacion.objects.using(alias).filter(producto_id=original.pk, nombre="Polos").delete()
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    for orden, texto in enumerate(
        (
            "Gabinete para instalaciones eléctricas exteriores",
            "Riel DIN incluido",
            "Cierre y entradas protegidas",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=original.pk,
            orden=orden,
            defaults={"texto": texto},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0060_cajas_metalicas_una_tarjeta_por_variante"),
    ]

    operations = [
        migrations.RunPython(separar_por_polos, restaurar_producto_unico),
    ]
