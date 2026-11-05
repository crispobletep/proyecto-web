from django.db import migrations


PRODUCTOS = (
    {
        "slug": "kalop-calota-sp-2-puestos-transparente",
        "nombre": "Calota S/P 2 puestos para tapa transparente",
        "imagen": "productos/catalogo/kalop-tableros/calota-sp-2-puestos-transparente.png",
        "alt": "Calota Kalop de 2 puestos con tapa transparente",
        "descripcion": "Calota Kalop para dos puestos, preparada para tapa transparente.",
        "caracteristicas": (
            "Formato para 2 puestos.",
            "Diseñada para instalación sobrepuesta.",
            "Compatible con tapa transparente.",
        ),
        "especificaciones": (
            ("Capacidad", "2", "puestos"),
            ("Montaje", "Sobrepuesto", ""),
            ("Tapa", "Transparente", ""),
        ),
    },
    {
        "slug": "kalop-calota-sobrepuesta-2-modulos-ip20-sin-tapa",
        "nombre": "Calota sobrepuesta para 2 módulos IP20 sin tapa",
        "imagen": "productos/catalogo/kalop-tableros/calota-sobrepuesta-2-modulos-ip20-sin-tapa.png",
        "alt": "Calota Kalop sobrepuesta para 2 módulos, sin tapa",
        "descripcion": "Calota Kalop de montaje sobrepuesto para dos módulos, sin tapa y con protección IP20.",
        "caracteristicas": (
            "Capacidad para 2 módulos.",
            "Montaje sobrepuesto.",
            "Versión sin tapa, protección IP20.",
        ),
        "especificaciones": (
            ("Capacidad", "2", "módulos"),
            ("Montaje", "Sobrepuesto", ""),
            ("Grado de protección", "IP20", ""),
            ("Tapa", "Sin tapa", ""),
        ),
    },
    {
        "slug": "kalop-calota-interior-1-4cc-tapa-transparente-gris",
        "nombre": "Calota interior 1–4 CC con tapa transparente gris",
        "imagen": "productos/catalogo/kalop-tableros/calota-interior-1-4cc-tapa-transparente-gris.png",
        "alt": "Calota Kalop interior 1–4 CC con tapa transparente gris",
        "descripcion": "Calota Kalop para instalación interior, configuración 1–4 CC y tapa transparente gris.",
        "caracteristicas": (
            "Formato para instalación interior.",
            "Configuración 1–4 CC.",
            "Incluye tapa transparente gris.",
        ),
        "especificaciones": (
            ("Configuración", "1–4 CC", ""),
            ("Instalación", "Interior", ""),
            ("Tapa", "Transparente gris", ""),
        ),
    },
    {
        "slug": "kalop-calota-interior-1-6cc-tapa-transparente-gris",
        "nombre": "Calota interior 1–6 CC con tapa transparente gris",
        "imagen": "productos/catalogo/kalop-tableros/calota-interior-1-6cc-tapa-transparente-gris.png",
        "alt": "Calota Kalop interior 1–6 CC con tapa transparente gris",
        "descripcion": "Calota Kalop para instalación interior, configuración 1–6 CC y tapa transparente gris.",
        "caracteristicas": (
            "Formato para instalación interior.",
            "Configuración 1–6 CC.",
            "Incluye tapa transparente gris.",
        ),
        "especificaciones": (
            ("Configuración", "1–6 CC", ""),
            ("Instalación", "Interior", ""),
            ("Tapa", "Transparente gris", ""),
        ),
    },
    {
        "slug": "kalop-caja-gris-ip55-tapa-2-modulos-2-puestos",
        "nombre": "Caja gris IP55 con tapa, 2 módulos y 2 puestos",
        "imagen": "productos/catalogo/kalop-tableros/caja-gris-ip55-tapa-2-modulos-2-puestos.png",
        "alt": "Caja Kalop gris IP55 con tapa para 2 módulos y 2 puestos",
        "descripcion": "Caja Kalop gris con tapa, protección IP55 y capacidad para dos módulos y dos puestos.",
        "caracteristicas": (
            "Capacidad para 2 módulos y 2 puestos.",
            "Caja gris con tapa.",
            "Protección IP55.",
        ),
        "especificaciones": (
            ("Módulos", "2", ""),
            ("Puestos", "2", ""),
            ("Color", "Gris", ""),
            ("Grado de protección", "IP55", ""),
            ("Tapa", "Incluida", ""),
        ),
    },
    {
        "slug": "kalop-caja-gris-ip55-tapa-3-modulos-3-puestos",
        "nombre": "Caja gris IP55 con tapa, 3 módulos y 3 puestos",
        "imagen": "productos/catalogo/kalop-tableros/caja-gris-ip55-tapa-3-modulos-3-puestos.png",
        "alt": "Caja Kalop gris IP55 con tapa para 3 módulos y 3 puestos",
        "descripcion": "Caja Kalop gris con tapa, protección IP55 y capacidad para tres módulos y tres puestos.",
        "caracteristicas": (
            "Capacidad para 3 módulos y 3 puestos.",
            "Caja gris con tapa.",
            "Protección IP55.",
        ),
        "especificaciones": (
            ("Módulos", "3", ""),
            ("Puestos", "3", ""),
            ("Color", "Gris", ""),
            ("Grado de protección", "IP55", ""),
            ("Tapa", "Incluida", ""),
        ),
    },
)


def agregar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    categoria = Categoria.objects.using(alias).get(slug="tableros-plasticos")
    marca = Marca.objects.using(alias).get(slug="kalop")
    siguiente_orden = (
        Producto.objects.using(alias)
        .filter(categoria_id=categoria.pk)
        .order_by("-orden")
        .values_list("orden", flat=True)
        .first()
        or 0
    ) + 10

    for posicion, datos in enumerate(PRODUCTOS):
        producto, creado = Producto.objects.using(alias).update_or_create(
            slug=datos["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": datos["nombre"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Tableros eléctricos",
                "descripcion": datos["descripcion"],
                "imagen": datos["imagen"],
                "texto_alternativo": datos["alt"],
                "etiqueta_visual": "KALOP",
                "orden": siguiente_orden + posicion * 10,
                "publicado": True,
            },
        )

        for orden, texto in enumerate(datos["caracteristicas"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )
        for orden, (nombre, valor, unidad) in enumerate(datos["especificaciones"], start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )


def revertir_productos(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(
        slug__in=[producto["slug"] for producto in PRODUCTOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0065_ocultar_modulos_y_bases_industriales"),
    ]

    operations = [
        migrations.RunPython(agregar_productos, revertir_productos),
    ]
