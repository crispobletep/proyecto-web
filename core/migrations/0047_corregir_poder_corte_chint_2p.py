from django.db import migrations


VARIANTES = (
    ("2P · 16 A · curva D · 10 kA", "2P · 16 A · curva D · 6 kA"),
    ("2P · 20 A · curva C · 10 kA", "2P · 20 A · curva C · 6 kA"),
    ("2P · 25 A · curva C · 10 kA", "2P · 25 A · curva C · 6 kA"),
    ("2P · 32 A · curva C · 10 kA", "2P · 32 A · curva C · 6 kA"),
    ("2P · 50 A · curva C · 10 kA", "2P · 50 A · curva C · 6 kA"),
    ("2P · 63 A · curva C · 10 kA", "2P · 63 A · curva C · 6 kA"),
)


def corregir(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    producto = Producto.objects.using(alias).filter(
        slug="interruptores-automaticos-2p-curva-c"
    ).first()
    if not producto:
        return

    for anterior, nuevo in VARIANTES:
        Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            nombre=anterior,
        ).update(nombre=nuevo)
    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk,
        texto="Montaje modular en riel DIN.",
    ).update(texto="Poder de corte de 6 kA en todas las variantes.")


def revertir(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Caracteristica = apps.get_model("core", "CaracteristicaProducto")
    producto = Producto.objects.using(alias).filter(
        slug="interruptores-automaticos-2p-curva-c"
    ).first()
    if not producto:
        return

    for anterior, nuevo in VARIANTES:
        Variante.objects.using(alias).filter(
            producto_id=producto.pk,
            nombre=nuevo,
        ).update(nombre=anterior)
    Caracteristica.objects.using(alias).filter(
        producto_id=producto.pk,
        texto="Poder de corte de 6 kA en todas las variantes.",
    ).update(texto="Montaje modular en riel DIN.")


class Migration(migrations.Migration):
    dependencies = [("core", "0046_agregar_marca_bright")]

    operations = [migrations.RunPython(corregir, revertir)]
