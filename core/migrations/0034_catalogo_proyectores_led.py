from django.db import migrations


AREA_IMAGE = "productos/catalogo/iluminacion/proyector-area-led.png"
CAMPANA_IMAGE = "productos/catalogo/iluminacion/campana-led-ufo-megabright.png"
SENSOR_IMAGE = "productos/catalogo/iluminacion/proyector-led-sensor-movimiento.png"

AREA_VARIANTS = (
    (20, 6500),
    (30, 6500),
    (50, 6500),
    (100, 6500),
    (200, 6500),
    (10, 3000),
    (20, 3000),
    (30, 3000),
    (50, 3000),
    (100, 3000),
    (150, 3000),
    (200, 3000),
    (150, 6500),
)


def agregar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Imagen = apps.get_model("core", "ImagenProducto")

    iluminacion, _ = Categoria.objects.using(alias).get_or_create(
        slug="iluminacion",
        defaults={"nombre": "Iluminación", "orden": 30, "activa": True},
    )
    iluminacion.activa = True
    iluminacion.save(using=alias, update_fields=("activa",))

    subcategorias = {}
    for slug, nombre, orden in (
        ("proyectores-area-led", "Proyectores de área LED", 10),
        ("campanas-led-ufo", "Campanas LED UFO", 20),
        ("proyectores-led-sensor", "Proyectores LED con sensor", 30),
    ):
        categoria, _ = Categoria.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "padre_id": iluminacion.pk,
                "orden": orden,
                "activa": True,
            },
        )
        subcategorias[slug] = categoria

    def guardar_imagen(producto, clave, ruta, alt, variante=None):
        imagen, _ = Imagen.objects.using(alias).update_or_create(
            clave=clave,
            defaults={
                "producto_id": producto.pk,
                "imagen": ruta,
                "texto_alternativo": alt,
                "orden": 1,
            },
        )
        imagen.variantes.set([variante.pk] if variante else [])

    # Cada combinación de potencia y temperatura de color es una ficha propia.
    for orden, (potencia, temperatura) in enumerate(AREA_VARIANTS, start=1):
        nombre = f"PROYECTOR DE ÁREA LED {potencia}W {temperatura}K"
        slug = f"proyector-area-led-{potencia}w-{temperatura}k"
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": subcategorias["proyectores-area-led"].pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Proyectores de área LED",
                "descripcion": f"Proyector de área LED de {potencia} W y {temperatura} K.",
                "imagen": AREA_IMAGE,
                "texto_alternativo": "Proyector de área LED negro",
                "etiqueta_visual": "ILUMINACIÓN",
                "orden": 300 + orden,
                "publicado": True,
            },
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Potencia",
            defaults={"valor": str(potencia), "unidad": "W", "orden": 1},
        )
        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Temperatura de color",
            defaults={"valor": str(temperatura), "unidad": "K", "orden": 2},
        )
        guardar_imagen(
            producto,
            f"proyector-area-led-{potencia}w-{temperatura}k",
            AREA_IMAGE,
            nombre,
        )

    # La ficha de campana mantiene la potencia de 100 W de la imagen y suma
    # las dos potencias solicitadas como variantes seleccionables.
    campana, _ = Producto.objects.using(alias).update_or_create(
        slug="campana-led-ufo-megabright",
        defaults={
            "categoria_id": subcategorias["campanas-led-ufo"].pk,
            "nombre": "Campana LED UFO Megabright",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Campanas LED UFO",
            "descripcion": "Campana LED UFO Megabright. Seleccione la potencia para solicitar cotización.",
            "imagen": CAMPANA_IMAGE,
            "texto_alternativo": "Campana LED UFO Megabright",
            "etiqueta_visual": "ILUMINACIÓN",
            "orden": 320,
            "publicado": True,
        },
    )
    for orden, potencia in enumerate((100, 150, 200), start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=campana.pk,
            nombre=f"{potencia} W",
            defaults={
                "modelo": "",
                "codigo": None,
                "imagen": CAMPANA_IMAGE,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Potencia",
            defaults={"valor": str(potencia), "unidad": "W", "orden": 1},
        )
        guardar_imagen(
            campana,
            f"campana-led-ufo-megabright-{potencia}w",
            CAMPANA_IMAGE,
            f"Campana LED UFO Megabright de {potencia} W",
            variante,
        )

    sensor, _ = Producto.objects.using(alias).update_or_create(
        slug="proyector-led-sensor-movimiento-6500k",
        defaults={
            "categoria_id": subcategorias["proyectores-led-sensor"].pk,
            "nombre": "Proyector LED con sensor de movimiento 6500 K",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Proyectores LED con sensor",
            "descripcion": "Proyector LED con sensor de movimiento y luz de 6500 K. Seleccione la potencia para solicitar cotización.",
            "imagen": SENSOR_IMAGE,
            "texto_alternativo": "Proyector LED con sensor de movimiento",
            "etiqueta_visual": "ILUMINACIÓN",
            "orden": 330,
            "publicado": True,
        },
    )
    for orden, potencia in enumerate((10, 20, 30, 50, 100), start=1):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=sensor.pk,
            nombre=f"{potencia} W · 6500 K",
            defaults={
                "modelo": "",
                "codigo": None,
                "imagen": SENSOR_IMAGE,
                "disponible": True,
                "orden": orden,
            },
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Potencia",
            defaults={"valor": str(potencia), "unidad": "W", "orden": 1},
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Temperatura de color",
            defaults={"valor": "6500", "unidad": "K", "orden": 2},
        )
        guardar_imagen(
            sensor,
            f"proyector-led-sensor-movimiento-{potencia}w-6500k",
            SENSOR_IMAGE,
            f"Proyector LED con sensor de movimiento de {potencia} W y 6500 K",
            variante,
        )


def revertir_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Imagen = apps.get_model("core", "ImagenProducto")

    Producto.objects.using(alias).filter(
        slug__in=[
            f"proyector-area-led-{potencia}w-{temperatura}k"
            for potencia, temperatura in AREA_VARIANTS
        ]
        + ["campana-led-ufo-megabright", "proyector-led-sensor-movimiento-6500k"]
    ).delete()
    Imagen.objects.using(alias).filter(
        clave__startswith="proyector-area-led-"
    ).delete()
    for prefijo in ("campana-led-ufo-megabright-", "proyector-led-sensor-movimiento-"):
        Imagen.objects.using(alias).filter(clave__startswith=prefijo).delete()
    Categoria.objects.using(alias).filter(
        slug__in=("proyectores-area-led", "campanas-led-ufo", "proyectores-led-sensor")
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0033_corregir_colores_enchufes_10a")]

    operations = [migrations.RunPython(agregar_productos, revertir_productos)]
