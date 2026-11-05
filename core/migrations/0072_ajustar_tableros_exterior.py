from django.db import migrations


AJUSTES = (
    (
        "tablero-exterior-cnc-ip65-4-polos",
        "tablero-exterior-cnc-ip65-5-polos",
        "CNC-TB-4P",
        "CNC-TB-5P",
        5,
    ),
    (
        "tablero-exterior-cnc-ip65-16-polos",
        "tablero-exterior-cnc-ip65-15-polos",
        "CNC-TB-16P",
        "CNC-TB-15P",
        15,
    ),
)


def actualizar_ficha(apps, alias, slug_anterior, slug_nuevo, codigo_anterior, codigo_nuevo, polos):
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Especificacion = apps.get_model("core", "EspecificacionProducto")
    EspecificacionVariante = apps.get_model("core", "EspecificacionVariante")

    Producto.objects.using(alias).filter(slug=slug_anterior).update(
        slug=slug_nuevo,
        nombre=f"Tablero exterior CNC IP65 {polos} polos",
        descripcion=(
            "Tablero eléctrico CNC para instalaciones exteriores, con "
            f"protección IP65. Capacidad: {polos} polos."
        ),
        texto_alternativo=f"Tablero eléctrico CNC IP65 de {polos} polos",
        codigo=codigo_nuevo,
    )
    Variante.objects.using(alias).filter(codigo=codigo_anterior).update(
        codigo=codigo_nuevo,
        nombre=f"{polos} polos",
    )
    Especificacion.objects.using(alias).filter(
        producto__slug=slug_nuevo,
        nombre="Polos",
    ).update(valor=str(polos))
    EspecificacionVariante.objects.using(alias).filter(
        variante__codigo=codigo_nuevo,
        nombre__in=("Capacidad", "Polos"),
    ).update(valor=str(polos))


def ajustar_tableros(apps, schema_editor):
    alias = schema_editor.connection.alias
    for slug_anterior, slug_nuevo, codigo_anterior, codigo_nuevo, polos in AJUSTES:
        actualizar_ficha(
            apps, alias, slug_anterior, slug_nuevo,
            codigo_anterior, codigo_nuevo, polos,
        )

    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Producto.objects.using(alias).filter(
        slug="tablero-exterior-cnc-ip65-6-polos"
    ).update(publicado=False)
    Variante.objects.using(alias).filter(codigo="CNC-TB-6P").update(disponible=False)


def revertir_ajustes(apps, schema_editor):
    alias = schema_editor.connection.alias
    for ajuste, polos_anterior in zip(AJUSTES, (4, 16)):
        slug_anterior, slug_nuevo, codigo_anterior, codigo_nuevo, _ = ajuste
        actualizar_ficha(
            apps, alias, slug_nuevo, slug_anterior,
            codigo_nuevo, codigo_anterior, polos_anterior,
        )

    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Producto.objects.using(alias).filter(
        slug="tablero-exterior-cnc-ip65-6-polos"
    ).update(publicado=True)
    Variante.objects.using(alias).filter(codigo="CNC-TB-6P").update(disponible=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0071_ordenar_proyectores_por_temperatura_y_potencia"),
    ]

    operations = [
        migrations.RunPython(ajustar_tableros, revertir_ajustes),
    ]
