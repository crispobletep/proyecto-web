from django.db import migrations


IMAGEN = "productos/catalogo/kalop-casquetes/macho-volante-2pt-16a-220v-ip44-ekoline.png"
PRODUCTOS = (
    {
        "slug": "enchufe-industrial-macho-volante",
        "nombre": "Macho volante IP44 16 A 2P+T 220 V",
        "descripcion": (
            "Enchufe industrial tipo macho volante. Selecciona la configuración "
            "de polos, corriente y tensión disponible."
        ),
        "alt": "Conectores industriales volantes, imagen referencial",
        "caracteristicas": (
            "Conector industrial volante tipo macho.",
            "Configuraciones disponibles: 2P+T, 3P+T y 3P+N+T.",
            "Opciones de 16 A y 32 A según configuración.",
        ),
        "variantes": (
            ("MV-2PT-16A-220-IP44", "2P+T · 16 A · 220 V · IP44", ("2P+T", "16", "220", "IP44")),
            ("MV-2PT-32A-220-IP44", "2P+T · 32 A · 220 V · IP44", ("2P+T", "32", "220", "IP44")),
            ("MV-3PT-16A-380", "3P+T · 16 A · 380 V", ("3P+T", "16", "380", "")),
            ("MV-3PNT-16A-380", "3P+N+T · 16 A · 380 V", ("3P+N+T", "16", "380", "")),
        ),
    },
    {
        "slug": "enchufe-industrial-hembra-volante",
        "nombre": "Hembra volante IP44 16 A 2P+T 220 V",
        "descripcion": (
            "Enchufe industrial tipo hembra volante. Selecciona la configuración "
            "de polos, corriente y tensión disponible."
        ),
        "alt": "Conector industrial volante, imagen referencial",
        "caracteristicas": (
            "Conector industrial volante tipo hembra.",
            "Configuraciones disponibles: 2P+T, 3P+T y 3P+N+T.",
            "Versiones de 16 A para 220 V o 380 V, según configuración.",
        ),
        "variantes": (
            ("HV-2PT-16A-220-IP44", "2P+T · 16 A · 220 V · IP44", ("2P+T", "16", "220", "IP44")),
            ("HV-3PT-16A-380", "3P+T · 16 A · 380 V", ("3P+T", "16", "380", "")),
            ("HV-3PNT-16A-380", "3P+N+T · 16 A · 380 V", ("3P+N+T", "16", "380", "")),
        ),
    },
)


def crear_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    ImagenProducto = apps.get_model("core", "ImagenProducto")

    original = Producto.objects.using(alias).get(slug="catalogo-kalop-casquetes")
    original.publicado = False
    original.save(using=alias, update_fields=["publicado"])
    Variante.objects.using(alias).filter(producto_id=original.pk).update(disponible=False)

    for orden, definicion in enumerate(PRODUCTOS, start=1):
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria_id": original.categoria_id,
                "nombre": definicion["nombre"],
                "marca": original.marca,
                "marca_nueva_id": original.marca_nueva_id,
                "modelo": "",
                "codigo": None,
                "subtitulo": original.subtitulo,
                "descripcion": definicion["descripcion"],
                "imagen": IMAGEN,
                "texto_alternativo": definicion["alt"],
                "etiqueta_visual": original.etiqueta_visual,
                "orden": original.orden + orden,
                "publicado": True,
            },
        )

        for posicion, texto in enumerate(definicion["caracteristicas"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                orden=posicion,
                defaults={"texto": texto},
            )

        variantes = []
        for posicion, (codigo, nombre, datos) in enumerate(definicion["variantes"], start=1):
            variante, _ = Variante.objects.using(alias).update_or_create(
                codigo=codigo,
                defaults={
                    "producto_id": producto.pk,
                    "nombre": nombre,
                    "modelo": "",
                    "imagen": IMAGEN,
                    "disponible": True,
                    "orden": posicion * 10,
                },
            )
            variantes.append(variante)

            especificaciones = [
                ("Polos", datos[0], ""),
                ("Corriente nominal", datos[1], "A"),
                ("Tensión nominal", datos[2], "V"),
            ]
            if datos[3]:
                especificaciones.append(("Grado de protección", datos[3], ""))
            for orden_spec, (nombre_spec, valor, unidad) in enumerate(especificaciones, start=1):
                EspecificacionVariante.objects.using(alias).update_or_create(
                    variante_id=variante.pk,
                    nombre=nombre_spec,
                    defaults={"valor": valor, "unidad": unidad, "orden": orden_spec},
                )

        imagen, _ = ImagenProducto.objects.using(alias).update_or_create(
            clave=f"{definicion['slug']}-imagen-referencial",
            defaults={
                "producto_id": producto.pk,
                "imagen": IMAGEN,
                "texto_alternativo": definicion["alt"],
                "orden": 1,
            },
        )
        imagen.variantes.set(variantes)


def revertir_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Cotizacion = apps.get_model("core", "Cotizacion")

    original = Producto.objects.using(alias).get(slug="catalogo-kalop-casquetes")
    for definicion in PRODUCTOS:
        producto = Producto.objects.using(alias).filter(slug=definicion["slug"]).first()
        if not producto:
            continue
        for variante in Variante.objects.using(alias).filter(producto_id=producto.pk):
            citas = Cotizacion.objects.using(alias).filter(variante_id=variante.pk)
            citas.update(producto_id=original.pk)
            if citas.exists():
                variante.producto_id = original.pk
                variante.disponible = False
                variante.save(using=alias, update_fields=["producto", "disponible"])
            else:
                variante.delete(using=alias)
        producto.delete(using=alias)

    original.publicado = True
    original.save(using=alias, update_fields=["publicado"])
    Variante.objects.using(alias).filter(
        producto_id=original.pk,
        codigo__in=("KAL-2P", "KAL-3P", "KAL-4P", "KAL-6P"),
    ).update(disponible=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0061_tableros_exterior_una_tarjeta_por_polos"),
    ]

    operations = [
        migrations.RunPython(crear_productos, revertir_productos),
    ]
