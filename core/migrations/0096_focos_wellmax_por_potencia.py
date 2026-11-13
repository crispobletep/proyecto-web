from django.db import migrations


ROOT = "productos/catalogo/iluminacion/focos-superficie/"
FOCOS = (
    (10, "wellmax-eagle-eye-10w.png"),
    (20, "wellmax-eagle-eye-20w.png"),
    (30, "wellmax-eagle-eye-30w.png"),
)


def organizar_focos_wellmax(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Marca = apps.get_model("core", "Marca")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="focos",
        defaults={"nombre": "Focos", "padre_id": iluminacion.pk, "orden": 61, "activa": True},
    )
    marca = Marca.objects.using(alias).filter(slug="wellmax").first()
    existentes = Producto.objects.using(alias).filter(slug="foco-led-superficie-wellmax-eagle-eye")

    for orden, (potencia, imagen_archivo) in enumerate(FOCOS, start=1):
        slug = "foco-led-superficie-wellmax-eagle-eye" if potencia == 10 else f"foco-led-superficie-wellmax-eagle-eye-{potencia}w"
        imagen = ROOT + imagen_archivo
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": f"Foco LED de superficie Wellmax Eagle Eye {potencia} W",
                "marca": "",
                "marca_nueva_id": marca.pk if marca else None,
                "modelo": "Eagle Eye",
                "codigo": None,
                "subtitulo": "Focos LED Wellmax",
                "descripcion": f"Foco LED Wellmax Eagle Eye de superficie, {potencia} W, con cabezal orientable. Disponible en color blanco o negro.",
                "imagen": imagen,
                "texto_alternativo": f"Foco LED de superficie Wellmax Eagle Eye {potencia} W en blanco y negro",
                "etiqueta_visual": "WELLMAX",
                "orden": 940 + (potencia // 10) * 10,
                "publicado": True,
            },
        )

        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Potencia",
            defaults={"valor": str(potencia), "unidad": "W", "orden": 1},
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Montaje",
            defaults={"valor": "Superficie", "unidad": "", "orden": 2},
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Orientación",
            defaults={"valor": "Giro 360 · inclinación 90", "unidad": "°", "orden": 3},
        )

        # Preserve the existing 10 W color choices while removing the other
        # power options from that card; each wattage gets its own product card.
        if potencia == 10:
            variantes_10w = []
            for variante in Variante.objects.using(alias).filter(producto_id=producto.pk):
                potencia_variante = EspecificacionVariante.objects.using(alias).filter(
                    variante_id=variante.pk,
                    nombre="Potencia",
                    valor="10",
                ).exists()
                if potencia_variante:
                    variantes_10w.append(variante)
                else:
                    variante.delete()

            for variante in variantes_10w:
                if variante.nombre.endswith("Blanco"):
                    color = "Blanco"
                else:
                    color = "Negro"
                variante.nombre = color
                variante.imagen = imagen
                variante.orden = 1 if color == "Blanco" else 2
                variante.save(update_fields=["nombre", "imagen", "orden"])

        for color_order, color in enumerate(("Blanco", "Negro"), start=1):
            variante, _ = Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=color,
                defaults={"imagen": imagen, "disponible": True, "orden": color_order},
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Color",
                defaults={"valor": color, "unidad": "", "orden": 1},
            )

        features = (
            f"Potencia: {potencia} W.",
            "Disponible en color blanco o negro.",
            "Cabezal orientable: giro 360° e inclinación 90°.",
        )
        for feature_order, text in enumerate(features, start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=feature_order,
                defaults={"texto": text},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0095_actualizar_paneles_avc_calidos")]

    operations = [migrations.RunPython(organizar_focos_wellmax, migrations.RunPython.noop)]
