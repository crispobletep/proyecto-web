from django.db import migrations


FICHAS = (
    {
        "slug": "modulo-tomacorriente-stanford-10a",
        "nombre": "Módulo tomacorriente Stanford 10 A",
        "modelo": "10 A",
        "clave": "stanford-modulo-tomacorriente-10a",
        "imagenes": {
            "Blanco": "productos/catalogo/staford-enchufes/staford-modulo-simple-10a-blanco.png",
            "Negro": "productos/catalogo/staford-enchufes/staford-modulo-simple-10a-negro.png",
        },
    },
    {
        "slug": "modulo-tomacorriente-stanford-10-16a",
        "nombre": "Módulo tomacorriente Stanford 10/16 A",
        "modelo": "10/16 A",
        "clave": "stanford-modulo-tomacorriente-10-16a",
        "imagenes": {
            "Blanco": "productos/catalogo/staford-enchufes/staford-modulo-simple-10-16a-blanco.png",
            "Negro": "productos/catalogo/staford-enchufes/staford-modulo-simple-10-16a-negro.png",
        },
    },
)

FICHAS_ENCHUFE_MODULAR_ANTERIORES = {
    "catalogo-staford-enchufesstf-es-10a": 379,
    "catalogo-staford-enchufesstf-es-1016": 409,
}


def crear_fichas_tomacorriente(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")
    Categoria = apps.get_model("core", "Categoria")
    Marca = apps.get_model("core", "Marca")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    categoria = Categoria.objects.using(alias).filter(slug="modulos-electricos").first()
    marca = Marca.objects.using(alias).filter(slug="stanford").first()
    if not categoria or not marca:
        raise RuntimeError("Se necesita la categoría Módulos eléctricos y la marca Stanford.")

    categoria.activa = True
    categoria.save(using=alias, update_fields=("activa",))

    for ficha in FICHAS:
        producto, _ = Producto.objects.using(alias).update_or_create(
            slug=ficha["slug"],
            defaults={
                "categoria_id": categoria.pk,
                "nombre": ficha["nombre"],
                "marca": "",
                "marca_nueva_id": marca.pk,
                "modelo": ficha["modelo"],
                "codigo": None,
                "subtitulo": categoria.nombre,
                "descripcion": (
                    f"{ficha['nombre']}. Módulo tomacorriente de la línea Stanford. "
                    "Seleccione el color disponible para solicitar cotización."
                ),
                "imagen": ficha["imagenes"]["Blanco"],
                "texto_alternativo": ficha["nombre"],
                "etiqueta_visual": "MÓDULOS STANFORD",
                "orden": 69,
                "publicado": True,
            },
        )

        for orden, (color, ruta) in enumerate(ficha["imagenes"].items(), start=1):
            variante, _ = Variante.objects.using(alias).get_or_create(
                producto_id=producto.pk,
                nombre=color,
                defaults={
                    "codigo": None,
                    "modelo": "",
                    "imagen": ruta,
                    "disponible": True,
                    "orden": orden,
                },
            )
            variante.codigo = None
            variante.imagen = ruta
            variante.disponible = True
            variante.orden = orden
            variante.save(
                using=alias,
                update_fields=("codigo", "imagen", "disponible", "orden"),
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variante.pk,
                nombre="Color",
                defaults={"valor": color, "unidad": "", "orden": 1},
            )

            imagen, _ = Imagen.objects.using(alias).update_or_create(
                clave=f"{ficha['clave']}-{color.casefold()}",
                defaults={
                    "producto_id": producto.pk,
                    "imagen": ruta,
                    "texto_alternativo": f"{ficha['nombre']}, color {color}",
                    "orden": orden,
                },
            )
            imagen.variantes.set([variante.pk])

        Especificacion.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre="Tipo de módulo",
            defaults={"valor": ficha["modelo"], "unidad": "", "orden": 1},
        )
        for orden, texto in enumerate(
            (
                "Módulo tomacorriente de la línea Stanford",
                "Disponible en blanco y negro",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=producto.pk,
                texto=texto,
                defaults={"orden": orden},
            )

    # Estos mecanismos de enchufe son los productos modulares que se retiraron;
    # las nuevas fichas de tomacorriente pertenecen a Módulos eléctricos.
    for slug, orden in FICHAS_ENCHUFE_MODULAR_ANTERIORES.items():
        Producto.objects.using(alias).filter(slug=slug).update(
            publicado=False,
            orden=orden,
        )

    categoria_enchufes = Categoria.objects.using(alias).filter(
        slug="enchufes-verticales"
    ).first()
    if categoria_enchufes and not Producto.objects.using(alias).filter(
        categoria_id=categoria_enchufes.pk,
        publicado=True,
    ).exists():
        categoria_enchufes.activa = False
        categoria_enchufes.save(using=alias, update_fields=("activa",))


def revertir_fichas_tomacorriente(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Categoria = apps.get_model("core", "Categoria")

    Producto.objects.using(alias).filter(
        slug__in=[ficha["slug"] for ficha in FICHAS]
    ).delete()

    for slug in FICHAS_ENCHUFE_MODULAR_ANTERIORES:
        Producto.objects.using(alias).filter(slug=slug).update(
            publicado=True,
            orden=69,
        )
    categoria = Categoria.objects.using(alias).filter(
        slug="enchufes-verticales"
    ).first()
    if categoria:
        categoria.activa = True
        categoria.save(using=alias, update_fields=("activa",))


class Migration(migrations.Migration):
    dependencies = [("core", "0030_priorizar_modulos_simples_en_catalogo")]

    operations = [
        migrations.RunPython(crear_fichas_tomacorriente, revertir_fichas_tomacorriente),
    ]
