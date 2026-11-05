from django.db import migrations


PRODUCTOS = (
    {
        "codigo": "GAB-MET-250-200-150-1P",
        "slug": "gabinete-metalico-250x200x150",
        "nombre": "Gabinete metálico 250 × 200 × 150 mm",
    },
    {
        "codigo": "GAB-MET-300-200-150-IP65",
        "slug": "gabinete-metalico-300x200x150-ip65",
        "nombre": "Gabinete metálico 300 × 200 × 150 mm IP65",
    },
    {
        "codigo": "GAB-MET-400-300-200-IP65",
        "slug": "gabinete-metalico-400x300x200-ip65-estandar",
        "nombre": "Gabinete metálico 400 × 300 × 200 mm IP65 sin chasis",
    },
    {
        "codigo": "GAB-MET-400-300-200-IP65-CH",
        "slug": "gabinete-metalico-400x300x200-ip65-con-chasis",
        "nombre": "Gabinete metálico 400 × 300 × 200 mm IP65 con chasis",
    },
    {
        "codigo": "GAB-MET-500-400-200-IP65",
        "slug": "gabinete-metalico-500x400x200-ip65-estandar",
        "nombre": "Gabinete metálico 500 × 400 × 200 mm IP65 sin chasis",
    },
    {
        "codigo": "GAB-MET-500-400-200-IP65-CH",
        "slug": "gabinete-metalico-500x400x200-ip65-con-chasis",
        "nombre": "Gabinete metálico 500 × 400 × 200 mm IP65 con chasis",
    },
    {
        "codigo": "GAB-MET-600-400-200-IP65",
        "slug": "gabinete-metalico-600x400x200-ip65-estandar",
        "nombre": "Gabinete metálico 600 × 400 × 200 mm IP65 sin chasis",
    },
    {
        "codigo": "GAB-MET-600-400-200-IP65-CH",
        "slug": "gabinete-metalico-600x400x200-ip65-con-chasis",
        "nombre": "Gabinete metálico 600 × 400 × 200 mm IP65 con chasis",
    },
)


def separar_gabinetes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    original = Producto.objects.using(alias).get(slug="gabinetes-metalicos-una-puerta")
    variantes = {
        variante.codigo: variante
        for variante in Variante.objects.using(alias).filter(producto_id=original.pk)
    }

    for posicion, definicion in enumerate(PRODUCTOS, start=1):
        variante = variantes[definicion["codigo"]]
        especificaciones_variante = list(
            EspecificacionVariante.objects.using(alias)
            .filter(variante_id=variante.pk)
            .order_by("orden", "id")
        )
        image_path = variante.imagen.name if variante.imagen else original.imagen.name
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": original.categoria_id,
                "nombre": definicion["nombre"],
                "marca": "",
                "marca_nueva_id": None,
                "modelo": variante.modelo,
                "codigo": variante.codigo,
                "subtitulo": original.categoria.nombre,
                "descripcion": (
                    f"Gabinete metálico de una puerta en medidas "
                    f"{next(x.valor for x in especificaciones_variante if x.nombre == 'Alto')} × "
                    f"{next(x.valor for x in especificaciones_variante if x.nombre == 'Ancho')} × "
                    f"{next(x.valor for x in especificaciones_variante if x.nombre == 'Profundidad')} mm."
                ),
                "imagen": image_path,
                "texto_alternativo": definicion["nombre"],
                "etiqueta_visual": "",
                "orden": original.orden + posicion,
                "publicado": True,
            },
        )

        caracteristicas = [
            "Gabinete metálico para distribución y control eléctrico.",
            "Puerta frontal con sistema de cierre.",
        ]
        for dato in especificaciones_variante:
            if dato.nombre == "Grado de protección":
                caracteristicas.append(f"Grado de protección {dato.valor}.")
            elif dato.nombre == "Chasis interior":
                caracteristicas.append(
                    "Chasis interior incluido."
                    if dato.valor == "Incluido"
                    else "Chasis interior no incluido."
                )
        for orden, texto in enumerate(caracteristicas, start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )

        especificaciones_producto = [
            ("Material", "Metálico", ""),
            ("Aplicación", "Distribución y control eléctrico", ""),
            (
                "Dimensiones",
                " × ".join(
                    next(x.valor for x in especificaciones_variante if x.nombre == eje)
                    for eje in ("Alto", "Ancho", "Profundidad")
                ),
                "mm",
            ),
        ]
        especificaciones_producto.extend(
            (dato.nombre, dato.valor, dato.unidad)
            for dato in especificaciones_variante
        )
        for orden, (nombre, valor, unidad) in enumerate(especificaciones_producto, start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

        Imagen.objects.using(alias).update_or_create(
            clave=f"{definicion['slug']}-imagen-principal",
            defaults={
                "producto_id": producto.pk,
                "imagen": image_path,
                "texto_alternativo": definicion["nombre"],
                "orden": 1,
            },
        )

    original.publicado = False
    original.save(using=alias, update_fields=["publicado"])
    Variante.objects.using(alias).filter(producto_id=original.pk).update(disponible=False)


def restaurar_gabinetes(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    original = Producto.objects.using(alias).get(slug="gabinetes-metalicos-una-puerta")
    original.publicado = True
    original.save(using=alias, update_fields=["publicado"])
    Variante.objects.using(alias).filter(producto_id=original.pk).update(disponible=True)
    Producto.objects.using(alias).filter(
        slug__in=[producto["slug"] for producto in PRODUCTOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0055_quitar_marca_tablero_4_modulos"),
    ]

    operations = [
        migrations.RunPython(separar_gabinetes, restaurar_gabinetes),
    ]
