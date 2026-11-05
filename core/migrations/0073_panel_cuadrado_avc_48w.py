from django.db import migrations


SLUG = "panel-led-embutido-cuadrado-avc-48w-603x603mm"
IMAGEN = (
    "productos/catalogo/iluminacion/"
    "avc-panel-led-embutido-cuadrado-48w-603x603mm.png"
)
TEMPERATURAS = (3000, 4000, 6500)


def agregar_panel(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    categoria = Categoria.objects.using(alias).get(slug="plafones-led")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug=SLUG,
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Panel LED embutido cuadrado AVC 48 W · 603 × 603 mm",
            "marca": "AVC",
            "subtitulo": "Panel embutido cuadrado",
            "descripcion": (
                "Panel LED cuadrado de 48 W para instalación embutida. "
                "Formato de 603 × 603 mm, disponible en 3000 K, 4000 K y 6500 K."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": "Panel LED AVC cuadrado embutido de 48 W",
            "etiqueta_visual": "PANELES LED",
            "orden": 550,
            "publicado": True,
        },
    )

    for orden, (nombre, valor, unidad) in enumerate(
        (
            ("Potencia", "48", "W"),
            ("Dimensiones", "603 × 603", "mm"),
            ("Instalación", "Embutido", ""),
            ("Protección", "IP20", ""),
        ),
        start=1,
    ):
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=nombre,
            defaults={"valor": valor, "unidad": unidad, "orden": orden},
        )

    for orden, texto in enumerate(
        (
            "Panel LED cuadrado para instalación embutida.",
            "Formato de 603 × 603 mm.",
            "Disponible en tres temperaturas de color.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            orden=orden,
            defaults={"texto": texto},
        )

    for orden, temperatura in enumerate(TEMPERATURAS, start=1):
        nombre = f"{temperatura} K"
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=nombre,
            defaults={
                "codigo": None,
                "modelo": "",
                "imagen": IMAGEN,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Temperatura de color",
            defaults={"valor": str(temperatura), "unidad": "K", "orden": 1},
        )
        if temperatura == 6500:
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Flujo luminoso",
                defaults={"valor": "5200", "unidad": "lm", "orden": 2},
            )


def ocultar_panel(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Producto.objects.using(alias).filter(slug=SLUG).update(publicado=False)
    Variante.objects.using(alias).filter(producto__slug=SLUG).update(
        disponible=False
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0072_ajustar_tableros_exterior"),
    ]

    operations = [
        migrations.RunPython(agregar_panel, ocultar_panel),
    ]
