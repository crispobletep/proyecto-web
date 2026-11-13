from django.db import migrations


IMAGE = "productos/catalogo/tableros-cnc/tableros-metalicos/tablero-metalico.webp"
POLOS = (18, 28, 36, 45, 54, 72, 100)


def agregar_tableros_metalicos(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    categoria = Categoria.objects.using(alias).get(slug="gabinetes-metalicos")

    for index, polos in enumerate(POLOS):
        slug = f"tablero-metalico-{polos}-polos"
        nombre = f"Tablero metálico de {polos} polos"
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=slug,
            defaults={
                "categoria_id": categoria.pk,
                "nombre": nombre,
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Tableros metálicos",
                "descripcion": (
                    f"Tablero metálico de distribución de {polos} polos, "
                    "disponible para instalación embutida o sobrepuesta."
                ),
                "imagen": IMAGE,
                "texto_alternativo": f"Imagen referencial de tablero metálico de {polos} polos",
                "etiqueta_visual": "TABLERO METÁLICO",
                "orden": 2090 + index * 10,
                "publicado": True,
            },
        )

        Especificacion.objects.using(alias).update_or_create(
            producto_id=product.pk,
            nombre="Cantidad de polos",
            defaults={"valor": str(polos), "unidad": "polos", "orden": 1},
        )

        for variant_order, montaje in enumerate(("Embutido", "Sobrepuesto"), start=1):
            variant, _ = Variante.objects.using(alias).update_or_create(
                producto_id=product.pk,
                nombre=montaje,
                defaults={"imagen": IMAGE, "disponible": True, "orden": variant_order},
            )
            EspecificacionVariante.objects.using(alias).update_or_create(
                variante_id=variant.pk,
                nombre="Tipo de montaje",
                defaults={"valor": montaje, "unidad": "", "orden": 1},
            )

        for feature_order, text in enumerate(
            (
                f"Capacidad: {polos} polos.",
                "Disponible para montaje embutido o sobrepuesto.",
            ),
            start=1,
        ):
            Caracteristica.objects.using(alias).update_or_create(
                producto_id=product.pk,
                orden=feature_order,
                defaults={"texto": text},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0087_bases_para_panel_led")]
    operations = [migrations.RunPython(agregar_tableros_metalicos, migrations.RunPython.noop)]
