from django.db import migrations


IMAGEN_SOBREPUESTO = "productos/catalogo/kalop-casquetes/macho-sobrepuesto-2pt-16a-220v-ip44-ekoline.png"
IMAGEN_VOLANTE = "productos/catalogo/kalop-casquetes/macho-volante-2pt-16a-220v-ip44-ekoline.png"
VARIANTES_VOLANTE = (
    ("MV-3PT-32A-380-IP44", "3P+T · 32 A · 380 V · IP44", "3P+T", "32", "380"),
    ("MV-3PNT-32A-380-IP44", "3P+N+T · 32 A · 380 V · IP44", "3P+N+T", "32", "380"),
)
VARIANTES_SOBREPUESTO = (
    ("MS-2PT-16A-220-IP44", "2P+T · 16 A · 220 V · IP44", "2P+T", "16", "220"),
    ("MS-3PT-16A-380-IP44", "3P+T · 16 A · 380 V · IP44", "3P+T", "16", "380"),
    ("MS-2PT-32A-220-IP44", "2P+T · 32 A · 220 V · IP44", "2P+T", "32", "220"),
    ("MS-3PT-32A-380-IP44", "3P+T · 32 A · 380 V · IP44", "3P+T", "32", "380"),
)


def crear_sobrepuestos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    macho = Producto.objects.using(alias).get(slug="enchufe-industrial-macho-volante")
    categoria = macho.categoria

    volante_variantes = []
    for posicion, (codigo, nombre, polos, amperaje, voltaje) in enumerate(VARIANTES_VOLANTE, start=5):
        variante, _ = Variante.objects.using(alias).update_or_create(
            codigo=codigo,
            defaults={
                "producto_id": macho.pk,
                "nombre": nombre,
                "modelo": "",
                "imagen": IMAGEN_VOLANTE,
                "disponible": True,
                "orden": posicion * 10,
            },
        )
        volante_variantes.append(variante)
        for orden, nombre_spec, valor, unidad in (
            (1, "Polos", polos, ""),
            (2, "Corriente nominal", amperaje, "A"),
            (3, "Tensión nominal", voltaje, "V"),
            (4, "Grado de protección", "IP44", ""),
        ):
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre=nombre_spec,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

    Imagen.objects.using(alias).filter(producto_id=macho.pk).update(imagen=IMAGEN_VOLANTE)
    imagen_volante = Imagen.objects.using(alias).get(producto_id=macho.pk)
    imagen_volante.variantes.set(
        list(Variante.objects.using(alias).filter(producto_id=macho.pk, disponible=True))
    )

    sobrepuesto, _ = Producto.objects.using(alias).update_or_create(
        slug="enchufe-industrial-macho-sobrepuesto",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Macho sobrepuesto 2P+T 16 A 220 V IP44",
            "marca": macho.marca,
            "marca_nueva_id": macho.marca_nueva_id,
            "modelo": "",
            "codigo": None,
            "subtitulo": macho.subtitulo,
            "descripcion": (
                "Enchufe industrial tipo macho para montaje sobrepuesto. "
                "Selecciona la configuración de polos, corriente y tensión disponible."
            ),
            "imagen": IMAGEN_SOBREPUESTO,
            "texto_alternativo": "Conectores macho industriales de montaje sobrepuesto, imagen referencial",
            "etiqueta_visual": macho.etiqueta_visual,
            "orden": macho.orden + 10,
            "publicado": True,
        },
    )

    for orden, texto in enumerate(
        (
            "Conector industrial de montaje sobrepuesto tipo macho.",
            "Configuraciones disponibles: 2P+T y 3P+T.",
            "Opciones de 16 A y 32 A, todas con protección IP44.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=sobrepuesto.pk,
            orden=orden,
            defaults={"texto": texto},
        )

    variantes_sobrepuestas = []
    for posicion, (codigo, nombre, polos, amperaje, voltaje) in enumerate(VARIANTES_SOBREPUESTO, start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            codigo=codigo,
            defaults={
                "producto_id": sobrepuesto.pk,
                "nombre": nombre,
                "modelo": "",
                "imagen": IMAGEN_SOBREPUESTO,
                "disponible": True,
                "orden": posicion * 10,
            },
        )
        variantes_sobrepuestas.append(variante)
        for orden, nombre_spec, valor, unidad in (
            (1, "Polos", polos, ""),
            (2, "Corriente nominal", amperaje, "A"),
            (3, "Tensión nominal", voltaje, "V"),
            (4, "Grado de protección", "IP44", ""),
        ):
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre=nombre_spec,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

    imagen, _ = Imagen.objects.using(alias).update_or_create(
        clave="enchufe-industrial-macho-sobrepuesto-imagen-referencial",
        defaults={
            "producto_id": sobrepuesto.pk,
            "imagen": IMAGEN_SOBREPUESTO,
            "texto_alternativo": sobrepuesto.texto_alternativo,
            "orden": 1,
        },
    )
    imagen.variantes.set(variantes_sobrepuestas)


def revertir_sobrepuestos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Imagen = apps.get_model("core", "ImagenProducto")

    macho = Producto.objects.using(alias).get(slug="enchufe-industrial-macho-volante")
    Imagen.objects.using(alias).filter(producto_id=macho.pk).update(
        imagen=IMAGEN_VOLANTE
    )
    for codigo, *_ in VARIANTES_VOLANTE:
        variante = Variante.objects.using(alias).filter(codigo=codigo).first()
        if variante:
            EspecificacionVariante.objects.using(alias).filter(variante_id=variante.pk).delete()
            variante.delete(using=alias)
    sobrepuesto = Producto.objects.using(alias).filter(slug="enchufe-industrial-macho-sobrepuesto").first()
    if sobrepuesto:
        for codigo, *_ in VARIANTES_SOBREPUESTO:
            variante = Variante.objects.using(alias).filter(codigo=codigo).first()
            if variante:
                EspecificacionVariante.objects.using(alias).filter(variante_id=variante.pk).delete()
                variante.delete(using=alias)
        sobrepuesto.delete(using=alias)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0062_machos_y_hembras_volantes"),
    ]

    operations = [
        migrations.RunPython(crear_sobrepuestos, revertir_sobrepuestos),
    ]
