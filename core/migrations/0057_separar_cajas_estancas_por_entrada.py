from django.db import migrations


PRODUCTO_CONOS = "cajas-estancas-con-conos"
VARIANTES = (
    # código, grupo, nuevo orden, orden original, orden original de imagen, texto alternativo
    ("CAJ-EST-80-80-40-L", "lisa", 10, 10, 2, "Caja estanca lisa de 80 × 80 × 40 mm"),
    ("CAJ-EST-80-80-50-C-IP55", "conos", 10, 20, 3, "Caja estanca con conos de 80 × 80 × 50 mm IP55"),
    ("CAJ-EST-100-100-70-C-IP65", "conos", 20, 30, 4, "Caja estanca con conos de 100 × 100 × 70 mm IP65"),
    ("CAJ-EST-100-100-70-L-IP65", "lisa", 20, 40, 1, "Caja estanca lisa de 100 × 100 × 70 mm IP65"),
    ("CAJ-EST-170-140-85-L", "lisa", 30, 50, 5, "Caja estanca lisa de 170 × 140 × 85 mm"),
    ("CAJ-EST-220-170-95-L-IP55", "lisa", 40, 60, 6, "Caja estanca lisa de 220 × 170 × 95 mm IP55"),
)


def separar_por_entrada(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="cajas-estancas-de-derivacion")
    variantes = {
        variante.codigo: variante
        for variante in Variante.objects.using(alias).filter(producto_id=original.pk)
    }
    variantes_conos = [
        variantes[codigo]
        for codigo, grupo, _, _, _, _ in VARIANTES
        if grupo == "conos"
    ]

    image_lisas = variantes["CAJ-EST-80-80-40-L"].imagen.name
    image_conos = variantes["CAJ-EST-80-80-50-C-IP55"].imagen.name

    conos, _ = Producto.objects.using(alias).update_or_create(
        slug=PRODUCTO_CONOS,
        defaults={
            "categoria_id": original.categoria_id,
            "nombre": "Cajas estancas con conos",
            "marca": original.marca,
            "marca_nueva_id": original.marca_nueva_id,
            "modelo": "",
            "codigo": None,
            "subtitulo": original.subtitulo,
            "descripcion": (
                "Caja estanca de derivación para instalación superficial, "
                "con conos de entrada para cables. Elige la medida disponible."
            ),
            "imagen": image_conos,
            "texto_alternativo": "Caja estanca de derivación con conos de entrada",
            "etiqueta_visual": original.etiqueta_visual,
            "orden": original.orden + 1,
            "publicado": True,
        },
    )

    original.nombre = "Cajas estancas lisas"
    original.descripcion = (
        "Cajas estancas de derivación para instalación superficial, "
        "con entradas laterales lisas. Elige la medida disponible."
    )
    original.imagen = image_lisas
    original.texto_alternativo = "Caja estanca de derivación con entradas lisas"
    original.save(
        using=alias,
        update_fields=["nombre", "descripcion", "imagen", "texto_alternativo"],
    )

    Caracteristica.objects.using(alias).update_or_create(
        producto_id=original.pk,
        orden=2,
        defaults={"texto": "Entradas laterales lisas."},
    )
    for orden, texto in enumerate(
        (
            "Tapa desmontable para acceso a las conexiones.",
            "Entradas laterales con conos para cables.",
            "Distintas dimensiones para adecuarse a cada instalación.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=conos.pk,
            orden=orden,
            defaults={"texto": texto},
        )

    for especificacion in Especificacion.objects.using(alias).filter(producto_id=original.pk):
        Especificacion.objects.using(alias).update_or_create(
            producto_id=conos.pk,
            nombre=especificacion.nombre,
            defaults={
                "valor": especificacion.valor,
                "unidad": especificacion.unidad,
                "orden": especificacion.orden,
            },
        )

    for codigo, grupo, orden, _, _, texto_alt in VARIANTES:
        variante = variantes[codigo]
        variante.orden = orden
        if grupo == "conos":
            variante.producto_id = conos.pk
            variante.save(using=alias, update_fields=["producto", "orden"])
            Cotizacion.objects.using(alias).filter(variante_id=variante.pk).update(
                producto_id=conos.pk
            )
            Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
                producto_id=conos.pk,
                orden=orden,
                texto_alternativo=texto_alt,
            )
        else:
            variante.save(using=alias, update_fields=["orden"])
            Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
                producto_id=original.pk,
                orden=orden,
                texto_alternativo=texto_alt,
            )


def restaurar_grupo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="cajas-estancas-de-derivacion")
    conos = Producto.objects.using(alias).filter(slug=PRODUCTO_CONOS).first()
    if conos:
        variantes_conos = Variante.objects.using(alias).filter(producto_id=conos.pk)
        Cotizacion.objects.using(alias).filter(producto_id=conos.pk).update(
            producto_id=original.pk
        )
        for variante in variantes_conos:
            old_order = next(item[3] for item in VARIANTES if item[0] == variante.codigo)
            old_image_order = next(item[4] for item in VARIANTES if item[0] == variante.codigo)
            variante.producto_id = original.pk
            variante.orden = old_order
            variante.save(using=alias, update_fields=["producto", "orden"])
            Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
                producto_id=original.pk,
                orden=old_image_order,
            )
        conos.delete(using=alias)

    original.nombre = "Cajas estancas de derivación"
    original.descripcion = (
        "Cajas aislantes para derivación y protección de conexiones en "
        "montaje superficial, disponibles con laterales lisos o conos de entrada."
    )
    original.imagen = "productos/catalogo/cajas-estancas/caja-estanca-lisa-100x100x70-ip65.png"
    original.texto_alternativo = "Caja estanca lisa de 100 x 100 x 70 mm IP65"
    original.save(
        using=alias,
        update_fields=["nombre", "descripcion", "imagen", "texto_alternativo"],
    )
    for orden, texto in enumerate(
        (
            "Tapa desmontable para acceso a las conexiones",
            "Alternativas lisas y con conos de entrada",
            "Distintas dimensiones para adecuarse a cada instalación",
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
        ("core", "0056_separar_gabinetes_metalicos_por_medida"),
    ]

    operations = [
        migrations.RunPython(separar_por_entrada, restaurar_grupo),
    ]
