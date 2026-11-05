from django.db import migrations


CAMBIOS = {
    "interruptores-automaticos-2p-curva-c": {
        "descripcion": (
            "Interruptores automáticos CHINT de 2 polos. Selecciona la "
            "corriente nominal, curva y poder de corte disponibles."
        ),
        "texto_alternativo": "Interruptor automático CHINT de 2 polos",
    },
    "interruptores-automaticos-4p-curva-c": {
        "descripcion": (
            "Interruptores automáticos CHINT de cuatro polos con curva C "
            "y poder de corte de 10 kA. Selecciona la corriente nominal disponible."
        ),
        "texto_alternativo": "Interruptor automático CHINT de 4 polos",
    },
}


def corregir_marca(apps, schema_editor):
    alias = schema_editor.connection.alias
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    chint = Marca.objects.using(alias).get(slug="chint")

    for slug, valores in CAMBIOS.items():
        Producto.objects.using(alias).filter(slug=slug).update(
            marca="",
            marca_nueva_id=chint.pk,
            etiqueta_visual="CHINT",
            **valores,
        )


def revertir_marca(apps, schema_editor):
    alias = schema_editor.connection.alias
    Marca = apps.get_model("core", "Marca")
    Producto = apps.get_model("core", "Producto")
    lexo = Marca.objects.using(alias).get(slug="lexo")
    anteriores = {
        "interruptores-automaticos-2p-curva-c": {
            "descripcion": (
                "Interruptores automáticos LEXO de 2 polos. Selecciona la "
                "corriente nominal, curva y capacidad de ruptura disponibles."
            ),
            "texto_alternativo": "Interruptor automático 2P",
        },
        "interruptores-automaticos-4p-curva-c": {
            "descripcion": (
                "Interruptores automáticos modulares con curva C. Selecciona "
                "polos, corriente nominal y capacidad de ruptura disponibles."
            ),
            "texto_alternativo": "Interruptores automáticos 4P",
        },
    }
    for slug, valores in anteriores.items():
        Producto.objects.using(alias).filter(slug=slug).update(
            marca="",
            marca_nueva_id=lexo.pk,
            etiqueta_visual="LEXO",
            **valores,
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0044_actualizar_imagenes_tableros_y_cables")]

    operations = [migrations.RunPython(corregir_marca, revertir_marca)]
