from django.db import migrations


IMAGEN = (
    "productos/catalogo/conductores-conexiones/barras/"
    "repartidor-tetrapolar-125-400a.jpeg"
)
AMPERAJES = (125, 160, 200, 250, 400)


def agregar_repartidores_tetrapolares(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    ImagenProducto = apps.get_model("core", "ImagenProducto")

    familia, _ = Categoria.objects.using(alias).update_or_create(
        slug="conexion-y-aislacion",
        defaults={"nombre": "Conexión y aislación", "padre_id": None, "orden": 30, "activa": True},
    )
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="barras-distribucion",
        defaults={
            "nombre": "Barras de conexión y distribución",
            "padre_id": familia.pk,
            "orden": 3,
            "activa": True,
        },
    )

    for orden, amperaje in enumerate(AMPERAJES, start=180):
        slug = (
            "barra-repartidora-tetrapolar-125a"
            if amperaje == 125
            else f"repartidor-tetrapolar-{amperaje}a"
        )
        nombre = f"Repartidor tetrapolar {amperaje} A"
        alt = "Repartidor tetrapolar de cobre con cubierta aislante"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Distribución tetrapolar para tableros",
                "descripcion": (
                    "Repartidor tetrapolar de cobre con cubierta aislante para "
                    "distribuir alimentación en tableros eléctricos. "
                    f"Capacidad nominal de {amperaje} A."
                ),
                "imagen": IMAGEN,
                "texto_alternativo": f"{alt}, capacidad de {amperaje} amperios",
                "etiqueta_visual": "DISTRIBUCIÓN",
                "orden": orden,
                "publicado": True,
            },
        )

        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        for posicion, texto in enumerate(
            (
                "Configuración tetrapolar",
                "Cubierta aislante transparente",
                f"Corriente nominal de {amperaje} A",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).create(
                producto_id=producto.pk,
                texto=texto,
                orden=posicion,
            )

        Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
        for posicion, (nombre_especificacion, valor, unidad) in enumerate(
            (("Polos", "4", ""), ("Corriente nominal", str(amperaje), "A")),
            start=1,
        ):
            Especificacion.objects.using(alias).create(
                producto_id=producto.pk,
                nombre=nombre_especificacion,
                valor=valor,
                unidad=unidad,
                orden=posicion,
            )

        # Mantiene las referencias de cotizaciones antiguas, pero deja visible
        # solo la variante por corriente que se muestra en esta ficha.
        Variante.objects.using(alias).filter(producto_id=producto.pk).update(
            disponible=False
        )
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"{amperaje} A",
            defaults={
                "modelo": "",
                "codigo": f"PH-TETRAPOLAR-{amperaje}A",
                "imagen": IMAGEN,
                "disponible": True,
                "orden": 1,
            },
        )
        EspecificacionVariante.objects.using(alias).filter(
            variante_id=variante.pk
        ).delete()
        for posicion, (nombre_especificacion, valor, unidad) in enumerate(
            (("Polos", "4", ""), ("Corriente nominal", str(amperaje), "A")),
            start=1,
        ):
            EspecificacionVariante.objects.using(alias).create(
                variante_id=variante.pk,
                nombre=nombre_especificacion,
                valor=valor,
                unidad=unidad,
                orden=posicion,
            )

        ImagenProducto.objects.using(alias).filter(
            producto_id=producto.pk,
            clave__startswith="carga-conductores-conexiones-",
        ).delete()
        imagen_catalogo, _ = ImagenProducto.objects.using(alias).update_or_create(
            clave=(
                "carga-conductores-conexiones-"
                f"barra-tetrapolar-{amperaje}a"
            ),
            defaults={
                "producto_id": producto.pk,
                "imagen": IMAGEN,
                "texto_alternativo": f"{alt}, capacidad de {amperaje} amperios",
                "orden": 1,
            },
        )
        imagen_catalogo.variantes.set([variante])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0133_quitar_marca_dex_del_selector_3p"),
    ]

    operations = [
        migrations.RunPython(
            agregar_repartidores_tetrapolares,
            migrations.RunPython.noop,
        ),
    ]
