from django.db import migrations


ROOT = "productos/catalogo/canalizacion-electrica/abrazaderas-caddy/"
MEDIDAS = (20, 25, 32)


def agregar_abrazaderas_caddy(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model(
        "core", "EspecificacionVariante"
    )

    familia = Categoria.objects.using(alias).get(
        slug="canalizacion-electrica"
    )
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="abrazaderas-caddy",
        defaults={
            "nombre": "Abrazaderas Caddy",
            "padre_id": familia.pk,
            "orden": 17,
            "activa": True,
        },
    )

    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="abrazadera-caddy-con-perno",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Abrazadera tipo Caddy con perno",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Abrazaderas Caddy",
            "descripcion": (
                "Abrazadera metálica tipo Caddy con perno para sujeción. "
                "Disponible en medidas de 20, 25 y 32 mm."
            ),
            "imagen": ROOT + "abrazadera-caddy-con-perno-20mm.png",
            "texto_alternativo": (
                "Abrazadera metálica tipo Caddy con perno, medida 20 mm"
            ),
            "etiqueta_visual": "ABRAZADERA CADDY",
            "orden": 920,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Abrazadera metálica tipo Caddy con perno.",
            "Medidas disponibles: 20, 25 y 32 mm.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )

    Especificacion.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        nombre="Tipo",
        defaults={
            "valor": "Caddy con perno",
            "unidad": "",
            "orden": 1,
        },
    )

    for orden, medida in enumerate(MEDIDAS, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"{medida} mm",
            defaults={
                "imagen": ROOT + f"abrazadera-caddy-con-perno-{medida}mm.png",
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Medida",
            defaults={
                "valor": str(medida),
                "unidad": "mm",
                "orden": 1,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0127_agregar_fusible_y_portafusible"),
    ]

    operations = [
        migrations.RunPython(
            agregar_abrazaderas_caddy,
            migrations.RunPython.noop,
        ),
    ]
