from django.db import migrations


PRODUCTOS = (
    ("CAJ-EST-80-80-40-L", "caja-estanca-80x80x40-lisa", "Caja estanca 80 × 80 × 40 mm lisa", "cajas-estancas-de-derivacion", 10),
    ("CAJ-EST-80-80-50-C-IP55", "caja-estanca-80x80x50-con-conos-ip55", "Caja estanca 80 × 80 × 50 mm con conos IP55", "cajas-estancas-con-conos", 10),
    ("CAJ-EST-100-100-70-L-IP65", "caja-estanca-100x100x70-lisa-ip65", "Caja estanca 100 × 100 × 70 mm lisa IP65", "cajas-estancas-de-derivacion", 20),
    ("CAJ-EST-100-100-70-C-IP65", "caja-estanca-100x100x70-con-conos-ip65", "Caja estanca 100 × 100 × 70 mm con conos IP65", "cajas-estancas-con-conos", 20),
    ("CAJ-EST-170-140-85-L", "caja-estanca-170x140x85-lisa", "Caja estanca 170 × 140 × 85 mm lisa", "cajas-estancas-de-derivacion", 30),
    ("CAJ-EST-220-170-95-L-IP55", "caja-estanca-220x170x95-lisa-ip55", "Caja estanca 220 × 170 × 95 mm lisa IP55", "cajas-estancas-de-derivacion", 40),
)


def separar_medidas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    originales = {
        producto.slug: producto
        for producto in Producto.objects.using(alias).filter(
            slug__in=("cajas-estancas-de-derivacion", "cajas-estancas-con-conos")
        )
    }
    variantes = {
        variante.codigo: variante
        for variante in Variante.objects.using(alias).filter(
            producto_id__in=[producto.pk for producto in originales.values()]
        )
    }

    for codigo, slug, nombre, grupo_original, orden in PRODUCTOS:
        original = originales[grupo_original]
        variante = variantes[codigo]
        especificaciones_variante = list(
            EspecificacionVariante.objects.using(alias)
            .filter(variante_id=variante.pk)
            .order_by("orden", "id")
        )
        image_path = variante.imagen.name
        tipo_entrada = next(
            dato.valor for dato in especificaciones_variante if dato.nombre == "Tipo de entrada"
        )
        dimensiones = next(
            dato.valor for dato in especificaciones_variante if dato.nombre == "Dimensiones"
        )
        grado_ip = next(
            (dato.valor for dato in especificaciones_variante if dato.nombre == "Grado de protección"),
            "",
        )
        detalle_entrada = (
            "entradas laterales lisas"
            if tipo_entrada.casefold() == "lisa"
            else "conos de entrada para cables"
        )

        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": original.categoria_id,
                "nombre": nombre,
                "marca": original.marca,
                "marca_nueva_id": original.marca_nueva_id,
                "modelo": variante.modelo,
                "codigo": codigo,
                "subtitulo": original.subtitulo,
                "descripcion": (
                    f"Caja estanca de derivación para instalación superficial, "
                    f"con {detalle_entrada}. "
                    f"Dimensiones: {dimensiones} mm."
                    + (f" Grado de protección {grado_ip}." if grado_ip else "")
                ),
                "imagen": image_path,
                "texto_alternativo": nombre,
                "etiqueta_visual": original.etiqueta_visual,
                "orden": original.orden + orden,
                "publicado": True,
            },
        )

        for especificacion in Especificacion.objects.using(alias).filter(producto_id=original.pk):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=especificacion.nombre,
                defaults={
                    "valor": especificacion.valor,
                    "unidad": especificacion.unidad,
                    "orden": especificacion.orden,
                },
            )
        for dato in especificaciones_variante:
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=dato.nombre,
                defaults={"valor": dato.valor, "unidad": dato.unidad, "orden": dato.orden + 10},
            )

        caracteristicas = [
            "Tapa desmontable para acceso a las conexiones.",
            f"Entradas laterales {tipo_entrada.casefold()}.",
            f"Grado de protección {grado_ip}." if grado_ip else "Instalación superficial.",
        ]
        for posicion, texto in enumerate(caracteristicas, start=1):
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
            texto_alternativo=nombre,
        )

    Producto.objects.using(alias).filter(
        slug__in=("cajas-estancas-de-derivacion", "cajas-estancas-con-conos")
    ).update(publicado=False)
    Variante.objects.using(alias).filter(
        producto__slug__in=("cajas-estancas-de-derivacion", "cajas-estancas-con-conos")
    ).update(disponible=False)


def restaurar_dos_grupos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    originales = {
        producto.slug: producto
        for producto in Producto.objects.using(alias).filter(
            slug__in=("cajas-estancas-de-derivacion", "cajas-estancas-con-conos")
        )
    }
    for codigo, slug, _, grupo_original, orden in PRODUCTOS:
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        original = originales[grupo_original]
        variante = Variante.objects.using(alias).get(codigo=codigo)
        Cotizacion.objects.using(alias).filter(variante_id=variante.pk).update(
            producto_id=original.pk
        )
        variante.producto_id = original.pk
        variante.disponible = True
        variante.orden = orden
        variante.save(using=alias, update_fields=["producto", "disponible", "orden"])
        Imagen.objects.using(alias).filter(variantes__pk=variante.pk).update(
            producto_id=original.pk,
            orden=orden,
        )
        producto.delete(using=alias)

    for slug in ("cajas-estancas-de-derivacion", "cajas-estancas-con-conos"):
        Producto.objects.using(alias).filter(slug=slug).update(publicado=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0057_separar_cajas_estancas_por_entrada"),
    ]

    operations = [
        migrations.RunPython(separar_medidas, restaurar_dos_grupos),
    ]
