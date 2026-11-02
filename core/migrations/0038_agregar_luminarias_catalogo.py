from django.db import migrations


PRODUCTOS = [
    ("luminaria-solar-logic-200w", "Luminaria pública solar LED 200 W Logic", "Logic", "Luminarias solares", "Luminaria solar peatonal de 200 W con panel solar y control remoto. Protección IP65 indicada en el empaque.", "productos/catalogo/iluminacion/nuevos/solar-logic-200w.png", ["200 W · 1900 lm"]),
    ("luminaria-solar-logic-150w", "Luminaria pública solar LED 150 W Logic", "Logic", "Luminarias solares", "Luminaria solar peatonal de 150 W con panel solar y control remoto. Protección IP65 indicada en el empaque.", "productos/catalogo/iluminacion/nuevos/solar-logic-150w.png", ["150 W"]),
    ("luminaria-solar-logic-100w", "Luminaria pública solar LED 100 W Logic", "Logic", "Luminarias solares", "Luminaria solar peatonal de 100 W con panel solar y control remoto. Protección IP65 indicada en el empaque.", "productos/catalogo/iluminacion/nuevos/solar-logic-100w.png", ["100 W"]),
    ("canoa-led-simple-120cm", "Canoa LED simple 120 cm", "", "Canoas LED", "Canoa lineal LED simple de 120 cm.", "productos/catalogo/iluminacion/nuevos/canoa-simple.png", ["Simple · 120 cm"]),
    ("canoa-led-simple-60cm", "Canoa LED simple 60 cm", "", "Canoas LED", "Canoa lineal LED simple de 60 cm. Imagen referencial del modelo simple.", "productos/catalogo/iluminacion/nuevos/canoa-simple.png", ["Simple · 60 cm"]),
    ("canoa-led-doble-120cm", "Canoa LED doble 120 cm", "", "Canoas LED", "Canoa lineal LED doble de 120 cm.", "productos/catalogo/iluminacion/nuevos/canoa-doble.png", ["Doble · 120 cm"]),
    ("canoa-led-doble-60cm", "Canoa LED doble 60 cm", "", "Canoas LED", "Canoa lineal LED doble de 60 cm. Imagen referencial del modelo doble.", "productos/catalogo/iluminacion/nuevos/canoa-doble.png", ["Doble · 60 cm"]),
    ("equipo-estanco-led-2x9w", "Equipo estanco LED 2 × 9 W", "", "Equipos estancos LED", "Equipo estanco para dos tubos LED de 9 W.", "productos/catalogo/iluminacion/nuevos/estanco-2x9w.png", ["2 × 9 W"]),
    ("equipo-estanco-led-1x18w", "Equipo estanco LED 1 × 18 W", "", "Equipos estancos LED", "Equipo estanco para un tubo LED de 18 W.", "productos/catalogo/iluminacion/nuevos/estanco-1x18w.png", ["1 × 18 W"]),
    ("tubo-led-18w-6500k-fsl", "Tubo LED 18 W 6500 K FSL", "FSL", "Tubos LED", "Tubo LED de luz fría 6500 K y 18 W, largo 120 cm.", "productos/catalogo/iluminacion/nuevos/tubo-fsl.png", ["18 W · 6500 K · 120 cm"]),
    ("tubo-led-18w-6500k-forceman", "Tubo LED 18 W 6500 K Forceman", "Forceman", "Tubos LED", "Tubo LED de luz fría 6500 K y 18 W, largo 120 cm.", "productos/catalogo/iluminacion/nuevos/tubo-forceman.png", ["18 W · 6500 K · 120 cm"]),
    ("tubo-led-9w-6500k-fsl", "Tubo LED 9 W 6500 K FSL", "FSL", "Tubos LED", "Tubo LED de luz fría 6500 K y 9 W, largo 60 cm. Imagen referencial del tubo LED.", "productos/catalogo/iluminacion/nuevos/tubo-fsl.png", ["9 W · 6500 K · 60 cm"]),
    ("tubo-led-9w-6500k-forceman", "Tubo LED 9 W 6500 K Forceman", "Forceman", "Tubos LED", "Tubo LED de luz fría 6500 K y 9 W, largo 60 cm. Imagen referencial del tubo LED.", "productos/catalogo/iluminacion/nuevos/tubo-forceman.png", ["9 W · 6500 K · 60 cm"]),
    ("tubo-led-18w-3000k-fsl", "Tubo LED 18 W 3000 K FSL", "FSL", "Tubos LED", "Tubo LED de luz cálida 3000 K y 18 W, largo 120 cm. Imagen referencial del tubo LED.", "productos/catalogo/iluminacion/nuevos/tubo-fsl.png", ["18 W · 3000 K · 120 cm"]),
    ("tubo-led-18w-3000k-forceman", "Tubo LED 18 W 3000 K Forceman", "Forceman", "Tubos LED", "Tubo LED de luz cálida 3000 K y 18 W, largo 120 cm. Imagen referencial del tubo LED.", "productos/catalogo/iluminacion/nuevos/tubo-forceman.png", ["18 W · 3000 K · 120 cm"]),
    ("tubo-led-9w-3000k-fsl", "Tubo LED 9 W 3000 K FSL", "FSL", "Tubos LED", "Tubo LED de luz cálida 3000 K y 9 W, largo 60 cm. Imagen referencial del tubo LED.", "productos/catalogo/iluminacion/nuevos/tubo-fsl.png", ["9 W · 3000 K · 60 cm"]),
]


def agregar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    familia, _ = Categoria.objects.using(alias).get_or_create(
        slug="iluminacion", defaults={"nombre": "Iluminación", "orden": 8}
    )
    categorias = {}
    for slug, nombre in (("luminarias-solares", "Luminarias solares"), ("canoas-led", "Canoas LED"), ("equipos-estancos-led", "Equipos estancos LED"), ("tubos-led", "Tubos LED")):
        categorias[ nombre ] = Categoria.objects.using(alias).filter(slug=slug).first()
        if categorias[nombre] is None:
            categorias[nombre] = Categoria.objects.using(alias).create(slug=slug, nombre=nombre, padre_id=familia.pk, orden=0)

    marcas = {}
    for nombre in ("Logic", "FSL", "Forceman"):
        marcas[nombre] = Marca.objects.using(alias).filter(nombre__iexact=nombre).first()
        if marcas[nombre] is None:
            slug = {"Logic": "logic", "FSL": "fsl", "Forceman": "forceman"}[nombre]
            marcas[nombre] = Marca.objects.using(alias).create(nombre=nombre, slug=slug)

    for slug, nombre, marca, categoria, descripcion, imagen, presentaciones in PRODUCTOS:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categorias[categoria].pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": marcas[marca].pk if marca else None,
                "subtitulo": categoria,
                "descripcion": descripcion,
                "imagen": imagen,
                "texto_alternativo": nombre,
                "etiqueta_visual": marca.upper() if marca else "ILUMINACIÓN LED",
                "publicado": True,
            },
        )
        for orden, presentacion in enumerate(presentaciones):
            Variante.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=presentacion,
                defaults={"disponible": True, "orden": orden},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0037_publicar_plafones_redondos")]
    operations = [migrations.RunPython(agregar_productos, migrations.RunPython.noop)]
