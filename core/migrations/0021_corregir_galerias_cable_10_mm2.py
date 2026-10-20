from django.db import migrations


def corregir_galerias(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Imagen = apps.get_model("core", "ImagenProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    producto_6 = Producto.objects.using(alias).filter(
        slug="cable-flexible-libre-halogenos-6mm2"
    ).first()
    producto_10 = Producto.objects.using(alias).filter(
        slug="cable-flexible-libre-halogenos-10mm2"
    ).first()
    if not producto_6 or not producto_10:
        return

    variantes_6 = list(producto_6.variantes.all())
    ids_6 = {variante.pk for variante in variantes_6}
    for imagen in Imagen.objects.using(alias).filter(
        clave__startswith="carga-conductores-conexiones-cable-6-"
    ):
        vinculadas = list(imagen.variantes.all())
        secciones = {
            EspecificacionVariante.objects.using(alias).filter(
                variante_id=variante.pk, nombre="Sección"
            ).values_list("valor", flat=True).first()
            for variante in vinculadas
        }
        if "6" in secciones:
            imagen.producto_id = producto_6.pk
            imagen.save(using=alias, update_fields=["producto"])
            imagen.variantes.set([variante for variante in vinculadas if variante.pk in ids_6])

    rojo_10 = producto_10.variantes.filter(nombre__iexact="Rojo").first()
    if rojo_10:
        producto_10.imagen = rojo_10.imagen.name
        producto_10.texto_alternativo = "Cable flexible libre de halógenos de 10 mm², color rojo"
        producto_10.save(using=alias, update_fields=["imagen", "texto_alternativo"])


class Migration(migrations.Migration):
    dependencies = [("core", "0020_imagen_cable_10_mm2")]

    operations = [migrations.RunPython(corregir_galerias, migrations.RunPython.noop)]
