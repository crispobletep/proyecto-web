import csv
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Cotizacion, ImagenProducto, Producto, VarianteProducto


class CargarCatalogoManifiestoTests(TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.media = self.raiz / "media"
        self.origen = self.raiz / "extraidos"
        self.origen.mkdir(parents=True)
        self.ajuste_media = override_settings(MEDIA_ROOT=self.media)
        self.ajuste_media.enable()

    def tearDown(self):
        self.ajuste_media.disable()
        self.temporal.cleanup()

    def crear_manifiesto(self):
        filas = (
            {
                "familia": "tableros-cnc",
                "titulo": "Tablero exterior CNC IP65 cerrado",
                "archivo": "tableros-cnc/cerrado.png",
                "codigos": "CNC-TB-2P | CNC-TB-4P",
                "uso": "principal",
                "lamina_fuente": "catalogo.png",
            },
            {
                "familia": "tableros-cnc",
                "titulo": "Tablero exterior CNC IP65 abierto",
                "archivo": "tableros-cnc/abierto.png",
                "codigos": "CNC-TB-2P | CNC-TB-4P",
                "uso": "adicional",
                "lamina_fuente": "catalogo.png",
            },
        )

        for fila in filas:
            ruta = self.origen / fila["archivo"]
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(b"imagen-de-prueba")

        manifiesto = self.origen / "manifesto_imagenes.csv"
        with manifiesto.open("w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=filas[0].keys())
            escritor.writeheader()
            escritor.writerows(filas)
        return manifiesto

    def test_validacion_no_modifica_la_base(self):
        manifiesto = self.crear_manifiesto()

        call_command("cargar_catalogo_manifiesto", manifiesto=manifiesto)

        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(VarianteProducto.objects.count(), 0)
        self.assertEqual(ImagenProducto.objects.count(), 0)

    def test_importacion_es_idempotente_y_conserva_relaciones_multiples(self):
        manifiesto = self.crear_manifiesto()

        for _ in range(2):
            call_command(
                "cargar_catalogo_manifiesto",
                manifiesto=manifiesto,
                aplicar=True,
            )

        producto = Producto.objects.get(slug="catalogo-tableros-cnc")
        self.assertFalse(producto.publicado)
        self.assertEqual(producto.variantes.count(), 2)
        self.assertEqual(producto.imagenes_catalogo.count(), 2)
        self.assertEqual(
            sum(
                imagen.variantes.count()
                for imagen in producto.imagenes_catalogo.all()
            ),
            4,
        )
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(VarianteProducto.objects.count(), 2)
        self.assertEqual(ImagenProducto.objects.count(), 2)


class CargarPilotosYLegrandTests(TestCase):
    nombres_imagenes = (
        "Piloto LED Voltimetro Y Amperimetro 22mm.png",
        "Piloto Voltimetro Led 22mm.png",
        "Luz Piloto Led 220V  AMARILLA.png",
        "Luz Piloto Led 220V roja.png",
        "Luz Piloto Led 220V Verde.png",
        "Piloto Led a riel Din 230VAC 50Hz CNC.png",
        "Luz Piloto Led A Riel Din Slim roja.png",
        "Luz Piloto Led A Riel Din Slim amarilla.png",
        "Luz Piloto Led A Riel Din Slim verde.png",
        "LUZ PILOTO ROJA RIEL DIN.png",
        "INTERRUPTOR AUT. RX3 1P 40A 6KA C LEGRAND.png",
        "INTERRUPTOR AUT. RX3 1P 32A 6KA C LEGRAND.png",
        "INTERRUPTOR AUT 25A 6KA C LEGRAND.png",
        "INTERRUPTOR AUT. RX3 1P 20A 6KA C LEGRAND.png",
        "INTERRUPTOR AUT 16A 6KA C LEGRAND.png",
        "INTERRUPTOR AUT 10A 6KA C LEGRAND.png",
    )

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.media = self.raiz / "media"
        self.origen = self.raiz / "origen"
        self.origen.mkdir()
        for nombre in self.nombres_imagenes:
            (self.origen / nombre).write_bytes(b"imagen-de-prueba")
        self.ajuste_media = override_settings(MEDIA_ROOT=self.media)
        self.ajuste_media.enable()

    def tearDown(self):
        self.ajuste_media.disable()
        self.temporal.cleanup()

    def test_importacion_publica_y_agrupa_variantes_sin_duplicar(self):
        for _ in range(2):
            call_command(
                "cargar_pilotos_y_legrand",
                origen=self.origen,
                aplicar=True,
            )

        self.assertEqual(Producto.objects.count(), 7)
        self.assertEqual(Producto.objects.filter(publicado=True).count(), 7)
        self.assertEqual(VarianteProducto.objects.count(), 12)
        self.assertEqual(ImagenProducto.objects.count(), 16)

        pilotos = Producto.objects.get(slug="luces-piloto-led-220v-22mm")
        self.assertEqual(pilotos.variantes.count(), 3)
        self.assertEqual(pilotos.imagenes_catalogo.count(), 3)

        legrand = Producto.objects.get(
            slug="interruptores-magnetotermicos-legrand-rx3-1p"
        )
        self.assertEqual(legrand.variantes.count(), 6)
        self.assertEqual(
            set(legrand.variantes.values_list("codigo", flat=True)),
            {"419838", "419840", "419841", "419842", "419843", "419844"},
        )

        pilotos_slim = Producto.objects.get(
            slug="luces-piloto-led-riel-din-slim-cnc-ycd9-1"
        )
        self.assertEqual(pilotos_slim.variantes.count(), 3)
        self.assertEqual(pilotos_slim.imagenes_catalogo.count(), 3)
        self.assertEqual(
            set(pilotos_slim.variantes.values_list("nombre", flat=True)),
            {
                "Luz Piloto Led A Riel Din Slim roja",
                "Luz Piloto Led A Riel Din Slim amarilla",
                "Luz Piloto Led A Riel Din Slim verde",
            },
        )

        respuesta = self.client.get("/productos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            "Piloto LED voltímetro y amperímetro 22 mm",
        )
        self.assertContains(
            respuesta,
            "Interruptores magnetotérmicos Legrand RX³ 1P",
        )
        self.assertContains(
            respuesta,
            "Luz Piloto Led A Riel Din Slim amarilla",
        )
        self.assertContains(respuesta, "419844")

    def test_imagen_manual_genera_clave_tecnica(self):
        call_command(
            "cargar_pilotos_y_legrand",
            origen=self.origen,
            aplicar=True,
        )
        producto = Producto.objects.first()
        imagen = ImagenProducto.objects.create(
            producto=producto,
            imagen="productos/catalogo/manual.png",
            texto_alternativo="Imagen manual",
        )

        self.assertTrue(imagen.clave.startswith("manual-"))


class SitioPublicoTests(TestCase):
    def test_paginas_principales_renderizan_con_datos_reales(self):
        for ruta in (
            "/",
            "/productos/",
            "/empresa/",
            "/servicios/",
            "/proyectos/",
            "/contacto/",
        ):
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200)

        respuesta = self.client.get("/contacto/")
        self.assertContains(respuesta, "+56 2 2983 688")
        self.assertContains(respuesta, "administracion@phinstalaciones.cl")
        self.assertContains(respuesta, "San Diego 1325")
        self.assertContains(respuesta, "76.096.219-5")

        servicios = self.client.get("/servicios/")
        self.assertNotContains(servicios, "Próximamente")
        self.assertContains(servicios, "Mantención eléctrica")

        proyectos = self.client.get("/proyectos/")
        self.assertNotContains(proyectos, 'href="#"')
        self.assertNotContains(proyectos, "proyectos demostrativos")
        self.assertContains(proyectos, "data-project-filter")

    def test_formulario_valida_y_registra_cotizacion(self):
        datos = {
            "nombre": "Cliente de prueba",
            "empresa": "Empresa de prueba",
            "email": "cliente@example.com",
            "telefono": "+56 9 1234 5678",
            "servicio": "Instalación eléctrica",
            "mensaje": "Necesito evaluar una instalación eléctrica.",
        }
        respuesta = self.client.post("/contacto/", datos)

        self.assertRedirects(respuesta, "/contacto/?enviado=1")
        self.assertEqual(Cotizacion.objects.count(), 1)

        datos["telefono"] = "12"
        respuesta = self.client.post("/contacto/", datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ingresa un teléfono válido")
        self.assertEqual(Cotizacion.objects.count(), 1)
