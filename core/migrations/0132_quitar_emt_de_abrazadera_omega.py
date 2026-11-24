from django.db import migrations


def quitar_emt_de_abrazadera_omega(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Categoria = apps.get_model("core", "Categoria")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")

    Categoria.objects.using(alias).filter(
        slug="abrazaderas-omega-emt"
    ).update(nombre="Abrazaderas Omega")

    producto = Producto.objects.using(alias).filter(
        slug="abrazadera-omega-emt"
    ).first()
    if not producto:
        return

    producto.nombre = "Abrazadera tipo Omega"
    producto.subtitulo = "Accesorios de canalización"
    producto.descripcion = (
        "Abrazadera metálica tipo Omega para fijación de canalización. "
        "Disponible en varias medidas."
    )
    producto.texto_alternativo = "Abrazadera metálica tipo Omega para canalización"
    producto.etiqueta_visual = "ABRAZADERA OMEGA"
    producto.save(
        using=alias,
        update_fields=(
            "nombre",
            "subtitulo",
            "descripcion",
            "texto_alternativo",
            "etiqueta_visual",
        ),
    )

    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk
    ).update(texto="Abrazadera metálica tipo Omega para fijación de canalización.")
    Especificacion.objects.using(alias).filter(
        producto_id=producto.pk,
        nombre="Tipo",
    ).update(valor="Abrazadera Omega")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0131_corregir_capacidades_calotas_interior"),
    ]

    operations = [
        migrations.RunPython(
            quitar_emt_de_abrazadera_omega,
            migrations.RunPython.noop,
        ),
    ]
