from django.db import migrations


CATEGORIAS = {
    "canoas-led": ("Canoas lineales", 10, True),
    "equipos-estancos-led": ("Equipos estancos", 20, True),
    "luminarias-solares": ("Luminarias solares", 30, True),
    "tubos-led": ("Tubos", 40, True),
    "plafones-led": ("Paneles y plafones", 50, True),
    "proyectores-area-led": ("Proyectores", 60, True),
    "campanas-led-ufo": ("Campanas", 70, True),
}
SLUGS_PROYECTORES_SENSOR = (
    "proyector-led-sensor-logic-10w-6500k",
    "proyector-led-sensor-logic-20w-6500k",
    "proyector-led-sensor-logic-30w-6500k",
    "proyector-led-sensor-logic-50w-6500k",
    "proyector-led-sensor-logic-100w-6500k",
)


def simplificar_filtros(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categorias = {
        categoria.slug: categoria
        for categoria in Categoria.objects.using(alias).filter(
            slug__in=(*CATEGORIAS.keys(), "proyectores-led-sensor", "proyectores-led", "luminarias-led")
        )
    }
    proyectores = categorias["proyectores-area-led"]
    Producto.objects.using(alias).filter(
        slug__in=SLUGS_PROYECTORES_SENSOR
    ).update(categoria_id=proyectores.pk)

    for slug, (nombre, orden, activa) in CATEGORIAS.items():
        Categoria.objects.using(alias).filter(slug=slug).update(
            nombre=nombre, orden=orden, activa=activa
        )

    Categoria.objects.using(alias).filter(
        slug__in=("proyectores-led-sensor", "proyectores-led", "luminarias-led")
    ).update(activa=False)


def restaurar_filtros(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")

    categorias = {
        categoria.slug: categoria
        for categoria in Categoria.objects.using(alias).filter(
            slug__in=(*CATEGORIAS.keys(), "proyectores-led-sensor", "proyectores-led", "luminarias-led")
        )
    }
    Producto.objects.using(alias).filter(
        slug__in=SLUGS_PROYECTORES_SENSOR
    ).update(categoria_id=categorias["proyectores-led-sensor"].pk)

    nombres_anteriores = {
        "canoas-led": ("Canoas LED", 0),
        "equipos-estancos-led": ("Equipos estancos LED", 0),
        "luminarias-solares": ("Luminarias solares", 0),
        "tubos-led": ("Tubos LED", 0),
        "plafones-led": ("Plafones LED", 3),
        "proyectores-area-led": ("Proyectores de área LED", 10),
        "campanas-led-ufo": ("Campanas LED UFO", 20),
        "proyectores-led-sensor": ("Proyectores LED con sensor", 30),
    }
    for slug, (nombre, orden) in nombres_anteriores.items():
        Categoria.objects.using(alias).filter(slug=slug).update(
            nombre=nombre, orden=orden, activa=True
        )
    Categoria.objects.using(alias).filter(
        slug__in=("proyectores-led", "luminarias-led")
    ).update(activa=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0051_separar_proyectores_sensor_logic"),
    ]

    operations = [
        migrations.RunPython(simplificar_filtros, restaurar_filtros),
    ]
