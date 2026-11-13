from django.db import migrations


IMAGE_ROOT = "productos/catalogo/amarras/"
MEASUREMENTS = (
    ("150", "3,6", 760),
    ("200", "4,8", 770),
    ("250", "4,8", 780),
    ("300", "4,8", 790),
    ("370", "4,8", 800),
)


def agregar_amarras(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="conexion-y-aislacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="amarras",
        defaults={
            "nombre": "Amarras",
            "padre_id": familia.pk,
            "orden": 11,
            "activa": True,
        },
    )

    for length, width, order in MEASUREMENTS:
        length_slug = length
        width_slug = width.replace(",", "-")
        measure = f"{length} × {width} mm"
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=f"amarra-plastica-{length_slug}x{width_slug}-mm",
            defaults={
                "categoria_id": categoria.pk,
                "nombre": f"Amarra plástica {measure}",
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Amarras plásticas",
                "descripcion": (
                    f"Amarra plástica de {length} mm de largo y {width} mm "
                    "de ancho. Disponible en color blanco o negro."
                ),
                "imagen": IMAGE_ROOT + "amarra-plastica-blanca.png",
                "texto_alternativo": f"Amarras plásticas blancas de {measure}",
                "etiqueta_visual": "AMARRAS",
                "orden": order,
                "publicado": True,
            },
        )

        for spec_order, (name, value, unit) in enumerate(
            (("Largo", length, "mm"), ("Ancho", width, "mm")),
            start=1,
        ):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=name,
                defaults={"valor": value, "unidad": unit, "orden": spec_order},
            )

        for variant_order, color in enumerate(("Blanco", "Negro"), start=1):
            image = IMAGE_ROOT + (
                "amarra-plastica-blanca.png"
                if color == "Blanco"
                else "amarra-plastica-negra.png"
            )
            variant, _ = Variante.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=color,
                defaults={"imagen": image, "disponible": True, "orden": variant_order},
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variant.pk,
                nombre="Color",
                defaults={"valor": color, "unidad": "", "orden": 1},
            )

        for feature_order, text in enumerate(
            (f"Medida: {measure}.", "Disponible en blanco o negro."),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=product.pk,
                orden=feature_order,
                defaults={"texto": text},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0085_banderola_salida_lexo")]
    operations = [migrations.RunPython(agregar_amarras, migrations.RunPython.noop)]
