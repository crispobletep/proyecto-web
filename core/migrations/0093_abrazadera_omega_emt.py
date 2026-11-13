from django.db import migrations


IMAGE = "productos/catalogo/canalizacion-electrica/abrazaderas-omega-emt/abrazadera-omega-emt.webp"
MEDIDAS = (16, 20, 25, 32, 40, 50, 63)


def agregar_abrazadera_omega_emt(apps, schema_editor):
    alias = schema_editor.connection.alias
    Categoria = apps.get_model("core", "Categoria")
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")

    familia = Categoria.objects.using(alias).get(slug="canalizacion-electrica")
    categoria, _ = Categoria.objects.using(alias).update_or_create(
        slug="abrazaderas-omega-emt",
        defaults={
            "nombre": "Abrazaderas Omega EMT",
            "padre_id": familia.pk,
            "orden": 15,
            "activa": True,
        },
    )
    producto, _ = Producto.objects.using(alias).update_or_create(
        slug="abrazadera-omega-emt",
        defaults={
            "categoria_id": categoria.pk,
            "nombre": "Abrazadera tipo Omega para EMT",
            "marca": "",
            "marca_nueva_id": None,
            "modelo": "",
            "codigo": None,
            "subtitulo": "Accesorios de canalización EMT",
            "descripcion": "Abrazadera metálica tipo Omega para fijación de canalización EMT. Disponible en varias medidas.",
            "imagen": IMAGE,
            "texto_alternativo": "Abrazadera metálica tipo Omega para canalización EMT",
            "etiqueta_visual": "ABRAZADERA OMEGA EMT",
            "orden": 900,
            "publicado": True,
        },
    )

    Especificacion.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        nombre="Tipo",
        defaults={"valor": "Abrazadera Omega EMT", "unidad": "", "orden": 1},
    )
    Caracteristica.objects.using(alias).update_or_create(
        producto_id=producto.pk,
        orden=1,
        defaults={"texto": "Abrazadera metálica tipo Omega para canalización EMT."},
    )

    for orden, medida in enumerate(MEDIDAS, start=1):
        nombre = f"{medida} mm"
        variante, _ = Variante.objects.using(alias).update_or_create(
            producto_id=producto.pk,
            nombre=nombre,
            defaults={"imagen": IMAGE, "disponible": True, "orden": orden},
        )
        EspecificacionVariante.objects.using(alias).update_or_create(
            variante_id=variante.pk,
            nombre="Medida",
            defaults={"valor": str(medida), "unidad": "mm", "orden": 1},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0092_agregar_selector_3p")]

    operations = [migrations.RunPython(agregar_abrazadera_omega_emt, migrations.RunPython.noop)]
