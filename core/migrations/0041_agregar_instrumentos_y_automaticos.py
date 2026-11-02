from django.db import migrations
from django.utils.text import slugify


BASE = "productos/catalogo/protecciones/nuevos/"

AUTOMATICOS_2P = [
    ("2P · 10 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-10a-curva-c-6ka.png"),
    ("2P · 16 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-16a-curva-c-6ka.png"),
    ("2P · 20 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-20a-curva-c-6ka.png"),
    ("2P · 25 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-25a-curva-c-6ka.png"),
    ("2P · 32 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-32a-curva-c-6ka-legrand.png"),
    ("2P · 40 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-40a-curva-c-6ka.png"),
    ("2P · 50 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-50a-curva-c-6ka.png"),
    ("2P · 63 A · curva C · 6 kA", "interruptor-autom-tico-mcb-2p-63a-curva-c-6ka.png"),
    ("2P · 10 A · curva C · 6 kA · alternativa", "interruptor-autom-tico-mcb-2p-10a-curva-c-6ka-chint.png"),
    ("2P · 16 A · curva D · 10 kA", "interruptor-autom-tico-mcb-2p-16a-curva-d-10ka-chint.png"),
    ("2P · 20 A · curva C · 10 kA", "interruptor-autom-tico-mcb-2p-20a-curva-c-10ka-chint.png"),
    ("2P · 25 A · curva C · 10 kA", "interruptor-autom-tico-mcb-2p-25a-curva-c-10ka-chint.png"),
    ("2P · 32 A · curva C · 10 kA", "interruptor-autom-tico-mcb-2p-32a-curva-c-10ka-chint.png"),
    ("2P · 40 A · curva C · 6 kA · alternativa", "interruptor-autom-tico-mcb-2p-40a-curva-c-6ka-chint.png"),
    ("2P · 50 A · curva C · 10 kA", "interruptor-autom-tico-mcb-2p-50a-curva-c-10ka.png"),
    ("2P · 63 A · curva C · 10 kA", "interruptor-autom-tico-mcb-2p-63a-curva-c-10ka-chint.png"),
]

AUTOMATICOS_4P = [
    ("4P · 10 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-10a-curva-c-10ka.png"),
    ("4P · 16 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-16a-curva-c-10ka.png"),
    ("4P · 20 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-20a-curva-c-10ka.png"),
    ("4P · 25 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-25a-curva-c-10ka.png"),
    ("4P · 32 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-32a-curva-c-10ka.png"),
    ("4P · 40 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-40a-curva-c-10ka.png"),
    ("4P · 50 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-50a-curva-c-10ka.png"),
    ("4P · 63 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-63a-curva-c-10ka.png"),
    ("4P · 80 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-63a-curva-c-10ka.png"),
    ("4P · 100 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-63a-curva-c-10ka.png"),
    ("4P · 125 A · curva C · 10 kA", "interruptor-autom-tico-mcb-4p-63a-curva-c-10ka.png"),
]


def agregar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    # La marca CHINT no se publica en el registro existente de 1P+N.
    Producto.objects.using(alias).filter(slug="interruptor-automatico-modular-1pn-16a").update(marca="", marca_nueva_id=None)

    proteccion = Categoria.objects.using(alias).get(slug="interruptores-automaticos")
    lexo = Marca.objects.using(alias).filter(nombre__iexact="LEXO").first()
    if lexo is None:
        lexo = Marca.objects.using(alias).create(nombre="LEXO", slug="lexo")

    for slug, nombre, variantes in (
        ("interruptores-automaticos-2p-curva-c", "Interruptores automáticos 2P", AUTOMATICOS_2P),
        ("interruptores-automaticos-4p-curva-c", "Interruptores automáticos 4P", AUTOMATICOS_4P),
    ):
        principal = next((f"{BASE}{archivo}" for etiqueta, archivo in variantes if "alternativa" not in etiqueta and ("63 A" in etiqueta or "10 A" in etiqueta)), f"{BASE}{variantes[0][1]}")
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": proteccion.pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": lexo.pk,
                "subtitulo": "Interruptores automáticos",
                "descripcion": "Interruptores automáticos modulares con curva C. Selecciona polos, corriente nominal y capacidad de ruptura disponibles.",
                "imagen": principal,
                "texto_alternativo": nombre,
                "etiqueta_visual": "LEXO",
                "publicado": True,
            },
        )
        for orden, (etiqueta, archivo) in enumerate(variantes):
            Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=etiqueta,
                defaults={"imagen": f"{BASE}{archivo}", "disponible": True, "orden": orden},
            )

    control = Categoria.objects.using(alias).get(slug="control-senalizacion")
    categoria, _ = Categoria.objects.using(alias).get_or_create(
        slug="instrumentos-medicion",
        defaults={"nombre": "Instrumentos de medición", "padre_id": control.pk, "orden": 0},
    )
    uni_t = Marca.objects.using(alias).filter(nombre__iexact="UNI-T").first()
    if uni_t is None:
        uni_t = Marca.objects.using(alias).create(nombre="UNI-T", slug="uni-t")

    instrumentos = (
        ("amperimetro-tenaza-ut203-plus", "Amperímetro de tenaza UT203+", "Amperímetro digital de tenaza UNI-T, modelo UT203+.", "amper-metro-tenaza-ut203-.png"),
        ("amperimetro-tenaza-ut202-plus", "Amperímetro de tenaza UT202+", "Amperímetro digital de tenaza UNI-T, modelo UT202+.", "amperimetro-tenaza-ut-202-uni-t.png"),
        ("detector-de-voltaje-ut12d", "Detector de voltaje UT12D", "Detector de voltaje UNI-T, modelo UT12D.", "detector-de-voltaje-ut-12-d.png"),
    )
    for slug, nombre, descripcion, archivo in instrumentos:
        stem = archivo.rsplit(".", 1)[0]
        imagen = f"productos/catalogo/protecciones/nuevos/{stem}.png"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": uni_t.pk,
                "subtitulo": "Instrumentos de medición",
                "descripcion": descripcion,
                "imagen": imagen,
                "texto_alternativo": nombre,
                "etiqueta_visual": "UNI-T",
                "publicado": True,
            },
        )
        Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=nombre.split(" de ")[-1],
            defaults={"disponible": True, "orden": 0},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0040_quitar_marca_del_nombre_productos")]
    operations = [migrations.RunPython(agregar_catalogo, migrations.RunPython.noop)]
