from django.db import migrations


IMAGE_ROOT = "productos/catalogo/tarugos-grapas/"


def agregar_tarugos_y_grapas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="conexion-y-aislacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="tarugos-y-grapas",
        defaults={
            "nombre": "Tarugos y grapas",
            "padre_id": familia.pk,
            "orden": 12,
            "activa": True,
        },
    )

    grapas, _ = Producto.objects.using(alias).update_or_create(
        slug="grapas-curvas-cable-toolmak",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Grapas curvas para cable TOOLMAK",
            "marca": "TOOLMAK",
            "marca_nueva_id": None,
            "modelo": "TMK19332",
            "codigo": None,
            "subtitulo": "Grapas para cable",
            "descripcion": (
                "Grapas curvas TOOLMAK para fijación de cables. Disponibles "
                "en medidas de 6, 7, 8 y 10 mm. La imagen corresponde al "
                "envase TOOLMAK de 10 mm."
            ),
            "imagen": IMAGE_ROOT + "grapas-curvas-toolmak-10mm.png",
            "texto_alternativo": "Envase TOOLMAK de grapas curvas para cable de 10 mm",
            "etiqueta_visual": "TARUGOS Y GRAPAS",
            "orden": 1,
            "publicado": True,
        },
    )
    Caracteristica.objects.using(alias).filter(producto_id=grapas.pk).delete()
    Caracteristica.objects.using(alias).create(
        producto_id=grapas.pk,
        texto="Grapas curvas para fijación de cables.",
        orden=1,
    )
    Caracteristica.objects.using(alias).create(
        producto_id=grapas.pk,
        texto="Medidas disponibles: 6, 7, 8 y 10 mm.",
        orden=2,
    )
    Especificacion.objects.using(alias).filter(producto_id=grapas.pk).delete()
    Especificacion.objects.using(alias).create(
        producto_id=grapas.pk,
        nombre="Material",
        valor="PE",
        unidad="",
        orden=1,
    )
    for orden, medida in enumerate(("10", "8", "7", "6"), start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=grapas.pk,
            nombre=f"{medida} mm",
            defaults={
                "imagen": "",
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Medida",
            defaults={"valor": medida, "unidad": "mm", "orden": 1},
        )

    tarugos = (
        (6, 2),
        (8, 3),
        (10, 4),
    )
    for medida, orden in tarugos:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=f"tarugo-plastico-con-tope-{medida}mm",
            defaults={
                "categoria_id": categoria.pk,
                "nombre": f"Tarugo plástico con tope {medida} mm",
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Tarugos",
                "descripcion": (
                    f"Tarugo plástico con tope de {medida} mm de diámetro."
                ),
                "imagen": IMAGE_ROOT + "tarugo-plastico-con-tope.png",
                "texto_alternativo": (
                    f"Tarugo plástico con tope de {medida} mm"
                ),
                "etiqueta_visual": "TARUGOS Y GRAPAS",
                "orden": orden,
                "publicado": True,
            },
        )
        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=f"Diámetro: {medida} mm.",
            orden=1,
        )
        Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre="Diámetro",
            valor=str(medida),
            unidad="mm",
            orden=1,
        )

    adicionales = (
        {
            "slug": "tarugo-vulcanita-cola-de-chancho",
            "nombre": "Tarugo para vulcanita tipo cola de chancho",
            "imagen": "tarugo-vulcanita-cola-de-chancho.png",
            "alt": "Tarugo para vulcanita tipo cola de chancho",
            "descripcion": "Tarugo tipo cola de chancho para fijaciones en placas de vulcanita.",
            "orden": 5,
        },
        {
            "slug": "tarugo-paloma-plastico-vulcanita",
            "nombre": "Tarugo paloma plástico para vulcanita",
            "imagen": "tarugo-paloma-plastico-vulcanita.png",
            "alt": "Tarugo paloma plástico para placas de vulcanita",
            "descripcion": "Tarugo paloma plástico para fijaciones en placas de vulcanita.",
            "orden": 6,
        },
    )
    for definition in adicionales:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definition["nombre"],
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Tarugos para vulcanita",
                "descripcion": definition["descripcion"],
                "imagen": IMAGE_ROOT + definition["imagen"],
                "texto_alternativo": definition["alt"],
                "etiqueta_visual": "TARUGOS Y GRAPAS",
                "orden": definition["orden"],
                "publicado": True,
            },
        )
        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto="Para fijaciones en placas de vulcanita.",
            orden=1,
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0110_agregar_catalogo_herramientas")]

    operations = [
        migrations.RunPython(agregar_tarugos_y_grapas, migrations.RunPython.noop)
    ]
