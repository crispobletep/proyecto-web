from django.db import migrations


IMAGE = "productos/catalogo/canalizacion-electrica/abrazaderas-eclipsables/abrazadera-eclipsable-20-25.jpg"


def agregar_abrazadera_eclipsable(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="canalizacion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="abrazaderas-eclipsables",
        defaults={
            "nombre": "Abrazaderas eclipsables",
            "padre_id": familia.pk,
            "orden": 16,
            "activa": True,
        },
    )
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="abrazadera-eclipsable-20-25-mm",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Abrazadera eclipsable 20–25 mm",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Accesorios de canalización",
            "descripcion": "Abrazadera eclipsable para sujeción de canalización, compatible con medidas de 20 a 25 mm.",
            "imagen": IMAGE,
            "texto_alternativo": "Abrazadera eclipsable negra para medidas de 20 a 25 mm",
            "etiqueta_visual": "ABRAZADERA ECLIPSABLE",
            "orden": 910,
            "publicado": True,
        },
    )
    Especificacion.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        nombre="Medida compatible",
        defaults={"valor": "20–25", "unidad": "mm", "orden": 1},
    )
    Caracteristica.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        orden=1,
        defaults={"texto": "Una unidad con rango de medida compatible de 20 a 25 mm."},
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0093_abrazadera_omega_emt")]

    operations = [migrations.RunPython(agregar_abrazadera_eclipsable, migrations.RunPython.noop)]
