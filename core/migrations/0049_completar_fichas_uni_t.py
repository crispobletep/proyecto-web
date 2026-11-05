from django.db import migrations


# Valores tomados de las fichas oficiales de UNI-T:
# https://meters.uni-trend.com/product/ut200plus-series/
# https://meters.uni-trend.com/product/ut12s-row-ut12d-row/

FICHAS = {
    "amperimetro-tenaza-ut202-plus": {
        "caracteristicas": (
            "Mide corriente alterna hasta 400 A.",
            "Mide tensión AC/DC hasta 600 V.",
            "Pinza de 28 mm, medición True RMS y pantalla de 4000 cuentas.",
        ),
        "especificaciones": (
            ("Corriente AC máxima", "400", "A"),
            ("Tensión AC/DC máxima", "600", "V"),
            ("Resistencia máxima", "40", "MΩ"),
            ("Capacitancia máxima", "4", "mF"),
            ("Rango de temperatura", "-40 a 1000", "°C"),
            ("Apertura de pinza", "28", "mm"),
            ("Pantalla", "4000", "cuentas"),
            ("True RMS", "Sí", ""),
        ),
    },
    "amperimetro-tenaza-ut203-plus": {
        "caracteristicas": (
            "Mide corriente AC y DC hasta 400 A.",
            "Mide tensión AC/DC hasta 600 V.",
            "Mide frecuencia de 10 Hz a 10 MHz y resistencia hasta 40 MΩ.",
        ),
        "especificaciones": (
            ("Corriente AC máxima", "400", "A"),
            ("Corriente DC máxima", "400", "A"),
            ("Tensión AC/DC máxima", "600", "V"),
            ("Resistencia máxima", "40", "MΩ"),
            ("Rango de frecuencia", "10 Hz a 10 MHz", ""),
            ("Apertura de pinza", "28", "mm"),
            ("Pantalla", "4000", "cuentas"),
            ("True RMS", "Sí", ""),
        ),
    },
    "detector-de-voltaje-ut12d": {
        "caracteristicas": (
            "Detector de tensión AC sin contacto.",
            "Dos modos: baja sensibilidad de 24 a 1000 V y alta de 90 a 1000 V.",
            "Indicadores LED y sonoro, linterna incorporada y apagado automático.",
        ),
        "especificaciones": (
            ("Rango de detección, modo bajo", "24 a 1000", "V AC"),
            ("Rango de detección, modo alto", "90 a 1000", "V AC"),
            ("Frecuencia", "50/60", "Hz"),
            ("Indicadores", "LED y zumbador", ""),
            ("Linterna incorporada", "Sí", ""),
            ("Apagado automático", "Sí", ""),
        ),
    },
}


def completar(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    for slug, ficha in FICHAS.items():
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        for orden, texto in enumerate(ficha["caracteristicas"], start=1):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                texto=texto,
                defaults={"orden": orden},
            )
        for orden, (nombre, valor, unidad) in enumerate(ficha["especificaciones"], start=1):
            Especificacion.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )


def revertir(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    for slug, ficha in FICHAS.items():
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue
        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk,
            texto__in=ficha["caracteristicas"],
        ).delete()
        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk,
            nombre__in=[item[0] for item in ficha["especificaciones"]],
        ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0048_renombrar_bright_megabright")]

    operations = [migrations.RunPython(completar, revertir)]
