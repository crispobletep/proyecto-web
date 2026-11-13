from django.db import migrations


ROOT = "productos/catalogo/"

KALOP_IMAGES = {
    "kalop-interruptor-doble": (
        "mecanismos-electricos/kalop-nuevos/catalogo-ks39651.png",
        "Vista referencial del interruptor doble KALOP KS39651 sobre fondo blanco",
    ),
    "kalop-pulsador": (
        "mecanismos-electricos/kalop-nuevos/catalogo-ks39657.png",
        "Vista referencial del pulsador KALOP KS39657 sobre fondo blanco",
    ),
    "kalop-interruptor-con-toma": (
        "mecanismos-electricos/kalop-nuevos/catalogo-ks39674.png",
        "Vista referencial del interruptor y tomacorriente KALOP KS39674 sobre fondo blanco",
    ),
    "kalop-tapon-ciego": (
        "mecanismos-electricos/kalop-nuevos/catalogo-kl40570.png",
        "Vista referencial del tapón ciego KALOP KL40570 sobre fondo blanco",
    ),
    "kalop-interruptor-16a": (
        "mecanismos-electricos/kalop-nuevos/catalogo-kl40100.png",
        "Vista referencial del interruptor KALOP KL40100 sobre fondo blanco",
    ),
    "kalop-tomacorriente-10a": (
        "mecanismos-electricos/kalop-nuevos/catalogo-ks39672.png",
        "Vista referencial del tomacorriente KALOP KS39672 sobre fondo blanco",
    ),
    "kalop-tomacorriente-bipolar": (
        "mecanismos-electricos/kalop-nuevos/catalogo-kl40230.png",
        "Vista referencial del tomacorriente KALOP KL40230 sobre fondo blanco",
    ),
    "kalop-tomacorriente-10-16a": (
        "mecanismos-electricos/kalop-nuevos/catalogo-kl40260.png",
        "Vista referencial del tomacorriente KALOP KL40260 sobre fondo blanco",
    ),
    "kalop-tomacorriente-triple": (
        "mecanismos-electricos/kalop-nuevos/catalogo-ks39673.png",
        "Vista referencial del tomacorriente triple KALOP KS39673 sobre fondo blanco",
    ),
}


def actualizar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    for slug, (path, alt) in KALOP_IMAGES.items():
        producto = Producto.objects.using(alias).get(slug=slug)
        producto.imagen = ROOT + path
        producto.texto_alternativo = alt
        producto.save(using=alias, update_fields=("imagen", "texto_alternativo"))

    analizador = Producto.objects.using(alias).get(
        slug="medidor-digital-chint-pd666-3s3"
    )
    analizador.imagen = (
        ROOT + "control-senalizacion/chint-nuevos/"
        "chint-medidor-pd666-3s3-catalogo.png"
    )
    analizador.texto_alternativo = (
        "Imagen referencial de un medidor digital de panel CHINT PD666-3S3 "
        "sobre fondo blanco"
    )
    analizador.save(using=alias, update_fields=("imagen", "texto_alternativo"))

    fsl = Producto.objects.using(alias).get(slug="ampolleta-led-fsl-gu10-6w")
    fsl.imagen = ROOT + "iluminacion/ampolletas-nuevas/fsl-gu10-6w-6500k-producto.png"
    fsl.texto_alternativo = (
        "Imagen referencial de ampolleta LED FSL GU10 de 6 W con luz fría"
    )
    fsl.descripcion = (
        "Ampolleta LED FSL de 6 W con base GU10 y flujo indicado de 510 lm. "
        "Disponible en luz cálida de 3000 K y luz fría de 6500 K."
    )
    fsl.save(
        using=alias,
        update_fields=("imagen", "texto_alternativo", "descripcion"),
    )
    Especificacion.objects.using(alias).filter(
        producto_id=fsl.pk, nombre="Temperatura de color"
    ).delete()

    for order, (name, value, image_name, temperature_label) in enumerate(
        (
            (
                "6 W · 3000 K cálida",
                "3000",
                "fsl-gu10-6w-3000k.png",
                "Luz cálida",
            ),
            (
                "6 W · 6500 K fría",
                "6500",
                "fsl-gu10-6w-6500k-producto.png",
                "Luz fría",
            ),
        ),
        start=1,
    ):
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=fsl.pk,
            nombre=name,
            defaults={
                "imagen": ROOT + "iluminacion/ampolletas-nuevas/" + image_name,
                "disponible": True,
                "orden": order,
            },
        )
        for spec_order, (spec_name, spec_value, unit) in enumerate(
            (
                ("Potencia", "6", "W"),
                ("Temperatura de color", value, "K"),
                ("Flujo luminoso", "510", "lm"),
                ("Base", "GU10", ""),
                ("Vida útil", "25000", "h"),
            ),
            start=1,
        ):
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre=spec_name,
                defaults={
                    "valor": spec_value,
                    "unidad": unit,
                    "orden": spec_order,
                },
            )

    for order, text in enumerate(
        (
            "Base GU10 y flujo indicado de 510 lm.",
            "Elige la presentación de luz cálida 3000 K o luz fría 6500 K.",
        ),
        start=1,
    ):
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=fsl.pk,
            orden=order,
            defaults={"texto": text},
        )
    Caracteristica.objects.using(alias).filter(producto_id=fsl.pk, orden__gt=2).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0102_actualizar_portada_edificios_mirador_azul")]

    operations = [
        migrations.RunPython(actualizar_catalogo, migrations.RunPython.noop),
    ]
