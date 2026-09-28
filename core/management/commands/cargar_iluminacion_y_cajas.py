from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Categoria,
    CaracteristicaProducto,
    Cotizacion,
    EspecificacionProducto,
    EspecificacionVariante,
    ImagenProducto,
    Marca,
    Producto,
    VarianteProducto,
)


IMAGENES = {
    "fsl-24w": {
        "origen": "PLAFON LED 24W FSL 6500K.png",
        "destino": "iluminacion/fsl-plafon-led-sobrepuesto-24w-6500k.png",
        "alt": "Plafón LED FSL sobrepuesto redondo de 24 W y 6500 K",
    },
    "avc-18w": {
        "origen": "FOCO EMB 18W 6500K.png",
        "destino": "iluminacion/avc-panel-led-embutido-18w-6500k.png",
        "alt": "Panel LED AVC embutido de 18 W, 1440 lm y 6500 K",
    },
    "fsl-embutido-24w": {
        "origen": "WhatsApp Image 2026-09-24 at 08.53.44.jpeg",
        "destino": "iluminacion/fsl-panel-led-embutido-24w-profesional.png",
        "alt": "Panel LED FSL redondo embutido de 24 W y 2060 lm",
        "preparada": True,
    },
    "avc-sobrepuesto-18w": {
        "origen": "WhatsApp Image 2026-09-24 at 08.52.51.jpeg",
        "destino": "iluminacion/avc-panel-led-sobrepuesto-18w-profesional.png",
        "alt": "Panel LED AVC redondo sobrepuesto de 18 W, 1440 lm y 6500 K",
        "preparada": True,
    },
    "gabinete-300-estandar": {
        "origen": "GABINETE METALICO 1 PUERTA 300X200X150 IP65.png",
        "destino": "gabinetes/gabinete-metalico-300x200x150-ip65.png",
        "alt": "Gabinete metálico IP65 de una puerta, 300 x 200 x 150 mm",
    },
    "gabinete-250-estandar": {
        "origen": "GABINETE 250X200X150 1PUERTA.png",
        "destino": "gabinetes/gabinete-metalico-250x200x150-una-puerta.png",
        "alt": "Gabinete metálico de una puerta, 250 x 200 x 150 mm",
    },
    "gabinete-600-chasis": {
        "origen": "Gabinete met. 1 puerta 600x400x200 IP65 c-chasis.png",
        "destino": "gabinetes/gabinete-metalico-600x400x200-ip65-con-chasis.png",
        "alt": "Gabinete metálico IP65 de 600 x 400 x 200 mm con chasis",
    },
    "gabinete-600-estandar": {
        "origen": "Gabinete Tablero Metálico 600x400x200 Ip65 1 Puerta.png",
        "destino": "gabinetes/gabinete-metalico-600x400x200-ip65-estandar.png",
        "alt": "Gabinete metálico IP65 de 600 x 400 x 200 mm, una puerta",
    },
    "gabinete-500-chasis": {
        "origen": "Gabinete met. 1 puerta 500x400x200 IP65 c-chasis.png",
        "destino": "gabinetes/gabinete-metalico-500x400x200-ip65-con-chasis.png",
        "alt": "Gabinete metálico IP65 de 500 x 400 x 200 mm con chasis",
    },
    "gabinete-500-estandar": {
        "origen": "Gabinete Tablero Metálico 500x400x200 IP65 1 Puerta.png",
        "destino": "gabinetes/gabinete-metalico-500x400x200-ip65-estandar.png",
        "alt": "Gabinete metálico IP65 de 500 x 400 x 200 mm, una puerta",
    },
    "gabinete-400-chasis": {
        "origen": "Gabinete met. 1 puerta 400x300x200 IP65 c-chasis.png",
        "destino": "gabinetes/gabinete-metalico-400x300x200-ip65-con-chasis.png",
        "alt": "Gabinete metálico IP65 de 400 x 300 x 200 mm con chasis",
    },
    "gabinete-400-estandar": {
        "origen": "Gabinete Tablero Metálico 400x300x200 Ip65 1 Puerta.png",
        "destino": "gabinetes/gabinete-metalico-400x300x200-ip65-estandar.png",
        "alt": "Gabinete metálico IP65 de 400 x 300 x 200 mm, una puerta",
    },
    "estanca-220-lisa": {
        "origen": (
            "Caja de distribución estanca lisa tecnopolímero "
            "220x170x95mm IP55.png"
        ),
        "destino": "cajas-estancas/caja-estanca-lisa-220x170x95-ip55.png",
        "alt": "Caja de distribución estanca lisa de 220 x 170 x 95 mm IP55",
    },
    "estanca-170-lisa": {
        "origen": "CAJA ESTANCA EXT. 170X140X85MM LISA.png",
        "destino": "cajas-estancas/caja-estanca-lisa-170x140x85.png",
        "alt": "Caja estanca exterior lisa de 170 x 140 x 85 mm",
    },
    "chuqui-metalica": {
        "origen": "Caja Chuqui Metálica.png",
        "destino": "cajas-metalicas/caja-chuqui-metalica.png",
        "alt": "Caja Chuqui metálica pregalvanizada",
    },
    "caja-a01": {
        "origen": "Caja A01 Con Tapa Pre-galvanizada 100x65x65mm.png",
        "destino": "cajas-metalicas/caja-a01-pregalvanizada-100x65x65.png",
        "alt": "Caja A01 pregalvanizada con tapa de 100 x 65 x 65 mm",
    },
    "caja-a11": {
        "origen": "Caja Pre-Galvanizada Pre-Picada A-11 100X100X65.png",
        "destino": "cajas-metalicas/caja-a11-prepicada-100x100x65.png",
        "alt": "Caja A11 pregalvanizada prepicada de 100 x 100 x 65 mm",
    },
    "estanca-100-lisa": {
        "origen": "Caja Estanca 100x100x70 lisa.png",
        "destino": "cajas-estancas/caja-estanca-lisa-100x100x70-ip65.png",
        "alt": "Caja estanca lisa de 100 x 100 x 70 mm IP65",
    },
    "estanca-100-conos": {
        "origen": "Caja Estanca 100x100x70 con conos.png",
        "destino": "cajas-estancas/caja-estanca-con-conos-100x100x70-ip65.png",
        "alt": "Caja estanca con conos de 100 x 100 x 70 mm IP65",
    },
    "estanca-80-conos": {
        "origen": "Caja Estanca 80x80 con conos.png",
        "destino": "cajas-estancas/caja-estanca-con-conos-80x80x50-ip55.png",
        "alt": "Caja estanca con conos de 80 x 80 x 50 mm IP55",
    },
    "estanca-80-lisa": {
        "origen": "CAJA ESTANCA EXT. 80X80X40MM LISA.png",
        "destino": "cajas-estancas/caja-estanca-lisa-80x80x40.png",
        "alt": "Caja estanca exterior lisa de 80 x 80 x 40 mm",
    },
    "chuqui-plastica": {
        "origen": "Caja Chuqui.png",
        "destino": "cajas-instalacion/caja-chuqui-superficie.png",
        "alt": "Caja Chuqui plástica para montaje eléctrico en superficie",
    },
    "caja-loza": {
        "origen": "Caja eléctrica loza con oreja metálica gris.png",
        "destino": "cajas-instalacion/caja-loza-oreja-metalica-gris.png",
        "alt": "Caja eléctrica gris para loza con oreja metálica",
    },
    "caja-tabique": {
        "origen": "Caja Distribucion 5-8 Tabique Gris C-Oreja Metalica.png",
        "destino": "cajas-instalacion/caja-tabique-5-8-oreja-metalica.png",
        "alt": "Caja eléctrica gris para tabique 5/8 con oreja metálica",
    },
}


def variante(nombre, codigo, imagen, especificaciones, modelo=""):
    return {
        "nombre": nombre,
        "codigo": codigo,
        "modelo": modelo,
        "imagen": imagen,
        "especificaciones": especificaciones,
    }


def especificaciones_gabinete(alto, ancho, profundidad, ip="", chasis=None):
    datos = [
        ("Alto", str(alto), "mm"),
        ("Ancho", str(ancho), "mm"),
        ("Profundidad", str(profundidad), "mm"),
        ("Número de puertas", "1", ""),
    ]
    if ip:
        datos.append(("Grado de protección", ip, ""))
    if chasis is not None:
        datos.append(("Chasis interior", "Incluido" if chasis else "No incluido", ""))
    return tuple(datos)


def especificaciones_caja(alto, ancho, profundidad, entrada, ip=""):
    datos = [
        ("Dimensiones", f"{alto} x {ancho} x {profundidad}", "mm"),
        ("Tipo de entrada", entrada, ""),
    ]
    if ip:
        datos.append(("Grado de protección", ip, ""))
    return tuple(datos)


PRODUCTOS = (
    {
        "slug": "plafon-led-sobrepuesto-fsl-6500k",
        "nombre": "Plafón LED sobrepuesto FSL 6500 K",
        "categoria": "plafones-led",
        "marca": "fsl",
        "modelo": "",
        "subtitulo": "Iluminación LED redonda de superficie",
        "descripcion": (
            "Plafón LED FSL de montaje sobrepuesto para iluminación general "
            "interior, con difusor blanco y luz fría de 6500 K."
        ),
        "imagen": "fsl-24w",
        "etiqueta": "ILUMINACIÓN",
        "orden": 200,
        "caracteristicas": (
            "Montaje sobrepuesto de instalación sencilla",
            "Difusor blanco de iluminación uniforme y bajo deslumbramiento",
            "Luz fría de 6500 K para iluminación interior",
        ),
        "especificaciones": (
            ("Tecnología", "LED", ""),
            ("Temperatura de color", "6500", "K"),
            ("Color de luz", "Fría", ""),
            ("Forma", "Redonda", ""),
            ("Vida útil declarada", "25000", "h"),
            ("Ángulo de apertura", "120", "°"),
            ("Índice de reproducción cromática", "≥ 80", "CRI"),
            ("Tipo de montaje", "Sobrepuesto", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "panel-led-embutido-fsl",
        "nombre": "Panel LED embutido FSL",
        "categoria": "plafones-led",
        "marca": "fsl",
        "modelo": "",
        "subtitulo": "Panel redondo para instalación empotrada",
        "descripcion": (
            "Panel LED FSL de formato redondo para montaje embutido en cielo, "
            "con encendido instantáneo, difusor uniforme y dos potencias "
            "disponibles para iluminación interior."
        ),
        "imagen": "fsl-embutido-24w",
        "etiqueta": "ILUMINACIÓN",
        "orden": 205,
        "caracteristicas": (
            "Montaje embutido con diseño delgado",
            "No dimerizable y de encendido instantáneo",
            "Dos años de garantía declarada por el fabricante",
        ),
        "especificaciones": (
            ("Tecnología", "LED", ""),
            ("Forma", "Redonda", ""),
            ("Tipo de montaje", "Embutido", ""),
            ("Ángulo de apertura", "120", "°"),
            ("Índice de reproducción cromática", "≥ 80", "CRI"),
            ("Vida útil declarada", "25000", "h"),
            ("Dimerizable", "No", ""),
            ("Garantía declarada", "2", "años"),
        ),
        "variantes": (),
    },
    {
        "slug": "panel-led-embutido-avc-6500k",
        "nombre": "Panel LED embutido AVC 6500 K",
        "categoria": "plafones-led",
        "marca": "avc",
        "modelo": "",
        "subtitulo": "Panel redondo de luz fría",
        "descripcion": (
            "Panel LED AVC para montaje embutido en cielo, de formato redondo "
            "y luz fría de 6500 K para iluminación interior."
        ),
        "imagen": "avc-18w",
        "etiqueta": "ILUMINACIÓN",
        "orden": 210,
        "caracteristicas": (
            "Diseño delgado para instalación embutida",
            "Flujo luminoso uniforme para iluminación interior",
            "Luz fría de 6500 K",
        ),
        "especificaciones": (
            ("Tecnología", "LED", ""),
            ("Temperatura de color", "6500", "K"),
            ("Color de luz", "Fría", ""),
            ("Forma", "Redonda", ""),
            ("Tipo de montaje", "Embutido", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "panel-led-sobrepuesto-avc-6500k",
        "nombre": "Panel LED sobrepuesto AVC 6500 K",
        "categoria": "plafones-led",
        "marca": "avc",
        "modelo": "",
        "subtitulo": "Panel redondo de superficie y luz fría",
        "descripcion": (
            "Panel LED AVC de montaje sobrepuesto, formato redondo y luz fría "
            "de 6500 K, diseñado para iluminación general interior."
        ),
        "imagen": "avc-sobrepuesto-18w",
        "etiqueta": "ILUMINACIÓN",
        "orden": 215,
        "caracteristicas": (
            "Instalación sobrepuesta sin perforación de embutido",
            "Luz fría de 6500 K y apertura amplia de 120°",
            "Formato redondo para iluminación general interior",
        ),
        "especificaciones": (
            ("Tecnología", "LED", ""),
            ("Temperatura de color", "6500", "K"),
            ("Color de luz", "Fría", ""),
            ("Forma", "Redonda", ""),
            ("Tipo de montaje", "Sobrepuesto", ""),
            ("Tensión de alimentación", "185–265", "V AC"),
            ("Ángulo de apertura", "120", "°"),
            ("Índice de reproducción cromática", "> 70", "CRI"),
            ("Vida útil declarada", "20000", "h"),
            ("Garantía declarada", "1", "año"),
        ),
        "variantes": (),
    },
    {
        "slug": "gabinetes-metalicos-una-puerta",
        "nombre": "Gabinetes metálicos de una puerta",
        "categoria": "gabinetes-metalicos",
        "marca": None,
        "modelo": "",
        "subtitulo": "Protección y montaje para tableros eléctricos",
        "descripcion": (
            "Gabinetes metálicos de una puerta para alojar equipos de "
            "distribución, control y automatización. Las versiones con chasis "
            "se identifican y muestran con su fotografía específica."
        ),
        "imagen": "gabinete-400-estandar",
        "etiqueta": "GABINETES",
        "orden": 100,
        "caracteristicas": (
            "Construcción metálica para uso eléctrico",
            "Puerta frontal con sistema de cierre",
            "Opciones estándar y opciones con chasis interior incluido",
        ),
        "especificaciones": (
            ("Material", "Metálico", ""),
            ("Número de puertas", "1", ""),
            ("Aplicación", "Distribución y control eléctrico", ""),
        ),
        "variantes": (
            variante(
                "250 x 200 x 150 mm · 1 puerta",
                "GAB-MET-250-200-150-1P",
                "gabinete-250-estandar",
                especificaciones_gabinete(250, 200, 150),
            ),
            variante(
                "300 x 200 x 150 mm · IP65",
                "GAB-MET-300-200-150-IP65",
                "gabinete-300-estandar",
                especificaciones_gabinete(300, 200, 150, "IP65"),
            ),
            variante(
                "400 x 300 x 200 mm · IP65 · estándar",
                "GAB-MET-400-300-200-IP65",
                "gabinete-400-estandar",
                especificaciones_gabinete(400, 300, 200, "IP65", False),
            ),
            variante(
                "400 x 300 x 200 mm · IP65 · con chasis",
                "GAB-MET-400-300-200-IP65-CH",
                "gabinete-400-chasis",
                especificaciones_gabinete(400, 300, 200, "IP65", True),
            ),
            variante(
                "500 x 400 x 200 mm · IP65 · estándar",
                "GAB-MET-500-400-200-IP65",
                "gabinete-500-estandar",
                especificaciones_gabinete(500, 400, 200, "IP65", False),
            ),
            variante(
                "500 x 400 x 200 mm · IP65 · con chasis",
                "GAB-MET-500-400-200-IP65-CH",
                "gabinete-500-chasis",
                especificaciones_gabinete(500, 400, 200, "IP65", True),
            ),
            variante(
                "600 x 400 x 200 mm · IP65 · estándar",
                "GAB-MET-600-400-200-IP65",
                "gabinete-600-estandar",
                especificaciones_gabinete(600, 400, 200, "IP65", False),
            ),
            variante(
                "600 x 400 x 200 mm · IP65 · con chasis",
                "GAB-MET-600-400-200-IP65-CH",
                "gabinete-600-chasis",
                especificaciones_gabinete(600, 400, 200, "IP65", True),
            ),
        ),
    },
    {
        "slug": "cajas-estancas-de-derivacion",
        "nombre": "Cajas estancas de derivación",
        "categoria": "cajas-estancas",
        "marca": None,
        "modelo": "",
        "subtitulo": "Protección de conexiones eléctricas",
        "descripcion": (
            "Cajas aislantes para derivación y protección de conexiones en "
            "montaje superficial, disponibles con laterales lisos o conos de entrada."
        ),
        "imagen": "estanca-100-lisa",
        "etiqueta": "CAJAS ESTANCAS",
        "orden": 110,
        "caracteristicas": (
            "Tapa desmontable para acceso a las conexiones",
            "Alternativas lisas y con conos de entrada",
            "Distintas dimensiones para adecuarse a cada instalación",
        ),
        "especificaciones": (
            ("Tipo de instalación", "Superficie", ""),
            ("Aplicación", "Derivación y protección de conexiones", ""),
            ("Color", "Gris claro", ""),
        ),
        "variantes": (
            variante(
                "80 x 80 x 40 mm · lisa",
                "CAJ-EST-80-80-40-L",
                "estanca-80-lisa",
                especificaciones_caja(80, 80, 40, "Lisa"),
            ),
            variante(
                "80 x 80 x 50 mm · con conos · IP55",
                "CAJ-EST-80-80-50-C-IP55",
                "estanca-80-conos",
                especificaciones_caja(80, 80, 50, "Con conos", "IP55"),
            ),
            variante(
                "100 x 100 x 70 mm · lisa · IP65",
                "CAJ-EST-100-100-70-L-IP65",
                "estanca-100-lisa",
                especificaciones_caja(100, 100, 70, "Lisa", "IP65"),
            ),
            variante(
                "100 x 100 x 70 mm · con conos · IP65",
                "CAJ-EST-100-100-70-C-IP65",
                "estanca-100-conos",
                especificaciones_caja(100, 100, 70, "Con conos", "IP65"),
            ),
            variante(
                "170 x 140 x 85 mm · lisa",
                "CAJ-EST-170-140-85-L",
                "estanca-170-lisa",
                especificaciones_caja(170, 140, 85, "Lisa"),
            ),
            variante(
                "220 x 170 x 95 mm · lisa · IP55",
                "CAJ-EST-220-170-95-L-IP55",
                "estanca-220-lisa",
                especificaciones_caja(220, 170, 95, "Lisa", "IP55"),
            ),
        ),
    },
    {
        "slug": "cajas-metalicas-pregalvanizadas",
        "nombre": "Cajas metálicas pregalvanizadas",
        "categoria": "cajas-metalicas",
        "marca": None,
        "modelo": "",
        "subtitulo": "Cajas de paso y montaje eléctrico",
        "descripcion": (
            "Cajas metálicas para canalización, paso y montaje de dispositivos "
            "eléctricos, con entradas prepicadas según la presentación."
        ),
        "imagen": "caja-a11",
        "etiqueta": "CAJAS METÁLICAS",
        "orden": 120,
        "caracteristicas": (
            "Fabricación en metal pregalvanizado",
            "Entradas prepicadas para canalización",
            "Formatos para paso, derivación y montaje",
        ),
        "especificaciones": (
            ("Material", "Acero pregalvanizado", ""),
            ("Aplicación", "Canalización y derivación eléctrica", ""),
        ),
        "variantes": (
            variante(
                "Caja Chuqui metálica",
                "CAJ-CHUQUI-MET",
                "chuqui-metalica",
                (
                    ("Tipo", "Chuqui metálica", ""),
                    ("Material", "Acero pregalvanizado", ""),
                    ("Entradas", "Prepicadas", ""),
                ),
            ),
            variante(
                "Caja A01 con tapa · 100 x 65 x 65 mm",
                "CAJ-A01-100-65-65",
                "caja-a01",
                (
                    ("Modelo", "A01", ""),
                    ("Dimensiones", "100 x 65 x 65", "mm"),
                    ("Tapa", "Incluida", ""),
                ),
                modelo="A01",
            ),
            variante(
                "Caja A11 prepicada · 100 x 100 x 65 mm",
                "CAJ-A11-100-100-65",
                "caja-a11",
                (
                    ("Modelo", "A11", ""),
                    ("Dimensiones", "100 x 100 x 65", "mm"),
                    ("Entradas", "Prepicadas", ""),
                ),
                modelo="A11",
            ),
        ),
    },
    {
        "slug": "caja-chuqui-superficie",
        "nombre": "Caja Chuqui de superficie",
        "categoria": "cajas-instalacion",
        "marca": None,
        "modelo": "",
        "subtitulo": "Base para mecanismos eléctricos",
        "descripcion": (
            "Caja plástica para instalar mecanismos eléctricos sobre muro, "
            "con puntos de fijación y entradas para canalización."
        ),
        "imagen": "chuqui-plastica",
        "etiqueta": "CAJAS DE INSTALACIÓN",
        "orden": 130,
        "caracteristicas": (
            "Montaje superficial",
            "Cuerpo de material aislante",
            "Preparada para fijación de mecanismos y canalización",
        ),
        "especificaciones": (
            ("Material", "Plástico aislante", ""),
            ("Tipo de montaje", "Superficie", ""),
            ("Aplicación", "Mecanismos eléctricos", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "cajas-embutidas-con-oreja-metalica",
        "nombre": "Cajas embutidas con oreja metálica",
        "categoria": "cajas-instalacion",
        "marca": None,
        "modelo": "",
        "subtitulo": "Montaje de mecanismos en loza o tabique",
        "descripcion": (
            "Cajas eléctricas grises para instalación embutida de mecanismos, "
            "con oreja metálica de fijación y versiones para loza o tabique."
        ),
        "imagen": "caja-loza",
        "etiqueta": "CAJAS DE INSTALACIÓN",
        "orden": 140,
        "caracteristicas": (
            "Oreja metálica para fijación del mecanismo",
            "Entradas preformadas para canalización",
            "Versiones específicas para loza y tabique 5/8",
        ),
        "especificaciones": (
            ("Tipo de montaje", "Embutido", ""),
            ("Color", "Gris", ""),
            ("Fijación", "Oreja metálica", ""),
        ),
        "variantes": (
            variante(
                "Para loza · oreja metálica",
                "CAJ-EMB-LOZA-OM",
                "caja-loza",
                (
                    ("Aplicación", "Loza", ""),
                    ("Tipo de montaje", "Embutido", ""),
                    ("Fijación", "Oreja metálica", ""),
                ),
            ),
            variante(
                "Para tabique 5/8 · oreja metálica",
                "CAJ-EMB-TAB-58-OM",
                "caja-tabique",
                (
                    ("Aplicación", "Tabique 5/8", ""),
                    ("Tipo de montaje", "Embutido", ""),
                    ("Fijación", "Oreja metálica", ""),
                ),
            ),
        ),
    },
)


class Command(BaseCommand):
    help = (
        "Valida o carga plafones LED, gabinetes metálicos y cajas eléctricas "
        "a partir de las imágenes proporcionadas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--origen",
            type=Path,
            default=Path.home() / "Downloads",
            help="Carpeta que contiene las imágenes originales.",
        )
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Crea o actualiza registros y copia las imágenes.",
        )
        parser.add_argument(
            "--no-publicar",
            action="store_true",
            help="Carga los productos como borradores en vez de publicarlos.",
        )
        parser.add_argument(
            "--sobrescribir-imagenes",
            action="store_true",
            help="Reemplaza las copias existentes en MEDIA_ROOT.",
        )

    def handle(self, *args, **options):
        origen = options["origen"].expanduser().resolve()
        rutas = {
            clave: self._ruta_origen_imagen(origen, datos)
            for clave, datos in IMAGENES.items()
        }
        faltantes = [
            rutas[clave]
            for clave, datos in IMAGENES.items()
            if not rutas[clave].is_file()
            and (
                options["sobrescribir_imagenes"]
                or not default_storage.exists(self._destino_imagen(datos))
            )
        ]
        if faltantes:
            detalle = "\n - ".join(str(ruta) for ruta in faltantes)
            raise CommandError(f"Faltan imágenes requeridas:\n - {detalle}")

        total_variantes = sum(len(producto["variantes"]) for producto in PRODUCTOS)
        self.stdout.write(
            f"Plan validado: {len(PRODUCTOS)} productos, {total_variantes} "
            f"variantes y {len(IMAGENES)} imágenes."
        )

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    "No se modificó el catálogo. Use --aplicar para cargarlo."
                )
            )
            return

        destinos = {
            clave: self._copiar_imagen(
                datos,
                rutas[clave],
                sobrescribir=options["sobrescribir_imagenes"],
            )
            for clave, datos in IMAGENES.items()
        }

        with transaction.atomic():
            categorias = self._crear_categorias()
            marcas = self._crear_marcas()
            for definicion in PRODUCTOS:
                self._cargar_producto(
                    definicion,
                    categorias,
                    marcas,
                    destinos,
                    publicar=not options["no_publicar"],
                )

        estado = "como borradores" if options["no_publicar"] else "publicados"
        self.stdout.write(
            self.style.SUCCESS(
                f"Carga terminada: {len(PRODUCTOS)} productos quedaron {estado}."
            )
        )

    def _destino_imagen(self, datos):
        return (
            PurePosixPath("productos")
            / "catalogo"
            / PurePosixPath(datos["destino"])
        ).as_posix()

    def _ruta_origen_imagen(self, origen, datos):
        if datos.get("preparada"):
            return (
                Path(settings.BASE_DIR)
                / "media"
                / "productos"
                / "catalogo"
                / PurePosixPath(datos["destino"])
            )
        return origen / datos["origen"]

    def _copiar_imagen(self, datos, origen, sobrescribir=False):
        destino = self._destino_imagen(datos)
        try:
            destino_local = Path(default_storage.path(destino)).resolve()
        except NotImplementedError:
            destino_local = None

        if destino_local == origen.resolve():
            return destino

        if sobrescribir and default_storage.exists(destino):
            default_storage.delete(destino)
        if not default_storage.exists(destino):
            with origen.open("rb") as archivo:
                nombre_guardado = default_storage.save(destino, File(archivo))
            if nombre_guardado != destino:
                raise CommandError(
                    f"El almacenamiento cambió {destino} por {nombre_guardado}."
                )
        return destino

    def _crear_categorias(self):
        iluminacion, _ = Categoria.objects.update_or_create(
            slug="iluminacion",
            defaults={
                "nombre": "Iluminación",
                "padre": None,
                "orden": 30,
                "activa": True,
            },
        )
        tableros, _ = Categoria.objects.update_or_create(
            slug="tableros-electricos",
            defaults={
                "nombre": "Tableros eléctricos",
                "padre": None,
                "orden": 40,
                "activa": True,
            },
        )
        definiciones = (
            ("plafones-led", "Plafones LED", iluminacion, 3),
            ("gabinetes-metalicos", "Gabinetes metálicos", tableros, 2),
            ("cajas-estancas", "Cajas estancas", tableros, 3),
            ("cajas-metalicas", "Cajas metálicas", tableros, 4),
            ("cajas-instalacion", "Cajas de instalación", tableros, 5),
        )
        categorias = {}
        for slug, nombre, padre, orden in definiciones:
            categorias[slug], _ = Categoria.objects.update_or_create(
                slug=slug,
                defaults={
                    "nombre": nombre,
                    "padre": padre,
                    "orden": orden,
                    "activa": True,
                },
            )
        return categorias

    def _crear_marcas(self):
        marcas = {}
        for slug, nombre in (("fsl", "FSL"), ("avc", "AVC")):
            marcas[slug], _ = Marca.objects.update_or_create(
                slug=slug,
                defaults={"nombre": nombre, "activa": True},
            )
        return marcas

    def _cargar_producto(
        self,
        definicion,
        categorias,
        marcas,
        destinos,
        publicar,
    ):
        producto, _ = Producto.objects.update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria": categorias[definicion["categoria"]],
                "nombre": definicion["nombre"],
                "marca_nueva": marcas.get(definicion["marca"]),
                "marca": "",
                "modelo": definicion["modelo"],
                "codigo": None,
                "subtitulo": definicion["subtitulo"],
                "descripcion": definicion["descripcion"],
                "imagen": destinos[definicion["imagen"]],
                "texto_alternativo": IMAGENES[definicion["imagen"]]["alt"],
                "etiqueta_visual": definicion["etiqueta"],
                "orden": definicion["orden"],
                "publicado": publicar,
            },
        )

        for orden, texto in enumerate(definicion["caracteristicas"], start=1):
            CaracteristicaProducto.objects.update_or_create(
                producto=producto,
                texto=texto,
                defaults={"orden": orden},
            )

        for orden, (nombre, valor, unidad) in enumerate(
            definicion["especificaciones"], start=1
        ):
            EspecificacionProducto.objects.update_or_create(
                producto=producto,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

        codigos_vigentes = {
            datos["codigo"] for datos in definicion["variantes"]
        }
        variantes_obsoletas = producto.variantes.exclude(
            codigo__in=codigos_vigentes
        )
        Cotizacion.objects.filter(
            variante__in=variantes_obsoletas
        ).update(variante=None)
        variantes_obsoletas.delete()

        variantes_por_imagen = {}
        for orden, datos in enumerate(definicion["variantes"], start=1):
            variante_objeto, _ = VarianteProducto.objects.update_or_create(
                codigo=datos["codigo"],
                defaults={
                    "producto": producto,
                    "nombre": datos["nombre"],
                    "modelo": datos["modelo"],
                    "imagen": destinos[datos["imagen"]],
                    "disponible": True,
                    "orden": orden,
                },
            )
            variantes_por_imagen.setdefault(datos["imagen"], []).append(
                variante_objeto
            )
            for posicion, (nombre, valor, unidad) in enumerate(
                datos["especificaciones"], start=1
            ):
                EspecificacionVariante.objects.update_or_create(
                    variante=variante_objeto,
                    nombre=nombre,
                    defaults={
                        "valor": valor,
                        "unidad": unidad,
                        "orden": posicion,
                    },
                )

        claves_imagen = [definicion["imagen"]]
        claves_imagen.extend(datos["imagen"] for datos in definicion["variantes"])
        for orden, clave in enumerate(dict.fromkeys(claves_imagen), start=1):
            imagen, _ = ImagenProducto.objects.update_or_create(
                clave=f"carga-iluminacion-cajas-{clave}",
                defaults={
                    "producto": producto,
                    "imagen": destinos[clave],
                    "texto_alternativo": IMAGENES[clave]["alt"],
                    "orden": orden,
                },
            )
            imagen.variantes.set(variantes_por_imagen.get(clave, []))
