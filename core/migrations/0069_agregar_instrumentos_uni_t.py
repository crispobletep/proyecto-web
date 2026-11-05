from django.db import migrations


PRODUCTOS = (
    {
        "slug": "uni-t-tester-digital-ut33c-plus",
        "nombre": "Tester digital UT33C+",
        "modelo": "UT33C+",
        "imagen": "productos/catalogo/uni-t-instrumentos/tester-digital-ut33c-plus.png",
        "alt": "Tester digital UNI-T UT33C+",
        "descripcion": "Tester digital UNI-T, modelo UT33C+.",
        "tipo": "Tester digital",
    },
    {
        "slug": "uni-t-multimetro-profesional-nct-ut89x",
        "nombre": "Multímetro digital profesional NCT UT-89X",
        "modelo": "UT-89X",
        "imagen": "productos/catalogo/uni-t-instrumentos/multimetro-profesional-nct-ut89x.png",
        "alt": "Multímetro digital profesional UNI-T NCT UT-89X",
        "descripcion": "Multímetro digital profesional UNI-T NCT, modelo UT-89X.",
        "tipo": "Multímetro digital profesional NCT",
    },
    {
        "slug": "uni-t-escaner-de-pared-ut387a",
        "nombre": "Escáner de pared UT387A",
        "modelo": "UT387A",
        "imagen": "productos/catalogo/uni-t-instrumentos/escaner-pared-ut387a.png",
        "alt": "Escáner de pared UNI-T UT387A",
        "descripcion": "Escáner de pared UNI-T, modelo UT387A.",
        "tipo": "Escáner de pared",
    },
    {
        "slug": "uni-t-luxometro-ut381a",
        "nombre": "Luxómetro digital UT381A",
        "modelo": "UT381A",
        "imagen": "productos/catalogo/uni-t-instrumentos/luxometro-ut381a.png",
        "alt": "Luxómetro digital UNI-T UT381A",
        "descripcion": "Luxómetro digital UNI-T, modelo UT381A.",
        "tipo": "Luxómetro digital",
    },
    {
        "slug": "uni-t-mini-luxometro-ut383",
        "nombre": "Mini luxómetro UT383",
        "modelo": "UT383",
        "imagen": "productos/catalogo/uni-t-instrumentos/mini-luxometro-ut383.png",
        "alt": "Mini luxómetro UNI-T UT383",
        "descripcion": "Mini luxómetro UNI-T, modelo UT383.",
        "tipo": "Mini luxómetro",
    },
    {
        "slug": "uni-t-telemetro-laser-lm50a",
        "nombre": "Telémetro láser LM50A",
        "modelo": "LM50A",
        "imagen": "productos/catalogo/uni-t-instrumentos/telemetro-laser-lm50a.png",
        "alt": "Telémetro láser UNI-T LM50A",
        "descripcion": "Telémetro láser UNI-T, modelo LM50A.",
        "tipo": "Telémetro láser",
    },
    {
        "slug": "uni-t-telemetro-laser-lm70a",
        "nombre": "Telémetro láser LM70A",
        "modelo": "LM70A",
        "imagen": "productos/catalogo/uni-t-instrumentos/telemetro-laser-lm70a.png",
        "alt": "Telémetro láser UNI-T LM70A",
        "descripcion": "Telémetro láser UNI-T, modelo LM70A.",
        "tipo": "Telémetro láser",
    },
    {
        "slug": "uni-t-telemetro-laser-lm600",
        "nombre": "Telémetro láser LM600",
        "modelo": "LM600",
        "imagen": "productos/catalogo/uni-t-instrumentos/telemetro-laser-lm600.png",
        "alt": "Telémetro láser UNI-T LM600",
        "descripcion": "Telémetro UNI-T, modelo LM600.",
        "tipo": "Telémetro",
    },
)


def agregar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    categoria = Categoria.objects.using(alias).get(slug="instrumentos-medicion")
    marca = Marca.objects.using(alias).get(slug="uni-t")

    for posicion, datos in enumerate(PRODUCTOS):
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=datos["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": datos["nombre"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": datos["modelo"],
                "codigo": None,
                "subtitulo": "Instrumentos de medición",
                "descripcion": datos["descripcion"],
                "imagen": datos["imagen"],
                "texto_alternativo": datos["alt"],
                "etiqueta_visual": "UNI-T",
                "orden": 160 + posicion * 10,
                "publicado": True,
            },
        )

        for orden, texto in enumerate(
            (datos["tipo"], f"Modelo {datos['modelo']}"),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=orden,
                defaults={"texto": texto},
            )
        for orden, (nombre, valor) in enumerate(
            (("Tipo de instrumento", datos["tipo"]), ("Modelo", datos["modelo"])),
            start=1,
        ):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"valor": valor, "unidad": "", "orden": orden},
            )


def revertir_productos(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Producto.objects.using(schema_editor.connection.alias).filter(
        slug__in=[producto["slug"] for producto in PRODUCTOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0068_ordenar_enchufes_por_formato"),
    ]

    operations = [
        migrations.RunPython(agregar_productos, revertir_productos),
    ]
