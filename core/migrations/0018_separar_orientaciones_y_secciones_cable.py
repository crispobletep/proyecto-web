from django.db import migrations


def separar_enchufes(apps, alias):
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    anterior = Categoria.objects.using(alias).filter(slug="enchufes").first()
    if not anterior:
        return

    padre = anterior.padre
    verticales, _ = Categoria.objects.using(alias).update_or_create(
        slug="enchufes-verticales",
        defaults={"nombre": "Enchufes verticales", "padre": padre, "orden": 10, "activa": True},
    )
    horizontales, _ = Categoria.objects.using(alias).update_or_create(
        slug="enchufes-horizontales",
        defaults={"nombre": "Enchufes horizontales", "padre": padre, "orden": 20, "activa": True},
    )

    for producto in Producto.objects.using(alias).filter(categoria_id=anterior.pk):
        orientacion = Especificacion.objects.using(alias).filter(
            producto_id=producto.pk, nombre="Orientación"
        ).values_list("valor", flat=True).first()
        if orientacion == "Horizontal":
            producto.categoria_id = horizontales.pk
        elif orientacion == "Vertical":
            producto.categoria_id = verticales.pk
        else:
            continue
        producto.save(using=alias, update_fields=["categoria"])

    if not Producto.objects.using(alias).filter(categoria_id=anterior.pk).exists():
        anterior.activa = False
        anterior.save(using=alias, update_fields=["activa"])


def section_for(variant):
    value = variant.especificaciones.filter(nombre="Sección").values_list("valor", flat=True).first()
    return value


def separar_cables_por_seccion(apps, alias):
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionProducto = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    base = Producto.objects.using(alias).filter(slug="cable-flexible-libre-halogenos").first()
    if not base:
        return

    secciones = ("1,5", "2,5", "4", "6", "10")
    variantes_por_seccion = {seccion: [] for seccion in secciones}
    for variante in Variante.objects.using(alias).filter(producto_id=base.pk):
        seccion = EspecificacionVariante.objects.using(alias).filter(
            variante_id=variante.pk, nombre="Sección"
        ).values_list("valor", flat=True).first()
        if seccion in variantes_por_seccion:
            variantes_por_seccion[seccion].append(variante)

    productos = {"1,5": base}
    for indice, seccion in enumerate(secciones[1:], start=1):
        slug_part = {"2,5": "2-5", "4": "4", "6": "6", "10": "10"}[seccion]
        producto, _ = Producto.objects.using(alias).get_or_create(
            slug=f"cable-flexible-libre-halogenos-{slug_part}mm2",
            defaults={
                "categoria_id": base.categoria_id,
                "nombre": f"Cable flexible libre de halógenos {seccion} mm²",
                "marca": base.marca,
                "marca_nueva_id": base.marca_nueva_id,
                "modelo": base.modelo,
                "codigo": None,
                "subtitulo": base.subtitulo,
                "descripcion": (
                    f"Cable flexible libre de halógenos de sección {seccion} mm² "
                    "para instalaciones eléctricas. Disponible en varios colores; "
                    "consulta la presentación y longitud al cotizar."
                ),
                "imagen": base.imagen.name,
                "texto_alternativo": f"Cable flexible libre de halógenos de {seccion} mm²",
                "etiqueta_visual": base.etiqueta_visual,
                "orden": base.orden + indice,
                "publicado": base.publicado,
            },
        )
        productos[seccion] = producto

    for seccion, producto in productos.items():
        producto.nombre = f"Cable flexible libre de halógenos {seccion} mm²"
        producto.descripcion = (
            f"Cable flexible libre de halógenos de sección {seccion} mm² "
            "para instalaciones eléctricas. Disponible en varios colores; "
            "consulta la presentación y longitud al cotizar."
        )
        producto.texto_alternativo = f"Cable flexible libre de halógenos de {seccion} mm²"
        producto.imagen = next(
            (v.imagen.name for v in variantes_por_seccion[seccion] if v.nombre.casefold().endswith("negro")),
            producto.imagen.name if producto.imagen else base.imagen.name,
        )
        producto.save(using=alias, update_fields=["nombre", "descripcion", "texto_alternativo", "imagen"])

        EspecificacionProducto.objects.using(alias).filter(producto_id=producto.pk).delete()
        EspecificacionProducto.objects.using(alias).create(
            producto_id=producto.pk, nombre="Tipo", valor="Cable flexible libre de halógenos", orden=1
        )
        EspecificacionProducto.objects.using(alias).create(
            producto_id=producto.pk, nombre="Sección nominal", valor=seccion, unidad="mm²", orden=2
        )
        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        for orden, texto in enumerate((
            "Aislación libre de halógenos",
            "Conductor flexible para canalizaciones eléctricas",
            f"Sección nominal de {seccion} mm²",
        ), start=1):
            Caracteristica.objects.using(alias).create(producto_id=producto.pk, texto=texto, orden=orden)

    for seccion, variantes in variantes_por_seccion.items():
        producto = productos[seccion]
        for variante in variantes:
            color = EspecificacionVariante.objects.using(alias).filter(
                variante_id=variante.pk, nombre="Color"
            ).values_list("valor", flat=True).first()
            variante.producto_id = producto.pk
            if color:
                variante.nombre = color
            variante.save(using=alias, update_fields=["producto", "nombre"])

    # Reasigna cada fotografía al producto de su sección según las variantes enlazadas.
    for imagen in Imagen.objects.using(alias).filter(producto_id__in=[p.pk for p in productos.values()]):
        vinculadas = list(imagen.variantes.all())
        secciones_imagen = {
            section_for(v) for v in vinculadas
        } - {None}
        if len(secciones_imagen) == 1:
            imagen.producto_id = productos[secciones_imagen.pop()].pk
            imagen.save(using=alias, update_fields=["producto"])

    # La lámina no incluye fotografías propias para 10 mm²; se reutiliza la de 6 mm².
    producto_10 = productos["10"]
    for variante in variantes_por_seccion["10"]:
        color = EspecificacionVariante.objects.using(alias).filter(
            variante_id=variante.pk, nombre="Color"
        ).values_list("valor", flat=True).first() or ""
        clave = f"carga-conductores-conexiones-cable-10-{color.lower()}"
        imagen, _ = Imagen.objects.using(alias).get_or_create(
            clave=clave,
            defaults={
                "producto_id": producto_10.pk,
                "imagen": variante.imagen.name,
                "texto_alternativo": f"Cable flexible libre de halógenos de 10 mm², color {color}",
                "orden": 1,
            },
        )
        imagen.producto_id = producto_10.pk
        imagen.save(using=alias, update_fields=["producto"])
        imagen.variantes.add(variante)


def migrar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    separar_enchufes(apps, alias)
    separar_cables_por_seccion(apps, alias)


class Migration(migrations.Migration):
    dependencies = [("core", "0017_orientacion_enchufes_stanford")]

    operations = [migrations.RunPython(migrar_catalogo, migrations.RunPython.noop)]
