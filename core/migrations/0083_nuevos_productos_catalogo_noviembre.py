from django.db import migrations


ROOT = "productos/catalogo/"

PRODUCTS = (
    {
        "slug": "diferencial-magnetotermico-chint-nb2le-1pn",
        "name": "Interruptor diferencial magnetotérmico CHINT NB2LE 1P+N",
        "brand": "chint", "category": "interruptores-diferenciales",
        "image": "protecciones/nuevos/chint-nb2le-c40.png",
        "alt": "Imagen referencial del interruptor diferencial CHINT NB2LE",
        "subtitle": "Protección eléctrica CHINT",
        "description": "Interruptor diferencial magnetotérmico CHINT NB2LE, 1P+N, 230/240 V, sensibilidad 30 mA y poder de corte indicado de 6000 A. Calibres disponibles según la etiqueta del producto.",
        "order": 610,
        "specs": (("Polos", "1P+N", ""), ("Tensión", "230/240", "V"), ("Sensibilidad diferencial", "30", "mA"), ("Poder de corte", "6000", "A")),
        "variants": tuple((f"Curva C · {a} A", f"protecciones/nuevos/chint-nb2le-c{a}.png", (("Corriente nominal", str(a), "A"),)) for a in (40, 32, 25, 20, 16, 10)),
        "features": ("Interruptor diferencial y magnetotérmico 1P+N.", "Sensibilidad indicada: 30 mA.", "Calibres C10, C16, C20, C25, C32 y C40."),
    },
    {
        "slug": "foco-led-superficie-wellmax-eagle-eye",
        "name": "Foco LED de superficie Wellmax Eagle Eye",
        "brand": "wellmax", "category": "proyectores-area-led",
        "image": "iluminacion/focos-superficie/wellmax-eagle-eye-30w.png",
        "alt": "Imagen referencial de focos Wellmax Eagle Eye en blanco y negro",
        "subtitle": "Iluminación LED Wellmax",
        "description": "Foco LED de superficie Wellmax Eagle Eye con cabezal orientable. Disponible en color blanco o negro y en las potencias indicadas en el envase.",
        "order": 620,
        "specs": (("Montaje", "Superficie", ""), ("Orientación", "Giro 360° · inclinación 90°", "")),
        "variants": tuple((f"{w} W · {c}", f"iluminacion/focos-superficie/wellmax-eagle-eye-{w}w.png", (("Potencia", str(w), "W"), ("Color", c, ""))) for w in (30, 20, 10) for c in ("Blanco", "Negro")),
        "features": ("Cabezal orientable: giro de 360° e inclinación de 90°.", "Variantes de 10 W, 20 W y 30 W.", "Colores blanco y negro."),
    },
    {
        "slug": "ampolleta-led-fsl-gu10-6w",
        "name": "Ampolleta LED FSL GU10 6 W",
        "brand": "fsl", "category": "luminarias-led",
        "image": "iluminacion/ampolletas-nuevas/fsl-gu10-6w-6500k.png",
        "alt": "Imagen referencial de ampolleta LED FSL GU10 de 6 W",
        "subtitle": "Ampolletas LED",
        "description": "Ampolleta LED FSL de 6 W con base GU10 y luz día de 6500 K.",
        "order": 630,
        "specs": (("Potencia", "6", "W"), ("Temperatura de color", "6500", "K"), ("Flujo luminoso", "510", "lm"), ("Base", "GU10", ""), ("Vida útil", "25000", "h")),
        "features": ("Luz día 6500 K.", "Base GU10.", "Flujo indicado: 510 lm."),
    },
    {
        "slug": "ampolleta-led-megabright-a60-e27",
        "name": "Ampolleta LED Megabright A60 E27",
        "brand": "megabright", "category": "luminarias-led",
        "image": "iluminacion/ampolletas-nuevas/megabright-a60-e27.png",
        "alt": "Imagen referencial de ampolleta LED A60 Megabright con base E27",
        "subtitle": "Ampolletas LED",
        "description": "Ampolleta LED Megabright A60 con base E27. Selecciona potencia y temperatura de color disponibles.",
        "order": 640,
        "specs": (("Formato", "A60", ""), ("Base", "E27", "")),
        "variants": (
            ("13 W · 6400 K fría", "iluminacion/ampolletas-nuevas/megabright-a60-e27.png", (("Potencia", "13", "W"), ("Temperatura de color", "6400", "K"), ("Vida útil", "15000", "h"))),
            ("13 W · 3000 K cálida", "iluminacion/ampolletas-nuevas/megabright-a60-e27.png", (("Potencia", "13", "W"), ("Temperatura de color", "3000", "K"), ("Vida útil", "10000", "h"))),
            ("9 W · 3000 K cálida", "iluminacion/ampolletas-nuevas/megabright-a60-e27.png", (("Potencia", "9", "W"), ("Temperatura de color", "3000", "K"), ("Vida útil", "15000", "h"))),
            ("9 W · 6400 K fría", "iluminacion/ampolletas-nuevas/megabright-a60-e27.png", (("Potencia", "9", "W"), ("Temperatura de color", "6400", "K"), ("Vida útil", "15000", "h"))),
        ),
        "features": ("Ampolleta formato A60.", "Base E27.", "Opciones de luz cálida 3000 K y fría 6400 K."),
    },
    {
        "slug": "ampolleta-led-wellmax-e27-alta-potencia",
        "name": "Ampolleta LED Wellmax E27 alta potencia",
        "brand": "wellmax", "category": "luminarias-led",
        "image": "iluminacion/ampolletas-nuevas/wellmax-led-e27.png",
        "alt": "Imagen referencial de ampolleta LED Wellmax de alta potencia con base E27",
        "subtitle": "Ampolletas LED",
        "description": "Ampolleta LED Wellmax de alta potencia con base E27. Las potencias disponibles se identifican en cada variante.",
        "order": 650,
        "specs": (("Base", "E27", ""),),
        "variants": tuple((f"{w} W", "iluminacion/ampolletas-nuevas/wellmax-led-e27.png", (("Potencia", str(w), "W"),)) for w in (18, 28, 38, 48)),
        "features": ("Base E27.", "Potencias disponibles: 18 W, 28 W, 38 W y 48 W."),
    },
    {
        "slug": "temporizador-digital-lexo-ahc-24h",
        "name": "Temporizador digital LEXO 0–24 h",
        "brand": "lexo", "category": "temporizadores",
        "image": "control-iluminacion/nuevos/lexo-timer-digital.png",
        "alt": "Imagen referencial del temporizador digital LEXO 0 a 24 horas",
        "subtitle": "Control de iluminación LEXO",
        "description": "Temporizador digital LEXO con reserva de marcha, rango 0–24 horas, 16 A y alimentación de 220 V, según el envase.",
        "order": 660,
        "specs": (("Tipo", "Digital", ""), ("Rango", "0–24", "h"), ("Corriente nominal", "16", "A"), ("Tensión", "220", "V"), ("Reserva de marcha", "Sí", "")),
        "features": ("Programación digital de 0 a 24 horas.", "Reserva de marcha.", "16 A · 220 V."),
    },
    {
        "slug": "temporizador-horario-lexo-sul-181h",
        "name": "Temporizador horario LEXO SUL 181H",
        "brand": "lexo", "category": "temporizadores",
        "image": "control-iluminacion/nuevos/lexo-timer-sul181h.png",
        "alt": "Imagen referencial del temporizador horario LEXO SUL 181H",
        "subtitle": "Control de iluminación LEXO",
        "description": "Temporizador horario LEXO SUL 181H con reserva de marcha, 16 A y alimentación de 220 V, según el envase.",
        "order": 670,
        "specs": (("Modelo", "SUL 181H", ""), ("Tipo", "Horario analógico", ""), ("Corriente nominal", "16", "A"), ("Tensión", "220", "V"), ("Reserva de marcha", "Sí", "")),
        "features": ("Programación horaria.", "Reserva de marcha.", "16 A · 220 V."),
    },
    {
        "slug": "sensor-movimiento-vkb-ke09-180",
        "name": "Sensor infrarrojo VKB KE09 180°",
        "brand": "vkb", "category": "sensores-movimiento",
        "image": "control-iluminacion/nuevos/vkb-sensor-pir-muro-180.png",
        "alt": "Imagen referencial de sensor infrarrojo VKB KE09 para muro y cielo",
        "subtitle": "Sensores VKB",
        "description": "Sensor infrarrojo VKB KE09 para instalación en muro o cielo, cobertura indicada de 180° y alimentación de 220 V, 50 Hz.",
        "order": 680,
        "specs": (("Modelo", "KE09", ""), ("Cobertura", "180", "°"), ("Tensión", "220", "V"), ("Frecuencia", "50", "Hz")),
        "features": ("Sensor infrarrojo de movimiento.", "Instalación en muro o cielo.", "Cobertura indicada: 180°."),
    },
    {
        "slug": "sensor-movimiento-vkb-ip44-12m",
        "name": "Sensor de movimiento infrarrojo VKB IP44",
        "brand": "vkb", "category": "sensores-movimiento",
        "image": "control-iluminacion/nuevos/vkb-sensor-pir-ip44.png",
        "alt": "Imagen referencial de sensor infrarrojo VKB blanco con protección IP44",
        "subtitle": "Sensores VKB",
        "description": "Sensor de movimiento infrarrojo VKB blanco, con alcance indicado de 12 m, cobertura 180°–360° y protección IP44.",
        "order": 690,
        "specs": (("Cobertura", "180–360", "°"), ("Alcance", "12", "m"), ("Protección", "IP44", ""), ("Color", "Blanco", "")),
        "features": ("Alcance indicado: 12 m.", "Protección IP44.", "Cobertura indicada: 180°–360°."),
    },
    {
        "slug": "sensor-movimiento-vkb-techo-360-ip20",
        "name": "Sensor infrarrojo VKB para cielo 360°",
        "brand": "vkb", "category": "sensores-movimiento",
        "image": "control-iluminacion/nuevos/vkb-sensor-techo-360.png",
        "alt": "Imagen referencial de sensor infrarrojo VKB para cielo",
        "subtitle": "Sensores VKB",
        "description": "Sensor infrarrojo VKB para montaje en cielo, con cobertura de 360°, alcance indicado de 12 m, protección IP20 y acabado blanco.",
        "order": 700,
        "specs": (("Montaje", "Cielo", ""), ("Cobertura", "360", "°"), ("Alcance", "12", "m"), ("Protección", "IP20", ""), ("Color", "Blanco", "")),
        "features": ("Montaje en cielo.", "Cobertura de 360° y alcance indicado de 12 m.", "Protección IP20."),
    },
    {
        "slug": "detector-humo-fotoelectrico-bekam",
        "name": "Detector de humo fotoeléctrico BEKAM",
        "brand": "bekam", "category": "detectores-seguridad",
        "image": "control-iluminacion/nuevos/bekam-detector-humo.png",
        "alt": "Imagen referencial de detector de humo fotoeléctrico BEKAM",
        "subtitle": "Seguridad y detección",
        "description": "Detector de humo fotoeléctrico BEKAM. La fotografía del envase no muestra otros datos técnicos legibles.",
        "order": 710,
        "specs": (("Tipo", "Fotoeléctrico", ""),),
        "features": ("Detección de humo fotoeléctrica.",),
    },
    {
        "slug": "fotocelda-vkb-1800w-200-240v",
        "name": "Fotocelda VKB 1800 W con disipador",
        "brand": "vkb", "category": "fotoceldas-y-bases",
        "image": "control-iluminacion/nuevos/vkb-fotocelda-1800w.png",
        "alt": "Imagen referencial de fotocelda VKB azul con disipador",
        "subtitle": "Control de iluminación VKB",
        "description": "Fotocelda VKB con disipador, capacidad indicada de 1800 W y alimentación de 200–240 VCA.",
        "order": 720,
        "specs": (("Potencia máxima", "1800", "W"), ("Tensión", "200–240", "VCA"), ("Disipador", "Sí", "")),
        "features": ("Capacidad indicada: 1800 W.", "Alimentación: 200–240 VCA.", "Incluye disipador."),
    },
    {
        "slug": "medidor-digital-chint-pd666-3s3",
        "name": "Analizador de red CHINT PD666-3S3",
        "brand": "chint", "category": "instrumentos-panel",
        "image": "control-senalizacion/chint-nuevos/chint-medidor-pd666-3s3.jpeg",
        "alt": "Envase del analizador de red CHINT PD666-3S3",
        "subtitle": "Instrumentos de panel CHINT",
        "description": "Medidor digital multifunción CHINT PD666-3S3, 450 V, 5 A, con pantalla LCD de 96 × 96 mm y comunicación Modbus RS485 según la etiqueta comercial.",
        "order": 730,
        "specs": (("Modelo", "PD666-3S3", ""), ("Tensión", "450", "V"), ("Corriente", "5", "A"), ("Pantalla", "LCD 96 × 96", "mm"), ("Comunicación", "Modbus RS485", "")),
        "features": ("Medición digital multifunción.", "Pantalla LCD 96 × 96 mm.", "Comunicación Modbus RS485 indicada en etiqueta local."),
    },
    {
        "slug": "disparador-shunt-chint-sht-x1",
        "name": "Bobina de disparo CHINT SHT-X1",
        "brand": "chint", "category": "interruptores-automaticos",
        "image": "protecciones/nuevos/chint-disparador-sht-x1.jpeg",
        "alt": "Bobina de disparo CHINT SHT-X1",
        "subtitle": "Accesorios de protección CHINT",
        "description": "Bobina de disparo CHINT SHT-X1 con tensión de control indicada de 230/400 VCA.",
        "order": 740,
        "specs": (("Modelo", "SHT-X1", ""), ("Tensión de control", "230/400", "VCA")),
        "features": ("Accesorio de disparo remoto para interruptor compatible.", "Tensión indicada: 230/400 VCA."),
    },
)

KALOP = (
    ("interruptor-doble", "Interruptor unipolar doble KALOP Tekna 10 A blanco", "KS39651", "interruptor-doble-ks39651.jpeg", "Interruptor unipolar doble", "10", "A"),
    ("pulsador", "Pulsador unipolar KALOP Tekna 10 A blanco", "KS39657", "pulsador-ks39657.jpeg", "Pulsador unipolar", "10", "A"),
    ("interruptor-con-toma", "Interruptor y tomacorriente KALOP 2P+T 10 A blanco", "KS39674", "interruptor-toma-ks39674.jpeg", "Interruptor unipolar + tomacorriente 2P+T", "10", "A"),
    ("tapon-ciego", "Tapón ciego KALOP blanco", "KL40570", "tapon-kl40570.jpeg", "Tapón ciego", "", ""),
    ("interruptor-16a", "Interruptor unipolar KALOP modular 16 A blanco", "KL40100", "interruptor-16a-kl40100.jpeg", "Interruptor unipolar", "16", "A"),
    ("tomacorriente-10a", "Tomacorriente KALOP Tekna 2P+T 10 A blanco", "KS39672", "tomacorriente-ks39672.jpeg", "Tomacorriente 2P+T", "10", "A"),
    ("tomacorriente-bipolar", "Tomacorriente bipolar KALOP con tierra central 10 A blanco", "KL40230", "toma-bipolar-kl40230.jpeg", "Tomacorriente bipolar con tierra central", "10", "A"),
    ("tomacorriente-10-16a", "Tomacorriente KALOP 2P+Tierra central 10–16 A blanco", "KL40260", "toma-10-16a-kl40260.jpeg", "Tomacorriente 2P+Tierra central", "10–16", "A"),
    ("tomacorriente-triple", "Tomacorriente triple KALOP Tekna 2P+T 10 A blanco", "KS39673", "toma-triple-ks39673.jpeg", "Tomacorriente triple 2P+T", "10", "A"),
)


def agregar_productos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Spec = apps.get_model("core", "EspecificacionProducto")
    SpecVar = apps.get_model("core", "EspecificacionVariante")
    Feature = apps.get_model("core", "CaracteristicaProducto")

    brand_names = {"wellmax": "Wellmax", "vkb": "VKB", "bekam": "BEKAM"}
    for slug, name in brand_names.items():
        Marca.objects.using(alias).get_or_create(slug=slug, defaults={"nombre": name, "activa": True})

    def subcategory(slug, name, parent_slug, order):
        parent = Categoria.objects.using(alias).get(slug=parent_slug)
        category, _ = Categoria.objects.using(alias).update_or_create(
            slug=slug,
            defaults={"nombre": name, "padre_id": parent.pk, "orden": order, "activa": True},
        )
        return category

    subcategory("temporizadores", "Temporizadores", "control-iluminacion", 8)
    subcategory("sensores-movimiento", "Sensores de movimiento", "control-iluminacion", 9)
    subcategory("detectores-seguridad", "Detectores de seguridad", "control-senalizacion", 8)

    all_products = list(PRODUCTS)
    for order, (suffix, name, sku, file_name, mechanism, rating, unit) in enumerate(KALOP, start=750):
        all_products.append({
            "slug": f"kalop-{suffix}", "name": name, "brand": "kalop",
            "category": "modulos-electricos", "image": f"mecanismos-electricos/kalop-nuevos/{file_name}",
            "alt": f"Envase con etiqueta del producto KALOP {sku}", "subtitle": "Mecanismos eléctricos KALOP",
            "description": f"Producto KALOP blanco. {mechanism}. Código de envase {sku}; los datos técnicos se limitan a lo legible en la etiqueta aportada.",
            "order": order, "sku": sku,
            "specs": tuple(x for x in (("Mecanismo", mechanism, ""), ("Corriente nominal", rating, unit), ("Tensión", "250", "V")) if x[1]),
            "features": (f"Código de producto: {sku}.", "Acabado blanco."),
        })

    for definition in all_products:
        category = Categoria.objects.using(alias).get(slug=definition["category"])
        brand = Marca.objects.using(alias).get(slug=definition["brand"])
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": category.pk, "nombre": definition["name"], "marca": "",
                "marca_nueva_id": brand.pk, "modelo": "", "codigo": definition.get("sku"),
                "subtitulo": definition["subtitle"], "descripcion": definition["description"],
                "imagen": ROOT + definition["image"], "texto_alternativo": definition["alt"],
                "etiqueta_visual": brand.nombre.upper(), "orden": definition["order"], "publicado": True,
            },
        )
        for order, (name, value, unit) in enumerate(definition.get("specs", ()), start=1):
            Spec.objects.using(alias).update_or_create(
                producto_id=product.pk, nombre=name,
                defaults={"valor": value, "unidad": unit, "orden": order},
            )
        for order, feature in enumerate(definition.get("features", ()), start=1):
            Feature.objects.using(alias).update_or_create(
                producto_id=product.pk, orden=order, defaults={"texto": feature},
            )
        for order, (variant_name, image, specs) in enumerate(definition.get("variants", ()), start=1):
            variant, _ = Variante.objects.using(alias).update_or_create(
                producto_id=product.pk, nombre=variant_name,
                defaults={"imagen": ROOT + image, "disponible": True, "orden": order},
            )
            for spec_order, (name, value, unit) in enumerate(specs, start=1):
                SpecVar.objects.using(alias).update_or_create(
                    variante_id=variant.pk, nombre=name,
                    defaults={"valor": value, "unidad": unit, "orden": spec_order},
                )


class Migration(migrations.Migration):
    dependencies = [("core", "0082_interruptores_placa_stanford")]
    operations = [migrations.RunPython(agregar_productos, migrations.RunPython.noop)]
