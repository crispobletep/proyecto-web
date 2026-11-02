from django.db import migrations


def ajustar_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")

    # Simplificar los nombres visibles sin alterar las presentaciones existentes.
    for slug, nombre in (
        ("interruptores-automaticos-lexo-1p", "Interruptores automáticos 1P"),
        ("interruptores-automaticos-lexo-1p-n", "Interruptores automáticos 1P+N"),
        ("interruptores-automaticos-trifasicos-lexo-3p", "Interruptores automáticos trifásicos 3P"),
    ):
        Producto.objects.using(alias).filter(slug=slug).update(nombre=nombre, texto_alternativo=nombre)

    diferencial_2p = Producto.objects.using(alias).filter(slug="interruptores-diferenciales-lexo-2p").first()
    diferencial_4p = Producto.objects.using(alias).filter(slug="interruptores-diferenciales-lexo-4p").first()
    if diferencial_2p and diferencial_4p:
        Variante.objects.using(alias).filter(producto_id=diferencial_4p.pk).update(producto_id=diferencial_2p.pk)
        diferencial_2p.nombre = "Interruptores diferenciales"
        diferencial_2p.subtitulo = "Interruptores diferenciales"
        diferencial_2p.descripcion = (
            "Interruptores diferenciales LEXO con sensibilidad de 30 mA. "
            "Selecciona la cantidad de polos y corriente nominal disponibles."
        )
        diferencial_2p.texto_alternativo = "Interruptor diferencial"
        diferencial_2p.save(using=alias, update_fields=("nombre", "subtitulo", "descripcion", "texto_alternativo"))
        diferencial_4p.publicado = False
        diferencial_4p.save(using=alias, update_fields=("publicado",))


class Migration(migrations.Migration):
    dependencies = [("core", "0038_agregar_luminarias_catalogo")]
    operations = [migrations.RunPython(ajustar_catalogo, migrations.RunPython.noop)]
