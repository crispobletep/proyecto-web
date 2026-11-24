from django.db import migrations


ROOT = "productos/catalogo/mecanismos-electricos/luzica/"

PRODUCTOS = (
    {
        "slug": "interruptor-triple-luzica-9-32-10a",
        "nombre": "Interruptor triple Luzica 9/32 · 10 A",
        "imagen": "interruptor-triple-9-32-10a-luzica.png",
        "tipo": "Interruptor triple",
        "mecanismo": "9/32",
        "corriente": "10",
        "orden": 580,
    },
    {
        "slug": "interruptor-doble-luzica-9-15-10a",
        "nombre": "Interruptor doble Luzica 9/15 · 10 A",
        "imagen": "interruptor-doble-9-15-10a-luzica.png",
        "tipo": "Interruptor doble",
        "mecanismo": "9/15",
        "corriente": "10",
        "orden": 590,
    },
    {
        "slug": "interruptor-simple-luzica-9-24-10a",
        "nombre": "Interruptor simple Luzica 9/24 · 10 A",
        "imagen": "interruptor-simple-9-24-10a-luzica.png",
        "tipo": "Interruptor simple",
        "mecanismo": "9/24",
        "corriente": "10",
        "orden": 600,
    },
    {
        "slug": "interruptor-simple-luzica-9-12-10a",
        "nombre": "Interruptor simple Luzica 9/12 · 10 A",
        "imagen": "interruptor-simple-9-12-10a-luzica.png",
        "tipo": "Interruptor simple",
        "mecanismo": "9/12",
        "corriente": "10",
        "orden": 610,
    },
    {
        "slug": "tomacorriente-doble-luzica-10-16a",
        "nombre": "Tomacorriente doble Luzica 10/16 A",
        "imagen": "tomacorriente-doble-10-16a-luzica.png",
        "tipo": "Tomacorriente doble",
        "mecanismo": "Doble",
        "corriente": "10/16",
        "orden": 620,
    },
    {
        "slug": "tomacorriente-simple-luzica-10-16a",
        "nombre": "Tomacorriente simple Luzica 10/16 A",
        "imagen": "tomacorriente-simple-10-16a-luzica.png",
        "tipo": "Tomacorriente simple",
        "mecanismo": "Simple",
        "corriente": "10/16",
        "orden": 630,
    },
    {
        "slug": "tomacorriente-triple-luzica-10a",
        "nombre": "Tomacorriente triple Luzica 10 A",
        "imagen": "tomacorriente-triple-10a-luzica.png",
        "tipo": "Tomacorriente triple",
        "mecanismo": "Triple",
        "corriente": "10",
        "orden": 640,
    },
    {
        "slug": "tomacorriente-doble-luzica-10a",
        "nombre": "Tomacorriente doble Luzica 10 A",
        "imagen": "tomacorriente-doble-10a-luzica.png",
        "tipo": "Tomacorriente doble",
        "mecanismo": "Doble",
        "corriente": "10",
        "orden": 650,
    },
    {
        "slug": "tomacorriente-simple-luzica-10a",
        "nombre": "Tomacorriente simple Luzica 10 A",
        "imagen": "tomacorriente-simple-10a-luzica.png",
        "tipo": "Tomacorriente simple",
        "mecanismo": "Simple",
        "corriente": "10",
        "orden": 660,
    },
)


def agregar_mecanismos_luzica(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    categoria = Categoria.objects.using(alias).get(slug="modulos-electricos")
    marca, _ = Marca.objects.using(alias).get_or_create(
        slug="luzica",
        defaults={"nombre": "Luzica", "activa": True},
    )

    for definicion in PRODUCTOS:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definicion["nombre"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": definicion["mecanismo"],
                "codigo": None,
                "subtitulo": "Módulos eléctricos",
                "descripcion": (
                    f"{definicion['nombre']}, instalado en placa. "
                    "Producto de la línea Luzica."
                ),
                "imagen": ROOT + definicion["imagen"],
                "texto_alternativo": definicion["nombre"],
                "etiqueta_visual": "LUZICA",
                "orden": definicion["orden"],
                "publicado": True,
            },
        )

        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, texto in enumerate(
            (
                f"Formato: {definicion['tipo']}.",
                f"Corriente nominal indicada: {definicion['corriente']} A.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).create(
                producto_id=producto.pk,
                texto=texto,
                orden=orden,
            )

        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, (nombre, valor, unidad) in enumerate(
            (
                ("Tipo", definicion["tipo"], ""),
                ("Mecanismo", definicion["mecanismo"], ""),
                ("Corriente nominal", definicion["corriente"], "A"),
            ),
            start=1,
        ):
            Especificacion.objects.using(alias).create(
                producto_id=producto.pk,
                nombre=nombre,
                valor=valor,
                unidad=unidad,
                orden=orden,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0125_agregar_prensa_terminal_hidraulica"),
    ]

    operations = [
        migrations.RunPython(
            agregar_mecanismos_luzica,
            migrations.RunPython.noop,
        ),
    ]
