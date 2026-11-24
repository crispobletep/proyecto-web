from django.db import migrations


PROYECTO = "remodelacion-edificio-a-hospital-del-trabajador"
PORTADA = "proyectos/achs-edificio-a/fachada-hospital-del-trabajador.jpeg"
GALERIA = (
    (
        "oficina-administrativa.jpeg",
        "Puesto de trabajo en las oficinas del Hospital del Trabajador ACHS",
    ),
    (
        "luminaria-bano.jpeg",
        "Luminaria instalada en el baño de pacientes del Hospital del Trabajador ACHS",
    ),
    (
        "iluminacion-area-atencion.jpeg",
        "Iluminación y módulos del área de atención del Hospital del Trabajador ACHS",
    ),
    (
        "tablero-electrico.jpeg",
        "Tablero eléctrico de distribución del Hospital del Trabajador ACHS",
    ),
    (
        "modulos-atencion.jpeg",
        "Módulos de atención con iluminación del Hospital del Trabajador ACHS",
    ),
    (
        "sala-espera.jpeg",
        "Sala de espera del Hospital del Trabajador ACHS",
    ),
    (
        "pulsador-emergencia.jpeg",
        "Pulsador de emergencia instalado en el Hospital del Trabajador ACHS",
    ),
    (
        "canalizacion-electrica.jpeg",
        "Canalización eléctrica en el Hospital del Trabajador ACHS",
    ),
    (
        "montaje-electrico.jpeg",
        "Montaje eléctrico en altura dentro del Hospital del Trabajador ACHS",
    ),
)


def cargar_galeria_achs(apps, schema_editor):
    alias = schema_editor.connection.alias
    Proyecto = apps.get_model("core", "Proyecto")
    ImagenProyecto = apps.get_model("core", "ImagenProyecto")
    proyecto = Proyecto.objects.using(alias).filter(slug=PROYECTO).first()
    if not proyecto:
        return

    proyecto.imagen = PORTADA
    proyecto.texto_alternativo = (
        "Fachada del Edificio A del Hospital del Trabajador ACHS en Providencia"
    )
    proyecto.save(using=alias, update_fields=["imagen", "texto_alternativo"])

    for orden, (archivo, alt) in enumerate(GALERIA, start=1):
        ImagenProyecto.objects.using(alias).update_or_create(
            proyecto_id=proyecto.pk,
            orden=orden,
            defaults={
                "imagen": f"proyectos/achs-edificio-a/{archivo}",
                "texto_alternativo": alt,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0116_agregar_luminaria_publica_street_light")]

    operations = [
        migrations.RunPython(cargar_galeria_achs, migrations.RunPython.noop),
    ]
