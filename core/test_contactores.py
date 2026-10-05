import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from core.models import ImagenProducto, Producto


class ContactoresTests(TestCase):
    def test_carga_repetible_con_imagen_por_variante(self):
        with tempfile.TemporaryDirectory() as temporal:
            origen = Path(temporal) / "contactores"
            origen.mkdir()
            for a in (9, 12, 18, 25, 32):
                Image.new("RGB", (5, 5)).save(origen / f"contactor-{a}a-220v.png")
            with override_settings(MEDIA_ROOT=temporal):
                call_command("cargar_contactores_stanford", origen=origen)
                self.assertEqual(Producto.objects.count(), 0)
                for _ in range(2):
                    call_command("cargar_contactores_stanford", origen=origen, aplicar=True)
                producto = Producto.objects.get(slug="contactores-stanford-220v")
                self.assertTrue(producto.publicado)
                self.assertEqual(producto.variantes.count(), 5)
                self.assertEqual(ImagenProducto.objects.count(), 5)
                for a, variante in zip((9, 12, 18, 25, 32), producto.variantes.all()):
                    self.assertEqual(variante.especificaciones.get(nombre="Corriente nominal").valor, str(a))
                    self.assertEqual(variante.imagen.name, f"contactores/contactor-{a}a-220v.png")
                    self.assertEqual(variante.imagenes_catalogo.get().imagen.name, variante.imagen.name)
                respuesta = self.client.get("/productos/?categoria=contactores")
                self.assertContains(respuesta, producto.nombre)
                for a in (9, 12, 18, 25, 32):
                    self.assertContains(respuesta, f"{a} A · 220 V")
