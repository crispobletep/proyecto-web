from django.db import migrations


IMAGEN = "productos/catalogo/kalop-casquetes/hembra-sobrepuesta-2pt-16a-220v-ip44-ekoline.png"
VARIANTES = (
    ("HS-2PT-16A-220-IP44", "2P+T · 16 A · 220 V · IP44", "2P+T", "16", "220"),
    ("HS-3PT-16A-380-IP44", "3P+T · 16 A · 380 V · IP44", "3P+T", "16", "380"),
    ("HS-3PNT-16A-380-IP44", "3P+N+T · 16 A · 380 V · IP44", "3P+N+T", "16", "380"),
    ("HS-2PT-32A-220-IP44", "2P+T · 32 A · 220 V · IP44", "2P+T", "32", "220"),
    ("HS-3PT-32A-380-IP44", "3P+T · 32 A · 380 V · IP44", "3P+T", "32", "380"),
    ("HS-3PNT-32A-380-IP44", "3P+N+T · 32 A · 380 V · IP44", "3P+N+T", "32", "380"),
)


def agregar_hembra_sobrepuesta(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    ImagenProducto = apps.get_model("core", "ImagenProducto")

    macho = Producto.objects.using(alias).get(slug="enchufe-industrial-macho-sobrepuesto")
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="enchufe-industrial-hembra-sobrepuesta",
        defaults={
            "categoria_id": macho.categoria_id,
            "nombre": "Hembra sobrepuesta 2P+T 16 A 220 V IP44",
            "marca": macho.marca,
            "marca_nueva_id": macho.marca_nueva_id,
            "modelo": "",
            "codigo": None,
            "subtitulo": macho.subtitulo,
            "descripcion": (
                "Enchufe industrial tipo hembra para montaje sobrepuesto. "
                "Selecciona la configuración de polos, corriente y tensión disponible."
            ),
            "imagen": IMAGEN,
            "texto_alternativo": "Conectores hembra industriales de montaje sobrepuesto",
            "etiqueta_visual": macho.etiqueta_visual,
            "orden": macho.orden + 10,
            "publicado": True,
        },
    )

    for orden, texto in enumerate(
        (
            "Conector industrial de montaje sobrepuesto tipo hembra.",
            "Configuraciones disponibles: 2P+T, 3P+T y 3P+N+T.",
            "Opciones de 16 A y 32 A con protección IP44.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            orden=orden,
            defaults={"texto": texto},
        )

    variantes = []
    for orden, (codigo, nombre, polos, amperaje, voltaje) in enumerate(VARIANTES, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            codigo=codigo,
            defaults={
                "producto_id": producto.pk,
                "nombre": nombre,
                "modelo": "",
                "imagen": IMAGEN,
                "disponible": True,
                "orden": orden * 10,
            },
        )
        variantes.append(variante)
        for orden_spec, nombre_spec, valor, unidad in (
            (1, "Polos", polos, ""),
            (2, "Corriente nominal", amperaje, "A"),
            (3, "Tensión nominal", voltaje, "V"),
            (4, "Grado de protección", "IP44", ""),
        ):
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre=nombre_spec,
                defaults={"valor": valor, "unidad": unidad, "orden": orden_spec},
            )

    imagen, _ = ImagenProducto.objects.using(alias).update_or_create(
        clave="enchufe-industrial-hembra-sobrepuesta-imagen",
        defaults={
            "producto_id": producto.pk,
            "imagen": IMAGEN,
            "texto_alternativo": producto.texto_alternativo,
            "orden": 1,
        },
    )
    imagen.variantes.set(variantes)


def revertir_hembra_sobrepuesta(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Cotizacion = apps.get_model("core", "Cotizacion")

    producto = Producto.objects.using(alias).filter(slug="enchufe-industrial-hembra-sobrepuesta").first()
    if not producto:
        return
    archivo = Producto.objects.using(alias).get(slug="catalogo-kalop-casquetes")
    for codigo, *_ in VARIANTES:
        variante = Variante.objects.using(alias).filter(codigo=codigo).first()
        if not variante:
            continue
        citas = Cotizacion.objects.using(alias).filter(variante_id=variante.pk)
        if citas.exists():
            citas.update(producto_id=archivo.pk)
            variante.producto_id = archivo.pk
            variante.disponible = False
            variante.save(using=alias, update_fields=["producto", "disponible"])
        else:
            EspecificacionVariante.objects.using(alias).filter(variante_id=variante.pk).delete()
            variante.delete(using=alias)
    producto.delete(using=alias)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0063_agregar_machos_sobrepuestos_y_variantes_32a"),
    ]

    operations = [
        migrations.RunPython(agregar_hembra_sobrepuesta, revertir_hembra_sobrepuesta),
    ]
