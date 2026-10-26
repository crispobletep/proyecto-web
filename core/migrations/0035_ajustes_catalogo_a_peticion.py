from django.db import migrations


CODIGOS_RETIRADOS = (
    "CHT-NY01",  # Fotocelda CHINT
    "STF-FC10",  # Fotocelda Stanford
    "LEG-412899",  # Base Legrand
    "CHT-BY01",  # Base CHINT
    "STF-BF10",  # Base Stanford
    "SOP-FC01",  # Soporte metálico
)


def ajustar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Categoria = apps.get_model("core", "Categoria")

    # Retirar del catálogo sin borrar el historial de cotizaciones.
    ids_retirados = list(
        Variante.objects.using(alias)
        .filter(codigo__in=CODIGOS_RETIRADOS)
        .values_list("producto_id", flat=True)
        .distinct()
    )
    Producto.objects.using(alias).filter(pk__in=ids_retirados).update(
        publicado=False
    )
    Variante.objects.using(alias).filter(
        codigo__in=CODIGOS_RETIRADOS
    ).update(disponible=False)

    # Conservar solo la base LEXO, con una presentación y referencia genéricas.
    base = Producto.objects.using(alias).filter(
        variantes__codigo="LEX-BF01"
    ).first()
    if base:
        base.nombre = "Base para fotocelda"
        base.descripcion = (
            "Base de tres pines para fotocelda."
        )
        base.texto_alternativo = "Base de tres pines para fotocelda"
        base.marca = ""
        base.marca_nueva_id = None
        base.save(
            using=alias,
            update_fields=(
                "nombre",
                "descripcion",
                "texto_alternativo",
                "marca",
                "marca_nueva",
            ),
        )
        Variante.objects.using(alias).filter(
            producto_id=base.pk,
            codigo="LEX-BF01",
        ).update(codigo="BASE-FC01")
        Imagen.objects.using(alias).filter(producto_id=base.pk).update(
            texto_alternativo="Base de tres pines para fotocelda"
        )

    # Retirar FLS/YLM en medidas distintas de 120 x 60. Mantener una ficha
    # genérica por montaje usando las presentaciones FLS como referencia.
    paneles = Producto.objects.using(alias).filter(
        slug__startswith="catalogo-plafones-ledplafones-led",
    )
    for producto in paneles:
        slug = producto.slug
        es_fls = "plafones-ledfls-" in slug
        es_12060 = "12060-" in slug
        es_yellmax = "plafones-ledyellmax-" in slug
        if not (es_fls or es_yellmax):
            continue
        if es_fls and es_12060:
            montaje = "sobrepuesto" if slug.endswith("-sppng") else "embutido"
            producto.nombre = f"Plafón LED 120 × 60 cm {montaje}"
            producto.descripcion = (
                f"Plafón LED de 120 × 60 cm para instalación {montaje}."
            )
            producto.texto_alternativo = producto.nombre
            producto.marca = ""
            producto.marca_nueva_id = None
            producto.etiqueta_visual = "PLAFONES LED"
            producto.save(
                using=alias,
                update_fields=(
                    "nombre",
                    "descripcion",
                    "texto_alternativo",
                    "marca",
                    "marca_nueva",
                    "etiqueta_visual",
                ),
            )
            Imagen.objects.using(alias).filter(producto_id=producto.pk).update(
                texto_alternativo=producto.nombre
            )
        else:
            producto.publicado = False
            producto.save(using=alias, update_fields=("publicado",))

    # Quitar Stanford de la ficha de contactores, la marca y los códigos visibles.
    contactores = Producto.objects.using(alias).filter(
        slug="contactores-stanford-220v"
    ).first()
    if contactores:
        contactores.nombre = "Contactores 220 V"
        contactores.descripcion = (
            "Contactores con bobina de 220 V. Selecciona la corriente nominal "
            "de 9, 12, 18, 25 o 32 A para solicitar una cotización."
        )
        contactores.texto_alternativo = "Contactor de 9 A y 220 V"
        contactores.marca = ""
        contactores.marca_nueva_id = None
        contactores.save(
            using=alias,
            update_fields=(
                "nombre",
                "descripcion",
                "texto_alternativo",
                "marca",
                "marca_nueva",
            ),
        )
        for variante in Variante.objects.using(alias).filter(
            producto_id=contactores.pk,
            codigo__startswith="STF-CONT-",
        ):
            variante.codigo = variante.codigo.removeprefix("STF-")
            variante.save(using=alias, update_fields=("codigo",))
        Imagen.objects.using(alias).filter(producto_id=contactores.pk).update(
            texto_alternativo="Contactor de 220 V"
        )

    Categoria.objects.using(alias).filter(
        slug="casquetes-industriales"
    ).update(nombre="Enchufes industriales")
    Producto.objects.using(alias).filter(
        slug="catalogo-kalop-casquetes"
    ).update(
        nombre="Enchufes industriales",
        subtitulo="Enchufes industriales",
        descripcion=(
            "Enchufes industriales KALOP. Seleccione la cantidad de polos "
            "para solicitar una cotización."
        ),
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0034_catalogo_proyectores_led")]

    operations = [migrations.RunPython(ajustar_catalogo, migrations.RunPython.noop)]
