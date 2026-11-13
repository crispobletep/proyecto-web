from django.db import migrations


PRODUCTS = (
    {
        "slug": "base-sobrepuesta-panel-led-1203x303-v-plb-5102",
        "name": "Base para sobreponer panel LED 1203 × 303 mm",
        "brand": "yell-max",
        "model": "V-PLB-5102",
        "image": "base-panel-led-1203x303-v-plb-5102.png",
        "alt": "Base blanca para sobreponer panel LED rectangular, modelo V-PLB-5102",
        "order": 810,
        "description": (
            "Base blanca para instalación sobrepuesta de panel LED, "
            "medida 1203 × 303 mm. Modelo V-PLB-5102."
        ),
        "specs": (
            ("Largo", "1203", "mm"),
            ("Ancho", "303", "mm"),
            ("Instalación", "Sobrepuesta", ""),
            ("Modelo", "V-PLB-5102", ""),
        ),
    },
    {
        "slug": "base-panel-led-603x603",
        "name": "Base para panel LED 603 × 603 mm",
        "brand": None,
        "model": "",
        "image": "base-panel-led-603x603.png",
        "alt": "Base blanca cuadrada para panel LED de 603 × 603 mm",
        "order": 820,
        "description": (
            "Base blanca cuadrada para montaje de panel LED de "
            "603 × 603 mm."
        ),
        "specs": (
            ("Largo", "603", "mm"),
            ("Ancho", "603", "mm"),
        ),
    },
)


def agregar_bases_panel(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="bases-panel-led",
        defaults={
            "nombre": "Bases para panel LED",
            "padre_id": iluminacion.pk,
            "orden": 10,
            "activa": True,
        },
    )

    for definition in PRODUCTS:
        brand = (
            Marca.objects.using(alias).get(slug=definition["brand"])
            if definition["brand"]
            else None
        )
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definition["name"],
                "marca": "",
                "marca_nueva_id": brand.pk if brand else None,
                "modelo": definition["model"],
                "codigo": None,
                "subtitulo": "Accesorios para panel LED",
                "descripcion": definition["description"],
                "imagen": "productos/catalogo/iluminacion/bases-panel-led/"
                + definition["image"],
                "texto_alternativo": definition["alt"],
                "etiqueta_visual": brand.nombre.upper() if brand else "PANEL LED",
                "orden": definition["order"],
                "publicado": True,
            },
        )

        for order, (name, value, unit) in enumerate(definition["specs"], start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=name,
                defaults={"valor": value, "unidad": unit, "orden": order},
            )

        for order, text in enumerate(
            (
                "Base para montaje de panel LED.",
                "Acabado blanco.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=product.pk,
                orden=order,
                defaults={"texto": text},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0086_agregar_amarras_plasticas")]
    operations = [migrations.RunPython(agregar_bases_panel, migrations.RunPython.noop)]
