from django.db import migrations
from django.utils.text import slugify


COLORES = (
    ("BL", "Blanco", "blanco"),
    ("NE", "Negro", "negro"),
    ("CH", "Champagne", "champagne"),
    ("CA", "Café", "cafe"),
)

MODELOS = (
    {
        "prefijo": "STF-ES-10A",
        "tipo": "simple",
        "corriente": "10",
        "archivo_corriente": "10a",
        "slug_placa": "catalogo-staford-enchufesstf-es-10a",
        "slug_modular": "catalogo-staford-enchufesstf-es-10a",
        "placa": {
            "BL": "enchufe-10a-simple-blanco.png",
            "NE": "enchufe-10a-simple-negro.png",
            "CH": "enchufe-10a-simple-champagne.png",
            "CA": "enchufe-10a-simple-cafe.png",
        },
    },
    {
        "prefijo": "STF-ED-10A",
        "tipo": "doble",
        "corriente": "10",
        "archivo_corriente": "10a",
        "slug_placa": "catalogo-staford-enchufesstf-ed-10a-horizontal",
        "slug_modular": "catalogo-staford-enchufesstf-ed-10a",
        "placa": {
            "BL": "enchufe-10a-doble-blanco.png",
            "NE": "enchufe-10a-doble-negro.png",
            "CH": "enchufe-10a-doble-champagne.png",
        },
    },
    {
        "prefijo": "STF-ET-10A",
        "tipo": "triple",
        "corriente": "10",
        "archivo_corriente": "10a",
        "slug_placa": "catalogo-staford-enchufesstf-et-10a-horizontal",
        "slug_modular": "catalogo-staford-enchufesstf-et-10a",
        "placa": {
            "BL": "enchufe-10a-triple-blanco.png",
            "NE": "enchufe-10a-triple-negro.png",
            "CH": "enchufe-10a-triple-champagne.png",
            "CA": "enchufe-triple-cafe.png",
        },
    },
    {
        "prefijo": "STF-ES-10/16",
        "tipo": "simple",
        "corriente": "10/16",
        "archivo_corriente": "10-16a",
        "slug_placa": "catalogo-staford-enchufesstf-es-1016",
        "slug_modular": "catalogo-staford-enchufesstf-es-1016",
        "placa": {
            "BL": "enchufe-1016-simple-blanco.png",
            "NE": "enchufe-1016-simple-negro.png",
            "CH": "enchufe-1016-simple-champagne.png",
            "CA": "enchufe-1016-simple-cafe.png",
        },
    },
    {
        "prefijo": "STF-ED-10/16",
        "tipo": "doble",
        "corriente": "10/16",
        "archivo_corriente": "10-16a",
        "slug_placa": "catalogo-staford-enchufesstf-ed-1016-horizontal",
        "slug_modular": "catalogo-staford-enchufesstf-ed-1016",
        "placa": {
            "BL": "enchufe-1016-doble-blanco.png",
            "NE": "enchufe-1016-doble-negro.png",
            "CA": "enchufe-1016-doble-cafe.png",
        },
    },
    {
        "prefijo": "STF-ET-10/16",
        "tipo": "triple",
        "corriente": "10/16",
        "archivo_corriente": "10-16a",
        "slug_placa": "catalogo-staford-enchufesstf-et-1016-horizontal",
        "slug_modular": "enchufe-triple-vertical-1016-a-stanford",
        "placa": {"BL": "enchufe-1016-triple-blanco.png"},
        "modular_colores": ("BL",),
    },
)


def ruta_modular(modelo, color_archivo):
    return (
        "productos/catalogo/staford-enchufes/"
        f"staford-{modelo['tipo']}-{modelo['archivo_corriente']}-{color_archivo}.png"
    )


def ruta_placa(archivo):
    return f"productos/catalogo/enchufes/{archivo}"


def nombre_producto(modelo, modular):
    corriente = modelo["corriente"]
    tipo = modelo["tipo"]
    if modular:
        return f"Enchufe modular {tipo} {corriente} A Stanford"
    return f"Enchufe {tipo} en placa {corriente} A Stanford"


def nombre_color(value):
    normalizado = (value or "").casefold().replace("é", "e")
    for codigo, nombre, nombre_archivo in COLORES:
        if normalizado in {nombre.casefold().replace("é", "e"), nombre_archivo}:
            return codigo, nombre, nombre_archivo
    return None


def actualizar_especificaciones_producto(Especificacion, alias, producto, modular):
    Especificacion.objects.using(alias).filter(
        producto_id=producto.pk,
        nombre__iexact="Orientación",
    ).delete()
    Especificacion.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        nombre="Sistema de montaje",
        defaults={
            "valor": "Mecanismo modular apilado" if modular else "Conjunto en placa",
            "unidad": "",
            "orden": 1,
        },
    )


def actualizar_caracteristicas(Caracteristica, alias, producto, modular):
    textos = (
        (
            "Mecanismo modular Stanford con tomas apiladas en altura",
            "Disponible en distintos colores",
            "Uso residencial y comercial",
        )
        if modular
        else (
            "Enchufe Stanford integrado en placa",
            "Disponible en los colores con imagen publicada",
            "Uso residencial y comercial",
        )
    )
    Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
    for orden, texto in enumerate(textos, start=1):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )


def crear_o_actualizar_variante(
    Variante,
    EspecificacionVariante,
    alias,
    producto,
    codigo,
    color,
    imagen,
    corriente,
    disponible=True,
    orden=1,
):
    variante, _ = Variante.objects.using(alias).get_or_create(
        codigo=codigo,
        defaults={
            "producto_id": producto.pk,
            "nombre": color,
            "imagen": imagen or "",
            "disponible": disponible,
            "orden": orden,
        },
    )
    variante.producto_id = producto.pk
    variante.nombre = color
    variante.imagen = imagen or ""
    variante.disponible = disponible
    variante.orden = orden
    variante.save(
        using=alias,
        update_fields=("producto", "nombre", "imagen", "disponible", "orden"),
    )
    EspecificacionVariante.objects.using(alias).filter(
        variante_id=variante.pk,
        nombre__iexact="Orientación",
    ).delete()
    for position, (nombre, valor, unidad) in enumerate(
        (
            ("Color", color, ""),
            ("Corriente nominal", corriente, "A"),
            ("Tensión nominal", "250", "V"),
        ),
        start=1,
    ):
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre=nombre,
            defaults={"valor": valor, "unidad": unidad, "orden": position},
        )
    return variante


def separar_formatos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    anterior = Categoria.objects.using(alias).filter(slug="enchufes").first()
    horizontal = Categoria.objects.using(alias).filter(slug="enchufes-horizontales").first()
    vertical = Categoria.objects.using(alias).filter(slug="enchufes-verticales").first()
    padre_id = (anterior or horizontal or vertical).padre_id if (anterior or horizontal or vertical) else None
    if not padre_id:
        return

    horizontal, _ = Categoria.objects.using(alias).update_or_create(
        slug="enchufes-horizontales",
        defaults={"nombre": "Enchufes en placa", "padre_id": padre_id, "orden": 20, "activa": True},
    )
    vertical, _ = Categoria.objects.using(alias).update_or_create(
        slug="enchufes-verticales",
        defaults={"nombre": "Enchufes modulares", "padre_id": padre_id, "orden": 10, "activa": True},
    )
    marca = Marca.objects.using(alias).filter(slug="stanford").first()
    marca_id = marca.pk if marca else None

    productos_placa = {}
    for modelo in MODELOS:
        producto_placa = Producto.objects.using(alias).filter(slug=modelo["slug_placa"]).first()
        if producto_placa:
            # Libera el slug base para la ficha modular correspondiente.
            if producto_placa.slug == modelo["slug_modular"]:
                producto_placa.slug = f"{producto_placa.slug}-horizontal"
            producto_placa.categoria_id = horizontal.pk
            producto_placa.nombre = nombre_producto(modelo, modular=False)
            producto_placa.subtitulo = horizontal.nombre
            producto_placa.descripcion = (
                f"{producto_placa.nombre}. Formato integrado en placa. "
                "Seleccione un color disponible para solicitar cotización."
            )
            producto_placa.texto_alternativo = producto_placa.nombre
            producto_placa.save(
                using=alias,
                update_fields=("slug", "categoria", "nombre", "subtitulo", "descripcion", "texto_alternativo"),
            )
            productos_placa[modelo["prefijo"]] = producto_placa

        if anterior:
            Producto.objects.using(alias).filter(categoria_id=anterior.pk).update(categoria_id=horizontal.pk)

    if anterior:
        anterior.activa = False
        anterior.save(using=alias, update_fields=["activa"])

    # Aparta los SKU históricos de placa antes de crear sus equivalentes modulares.
    for modelo in MODELOS:
        producto = productos_placa.get(modelo["prefijo"])
        if not producto:
            continue
        for variante in Variante.objects.using(alias).filter(producto_id=producto.pk):
            color_info = nombre_color(variante.nombre)
            if not color_info:
                variante.disponible = False
                variante.imagen = ""
                variante.save(using=alias, update_fields=["disponible", "imagen"])
                continue
            codigo_color, color, color_archivo = color_info
            codigo = f"{modelo['prefijo']}-{codigo_color}-H"
            conflicto = Variante.objects.using(alias).filter(codigo=codigo).exclude(pk=variante.pk).first()
            if conflicto:
                raise RuntimeError(f"El SKU horizontal {codigo} ya pertenece a otra variante.")
            variante.codigo = codigo
            archivo = modelo["placa"].get(codigo_color)
            variante.disponible = bool(archivo)
            variante.imagen = ruta_placa(archivo) if archivo else ""
            variante.nombre = color
            variante.save(
                using=alias,
                update_fields=("codigo", "disponible", "imagen", "nombre"),
            )
            EspecificacionVariante.objects.using(alias).filter(
                variante_id=variante.pk,
                nombre__iexact="Orientación",
            ).delete()
            for orden, (nombre, valor, unidad) in enumerate(
                (
                    ("Color", color, ""),
                    ("Corriente nominal", modelo["corriente"], "A"),
                    ("Tensión nominal", "250", "V"),
                ),
                start=1,
            ):
                EspecificacionVariante.objects.using(alias).update_or_create(
                    variante_id=variante.pk,
                    nombre=nombre,
                    defaults={"valor": valor, "unidad": unidad, "orden": orden},
                )

        actualizar_especificaciones_producto(Especificacion, alias, producto, modular=False)
        actualizar_caracteristicas(Caracteristica, alias, producto, modular=False)

        imagen_blanca = modelo["placa"].get("BL")
        if imagen_blanca:
            producto.imagen = ruta_placa(imagen_blanca)
            producto.save(using=alias, update_fields=["imagen"])

    # Cada conjunto modular se guarda en su propia ficha, con una variante por color.
    productos_modulares = {}
    for modelo in MODELOS:
        modular = Producto.objects.using(alias).filter(slug=modelo["slug_modular"]).first()
        imagen_blanca = ruta_modular(modelo, "blanco")
        nombre = nombre_producto(modelo, modular=True)
        producto_placa = productos_placa.get(modelo["prefijo"])
        orden_modular = max(producto_placa.orden - 1, 0) if producto_placa else 80
        if modular is None:
            modular = Producto.objects.using(alias).create(
                categoria_id=vertical.pk,
                nombre=nombre,
                marca="",
                marca_nueva_id=marca_id,
                modelo="",
                codigo=None,
                slug=modelo["slug_modular"],
                subtitulo=vertical.nombre,
                descripcion=(
                    f"{nombre}. Mecanismo Stanford con tomas apiladas en altura. "
                    "Seleccione el color correspondiente para solicitar cotización."
                ),
                imagen=imagen_blanca,
                texto_alternativo=nombre,
                etiqueta_visual="ENCHUFES",
                orden=orden_modular,
                publicado=True,
            )
        else:
            modular.categoria_id = vertical.pk
            modular.nombre = nombre
            modular.marca_nueva_id = marca_id or modular.marca_nueva_id
            modular.subtitulo = vertical.nombre
            modular.descripcion = (
                f"{nombre}. Mecanismo Stanford con tomas apiladas en altura. "
                "Seleccione el color correspondiente para solicitar cotización."
            )
            modular.imagen = imagen_blanca
            modular.texto_alternativo = nombre
            modular.orden = orden_modular
            modular.save(
                using=alias,
                update_fields=("categoria", "nombre", "marca_nueva", "subtitulo", "descripcion", "imagen", "texto_alternativo", "orden"),
            )
        productos_modulares[modelo["prefijo"]] = modular
        actualizar_especificaciones_producto(Especificacion, alias, modular, modular=True)
        actualizar_caracteristicas(Caracteristica, alias, modular, modular=True)

        colores_modulares = modelo.get("modular_colores", tuple(c[0] for c in COLORES))
        for orden, (codigo_color, color, color_archivo) in enumerate(
            (color for color in COLORES if color[0] in colores_modulares),
            start=1,
        ):
            ruta = ruta_modular(modelo, color_archivo)
            codigo = f"{modelo['prefijo']}-{codigo_color}"
            variante = crear_o_actualizar_variante(
                Variante,
                EspecificacionVariante,
                alias,
                modular,
                codigo,
                color,
                ruta,
                modelo["corriente"],
                orden=orden,
            )

            clave_legacy = (
                "manifiesto-staford-enchufes-staford-enchufes"
                f"staford-{modelo['tipo']}-{modelo['archivo_corriente']}-{color_archivo}png"
            )
            imagen = Imagen.objects.using(alias).filter(clave=clave_legacy).first()
            if not imagen:
                clave = slugify(f"stanford-modular-{modelo['prefijo']}-{color_archivo}")
                imagen = Imagen.objects.using(alias).filter(imagen=ruta).first()
                if not imagen:
                    imagen = Imagen.objects.using(alias).create(
                        producto_id=modular.pk,
                        clave=clave,
                        imagen=ruta,
                        texto_alternativo=f"{nombre}, color {color}",
                        orden=orden,
                    )
            imagen.producto_id = modular.pk
            imagen.imagen = ruta
            imagen.texto_alternativo = f"{nombre}, color {color}"
            imagen.orden = orden
            imagen.save(using=alias, update_fields=("producto", "imagen", "texto_alternativo", "orden"))
            imagen.variantes.set([variante])

    # Las galerías de placa solo muestran las fotos de las variantes activas y compatibles.
    for modelo in MODELOS:
        producto = productos_placa.get(modelo["prefijo"])
        if not producto:
            continue
        for variante in Variante.objects.using(alias).filter(producto_id=producto.pk, disponible=True):
            color_info = nombre_color(variante.nombre)
            if not color_info:
                continue
            codigo_color, color, _ = color_info
            clave = f"catalogo-placa-{producto.pk}-{codigo_color.lower()}"
            imagen, _ = Imagen.objects.using(alias).get_or_create(
                clave=clave,
                defaults={
                    "producto_id": producto.pk,
                    "imagen": variante.imagen.name,
                    "texto_alternativo": f"{producto.nombre}, color {color}",
                    "orden": variante.orden,
                },
            )
            imagen.producto_id = producto.pk
            imagen.imagen = variante.imagen.name
            imagen.texto_alternativo = f"{producto.nombre}, color {color}"
            imagen.orden = variante.orden
            imagen.save(using=alias, update_fields=("producto", "imagen", "texto_alternativo", "orden"))
            imagen.variantes.set([variante])

    for producto in productos_placa.values():
        for imagen in Imagen.objects.using(alias).filter(producto_id=producto.pk, imagen__icontains="staford-enchufes"):
            imagen.delete(using=alias)


class Migration(migrations.Migration):
    dependencies = [("core", "0022_nombre_marca_modulos_stanford")]

    operations = [migrations.RunPython(separar_formatos, migrations.RunPython.noop)]
