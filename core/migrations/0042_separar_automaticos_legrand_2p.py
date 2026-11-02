from django.db import migrations


LEGRAND_VARIANTES = (
    "2P · 10 A · curva C · 6 kA",
    "2P · 16 A · curva C · 6 kA",
    "2P · 20 A · curva C · 6 kA",
    "2P · 25 A · curva C · 6 kA",
    "2P · 32 A · curva C · 6 kA",
    "2P · 40 A · curva C · 6 kA",
    "2P · 50 A · curva C · 6 kA",
    "2P · 63 A · curva C · 6 kA",
)


def separar_legrand(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Marca = apps.get_model("core", "Marca")

    lexo = Marca.objects.using(alias).filter(nombre__iexact="LEXO").first()
    legrand = Marca.objects.using(alias).filter(nombre__iexact="Legrand").first()
    original = Producto.objects.using(alias).filter(slug="interruptores-automaticos-2p-curva-c").first()
    if not original or not legrand:
        return

    base_imagen = "productos/catalogo/protecciones/nuevos/interruptor-autom-tico-mcb-2p-10a-curva-c-6ka.png"
    nuevo, _ = Producto.objects.using(alias).update_or_create(
        slug="interruptores-automaticos-2p-legrand",
        defaults={
            "categoria_id": original.categoria_id,
            "nombre": "Interruptores automáticos 2P",
            "marca": "",
            "marca_nueva_id": legrand.pk,
            "subtitulo": "Interruptores automáticos",
            "descripcion": "Interruptores automáticos Legrand de 2 polos, curva C y capacidad de ruptura de 6 kA. Selecciona la corriente nominal.",
            "imagen": base_imagen,
            "texto_alternativo": "Interruptor automático Legrand 2P",
            "etiqueta_visual": "LEGRAND",
            "publicado": True,
        },
    )

    Variante.objects.using(alias).filter(
        producto_id=original.pk,
        nombre__in=LEGRAND_VARIANTES,
    ).update(producto_id=nuevo.pk)

    # Las alternativas restantes usan las imágenes suministradas para LEXO.
    variantes_lexo = Variante.objects.using(alias).filter(producto_id=original.pk)
    variantes_lexo.filter(nombre="2P · 10 A · curva C · 6 kA · alternativa").update(
        nombre="2P · 10 A · curva C · 6 kA"
    )
    variantes_lexo.filter(nombre="2P · 40 A · curva C · 6 kA · alternativa").update(
        nombre="2P · 40 A · curva C · 6 kA"
    )
    original.imagen = "productos/catalogo/protecciones/nuevos/interruptor-autom-tico-mcb-2p-10a-curva-c-6ka-chint.png"
    original.descripcion = "Interruptores automáticos LEXO de 2 polos. Selecciona la corriente nominal, curva y capacidad de ruptura disponibles."
    original.texto_alternativo = "Interruptor automático 2P"
    original.save(using=alias, update_fields=("imagen", "descripcion", "texto_alternativo"))


class Migration(migrations.Migration):
    dependencies = [("core", "0041_agregar_instrumentos_y_automaticos")]
    operations = [migrations.RunPython(separar_legrand, migrations.RunPython.noop)]
