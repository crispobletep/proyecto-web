from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Cotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('empresa', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('telefono', models.CharField(max_length=30)),
                ('servicio', models.CharField(max_length=100)),
                ('mensaje', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Cotización', 'verbose_name_plural': 'Cotizaciones', 'ordering': ['-fecha']},
        ),
    ]
