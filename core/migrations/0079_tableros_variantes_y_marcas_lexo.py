from django.db import migrations


BOARD_IMAGE_ROOT = "productos/catalogo/tableros-cnc/"
BOARD_PRODUCTS = (
    {
        "slug": "tablero-plastico-forceman-4-modulos",
        "polos": 4,
        "orden": 1360,
        "embutido": "tablero-forceman-4-modulos.png",
        "sobrepuesto": "tablero-forceman-4-modulos.png",
    },
    {
        "slug": "tablero-sobrepuesto-dex-6-polos",
        "polos": 6,
        "orden": 1370,
        "embutido": "tablero-dex-6-polos.png",
        "sobrepuesto": "tablero-dex-6-polos.png",
    },
    {
        "slug": "tablero-plastico-8-vias",
        "polos": 8,
        "orden": 1380,
        "embutido": "tablero-8-vias.png",
        "sobrepuesto": "tablero-8-vias.png",
    },
    {
        "slug": "tablero-plastico-12-vias",
        "polos": 12,
        "orden": 1390,
        "embutido": "tablero-12-vias.png",
        "sobrepuesto": "tablero-lexo-12-polos.png",
    },
    {
        "slug": "tablero-18-polos",
        "polos": 18,
        "orden": 1400,
        "embutido": "tablero-dex-18-polos.png",
        "sobrepuesto": "tablero-lexo-18-polos.png",
    },
    {
        "slug": "tablero-plastico-24-polos",
        "polos": 24,
        "orden": 1410,
        "embutido": "",
        "sobrepuesto": "",
    },
    {
        "slug": "tablero-plastico-36-vias",
        "polos": 36,
        "orden": 1420,
        "embutido": "tablero-36-vias-producto.png",
        "sobrepuesto": "tablero-36-vias-producto.png",
    },
)


def completar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Marca = apps.get_model("core", "Marca")

    tablero_base = Producto.objects.using(alias).get(slug="tablero-18-polos")
    descripcion_tablero = (
        "Tablero plástico de distribución de {polos} polos, disponible para "
        "montaje embutido o sobrepuesto."
    )
    for definicion in BOARD_PRODUCTS:
        producto, _ = Producto.objects.using(alias).get_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": tablero_base.categoria_id,
                "nombre": "",
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": tablero_base.subtitulo,
                "descripcion": "",
                "imagen": "",
                "texto_alternativo": "",
                "etiqueta_visual": "TABLEROS ELÉCTRICOS",
                "orden": definicion["orden"],
                "publicado": True,
            },
        )

        imagen_embutido = (
            BOARD_IMAGE_ROOT + definicion["embutido"]
            if definicion["embutido"]
            else ""
        )
        imagen_sobrepuesto = (
            BOARD_IMAGE_ROOT + definicion["sobrepuesto"]
            if definicion["sobrepuesto"]
            else ""
        )
        nombre = f"Tablero plástico de {definicion['polos']} polos"
        producto.nombre = nombre
        producto.descripcion = descripcion_tablero.format(
            polos=definicion["polos"]
        )
        producto.imagen = imagen_embutido or imagen_sobrepuesto
        producto.texto_alternativo = nombre
        producto.etiqueta_visual = "TABLEROS ELÉCTRICOS"
        producto.orden = definicion["orden"]
        producto.publicado = True
        producto.save(
            using=alias,
            update_fields=(
                "nombre", "descripcion", "imagen", "texto_alternativo",
                "etiqueta_visual", "orden", "publicado",
            ),
        )

        Caracteristica.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            orden=1,
            defaults={
                "texto": "Disponible para montaje embutido o sobrepuesto."
            },
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Polos",
            defaults={
                "valor": str(definicion["polos"]),
                "unidad": "polos",
                "orden": 1,
            },
        )

        for orden, (nombre_variante, montaje, imagen) in enumerate(
            (
                ("Embutido", "Embutido", imagen_embutido),
                ("Sobrepuesto", "Sobrepuesto", imagen_sobrepuesto),
            ),
            start=1,
        ):
            variante, _ = Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre_variante,
                defaults={
                    "codigo": None,
                    "modelo": "",
                    "imagen": imagen,
                    "disponible": True,
                    "orden": orden,
                },
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Montaje",
                defaults={"valor": montaje, "unidad": "", "orden": 1},
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Polos",
                defaults={
                    "valor": str(definicion["polos"]),
                    "unidad": "polos",
                    "orden": 2,
                },
            )

    # La tarjeta combinada sustituye a las tarjetas duplicadas de 12 y 18 polos.
    Producto.objects.using(alias).filter(
        slug="tablero-sobrepuesto-lexo-12-polos"
    ).update(publicado=False)
    Producto.objects.using(alias).filter(
        slug="tablero-embutido-dex-18-polos"
    ).update(publicado=False)

    lexo = Marca.objects.using(alias).get(slug="lexo")
    Producto.objects.using(alias).filter(
        slug__in=(
            "enchufe-industrial-macho-volante",
            "enchufe-industrial-hembra-volante",
            "enchufe-industrial-macho-sobrepuesto",
            "enchufe-industrial-hembra-sobrepuesta",
        ),
        publicado=True,
    ).update(marca_nueva_id=lexo.pk)

    equipo_base = Producto.objects.using(alias).get(
        slug="equipo-estanco-led-2x9w"
    )
    equipo, _ = Producto.objects.using(alias).get_or_create(
        slug="equipo-estanco-led-2x18w",
        defaults={
            "categoria_id": equipo_base.categoria_id,
            "nombre": "Equipo estanco LED 2 × 18 W",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": equipo_base.subtitulo,
            "descripcion": "Equipo estanco para dos tubos LED de 18 W.",
            "imagen": "",
            "texto_alternativo": "",
            "etiqueta_visual": "EQUIPOS ESTANCOS LED",
            "orden": 570,
            "publicado": True,
        },
    )
    equipo.nombre = "Equipo estanco LED 2 × 18 W"
    equipo.descripcion = "Equipo estanco para dos tubos LED de 18 W."
    equipo.imagen = ""
    equipo.texto_alternativo = "Equipo estanco LED para dos tubos de 18 W"
    equipo.etiqueta_visual = "EQUIPOS ESTANCOS LED"
    equipo.orden = 570
    equipo.publicado = True
    equipo.save(
        using=alias,
        update_fields=(
            "nombre", "descripcion", "imagen", "texto_alternativo",
            "etiqueta_visual", "orden", "publicado",
        ),
    )
    Variante.objects.using(alias).update_or_create(
        producto_id=equipo.pk,
        nombre="2 × 18 W",
        defaults={
            "codigo": None,
            "modelo": "",
            "imagen": "",
            "disponible": True,
            "orden": 1,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0078_intercambiar_imagenes_gabinetes_500_600"),
    ]

    operations = [
        migrations.RunPython(completar_catalogo),
    ]
