from django.db import migrations


IMAGES = (
    ("galeria-01.jpeg", "Comedor y cocina de los espacios comunes"),
    ("galeria-02.jpeg", "Sala de estar con vista a los jardines"),
    ("galeria-03.jpeg", "Juegos infantiles y áreas verdes del edificio"),
)


def cargar_galeria(apps, schema_editor):
    alias = schema_editor.connection.alias
    Proyecto = apps.get_model("core", "Proyecto")
    ImagenProyecto = apps.get_model("core", "ImagenProyecto")
    proyecto = Proyecto.objects.using(alias).filter(slug="edificios-mirador-azul").first()
    if not proyecto:
        return

    proyecto.imagen = "proyectos/edificios-mirador-azul/portada.jpeg"
    proyecto.texto_alternativo = "Sala de estar luminosa en Edificios Mirador Azul"
    proyecto.save(using=alias, update_fields=["imagen", "texto_alternativo"])

    for orden, (filename, alt) in enumerate(IMAGES, start=1):
        ImagenProyecto.objects.using(alias).update_or_create(
            proyecto_id=proyecto.pk,
            orden=orden,
            defaults={
                "imagen": f"proyectos/edificios-mirador-azul/{filename}",
                "texto_alternativo": alt,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0100_galeria_edificio_froilan_lagos")]

    operations = [
        migrations.RunPython(cargar_galeria, migrations.RunPython.noop),
    ]
