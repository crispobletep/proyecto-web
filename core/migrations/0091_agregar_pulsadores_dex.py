from django.db import migrations


ROOT = "productos/catalogo/control-senalizacion/pulsadores/"
PRODUCTS = (
    {
        "slug": "selector-2-posiciones-dex-electric",
        "name": "Selector de 2 posiciones DEX Electric",
        "image": "selector-2-posiciones.webp",
        "alt": "Selector negro de 2 posiciones DEX Electric",
        "description": "Selector eléctrico negro de 2 posiciones DEX Electric, con bloque de contacto ZB2-BE102.",
        "order": 850,
        "specs": (("Posiciones", "2", ""), ("Modelo de contacto", "ZB2-BE102", ""), ("Contacto", "NC", ""), ("Corriente térmica Ith", "10", "A"), ("Tensión de aislamiento Ui", "600", "V"), ("Categoría de empleo", "AC-15 · 240 V · 3 A", "")),
        "features": ("Selector negro de 2 posiciones.", "Bloque de contacto identificado como ZB2-BE102 (NC)."),
    },
    {
        "slug": "boton-emergencia-rojo-dex-electric",
        "name": "Botón de emergencia rojo DEX Electric",
        "image": "boton-emergencia-rojo.webp",
        "alt": "Botón de emergencia rojo tipo hongo DEX Electric",
        "description": "Botón de emergencia rojo tipo hongo DEX Electric para accionamiento manual.",
        "order": 860,
        "specs": (("Tipo de accionador", "Emergencia tipo hongo", ""), ("Color", "Rojo", "")),
        "features": ("Accionador tipo hongo de color rojo.", "Para funciones de parada de emergencia según el circuito de control instalado."),
    },
    {
        "slug": "pulsador-verde-dex-electric-zb2-be101",
        "name": "Pulsador verde DEX Electric ZB2-BE101",
        "image": "pulsador-verde.webp",
        "alt": "Pulsador verde DEX Electric con contacto normalmente abierto",
        "description": "Pulsador verde DEX Electric con bloque de contacto identificado como ZB2-BE101.",
        "order": 870,
        "specs": (("Modelo", "ZB2-BE101", ""), ("Contacto", "NO", ""), ("Corriente térmica Ith", "10", "A"), ("Tensión de aislamiento Ui", "600", "V"), ("Categoría de empleo", "AC-15 · 240 V · 3 A", "")),
        "features": ("Accionador verde.", "Contacto normalmente abierto (NO), según el marcado del bloque."),
    },
    {
        "slug": "pulsador-rojo-dex-electric-zb2-be102",
        "name": "Pulsador rojo DEX Electric ZB2-BE102",
        "image": "pulsador-rojo.webp",
        "alt": "Pulsador rojo DEX Electric con contacto normalmente cerrado",
        "description": "Pulsador rojo DEX Electric con bloque de contacto identificado como ZB2-BE102.",
        "order": 880,
        "specs": (("Modelo", "ZB2-BE102", ""), ("Contacto", "NC", ""), ("Corriente térmica Ith", "10", "A"), ("Tensión de aislamiento Ui", "600", "V"), ("Categoría de empleo", "AC-15 · 240 V · 3 A", "")),
        "features": ("Accionador rojo.", "Contacto normalmente cerrado (NC), según el marcado del bloque."),
    },
)


def agregar_pulsadores(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="control-senalizacion")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="pulsadores",
        defaults={"nombre": "Pulsadores", "padre_id": familia.pk, "orden": 10, "activa": True},
    )

    for product_data in PRODUCTS:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=product_data["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": product_data["name"],
                "marca": "DEX Electric",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Pulsadores y selectores DEX Electric",
                "descripcion": product_data["description"],
                "imagen": ROOT + product_data["image"],
                "texto_alternativo": product_data["alt"],
                "etiqueta_visual": "DEX ELECTRIC",
                "orden": product_data["order"],
                "publicado": True,
            },
        )
        for orden, (nombre, valor, unidad) in enumerate(product_data["specs"], start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )
        for orden, texto in enumerate(product_data["features"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0090_actualizar_imagen_prensaestopas")]

    operations = [migrations.RunPython(agregar_pulsadores, migrations.RunPython.noop)]
