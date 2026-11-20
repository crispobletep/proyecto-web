from django.db import migrations


DESCRIPCIONES = {
    "catalogo-canalizacion-electricacanalizacion-electricasalida-caja-emtpng": (
        "Salida a caja EMT de acero galvanizado, compatible con canalización "
        "EMT. Disponible en 20, 25 y 32 mm."
    ),
    "catalogo-canalizacion-electricacanalizacion-electricasalida-caja-pvcpng": (
        "Salida a caja para canalización de PVC eléctrico. Disponible en "
        "16, 20, 25, 32, 40 y 50 mm."
    ),
    "catalogo-canalizacion-electricacanalizacion-electricaadaptador-caja-flexpng": (
        "Adaptador a caja para conduit flexible. Disponible en 20, 25 y 32 mm."
    ),
    "catalogo-fotoceldasfotoceldaslegrand-leg-412898png": (
        "Fotocelda KALOP de 220 V y 10 A, con protección IP54."
    ),
    "catalogo-fotoceldasfotoceldaslexo-lex-fc01png": (
        "Fotocelda LEXO de 220 V y 10 A, con protección IP44."
    ),
    "gabinetes-metalicos-una-puerta": (
        "Gabinetes metálicos de una puerta para equipos de distribución, "
        "control y automatización. Disponibles en versiones estándar y con "
        "chasis interior, en varias dimensiones."
    ),
}


def simplificar_descripciones(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    for slug, descripcion in DESCRIPCIONES.items():
        Producto.objects.using(alias).filter(slug=slug).update(descripcion=descripcion)


class Migration(migrations.Migration):
    dependencies = [("core", "0112_redactar_descripciones_de_catalogo")]

    operations = [
        migrations.RunPython(simplificar_descripciones, migrations.RunPython.noop)
    ]
