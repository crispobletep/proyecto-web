from django.db import migrations


ROOT = "productos/catalogo/herramientas/"

PRODUCTOS = (
    {
        "slug": "broca-pino-toolmak",
        "nombre": "Broca pino TOOLMAK",
        "marca": "TOOLMAK",
        "categoria": "brocas-perforacion",
        "imagen": "broca-pino-toolmak.png",
        "alt": "Broca pino escalonada TOOLMAK sobre fondo blanco",
        "descripcion": "Broca pino escalonada TOOLMAK para perforación. Disponible en dos rangos de diámetro.",
        "subtitulo": "Brocas y perforación",
        "etiqueta": "BROCAS Y PERFORACIÓN",
        "orden": 1,
        "caracteristicas": ("Broca escalonada para perforación.",),
        "especificaciones": (("Tipo", "Broca pino", ""),),
        "variantes": (
            ("4–20 mm", "Rango de diámetro", "4–20", "mm"),
            ("4–32 mm", "Rango de diámetro", "4–32", "mm"),
        ),
    },
    {
        "slug": "disco-corte-stanley-4-1-2-115mm",
        "nombre": "Disco de corte Stanley 4 1/2″ (115 mm)",
        "marca": "Stanley",
        "categoria": "discos-corte",
        "imagen": "disco-corte-stanley-115mm.png",
        "alt": "Disco Stanley para corte de metal y acero inoxidable de 115 mm",
        "descripcion": "Disco Stanley tipo 41 para corte de metal y acero inoxidable. La etiqueta indica 115 mm de diámetro, 1,0 mm de espesor y eje de 22 mm.",
        "subtitulo": "Discos de corte",
        "etiqueta": "DISCOS DE CORTE",
        "orden": 1,
        "caracteristicas": ("Uso indicado: corte de metal y acero inoxidable.", "Tipo 41."),
        "especificaciones": (("Diámetro", "115", "mm"), ("Espesor", "1,0", "mm"), ("Diámetro del eje", "22", "mm"), ("Equivalencia", "4 1/2", "pulg")),
    },
    {
        "slug": "alicate-pelacable-automatico-kamasa-7",
        "nombre": "Alicate pelacable automático KAMASA 7″",
        "marca": "KAMASA",
        "modelo": "KM-027",
        "categoria": "herramientas-manuales",
        "imagen": "alicate-pelacable-kamasa-7.png",
        "alt": "Alicate pelacable automático KAMASA Professional de 7 pulgadas",
        "descripcion": "Alicate pelacable automático KAMASA Professional. El envase indica 7 pulgadas (180 mm) y referencia KM-027.",
        "subtitulo": "Herramientas manuales",
        "etiqueta": "HERRAMIENTAS MANUALES",
        "orden": 1,
        "caracteristicas": ("Pelado automático de cables.", "Largo indicado: 7″ (180 mm)."),
        "especificaciones": (("Largo", "7", "pulg (180 mm)"), ("Referencia", "KM-027", "")),
    },
    {
        "slug": "alicate-cortante",
        "nombre": "Alicate cortante",
        "marca": "",
        "categoria": "herramientas-manuales",
        "imagen": "alicate-cortante.png",
        "alt": "Alicate cortante con mangos aislados en tonos gris y amarillo",
        "descripcion": "Alicate cortante de uso manual para trabajos eléctricos y de instalación.",
        "subtitulo": "Herramientas manuales",
        "etiqueta": "HERRAMIENTAS MANUALES",
        "orden": 2,
        "caracteristicas": ("Herramienta manual de corte.",),
    },
    {
        "slug": "alicate-universal-stanley",
        "nombre": "Alicate universal Stanley",
        "marca": "Stanley",
        "categoria": "herramientas-manuales",
        "imagen": "alicate-universal-stanley.png",
        "alt": "Alicate universal Stanley con mangos negros y amarillos",
        "descripcion": "Alicate universal Stanley para sujetar, doblar y cortar en trabajos de instalación.",
        "subtitulo": "Herramientas manuales",
        "etiqueta": "HERRAMIENTAS MANUALES",
        "orden": 3,
        "caracteristicas": ("Herramienta manual de sujeción y corte.",),
    },
    {
        "slug": "alicate-punta-larga-stanley",
        "nombre": "Alicate de punta larga Stanley",
        "marca": "Stanley",
        "categoria": "herramientas-manuales",
        "imagen": "alicate-punta-larga-stanley.png",
        "alt": "Alicate Stanley de punta larga con mangos negros y amarillos",
        "descripcion": "Alicate de punta larga Stanley para sujetar y manipular elementos en espacios reducidos.",
        "subtitulo": "Herramientas manuales",
        "etiqueta": "HERRAMIENTAS MANUALES",
        "orden": 4,
        "caracteristicas": ("Punta larga para trabajos de precisión.",),
    },
    {
        "slug": "crimpadora-terminales-ferrule-dex",
        "nombre": "Crimpadora para terminales ferrule DEX Electric",
        "marca": "DEX Electric",
        "categoria": "herramientas-manuales",
        "imagen": "crimpadora-ferrulas-dex.webp",
        "alt": "Crimpadora manual DEX Electric para terminales ferrule",
        "descripcion": "Herramienta manual para crimpar terminales tipo ferrule.",
        "subtitulo": "Herramientas manuales",
        "etiqueta": "HERRAMIENTAS MANUALES",
        "orden": 5,
        "caracteristicas": ("Crimpado manual de terminales ferrule.",),
    },
)


def agregar_catalogo_herramientas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia, _ = Categoria.objects.using(alias).update_or_create(
        slug="herramientas",
        defaults={"nombre": "Herramientas", "padre_id": None, "orden": 50, "activa": True},
    )
    categorias = (
        ("brocas-perforacion", "Brocas y perforación", 1),
        ("herramientas-manuales", "Herramientas manuales", 2),
        ("discos-corte", "Discos de corte", 3),
    )
    categorias_por_slug = {}
    for slug, nombre, orden in categorias:
        categoria, _ = Categoria.objects.using(alias).update_or_create(
            slug=slug,
            defaults={"nombre": nombre, "padre_id": familia.pk, "orden": orden, "activa": True},
        )
        categorias_por_slug[slug] = categoria

    definiciones = list(PRODUCTOS)
    for diameter, length in (
        (6, 110), (6, 160), (8, 110), (8, 160), (10, 110), (10, 160), (12, 110)
    ):
        definiciones.append({
            "slug": f"broca-rotomartillo-sds-plus-{diameter}x{length}mm",
            "nombre": f"Broca rotomartillo SDS Plus {diameter} × {length} mm",
            "marca": "",
            "categoria": "brocas-perforacion",
            "imagen": "broca-rotomartillo-sds.png",
            "alt": f"Broca SDS Plus para rotomartillo de {diameter} × {length} mm; imagen de referencia Asaki",
            "descripcion": f"Broca para rotomartillo con encastre SDS Plus, diámetro de {diameter} mm y largo de {length} mm.",
            "subtitulo": "Brocas y perforación",
            "etiqueta": "BROCAS Y PERFORACIÓN",
            "orden": 10 + len(definiciones),
            "caracteristicas": ("Encastre SDS Plus.", f"Diámetro: {diameter} mm.", f"Largo: {length} mm."),
            "especificaciones": (("Diámetro", str(diameter), "mm"), ("Largo", str(length), "mm"), ("Encastre", "SDS Plus", "")),
        })

    for diameter in (20, 22, 25, 32, 40, 50, 63):
        definiciones.append({
            "slug": f"sierra-copa-metal-guia-{diameter}mm",
            "nombre": f"Sierra copa para metal con guía {diameter} mm",
            "marca": "",
            "categoria": "brocas-perforacion",
            "imagen": "sierra-copa-metal-con-guia.png",
            "alt": f"Sierra copa para metal con guía de {diameter} mm",
            "descripcion": f"Sierra copa para metal con guía, de {diameter} mm de diámetro.",
            "subtitulo": "Brocas y perforación",
            "etiqueta": "BROCAS Y PERFORACIÓN",
            "orden": 30 + len(definiciones),
            "caracteristicas": ("Incluye guía de centrado.", f"Diámetro: {diameter} mm."),
            "especificaciones": (("Diámetro", str(diameter), "mm"),),
        })

    for size in ("1/2", "5/8", "1", "3/8"):
        slug_size = size.replace("/", "-")
        definiciones.append({
            "slug": f"broca-paleta-{slug_size}-pulg",
            "nombre": f"Broca paleta {size}″",
            "marca": "",
            "categoria": "brocas-perforacion",
            "imagen": "broca-paleta.png",
            "alt": f"Broca paleta para madera de {size} pulgadas",
            "descripcion": f"Broca paleta para perforación en madera, de {size} pulgadas.",
            "subtitulo": "Brocas y perforación",
            "etiqueta": "BROCAS Y PERFORACIÓN",
            "orden": 50 + len(definiciones),
            "caracteristicas": ("Tipo paleta para perforación en madera.", f"Diámetro: {size}″."),
            "especificaciones": (("Diámetro", size, "pulg"),),
        })

    for definition in definiciones:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=definition["slug"],
            defaults={
                "categoria_id": categorias_por_slug[definition["categoria"]].pk,
                "nombre": definition["nombre"],
                "marca": definition.get("marca", ""),
                "marca_nueva_id": None,
                "modelo": definition.get("modelo", ""),
                "codigo": None,
                "subtitulo": definition["subtitulo"],
                "descripcion": definition["descripcion"],
                "imagen": ROOT + definition["imagen"],
                "texto_alternativo": definition["alt"],
                "etiqueta_visual": definition["etiqueta"],
                "orden": definition["orden"],
                "publicado": True,
            },
        )
        Caracteristica.objects.using(alias).filter(producto_id=producto.pk).delete()
        for orden, texto in enumerate(definition.get("caracteristicas", ()), start=1):
            Caracteristica.objects.using(alias).create(
                producto_id=producto.pk, texto=texto, orden=orden
            )
        Especificacion.objects.using(alias).filter(producto_id=producto.pk).delete()
        for orden, (nombre, valor, unidad) in enumerate(definition.get("especificaciones", ()), start=1):
            Especificacion.objects.using(alias).create(
                producto_id=producto.pk,
                nombre=nombre,
                valor=valor,
                unidad=unidad,
                orden=orden,
            )
        if definition.get("variantes"):
            for variante, nombre_spec, valor_spec, unidad_spec in definition["variantes"]:
                variant, _ = Variante.objects.using(alias).update_or_create(
                    producto_id=producto.pk,
                    nombre=variante,
                    defaults={"imagen": "", "disponible": True, "orden": definition["variantes"].index((variante, nombre_spec, valor_spec, unidad_spec)) + 1},
                )
                EspecificacionVariante.objects.using(alias).update_or_create(
                    variante_id=variant.pk,
                    nombre=nombre_spec,
                    defaults={"valor": valor_spec, "unidad": unidad_spec, "orden": 1},
                )


class Migration(migrations.Migration):
    dependencies = [("core", "0109_agregar_reles_termicos")]

    operations = [migrations.RunPython(agregar_catalogo_herramientas, migrations.RunPython.noop)]
