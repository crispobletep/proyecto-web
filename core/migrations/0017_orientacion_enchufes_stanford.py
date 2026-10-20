import re

from django.db import migrations


def diferenciar_orientacion(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    productos = Producto.objects.using(alias).filter(
        categoria__slug="enchufes",
        marca_nueva__slug="stanford",
    ).select_related("categoria", "marca_nueva")

    for producto in productos:
        imagen = (producto.imagen.name or "").casefold()
        nombre = producto.nombre
        tipo = re.search(r"\b(simple|doble|triple)\b", nombre, re.IGNORECASE)
        if not tipo:
            continue

        tipo_nombre = tipo.group(1).lower()
        if "staford-enchufes/" in imagen:
            orientacion = "Vertical"
        elif "enchufes/" in imagen and tipo_nombre in {"doble", "triple"}:
            orientacion = "Horizontal"
        elif "enchufes/" in imagen and tipo_nombre == "simple":
            # Una sola toma, con sus polos dispuestos en columna.
            orientacion = "Vertical"
        else:
            continue

        base = re.sub(r"\s+(horizontal|vertical)\b", "", nombre, flags=re.IGNORECASE)
        tipo_match = re.search(r"\b(simple|doble|triple)\b", base, re.IGNORECASE)
        nuevo_nombre = (
            f"{base[:tipo_match.end()]} {orientacion.lower()}"
            f"{base[tipo_match.end():]}"
        )
        if nuevo_nombre != nombre:
            producto.nombre = nuevo_nombre
            producto.save(using=alias, update_fields=["nombre"])

        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Orientación",
            defaults={"valor": orientacion, "unidad": "", "orden": 10},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0016_unificar_stanford")]

    operations = [
        migrations.RunPython(diferenciar_orientacion, migrations.RunPython.noop),
    ]
