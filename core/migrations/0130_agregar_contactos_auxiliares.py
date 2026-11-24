from django.db import migrations


ROOT = "productos/catalogo/control-senalizacion/contactos-auxiliares/"

PRODUCTOS = (
    {
        "slug": "contacto-auxiliar-lay5-be101",
        "nombre": "Contacto auxiliar LAY5-BE101 1NO",
        "marca_id": None,
        "modelo": "LAY5-BE101",
        "imagen": "contacto-auxiliar-lay5-be101.png",
        "alt": "Bloque de contacto auxiliar LAY5-BE101 con contacto normalmente abierto",
        "descripcion": (
            "Bloque de contacto auxiliar LAY5-BE101 con un contacto "
            "normalmente abierto (NO), bornes 3–4, tensión de aislamiento "
            "Ui de 400 V~ e Ith indicada de 10(6) A."
        ),
        "etiqueta": "CONTACTO AUXILIAR",
        "orden": 1,
        "caracteristicas": (
            "Un contacto normalmente abierto (1 NO).",
            "Bornes indicados: 3–4.",
            "Ui 400 V~ e Ith 10(6) A, según el marcado del dispositivo.",
        ),
        "especificaciones": (
            ("Modelo", "LAY5-BE101", ""),
            ("Configuración de contactos", "1 NO", ""),
            ("Bornes", "3–4", ""),
            ("Tensión de aislamiento Ui", "400", "V~"),
            ("Corriente indicada Ith", "10(6)", "A"),
        ),
    },
    {
        "slug": "contacto-auxiliar-cnc-f4-dn11",
        "nombre": "Contacto auxiliar CNC F4-DN11 1NO+1NC",
        "marca_id": "cnc",
        "modelo": "F4-DN11",
        "imagen": "contacto-auxiliar-cnc-f4-dn11.png",
        "alt": "Contacto auxiliar CNC F4-DN11 con un contacto NO y uno NC",
        "descripcion": (
            "Contacto auxiliar CNC F4-DN11 con un contacto normalmente "
            "abierto (NO) y uno normalmente cerrado (NC). El marcado indica "
            "Ui de 660 V e Ith de 10 A."
        ),
        "etiqueta": "CONTACTO AUXILIAR CNC",
        "orden": 2,
        "caracteristicas": (
            "Configuración de contactos: 1 NO + 1 NC.",
            "Bornes NO: 53–54; bornes NC: 61–62.",
            "Ui 660 V e Ith 10 A, según el marcado del dispositivo.",
        ),
        "especificaciones": (
            ("Modelo", "F4-DN11", ""),
            ("Configuración de contactos", "1 NO + 1 NC", ""),
            ("Bornes NO", "53–54", ""),
            ("Bornes NC", "61–62", ""),
            ("Tensión de aislamiento Ui", "660", "V"),
            ("Corriente térmica Ith", "10", "A"),
        ),
    },
)


def agregar_contactos_auxiliares(apps, schema_editor):
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
        slug="contactos-auxiliares",
        defaults={
            "nombre": "Contactos auxiliares",
            "padre_id": familia.pk,
            "orden": 2,
            "activa": True,
        },
    )

    cnc = Marca.objects.using(alias).get(slug="cnc")
    for definicion in PRODUCTOS:
        marca_id = (
            cnc.pk if definicion["marca_id"] == "cnc" else None
        )
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": definicion["nombre"],
                "marca": "",
                "marca_nueva_id": marca_id,
                "modelo": definicion["modelo"],
                "codigo": None,
                "subtitulo": "Contactos auxiliares",
                "descripcion": definicion["descripcion"],
                "imagen": ROOT + definicion["imagen"],
                "texto_alternativo": definicion["alt"],
                "etiqueta_visual": definicion["etiqueta"],
                "orden": definicion["orden"],
                "publicado": True,
            },
        )

        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, texto in enumerate(
            definicion["caracteristicas"], start=1
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
            definicion["especificaciones"], start=1
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
        ("core", "0129_agregar_automaticos_same"),
    ]

    operations = [
        migrations.RunPython(
            agregar_contactos_auxiliares,
            migrations.RunPython.noop,
        ),
    ]
