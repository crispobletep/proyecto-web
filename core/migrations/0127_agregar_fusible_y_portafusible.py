from django.db import migrations


ROOT = "productos/catalogo/protecciones/fusibles/"


def agregar_fusible_y_portafusible(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    familia = Categoria.objects.using(alias).get(slug="proteccion-electrica")
    definiciones_categoria = (
        ("fusibles", "Fusibles", 5),
        ("portafusibles", "Portafusibles", 6),
    )
    categorias = {}
    for slug, nombre, orden in definiciones_categoria:
        categoria, _ = Categoria.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "padre_id": familia.pk,
                "orden": orden,
                "activa": True,
            },
        )
        categorias[slug] = categoria

    cnc = Marca.objects.using(alias).get(slug="cnc")
    productos = (
        {
            "slug": "fusible-cilindrico-10-3x38mm-2a",
            "nombre": "Fusible cilíndrico 10,3 × 38 mm · 2 A",
            "categoria": "fusibles",
            "marca_id": None,
            "marca": "",
            "modelo": "",
            "imagen": "fusible-cilindrico-10-3x38mm-2a.png",
            "alt": "Fusible cilíndrico de 2 A y 10,3 × 38 mm",
            "descripcion": (
                "Fusible cilíndrico de 2 A, formato 10,3 × 38 mm. "
                "El cuerpo indica tensión de hasta 1000 V DC."
            ),
            "etiqueta": "FUSIBLES",
            "orden": 1,
            "caracteristicas": (
                "Fusible cilíndrico para portafusible compatible.",
                "Corriente nominal: 2 A.",
                "Tensión indicada: hasta 1000 V DC.",
            ),
            "especificaciones": (
                ("Formato", "10,3 × 38", "mm"),
                ("Corriente nominal", "2", "A"),
                ("Tensión máxima indicada", "1000", "V DC"),
            ),
        },
        {
            "slug": "portafusible-cnc-rt18-32x-1p-10x38mm",
            "nombre": "Portafusible CNC RT18-32X 1P 10 × 38 mm",
            "categoria": "portafusibles",
            "marca_id": cnc.pk,
            "marca": "",
            "modelo": "RT18-32X",
            "imagen": "portafusible-cnc-rt18-32x-1p-10x38mm.png",
            "alt": (
                "Portafusible CNC RT18-32X unipolar para fusible 10 × 38 mm"
            ),
            "descripcion": (
                "Portafusible unipolar CNC RT18-32X para fusible cilíndrico "
                "10 × 38 mm, montaje en riel DIN. Corriente nominal de 32 A "
                "y tensión indicada de 690 V."
            ),
            "etiqueta": "PORTAFUSIBLES CNC",
            "orden": 1,
            "caracteristicas": (
                "Montaje en riel DIN.",
                "Compatible con fusible cilíndrico 10 × 38 mm.",
                "Indicador visual rojo en el portafusible.",
            ),
            "especificaciones": (
                ("Polos", "1", "P"),
                ("Formato de fusible", "10 × 38", "mm"),
                ("Corriente nominal", "32", "A"),
                ("Tensión nominal", "690", "V"),
                ("Montaje", "Riel DIN", ""),
            ),
        },
    )

    for definicion in productos:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": categorias[definicion["categoria"]].pk,
                "nombre": definicion["nombre"],
                "marca": definicion["marca"],
                "marca_nueva_id": definicion["marca_id"],
                "modelo": definicion["modelo"],
                "codigo": None,
                "subtitulo": categorias[definicion["categoria"]].nombre,
                "descripcion": definicion["descripcion"],
                "imagen": ROOT + definicion["imagen"],
                "texto_alternativo": definicion["alt"],
                "etiqueta_visual": definicion["etiqueta"],
                "orden": definicion["orden"],
                "publicado": True,
            },
        )

        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, texto in enumerate(definicion["caracteristicas"], start=1):
            Caracteristica.objects.using(alias).create(
                producto_id=producto.pk,
                texto=texto,
                orden=orden,
            )

        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, (nombre, valor, unidad) in enumerate(
            definicion["especificaciones"], start=1
        ):
            Especificacion.objects.using(alias).create(
                producto_id=producto.pk,
                nombre=nombre,
                valor=valor,
                unidad=unidad,
                orden=orden,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0126_agregar_mecanismos_luzica"),
    ]

    operations = [
        migrations.RunPython(
            agregar_fusible_y_portafusible,
            migrations.RunPython.noop,
        ),
    ]
