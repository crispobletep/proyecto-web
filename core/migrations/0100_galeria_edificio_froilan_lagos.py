from django.db import migrations, models
import django.db.models.deletion


IMAGES = (
    ("galeria-01.jpeg", "Sala eléctrica con tableros del edificio"),
    ("galeria-02.jpeg", "Sala de reuniones del Edificio Froilán Lagos"),
    ("galeria-03.jpeg", "Salón gourmet del edificio"),
    ("galeria-04.jpeg", "Sala de juegos con mesa de pool"),
    ("galeria-05.jpeg", "Living y comedor de los espacios comunes"),
    ("galeria-06.jpeg", "Sala de estar y muro decorativo"),
    ("galeria-07.jpeg", "Espacio de estar con iluminación decorativa"),
    ("galeria-08.jpeg", "Lavandería común del edificio"),
    ("galeria-09.jpeg", "Gimnasio equipado del edificio"),
    ("galeria-10.jpeg", "Salón común con comedor y estar"),
    ("galeria-11.jpeg", "Salón gourmet con vista al exterior"),
    ("galeria-12.jpeg", "Living y comedor de los espacios comunes"),
    ("galeria-13.jpeg", "Terraza común con quincho y mobiliario"),
)


def cargar_galeria(apps, schema_editor):
    alias = schema_editor.connection.alias
    Proyecto = apps.get_model("core", "Proyecto")
    ImagenProyecto = apps.get_model("core", "ImagenProyecto")
    proyecto = Proyecto.objects.using(alias).filter(slug="edificio-froilan-lagos").first()
    if not proyecto:
        return

    proyecto.imagen = "proyectos/edificio-froilan-lagos/portada.jpeg"
    proyecto.texto_alternativo = "Vista exterior del Edificio Froilán Lagos en Santiago"
    proyecto.save(using=alias, update_fields=["imagen", "texto_alternativo"])

    for orden, (filename, alt) in enumerate(IMAGES, start=1):
        ImagenProyecto.objects.using(alias).update_or_create(
            proyecto_id=proyecto.pk,
            orden=orden,
            defaults={
                "imagen": f"proyectos/edificio-froilan-lagos/{filename}",
                "texto_alternativo": alt,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0099_imagenes_ampolleta_megabright_por_temperatura")]

    operations = [
        migrations.CreateModel(
            name="ImagenProyecto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("imagen", models.ImageField(upload_to="proyectos/galeria/")),
                ("texto_alternativo", models.CharField(blank=True, max_length=180)),
                ("orden", models.PositiveIntegerField(default=0)),
                ("proyecto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="imagenes", to="core.proyecto")),
            ],
            options={
                "ordering": ["orden", "pk"],
                "verbose_name": "Imagen de proyecto",
                "verbose_name_plural": "Imágenes de proyectos",
            },
        ),
        migrations.RunPython(cargar_galeria, migrations.RunPython.noop),
    ]
