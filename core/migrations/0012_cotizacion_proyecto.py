import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_eliminar_variantes_plafones_led"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizacion",
            name="proyecto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cotizaciones",
                to="core.proyecto",
                verbose_name="Proyecto de referencia",
            ),
        ),
    ]
