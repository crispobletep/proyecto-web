from django.db import migrations


CORRECCIONES = (
    (
        "kalop-calota-interior-1-4cc-tapa-transparente-gris",
        "Calota interior 4 CC con tapa transparente gris",
        "4",
    ),
    (
        "kalop-calota-interior-1-6cc-tapa-transparente-gris",
        "Calota interior 6 CC con tapa transparente gris",
        "6",
    ),
)


def corregir_capacidades_calotas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    for slug, nombre, capacidad in CORRECCIONES:
        producto = Producto.objects.using(alias).filter(slug=slug).first()
        if not producto:
            continue

        producto.nombre = nombre
        producto.descripcion = (
            f"Calota Kalop para instalación interior, configuración de "
            f"{capacidad} CC y tapa transparente gris."
        )
        producto.texto_alternativo = nombre
        producto.save(
            using=alias,
            update_fields=("nombre", "descripcion", "texto_alternativo"),
        )

        Caracteristica.objects.using(alias).filter(
            producto_id=producto.pk
        ).delete()
        for orden, texto in enumerate(
            (
                "Formato para instalación interior.",
                f"Configuración: {capacidad} CC.",
                "Incluye tapa transparente gris.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).create(
                producto_id=producto.pk,
                texto=texto,
                orden=orden,
            )

        Especificacion.objects.using(alias).filter(
            producto_id=producto.pk,
            nombre="Configuración",
        ).update(valor=f"{capacidad} CC", unidad="")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0130_agregar_contactos_auxiliares"),
    ]

    operations = [
        migrations.RunPython(
            corregir_capacidades_calotas,
            migrations.RunPython.noop,
        ),
    ]
