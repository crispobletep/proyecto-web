from django.db import migrations


ROOT = "productos/catalogo/protecciones/automaticos-same/"
CALIBRES = (10, 16, 20, 25, 30, 40)


def agregar_automaticos_same(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model(
        "core", "EspecificacionVariante"
    )

    familia = Categoria.objects.using(alias).get(slug="proteccion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="automaticos-same",
        defaults={
            "nombre": "Automáticos SAME",
            "padre_id": familia.pk,
            "orden": 7,
            "activa": True,
        },
    )
    marca, _ = Marca.objects.using(alias).get_or_create(
        slug="same",
        defaults={"nombre": "SAME", "activa": True},
    )

    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="interruptores-automaticos-same-1p",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Interruptores automáticos SAME 1P",
            "marca": "",
            "marca_nueva_id": marca.pk,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Automáticos SAME",
            "descripcion": (
                "Interruptores automáticos SAME SG unipolares, curva B, "
                "230 V y poder de corte indicado de 6 kA. Selecciona el "
                "calibre requerido."
            ),
            "imagen": ROOT + "interruptor-automatico-same-1p-10a.png",
            "texto_alternativo": (
                "Interruptor automático SAME SG unipolar, curva B, 10 A"
            ),
            "etiqueta_visual": "AUTOMÁTICOS SAME",
            "orden": 700,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Interruptor automático unipolar (1P).",
            "Curva B y tensión nominal indicada de 230 V~.",
            "Poder de corte indicado: 6000 A (6 kA).",
            "Calibres ordenados de menor a mayor: 10, 16, 20, 25, 30 y 40 A.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).create(
            producto_id=producto.pk,
            texto=texto,
            orden=orden,
        )

    Especificacion.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, (nombre, valor, unidad) in enumerate(
        (
            ("Polos", "1P", ""),
            ("Curva de disparo", "B", ""),
            ("Tensión nominal", "230", "V~"),
            ("Poder de corte", "6000", "A (6 kA)"),
        ),
        start=1,
    ):
        Especificacion.objects.using(alias).create(
            producto_id=producto.pk,
            nombre=nombre,
            valor=valor,
            unidad=unidad,
            orden=orden,
        )

    for orden, calibre in enumerate(CALIBRES, start=1):
        modelo = f"4001A6-B{calibre}"
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=f"1P · {calibre} A · curva B",
            defaults={
                "modelo": modelo,
                "codigo": None,
                "imagen": ROOT + f"interruptor-automatico-same-1p-{calibre}a.png",
                "disponible": True,
                "orden": orden,
            },
        )
        for spec_orden, (nombre, valor, unidad) in enumerate(
            (
                ("Corriente nominal", str(calibre), "A"),
                ("Modelo", modelo, ""),
            ),
            start=1,
        ):
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre=nombre,
                defaults={
                    "valor": valor,
                    "unidad": unidad,
                    "orden": spec_orden,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0128_agregar_abrazaderas_caddy_con_perno"),
    ]

    operations = [
        migrations.RunPython(
            agregar_automaticos_same,
            migrations.RunPython.noop,
        ),
    ]
