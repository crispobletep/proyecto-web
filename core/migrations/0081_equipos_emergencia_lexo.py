from django.db import migrations


PRODUCTS = (
    {
        "slug": "lampara-emergencia-lexo-2x12w-200lm",
        "name": "Lámpara de emergencia LED 2 × 1,2 W",
        "description": (
            "Lámpara de emergencia LED LEXO con dos focos orientables, "
            "flujo luminoso de 200 lm y luz fría de 6500 K."
        ),
        "image": (
            "productos/catalogo/iluminacion/nuevos/"
            "lampara-emergencia-lexo-2x12w-200lm-6500k.png"
        ),
        "alt": "Lámpara de emergencia LEXO con dos focos orientables",
        "order": 590,
        "features": (
            "Dos focos orientables de 1,2 W",
            "Flujo luminoso: 200 lm",
            "Temperatura de color: 6500 K",
        ),
        "specs": (("Potencia", "2 × 1,2", "W"), ("Flujo luminoso", "200", "lm"), ("Temperatura de color", "6500", "K")),
    },
    {
        "slug": "lampara-emergencia-led-lexo-recargable-6500k",
        "name": "Lámpara de emergencia LED recargable 6500 K",
        "description": (
            "Lámpara de emergencia LED LEXO recargable, con dos focos "
            "orientables y luz fría de 6500 K."
        ),
        "image": (
            "productos/catalogo/iluminacion/nuevos/"
            "lampara-emergencia-led-lexo-recargable-6500k.png"
        ),
        "alt": "Lámpara de emergencia LED LEXO recargable con dos focos",
        "order": 600,
        "features": (
            "Batería recargable",
            "Dos focos orientables",
            "Temperatura de color: 6500 K",
        ),
        "specs": (("Alimentación", "Recargable", ""), ("Temperatura de color", "6500", "K")),
    },
)


def agregar_equipos_emergencia(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    iluminacion = Categoria.objects.using(alias).get(slug="iluminacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="equipos-emergencia",
        defaults={
            "nombre": "Equipos de emergencia",
            "padre_id": iluminacion.pk,
            "orden": 8,
            "activa": True,
        },
    )
    lexo = Marca.objects.using(alias).get(slug="lexo")

    for definition in PRODUCTS:
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definition["name"],
                "marca": "",
                "marca_nueva_id": lexo.pk,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Equipos de emergencia",
                "descripcion": definition["description"],
                "imagen": definition["image"],
                "texto_alternativo": definition["alt"],
                "etiqueta_visual": "LEXO",
                "orden": definition["order"],
                "publicado": True,
            },
        )
        for order, feature in enumerate(definition["features"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=product.pk,
                orden=order,
                defaults={"texto": feature},
            )
        for order, (name, value, unit) in enumerate(definition["specs"], start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=name,
                defaults={"valor": value, "unidad": unit, "orden": order},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0080_imagenes_referenciales_catalogo")]
    operations = [migrations.RunPython(agregar_equipos_emergencia, migrations.RunPython.noop)]
