from django.db import migrations


PRODUCTOS = (
    {
        "codigo": "CAJ-A01-100-65-65",
        "slug": "caja-metalica-a01-100x65x65",
        "nombre": "Caja metálica A01 100 × 65 × 65 mm",
        "alt": "Caja A01 pregalvanizada con tapa de 100 x 65 x 65 mm",
        "orden": 10,
        "caracteristicas": (
            "Fabricación en metal pregalvanizado.",
            "Tapa incluida.",
            "Uso para paso y canalización eléctrica.",
        ),
    },
    {
        "codigo": "CAJ-A11-100-100-65",
        "slug": "caja-metalica-a11-100x100x65",
        "nombre": "Caja metálica A11 100 × 100 × 65 mm",
        "alt": "Caja A11 pregalvanizada prepicada de 100 x 100 x 65 mm",
        "orden": 20,
        "caracteristicas": (
            "Fabricación en metal pregalvanizado.",
            "Entradas prepicadas para canalización.",
            "Formato A11.",
        ),
    },
    {
        "codigo": "CAJ-CHUQUI-MET",
        "slug": "caja-metalica-chuqui-pregalvanizada",
        "nombre": "Caja metálica tipo Chuqui pregalvanizada",
        "alt": "Caja Chuqui metálica pregalvanizada",
        "orden": 30,
        "caracteristicas": (
            "Fabricación en metal pregalvanizado.",
            "Entradas prepicadas para canalización.",
            "Formato tipo Chuqui.",
        ),
    },
)


def separar_cajas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="cajas-metalicas-pregalvanizadas")
    especificaciones_comunes = list(
        Especificacion.objects.using(alias).filter(producto_id=original.pk)
    )
    variantes = {
        variante.codigo: variante
        for variante in Variante.objects.using(alias).filter(producto_id=original.pk)
    }

    for definicion in PRODUCTOS:
        variante = variantes[definicion["codigo"]]
        specs_variante = list(
            EspecificacionVariante.objects.using(alias)
            .filter(variante_id=variante.pk)
            .order_by("orden", "id")
        )
        image_path = variante.imagen.name
        if definicion["codigo"] == "CAJ-A01-100-65-65":
            producto = original
            producto.nombre = definicion["nombre"]
            producto.descripcion = (
                "Caja metálica pregalvanizada A01 para paso y canalización eléctrica, "
                "con tapa. Dimensiones: 100 × 65 × 65 mm."
            )
            producto.imagen = image_path
            producto.texto_alternativo = definicion["alt"]
            producto.codigo = variante.codigo
            producto.save(
                using=alias,
                update_fields=["nombre", "descripcion", "imagen", "texto_alternativo", "codigo"],
            )
        else:
            descripcion = (
                "Caja metálica pregalvanizada A11 para canalización eléctrica, "
                "con entradas prepicadas. Dimensiones: 100 × 100 × 65 mm."
                if definicion["codigo"] == "CAJ-A11-100-100-65"
                else "Caja metálica pregalvanizada tipo Chuqui para canalización y paso, con entradas prepicadas."
            )
            producto, _ = Producto.objects.using(alias).update_or_create(
                slug=definicion["slug"],
                defaults={
                    "categoria_id": original.categoria_id,
                    "nombre": definicion["nombre"],
                    "marca": original.marca,
                    "marca_nueva_id": original.marca_nueva_id,
                    "modelo": variante.modelo,
                    "codigo": variante.codigo,
                    "subtitulo": original.subtitulo,
                    "descripcion": descripcion,
                    "imagen": image_path,
                    "texto_alternativo": definicion["alt"],
                    "etiqueta_visual": original.etiqueta_visual,
                    "orden": original.orden + definicion["orden"],
                    "publicado": True,
                },
            )

        for spec in especificaciones_comunes:
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=spec.nombre,
                defaults={"valor": spec.valor, "unidad": spec.unidad, "orden": spec.orden},
            )
        for spec in specs_variante:
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=spec.nombre,
                defaults={"valor": spec.valor, "unidad": spec.unidad, "orden": spec.orden + 10},
            )

        for posicion, texto in enumerate(definicion["caracteristicas"], start=1):
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
        Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
            producto_id=producto.pk,
            orden=10,
            texto_alternativo=definicion["alt"],
        )


def restaurar_grupo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="cajas-metalicas-pregalvanizadas")
    orders = {
        "CAJ-A01-100-65-65": (10, 3, "Caja A01 pregalvanizada con tapa de 100 x 65 x 65 mm"),
        "CAJ-A11-100-100-65": (20, 1, "Caja A11 pregalvanizada prepicada de 100 x 100 x 65 mm"),
        "CAJ-CHUQUI-MET": (30, 2, "Caja Chuqui metálica pregalvanizada"),
    }
    for definicion in PRODUCTOS:
        codigo = definicion["codigo"]
        variante = Variante.objects.using(alias).get(codigo=codigo)
        old_variant_order, old_image_order, old_alt = orders[codigo]
        Cotizacion.objects.using(alias).filter(variante_id=variante.pk).update(
            producto_id=original.pk
        )
        variante.producto_id = original.pk
        variante.disponible = True
        variante.orden = old_variant_order
        variante.save(using=alias, update_fields=["producto", "disponible", "orden"])
        Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
            producto_id=original.pk,
            orden=old_image_order,
            texto_alternativo=old_alt,
        )
        if codigo != "CAJ-A01-100-65-65":
            Producto.objects.using(alias).filter(slug=definicion["slug"]).delete()

    original.nombre = "Cajas metálicas pregalvanizadas"
    original.descripcion = (
        "Cajas metálicas para canalización, paso y montaje de dispositivos eléctricos, "
        "con entradas prepicadas según la presentación."
    )
    original.imagen = "productos/catalogo/cajas-metalicas/caja-a11-prepicada-100x100x65.png"
    original.texto_alternativo = "Caja A11 pregalvanizada prepicada de 100 x 100 x 65 mm"
    original.codigo = None
    original.save(
        using=alias,
        update_fields=["nombre", "descripcion", "imagen", "texto_alternativo", "codigo"],
    )
    Especificacion.objects.using(alias).filter(producto_id=original.pk).exclude(
        nombre__in=("Material", "Aplicación")
    ).delete()
    for orden, texto in enumerate(
        (
            "Fabricación en metal pregalvanizado",
            "Entradas prepicadas para canalización",
            "Formatos para paso, derivación y montaje",
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
        ("core", "0059_corregir_texto_cajas_lisas"),
    ]

    operations = [
        migrations.RunPython(separar_cajas, restaurar_grupo),
    ]
