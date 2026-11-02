from django.db import migrations
from django.utils.text import slugify


def agregar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")

    familia, _ = Categoria.objects.using(alias).get_or_create(
        slug="tableros-electricos",
        defaults={"nombre": "Tableros eléctricos", "orden": 5},
    )
    tableros, _ = Categoria.objects.using(alias).get_or_create(
        slug="tableros-plasticos",
        defaults={"nombre": "Tableros plásticos", "padre_id": familia.pk},
    )
    conductores = Categoria.objects.using(alias).filter(slug="conductores-conexiones").first()
    if conductores is None:
        conductores, _ = Categoria.objects.using(alias).get_or_create(
            slug="conductores-electricos",
            defaults={"nombre": "Conductores eléctricos", "orden": 2},
        )
    cables, _ = Categoria.objects.using(alias).get_or_create(
        slug="cordones-electricos",
        defaults={"nombre": "Cordones eléctricos", "padre_id": conductores.pk},
    )

    board_items = [
        ("tablero-plastico-36-vias", "Tablero plástico de distribución 36 vías", "", "WhatsApp Image 2026-10-30 at 09.28.52.jpeg"),
        ("tablero-plastico-forceman", "Tablero plástico Forceman", "Forceman", "WhatsApp Image 2026-10-30 at 09.28.38.jpeg"),
        ("tablero-sobrepuesto-lexo-18-polos", "Tablero sobrepuesto 18 polos", "LEXO", "WhatsApp Image 2026-10-30 at 09.28.18.jpeg"),
        ("tablero-embutido-dex-18-polos", "Tablero embutido 18 polos", "", "WhatsApp Image 2026-10-30 at 09.28.12.jpeg"),
        ("tablero-plastico-12-vias", "Tablero plástico de distribución 12 vías", "", "WhatsApp Image 2026-10-30 at 09.27.56.jpeg"),
        ("tablero-sobrepuesto-lexo-12-polos", "Tablero sobrepuesto 12 polos", "LEXO", "WhatsApp Image 2026-10-30 at 09.27.46.jpeg"),
        ("tablero-plastico-8-vias", "Tablero plástico de distribución 8 vías", "", "WhatsApp Image 2026-10-30 at 09.27.04.jpeg"),
        ("tablero-sobrepuesto-dex-6-polos", "Tablero sobrepuesto 6 polos", "", "WhatsApp Image 2026-10-30 at 09.26.52.jpeg"),
        ("tablero-plastico-forceman-4-modulos", "Tablero plástico Forceman 4 módulos", "Forceman", "tableros plásticos de 4 emb y s-p.jpeg"),
    ]
    for slug, nombre, marca_nombre, imagen in board_items:
        marca = Marca.objects.using(alias).filter(nombre__iexact=marca_nombre).first() if marca_nombre else None
        Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": tableros.pk,
                "nombre": nombre,
                "marca": "" if marca else marca_nombre,
                "marca_nueva_id": marca.pk if marca else None,
                "subtitulo": "Tableros eléctricos",
                "descripcion": f"{nombre}. Imagen de referencia tomada de su embalaje.",
                "imagen": f"productos/{imagen}",
                "texto_alternativo": nombre,
                "etiqueta_visual": marca_nombre,
                "publicado": True,
            },
        )

    cable_names = [
        "Cordón eléctrico 2x0,75mm2 negro", "Cordón eléctrico 2x1mm2 negro",
        "Cordón eléctrico 2x1,5mm2 negro", "Cordón eléctrico 3x0,75mm2 negro",
        "Cordón eléctrico 3x1mm2 negro", "Cordón eléctrico 3x1,5mm2 negro",
        "Cordón eléctrico 3x2,5mm2 negro", "Cordón eléctrico 4x1,5mm2 negro",
        "Cordón eléctrico 4x2,5mm2 negro", "Cordón eléctrico 5x1,5mm2 negro",
        "Cordón eléctrico 5x2,5mm2 negro",
    ]
    for nombre in cable_names:
        slug = slugify(nombre).replace("75mm2", "075mm2")
        Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": cables.pk,
                "nombre": nombre,
                "subtitulo": "Cordones eléctricos",
                "descripcion": f"{nombre}.",
                "imagen": "productos/WhatsApp Image 2026-11-01 at 11.25.33.jpeg",
                "texto_alternativo": "Cordón eléctrico negro enrollado sobre fondo blanco",
                "publicado": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0042_separar_automaticos_legrand_2p")]
    operations = [migrations.RunPython(agregar_catalogo, migrations.RunPython.noop)]
