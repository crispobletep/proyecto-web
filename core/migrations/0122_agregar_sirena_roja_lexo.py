from django.db import migrations


IMAGEN = (
    "productos/catalogo/control-senalizacion/"
    "sirena-lexo-roja-220v.png"
)


def agregar_sirena_roja_lexo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    familia = Categoria.objects.using(alias).get(
        slug="control-senalizacion"
    )
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="sirenas-y-alarmas",
        defaults={
            "nombre": "Sirenas y alarmas",
            "padre_id": familia.pk,
            "orden": 12,
            "activa": True,
        },
    )
    marca = Marca.objects.using(alias).get(slug="lexo")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="sirena-roja-lexo-220v",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Sirena roja Lexo 220 V",
            "marca": "",
            "marca_nueva_id": marca.pk,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Sirenas y alarmas",
            "descripcion": (
                "Sirena roja Lexo para señalización acústica. El envase "
                "indica alimentación de 220 V y nivel sonoro de 100 dB."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": (
                "Sirena eléctrica roja Lexo con rejilla frontal y base de montaje"
            ),
            "etiqueta_visual": "SIRENAS Y ALARMAS",
            "orden": 1,
            "publicado": True,
        },
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).delete()
    for orden, texto in enumerate(
        (
            "Sirena eléctrica de color rojo.",
            "Tensión de alimentación: 220 V.",
            "Nivel sonoro indicado en el envase: 100 dB.",
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
            ("Tensión", "220", "V"),
            ("Nivel sonoro", "100", "dB"),
            ("Color", "Rojo", ""),
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
        ("core", "0121_agregar_cinta_pasacable_kalop"),
    ]

    operations = [
        migrations.RunPython(
            agregar_sirena_roja_lexo,
            migrations.RunPython.noop,
        ),
    ]
