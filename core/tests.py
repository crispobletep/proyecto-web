import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings

from core.management.commands.cargar_iluminacion_y_cajas import (
    IMAGENES as IMAGENES_ILUMINACION_Y_CAJAS,
)
from core.management.commands.cargar_ferrules_y_cintas import (
    IMAGENES as IMAGENES_FERRULES_Y_CINTAS,
)

from .models import (
    Categoria,
    Cotizacion,
    ImagenProducto,
    Producto,
    Proyecto,
    VarianteProducto,
)


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

    def crear_manifiesto_plafones(self):
        filas = (
            {
                "familia": "plafones-led",
                "titulo": "AVC 60 x 60 cm embutido",
                "archivo": "plafones-led/avc-6060-emb.png",
                "codigos": "AVC-6060-6E | AVC-6060-12E",
                "uso": "principal",
                "lamina_fuente": "catalogo.png",
            },
            {
                "familia": "plafones-led",
                "titulo": "AVC 60 x 60 cm sobrepuesto",
                "archivo": "plafones-led/avc-6060-sp.png",
                "codigos": "AVC-6060-6S | AVC-6060-12S",
                "uso": "principal",
                "lamina_fuente": "catalogo.png",
            },
        )

        for fila in filas:
            ruta = self.origen / fila["archivo"]
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(b"imagen-de-prueba")

        manifiesto = self.origen / "manifesto_plafones.csv"
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

    def test_plafones_embutidos_y_sobrepuestos_no_crean_variantes(self):
        manifiesto = self.crear_manifiesto_plafones()

        call_command(
            "cargar_catalogo_manifiesto",
            manifiesto=manifiesto,
            aplicar=True,
            publicar=True,
        )
        producto = Producto.objects.get(nombre="AVC 60 x 60 cm embutido")
        VarianteProducto.objects.create(
            producto=producto,
            nombre="Variante obsoleta",
            codigo="AVC-OBSOLETA",
        )

        call_command(
            "cargar_catalogo_manifiesto",
            manifiesto=manifiesto,
            aplicar=True,
            publicar=True,
        )

        plafones = Producto.objects.filter(categoria__slug="plafones-led")
        self.assertEqual(plafones.count(), 2)
        self.assertFalse(
            VarianteProducto.objects.filter(producto__in=plafones).exists()
        )
        self.assertFalse(
            ImagenProducto.objects.filter(
                producto__in=plafones,
                variantes__isnull=False,
            ).exists()
        )


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


class CargarFerrulesYCintasTests(TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.media = self.raiz / "media"
        self.origen = self.raiz / "origen"
        self.origen.mkdir()
        for datos in IMAGENES_FERRULES_Y_CINTAS.values():
            (self.origen / datos["origen"]).write_bytes(b"imagen-de-prueba")
        self.ajuste_media = override_settings(MEDIA_ROOT=self.media)
        self.ajuste_media.enable()

    def tearDown(self):
        self.ajuste_media.disable()
        self.temporal.cleanup()

    def test_validacion_no_modifica_el_catalogo(self):
        call_command("cargar_ferrules_y_cintas", origen=self.origen)

        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(VarianteProducto.objects.count(), 0)
        self.assertEqual(ImagenProducto.objects.count(), 0)

    def test_carga_publica_fichas_variantes_e_imagenes_sin_duplicar(self):
        for _ in range(2):
            call_command(
                "cargar_ferrules_y_cintas",
                origen=self.origen,
                aplicar=True,
            )

        self.assertEqual(Producto.objects.count(), 5)
        self.assertEqual(Producto.objects.filter(publicado=True).count(), 5)
        self.assertEqual(VarianteProducto.objects.count(), 9)
        self.assertEqual(ImagenProducto.objects.count(), 12)

        ferrules = Producto.objects.get(
            slug="ferrules-aislados-1-5-a-10-mm2"
        )
        self.assertEqual(ferrules.variantes.count(), 5)
        self.assertEqual(ferrules.imagenes_catalogo.count(), 5)
        self.assertEqual(
            set(ferrules.variantes.values_list("nombre", flat=True)),
            {
                "1,5 mm² · 16 AWG · Azul",
                "2,5 mm² · 14 AWG · Gris",
                "4 mm² · 12 AWG · Naranjo",
                "6 mm² · 10 AWG · Verde",
                "10 mm² · 8 AWG · Café",
            },
        )

        lexo = Producto.objects.get(
            slug="cinta-aislante-vinilica-lexo-19mm-20m"
        )
        self.assertEqual(lexo.variantes.count(), 4)
        self.assertEqual(lexo.imagenes_catalogo.count(), 4)
        self.assertEqual(
            set(lexo.variantes.values_list("nombre", flat=True)),
            {"Azul", "Verde", "Blanca", "Roja"},
        )

        temflex = Producto.objects.get(
            slug="cinta-aislante-3m-temflex-165-negra"
        )
        self.assertEqual(temflex.codigo, "165BK4A")
        self.assertEqual(
            temflex.especificaciones.get(nombre="Espesor nominal").valor,
            "0,15",
        )

        respuesta = self.client.get("/productos/?familia=conexion-y-aislacion")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ferrules aislados de 1,5 a 10 mm²")
        self.assertContains(respuesta, "Cinta aislante vinílica LEXO")
        self.assertContains(respuesta, "Cinta de goma autofundente FSL")
        self.assertContains(respuesta, "165BK4A")


class CargarIluminacionYCajasTests(TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.media = self.raiz / "media"
        self.origen = self.raiz / "origen"
        self.origen.mkdir()
        for datos in IMAGENES_ILUMINACION_Y_CAJAS.values():
            (self.origen / datos["origen"]).write_bytes(b"imagen-de-prueba")
        self.ajuste_media = override_settings(MEDIA_ROOT=self.media)
        self.ajuste_media.enable()

    def tearDown(self):
        self.ajuste_media.disable()
        self.temporal.cleanup()

    def test_validacion_no_modifica_el_catalogo(self):
        call_command("cargar_iluminacion_y_cajas", origen=self.origen)

        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(VarianteProducto.objects.count(), 0)
        self.assertEqual(ImagenProducto.objects.count(), 0)

    def test_carga_publica_productos_variantes_e_imagenes_sin_duplicar(self):
        for _ in range(2):
            call_command(
                "cargar_iluminacion_y_cajas",
                origen=self.origen,
                aplicar=True,
            )

        self.assertEqual(Producto.objects.count(), 9)
        self.assertEqual(Producto.objects.filter(publicado=True).count(), 9)
        self.assertEqual(VarianteProducto.objects.count(), 19)
        self.assertEqual(ImagenProducto.objects.count(), 24)

        plafon = Producto.objects.get(
            slug="plafon-led-sobrepuesto-fsl-6500k"
        )
        self.assertEqual(plafon.variantes.count(), 0)

        fsl_embutido = Producto.objects.get(slug="panel-led-embutido-fsl")
        self.assertEqual(fsl_embutido.variantes.count(), 0)

        avc_sobrepuesto = Producto.objects.get(
            slug="panel-led-sobrepuesto-avc-6500k"
        )
        self.assertEqual(avc_sobrepuesto.variantes.count(), 0)

        plafones = Producto.objects.filter(categoria__slug="plafones-led")
        self.assertFalse(
            VarianteProducto.objects.filter(producto__in=plafones).exists()
        )

        gabinetes = Producto.objects.get(
            slug="gabinetes-metalicos-una-puerta"
        )
        self.assertEqual(gabinetes.variantes.count(), 8)
        self.assertEqual(
            gabinetes.variantes.filter(nombre__icontains="con chasis").count(),
            3,
        )
        for variante in gabinetes.variantes.filter(
            nombre__icontains="con chasis"
        ):
            self.assertIn("con-chasis", variante.imagen.name)

        respuesta = self.client.get("/productos/?familia=tableros-electricos")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Gabinetes metálicos de una puerta")
        self.assertContains(respuesta, "Cajas estancas de derivación")
        self.assertContains(respuesta, "Caja Chuqui de superficie")
        self.assertContains(respuesta, "GAB-MET-600-400-200-IP65-CH")

        iluminacion = self.client.get("/productos/?familia=iluminacion")
        self.assertEqual(iluminacion.status_code, 200)
        self.assertContains(iluminacion, "Panel LED embutido FSL")
        self.assertContains(iluminacion, "Panel LED sobrepuesto AVC 6500 K")
        self.assertNotContains(iluminacion, "FSL-PL-E-24W")
        self.assertNotContains(iluminacion, "AVC-PL-S-18W-6500K")
        self.assertContains(iluminacion, "Cotizar este producto", count=4)


class CargarProyectosInicialesTests(TestCase):
    nombres_imagenes = (
        "fueron dos torres en mirador azul.jpeg",
        "Remodelación Edificio A, Hospital del trabajador.jpeg",
    )
    imagenes_incluidas = (
        "edificio-el-estero.png",
        "edificio-froilan-lagos.jpg",
        "edificio-martin-de-zamora.jpg",
    )

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.media = self.raiz / "media"
        self.origen = self.raiz / "origen"
        self.origen.mkdir()
        (self.media / "proyectos").mkdir(parents=True)
        for nombre in self.nombres_imagenes:
            (self.origen / nombre).write_bytes(b"imagen-de-prueba")
        for nombre in self.imagenes_incluidas:
            (self.media / "proyectos" / nombre).write_bytes(
                b"imagen-oficial-de-prueba"
            )
        self.ajuste_media = override_settings(MEDIA_ROOT=self.media)
        self.ajuste_media.enable()

    def tearDown(self):
        self.ajuste_media.disable()
        self.temporal.cleanup()

    def test_simulacion_no_modifica_la_base(self):
        call_command("cargar_proyectos_iniciales", origen=self.origen)

        self.assertEqual(Proyecto.objects.count(), 0)

    def test_carga_publica_proyectos_y_es_idempotente(self):
        for _ in range(2):
            call_command(
                "cargar_proyectos_iniciales",
                origen=self.origen,
                aplicar=True,
            )

        self.assertEqual(Proyecto.objects.count(), 5)
        self.assertEqual(Proyecto.objects.filter(publicado=True).count(), 5)
        self.assertEqual(Proyecto.objects.exclude(imagen="").count(), 5)

        mirador = Proyecto.objects.get(slug="edificios-mirador-azul")
        self.assertEqual(mirador.estado, "finalizado")
        self.assertIn("Torre", mirador.texto_alternativo)
        self.assertIn("google.com/maps", mirador.enlace_mapa)
        with self.settings(GOOGLE_MAPS_EMBED_API_KEY="clave-de-prueba"):
            self.assertIn("maps/embed/v1/place", mirador.enlace_mapa_embebido)
            self.assertIn("clave-de-prueba", mirador.enlace_mapa_embebido)

        with self.settings(GOOGLE_MAPS_EMBED_API_KEY="clave-de-prueba"):
            respuesta = self.client.get("/proyectos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Edificios Mirador Azul")
        self.assertContains(respuesta, "Hospital del Trabajador")
        self.assertContains(respuesta, "data-project-category=\"residencial\"")
        self.assertContains(respuesta, "Ver referencia oficial")
        self.assertContains(respuesta, "Ver ubicación")
        self.assertNotContains(respuesta, "Fotografía próximamente")
        self.assertContains(respuesta, "data-map-preview", count=5)
        self.assertContains(respuesta, "data-map-address-preview", count=5)
        self.assertContains(respuesta, "data-map-src", count=5)


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
                self.assertNotContains(respuesta, "76.096.219-5")

        respuesta = self.client.get("/contacto/")
        self.assertContains(respuesta, "+56 2 2983 688")
        self.assertContains(respuesta, "administracion@phinstalaciones.cl")
        self.assertContains(respuesta, "San Diego 1325")

        servicios = self.client.get("/servicios/")
        self.assertNotContains(servicios, "Próximamente")
        self.assertContains(servicios, "Mantención eléctrica")

        proyectos = self.client.get("/proyectos/")
        self.assertNotContains(proyectos, 'href="#"')
        self.assertNotContains(proyectos, "proyectos demostrativos")
        self.assertContains(proyectos, "data-project-filter")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="web@phinstalaciones.cl",
        COTIZACIONES_EMAIL="administracion@phinstalaciones.cl",
    )
    def test_formulario_valida_registra_y_notifica_cotizacion(self):
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
        cotizacion = Cotizacion.objects.get()
        self.assertEqual(cotizacion.telefono, "+56912345678")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].to,
            ["administracion@phinstalaciones.cl"],
        )
        self.assertEqual(mail.outbox[0].reply_to, ["cliente@example.com"])
        self.assertIn(
            f"COT-{cotizacion.pk:06d}",
            mail.outbox[0].subject,
        )
        self.assertIn(
            "Contacta al cliente para confirmar los antecedentes",
            mail.outbox[0].body,
        )
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        contenido_html, tipo = mail.outbox[0].alternatives[0]
        self.assertEqual(tipo, "text/html")
        self.assertIn("Datos del cliente", contenido_html)
        self.assertIn("Necesito evaluar una instalación eléctrica", contenido_html)
        self.assertEqual(mail.outbox[1].to, ["cliente@example.com"])
        self.assertIn("Recibimos tu solicitud", mail.outbox[1].subject)
        self.assertIn(
            "fue registrada correctamente",
            mail.outbox[1].alternatives[0][0],
        )

        datos["telefono"] = "1234567890"
        respuesta = self.client.post("/contacto/", datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ingresa un teléfono chileno válido")
        self.assertEqual(Cotizacion.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

        datos["telefono"] = "912345678"
        datos["email"] = "correo-invalido"
        respuesta = self.client.post("/contacto/", datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ingresa un correo electrónico válido")
        self.assertEqual(Cotizacion.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="phcotizacion@phinstalaciones.cl",
        COTIZACIONES_EMAIL="phcotizacion@phinstalaciones.cl",
    )
    def test_cotizacion_desde_producto_conserva_y_envia_la_seleccion(self):
        familia = Categoria.objects.create(
            nombre="Iluminación",
            slug="iluminacion-prueba",
        )
        categoria = Categoria.objects.create(
            nombre="Plafones",
            slug="plafones-prueba",
            padre=familia,
        )
        producto = Producto.objects.create(
            categoria=categoria,
            nombre="Plafón LED de prueba",
            slug="plafon-led-prueba",
            subtitulo="Iluminación LED",
            descripcion="Producto para comprobar la cotización.",
            publicado=True,
        )

        seleccion = self.client.get(
            "/contacto/?producto=plafon-led-prueba"
        )
        self.assertContains(seleccion, "Producto seleccionado")
        self.assertContains(seleccion, producto.nombre)
        self.assertContains(seleccion, "disponibilidad, plazo de entrega")

        respuesta = self.client.post(
            "/contacto/",
            {
                "producto_id": producto.pk,
                "nombre": "Cliente producto",
                "empresa": "Empresa de prueba",
                "email": "producto@example.com",
                "telefono": "912345678",
                "servicio": "Productos",
                "mensaje": "Necesito veinte unidades para una instalación.",
            },
        )

        self.assertRedirects(respuesta, "/contacto/?enviado=1")
        cotizacion = Cotizacion.objects.get()
        self.assertEqual(cotizacion.producto, producto)
        self.assertIsNone(cotizacion.proyecto)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(producto.nombre, mail.outbox[0].subject)
        self.assertIn(producto.nombre, mail.outbox[0].body)
        self.assertEqual(mail.outbox[1].to, ["producto@example.com"])
        self.assertIn(producto.nombre, mail.outbox[1].body)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="phcotizacion@phinstalaciones.cl",
        COTIZACIONES_EMAIL="phcotizacion@phinstalaciones.cl",
    )
    def test_cotizacion_desde_proyecto_conserva_y_envia_la_referencia(self):
        proyecto = Proyecto.objects.create(
            nombre="Proyecto hospitalario de prueba",
            slug="proyecto-hospitalario-prueba",
            sector="hospitalario",
            descripcion="Proyecto usado para comprobar cotizaciones.",
            estado="finalizado",
            direccion="Santiago, Chile",
            publicado=True,
        )

        seleccion = self.client.get(
            "/contacto/?proyecto=proyecto-hospitalario-prueba"
        )
        self.assertContains(seleccion, "Proyecto de referencia")
        self.assertContains(seleccion, proyecto.nombre)
        self.assertContains(seleccion, "proyecto similar")

        respuesta = self.client.post(
            "/contacto/",
            {
                "proyecto_id": proyecto.pk,
                "nombre": "Cliente proyecto",
                "empresa": "Mandante de prueba",
                "email": "proyecto@example.com",
                "telefono": "+56 9 8765 4321",
                "servicio": "Proyecto especial / Otro",
                "mensaje": "Necesito desarrollar una obra de características similares.",
            },
        )

        self.assertRedirects(respuesta, "/contacto/?enviado=1")
        cotizacion = Cotizacion.objects.get()
        self.assertEqual(cotizacion.proyecto, proyecto)
        self.assertIsNone(cotizacion.producto)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(proyecto.nombre, mail.outbox[0].subject)
        self.assertIn(proyecto.nombre, mail.outbox[0].body)
        contenido_html = mail.outbox[0].alternatives[0][0]
        self.assertIn("Proyecto de referencia", contenido_html)
        self.assertIn("Salud", contenido_html)
        self.assertEqual(mail.outbox[1].to, ["proyecto@example.com"])
        self.assertIn(proyecto.nombre, mail.outbox[1].body)

    @patch(
        "core.views.enviar_notificacion_cotizacion",
        side_effect=RuntimeError("SMTP no disponible"),
    )
    def test_un_fallo_de_correo_no_pierde_la_cotizacion(self, _notificar):
        datos = {
            "nombre": "Cliente de prueba",
            "empresa": "",
            "email": "cliente@example.com",
            "telefono": "912345678",
            "servicio": "Mantención",
            "mensaje": "Necesito coordinar una mantención preventiva.",
        }

        with self.assertLogs("core.views", level="ERROR"):
            respuesta = self.client.post("/contacto/", datos)

        self.assertRedirects(respuesta, "/contacto/?enviado=1")
        self.assertEqual(Cotizacion.objects.count(), 1)
