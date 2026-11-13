from django.db import migrations


IMAGE_ROOT = "productos/catalogo/mecanismos-electricos/stanford/"

PRODUCTS = (
    {
        "slug": "interruptor-simple-stanford-9-12",
        "name": "Interruptor simple Stanford 9/12",
        "mechanism": "Simple 9/12 · 10 A",
        "order": 530,
        "images": {
            "Blanco": "interruptor-simple-9-12-blanco.png",
            "Champagne": "interruptor-simple-9-12-champagne.png",
            "Café": "interruptor-simple-9-12-cafe.png",
            "Negro": "interruptor-simple-9-12-negro.png",
        },
    },
    {
        "slug": "interruptor-doble-stanford-9-15",
        "name": "Interruptor doble Stanford 9/15",
        "mechanism": "Doble 9/15 · 10 A",
        "order": 540,
        "images": {
            "Blanco": "interruptor-doble-9-15-blanco.png",
            "Champagne": "interruptor-doble-9-15-champagne.png",
            "Café": "interruptor-doble-9-15-cafe.png",
            "Negro": "interruptor-doble-9-15-negro.png",
        },
    },
    {
        "slug": "interruptor-simple-stanford-9-24",
        "name": "Interruptor simple Stanford 9/24",
        "mechanism": "Simple 9/24 · 10 A",
        "order": 550,
        "images": {
            "Blanco": "interruptor-simple-9-24-blanco.png",
            "Champagne": "interruptor-simple-9-24-champagne.png",
            "Café": "interruptor-simple-9-12-cafe.png",
            "Negro": "interruptor-simple-9-24-negro.png",
        },
    },
    {
        "slug": "interruptor-triple-stanford-9-32",
        "name": "Interruptor triple Stanford 9/32",
        "mechanism": "Triple 9/32 · 10 A",
        "order": 560,
        "images": {
            "Blanco": "interruptor-triple-9-32-blanco.png",
            "Champagne": "interruptor-triple-9-32-champagne.png",
            "Café": "interruptor-triple-9-32-cafe.png",
            "Negro": "interruptor-triple-9-32-negro.png",
        },
    },
    {
        "slug": "interruptor-stanford-9-12-con-toma-2pt",
        "name": "Interruptor Stanford 9/12 con toma 2P+T",
        "mechanism": "9/12 + toma 2P+T · 10 A",
        "order": 570,
        "images": {
            "Blanco": "interruptor-9-12-toma-2pt-blanco.png",
            "Champagne": "interruptor-9-12-toma-2pt-champagne.png",
            "Café": "interruptor-9-12-toma-2pt-cafe.png",
            "Negro": "interruptor-9-12-toma-2pt-negro.png",
        },
    },
)


def agregar_interruptores_stanford(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    categoria = Categoria.objects.using(alias).get(slug="modulos-electricos")
    marca = Marca.objects.using(alias).get(slug="stanford")
    for definition in PRODUCTS:
        first_image = IMAGE_ROOT + definition["images"]["Blanco"]
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definition["name"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Interruptores Stanford",
                "descripcion": (
                    f"{definition['name']}, instalado en placa. "
                    "Disponible en cuatro colores para solicitar cotización."
                ),
                "imagen": first_image,
                "texto_alternativo": definition["name"],
                "etiqueta_visual": "STANFORD",
                "orden": definition["order"],
                "publicado": True,
            },
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=product.pk,
            nombre="Mecanismo",
            defaults={
                "valor": definition["mechanism"],
                "unidad": "",
                "orden": 1,
            },
        )
        for order, color in enumerate(("Blanco", "Champagne", "Café", "Negro"), start=1):
            image = IMAGE_ROOT + definition["images"][color]
            variant, _ = Variante.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=color,
                defaults={
                    "codigo": None,
                    "modelo": "",
                    "imagen": image,
                    "disponible": True,
                    "orden": order,
                },
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variant.pk,
                nombre="Color",
                defaults={"valor": color, "unidad": "", "orden": 1},
            )
        for order, text in enumerate(
            (
                "Conjunto de interruptor montado en placa.",
                "Disponible en blanco, champagne, café y negro.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=product.pk,
                texto=text,
                defaults={"orden": order},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0081_equipos_emergencia_lexo")]
    operations = [
        migrations.RunPython(agregar_interruptores_stanford, migrations.RunPython.noop)
    ]
