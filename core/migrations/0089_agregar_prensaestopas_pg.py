from django.db import migrations


IMAGE = "productos/catalogo/canalizacion-electrica/prensaestopas/prensaestopa-negra.png"
SIZES = ("PG7", "PG9", "PG11", "PG13,5", "PG16", "PG21", "PG26")


def agregar_prensaestopas(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="canalizacion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="prensaestopas",
        defaults={
            "nombre": "Prensaestopas",
            "padre_id": familia.pk,
            "orden": 12,
            "activa": True,
        },
    )
    base_order = max(Producto.objects.using(alias).values_list("orden", flat=True)) + 10

    for index, size in enumerate(SIZES):
        slug_size = size.lower().replace(",", "-")
        product, _ = Producto.objects.using(alias).update_or_create(
            slug=f"prensaestopa-{slug_size}",
            defaults={
                "categoria_id": categoria.pk,
                "nombre": f"Prensaestopa {size}",
                "marca": "",
                "marca_nueva_id": None,
                "modelo": "",
                "codigo": None,
                "subtitulo": "Prensaestopas",
                "descripcion": f"Prensaestopa con rosca PG {size.removeprefix('PG')}.",
                "imagen": IMAGE,
                "texto_alternativo": f"Imagen referencial de prensaestopa negra {size}",
                "etiqueta_visual": "PRENSAESTOPA",
                "orden": base_order + index * 10,
                "publicado": True,
            },
        )

        Especificacion.objects.using(alias).update_or_create(
            producto_id=product.pk,
            nombre="Rosca",
            defaults={"valor": size, "unidad": "", "orden": 1},
        )
        Caracteristica.objects.using(alias).update_or_create(
            producto_id=product.pk,
            orden=1,
            defaults={"texto": f"Tamaño de rosca: {size}."},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0088_tableros_metalicos_por_polos")]
    operations = [migrations.RunPython(agregar_prensaestopas, migrations.RunPython.noop)]
