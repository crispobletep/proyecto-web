from core.catalog_imports import retirar_variantes
from pathlib import Path, PurePosixPath

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Categoria,
    CaracteristicaProducto,
    EspecificacionProducto,
    EspecificacionVariante,
    ImagenProducto,
    Marca,
    Producto,
    VarianteProducto,
)


IMAGENES = {
    "ferrule-1-5-azul": {
        "origen": "FERRUL 16AWG AZUL 1,5mm2.png",
        "destino": "ferrules/ferrule-1-5mm2-16awg-azul.png",
        "alt": "Ferrule aislado azul para conductor de 1,5 mm² o 16 AWG",
    },
    "ferrule-2-5-gris": {
        "origen": "FERRULE 2,5 mm (14 AWG) GRIS.png",
        "destino": "ferrules/ferrule-2-5mm2-14awg-gris.png",
        "alt": "Ferrule aislado gris para conductor de 2,5 mm² o 14 AWG",
    },
    "ferrule-4-naranjo": {
        "origen": "FERRULE 4mm (12 AWG) NARANJO.png",
        "destino": "ferrules/ferrule-4mm2-12awg-naranjo.png",
        "alt": "Ferrule aislado naranjo para conductor de 4 mm² o 12 AWG",
    },
    "ferrule-6-verde": {
        "origen": "FERRULE 6mm (10 AWG) VERDE.png",
        "destino": "ferrules/ferrule-6mm2-10awg-verde.png",
        "alt": "Ferrule aislado verde para conductor de 6 mm² o 10 AWG",
    },
    "ferrule-10-cafe": {
        "origen": "FERRULE 10mm (8 AWG) CAFE.png",
        "destino": "ferrules/ferrule-10mm2-8awg-cafe.png",
        "alt": "Ferrule aislado café para conductor de 10 mm² o 8 AWG",
    },
    "lexo-verde": {
        "origen": "CINTA AISLANTE VINÍLICO 19 MM 20 METROS VERDE.png",
        "destino": "cintas/cinta-aislante-lexo-19mm-20m-verde.png",
        "alt": "Cinta aislante vinílica LEXO de 19 mm por 20 m, color verde",
    },
    "lexo-blanca": {
        "origen": "CINTA AISLANTE VINÍLICO 19 MM 20 METROS BLANCa.png",
        "destino": "cintas/cinta-aislante-lexo-19mm-20m-blanca.png",
        "alt": "Cinta aislante vinílica LEXO de 19 mm por 20 m, color blanco",
    },
    "lexo-roja": {
        "origen": "CINTA AISLANTE VINÍLICO 19 MM 20 METROS ROJA.png",
        "destino": "cintas/cinta-aislante-lexo-19mm-20m-roja.png",
        "alt": "Cinta aislante vinílica LEXO de 19 mm por 20 m, color rojo",
    },
    "lexo-azul": {
        "origen": "CINTA AISLANTE VINÍLICO 19 MM 20 METROS AZUL.png",
        "destino": "cintas/cinta-aislante-lexo-19mm-20m-azul.png",
        "alt": "Cinta aislante vinílica LEXO de 19 mm por 20 m, color azul",
    },
    "3m-temflex-165-negra": {
        "origen": "CINTA AISLANTE VINILICA 19MM X18MTS NEGRA TEMFLEX 165 3M.png",
        "destino": "cintas/cinta-aislante-3m-temflex-165-negra.png",
        "alt": "Cinta aislante vinílica negra 3M Temflex 165",
    },
    "fsl-autofundente": {
        "origen": "Cinta De Goma Autofundente 20mm X 5mts - Fsl.png",
        "destino": "cintas/cinta-goma-autofundente-fsl-20mm-5m.png",
        "alt": "Cinta de goma autofundente FSL de 20 mm por 5 m",
    },
    "fsl-pvc-negra": {
        "origen": "Cinta Aislante Negra FSL 1.9mm 16m PVC Eléctrica.png",
        "destino": "cintas/cinta-aislante-pvc-fsl-negra-19mm-16m.png",
        "alt": "Cinta aislante eléctrica negra FSL de PVC, 19 mm por 16 m",
    },
}


def variante_ferrule(seccion, awg, color, imagen):
    return {
        "nombre": f"{seccion} mm² · {awg} AWG · {color}",
        "modelo": "",
        "codigo": None,
        "imagen": imagen,
        "especificaciones": (
            ("Sección del conductor", seccion, "mm²"),
            ("Calibre equivalente", awg, "AWG"),
            ("Color del aislante", color, ""),
        ),
    }


def variante_lexo(color, imagen, codigo=None):
    return {
        "nombre": color,
        "modelo": "19 mm × 20 m",
        "codigo": codigo,
        "imagen": imagen,
        "especificaciones": (
            ("Color", color, ""),
            ("Ancho", "19", "mm"),
            ("Longitud", "20", "m"),
        ),
    }


PRODUCTOS = (
    {
        "slug": "ferrules-aislados-1-5-a-10-mm2",
        "nombre": "Ferrules aislados de 1,5 a 10 mm²",
        "categoria": "terminales-puntera",
        "marca": None,
        "modelo": "",
        "codigo": None,
        "subtitulo": "Terminales tubulares para conductores flexibles",
        "descripcion": (
            "Terminales puntera aislados para ordenar los filamentos de "
            "conductores flexibles y preparar una terminación uniforme antes "
            "del prensado y la conexión en borneras o equipos eléctricos."
        ),
        "imagen": "ferrule-1-5-azul",
        "etiqueta": "CONEXIÓN",
        "orden": 120,
        "caracteristicas": (
            "Formato tubular para terminaciones de conductores flexibles",
            "Collar aislante coloreado para identificar cada presentación",
            "Cinco calibres disponibles entre 1,5 y 10 mm²",
        ),
        "especificaciones": (
            ("Tipo", "Terminal puntera aislado (ferrule)", ""),
            ("Rango de sección", "1,5-10", "mm²"),
            ("Rango equivalente", "16-8", "AWG"),
            ("Método de instalación", "Prensado", ""),
        ),
        "variantes": (
            variante_ferrule("1,5", "16", "Azul", "ferrule-1-5-azul"),
            variante_ferrule("2,5", "14", "Gris", "ferrule-2-5-gris"),
            variante_ferrule("4", "12", "Naranjo", "ferrule-4-naranjo"),
            variante_ferrule("6", "10", "Verde", "ferrule-6-verde"),
            variante_ferrule("10", "8", "Café", "ferrule-10-cafe"),
        ),
    },
    {
        "slug": "cinta-aislante-vinilica-lexo-19mm-20m",
        "nombre": "Cinta aislante vinílica LEXO 19 mm × 20 m",
        "categoria": "cintas-aislantes",
        "marca": "lexo",
        "modelo": "19 mm × 20 m",
        "codigo": None,
        "subtitulo": "Aislación y codificación por color",
        "descripcion": (
            "Cinta vinílica autoextinguible LEXO para aislación eléctrica, "
            "identificación de conductores y trabajos de uso general en baja "
            "y media tensión."
        ),
        "imagen": "lexo-azul",
        "etiqueta": "AISLACIÓN",
        "orden": 130,
        "caracteristicas": (
            "Material vinílico retardante a la llama",
            "Resistencia a rayos UV",
            "Cuatro colores disponibles para identificación",
        ),
        "especificaciones": (
            ("Material", "Vinilo", ""),
            ("Ancho", "19", "mm"),
            ("Longitud", "20", "m"),
            ("Espesor", "0,13", "mm"),
            ("Tensión de aplicación", "Hasta 600", "V"),
            ("Temperatura de operación", "-5 a 105", "°C"),
            ("Comportamiento al fuego", "Autoextinguible", ""),
        ),
        "variantes": (
            variante_lexo("Azul", "lexo-azul", "3210624"),
            variante_lexo("Verde", "lexo-verde", "3210626"),
            variante_lexo("Blanca", "lexo-blanca", "3210628"),
            variante_lexo("Roja", "lexo-roja"),
        ),
    },
    {
        "slug": "cinta-aislante-3m-temflex-165-negra",
        "nombre": "Cinta aislante negra 3M Temflex 165",
        "categoria": "cintas-aislantes",
        "marca": "3m",
        "modelo": "Temflex 165",
        "codigo": "165BK4A",
        "subtitulo": "Cinta vinílica multipropósito",
        "descripcion": (
            "Cinta eléctrica de PVC de uso general para aislación, reparación "
            "de cubiertas, agrupación de cables, identificación y protección "
            "mecánica en aplicaciones de hasta 600 V."
        ),
        "imagen": "3m-temflex-165-negra",
        "etiqueta": "AISLACIÓN",
        "orden": 140,
        "caracteristicas": (
            "Construcción flexible de PVC con adhesivo sensible a la presión",
            "Retardante a la llama y resistente a la humedad",
            "Uso interior y exterior protegido",
        ),
        "especificaciones": (
            ("Material de respaldo", "PVC", ""),
            ("Color", "Negro", ""),
            ("Ancho", "19", "mm"),
            ("Longitud", "18,3", "m"),
            ("Espesor nominal", "0,15", "mm"),
            ("Tensión máxima", "600", "V"),
            ("Temperatura de operación", "0 a 90", "°C"),
            ("Certificaciones", "UL 510, CSA y VDE", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "cinta-goma-autofundente-fsl-20mm-5m",
        "nombre": "Cinta de goma autofundente FSL 20 mm × 5 m",
        "categoria": "cintas-aislantes",
        "marca": "fsl",
        "modelo": "",
        "codigo": None,
        "subtitulo": "Sellado y aislación eléctrica autofundente",
        "descripcion": (
            "Cinta de goma EPR autofundente para conformar una capa continua "
            "de aislación y sellado en empalmes y terminaciones eléctricas de "
            "baja y alta tensión."
        ),
        "imagen": "fsl-autofundente",
        "etiqueta": "AISLACIÓN",
        "orden": 150,
        "caracteristicas": (
            "Goma EPR que se integra sobre sí misma durante la aplicación",
            "Alta capacidad de elongación para adaptarse a la conexión",
            "Apta para aplicaciones de baja y alta tensión",
        ),
        "especificaciones": (
            ("Material", "Goma EPR", ""),
            ("Color", "Negro", ""),
            ("Ancho", "20", "mm"),
            ("Longitud", "5", "m"),
            ("Espesor", "0,8", "mm"),
            ("Elongación", "500", "%"),
            ("Resistencia a la tracción", "≥ 1,7", "MPa"),
            ("Rigidez dieléctrica", "17", "kV/mm"),
        ),
        "variantes": (),
    },
    {
        "slug": "cinta-aislante-pvc-fsl-negra-19mm-16m",
        "nombre": "Cinta aislante negra FSL 19 mm × 16 m",
        "categoria": "cintas-aislantes",
        "marca": "fsl",
        "modelo": "FSL-JY",
        "codigo": None,
        "subtitulo": "Aislación eléctrica de PVC",
        "descripcion": (
            "Cinta adhesiva de PVC negra para aislación y protección de "
            "conductores, empalmes y cableados eléctricos de uso general."
        ),
        "imagen": "fsl-pvc-negra",
        "etiqueta": "AISLACIÓN",
        "orden": 160,
        "caracteristicas": (
            "Adhesión reforzada para trabajos eléctricos de uso general",
            "Resistente al fuego según la información del envase",
            "Formato negro para terminación y protección de cableados",
        ),
        "especificaciones": (
            ("Material", "PVC", ""),
            ("Color", "Negro", ""),
            ("Ancho", "19", "mm"),
            ("Longitud", "16", "m"),
            ("Tensión máxima", "600", "V"),
            ("Temperatura máxima", "80", "°C"),
        ),
        "variantes": (),
    },
)


class Command(BaseCommand):
    help = (
        "Valida o carga ferrules y cintas aislantes a partir de las "
        "imágenes proporcionadas."
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
            clave: origen / datos["origen"]
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

        total_variantes = sum(len(item["variantes"]) for item in PRODUCTOS)
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

    def _copiar_imagen(self, datos, origen, sobrescribir=False):
        destino = self._destino_imagen(datos)

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

    def _destino_imagen(self, datos):
        return (
            PurePosixPath("productos")
            / "catalogo"
            / PurePosixPath(datos["destino"])
        ).as_posix()

    def _crear_categorias(self):
        familia, _ = Categoria.objects.update_or_create(
            slug="conexion-y-aislacion",
            defaults={
                "nombre": "Conexión y aislación",
                "padre": None,
                "orden": 30,
                "activa": True,
            },
        )
        definiciones = (
            ("terminales-puntera", "Terminales puntera", 1),
            ("cintas-aislantes", "Cintas aislantes", 2),
        )
        categorias = {}
        for slug, nombre, orden in definiciones:
            categorias[slug], _ = Categoria.objects.update_or_create(
                slug=slug,
                defaults={
                    "nombre": nombre,
                    "padre": familia,
                    "orden": orden,
                    "activa": True,
                },
            )
        return categorias

    def _crear_marcas(self):
        marcas = {}
        for slug, nombre in (("3m", "3M"), ("fsl", "FSL"), ("lexo", "LEXO")):
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
                "codigo": definicion["codigo"],
                "subtitulo": definicion["subtitulo"],
                "descripcion": definicion["descripcion"],
                "imagen": destinos[definicion["imagen"]],
                "texto_alternativo": IMAGENES[definicion["imagen"]]["alt"],
                "etiqueta_visual": definicion["etiqueta"],
                "orden": definicion["orden"],
                "publicado": publicar,
            },
        )

        textos = set(definicion["caracteristicas"])
        producto.caracteristicas.exclude(texto__in=textos).delete()
        for orden, texto in enumerate(definicion["caracteristicas"], start=1):
            CaracteristicaProducto.objects.update_or_create(
                producto=producto,
                texto=texto,
                defaults={"orden": orden},
            )

        nombres_especificaciones = {
            nombre for nombre, _valor, _unidad in definicion["especificaciones"]
        }
        producto.especificaciones.exclude(
            nombre__in=nombres_especificaciones
        ).delete()
        for orden, (nombre, valor, unidad) in enumerate(
            definicion["especificaciones"], start=1
        ):
            EspecificacionProducto.objects.update_or_create(
                producto=producto,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

        variantes = {}
        nombres_variantes = {item["nombre"] for item in definicion["variantes"]}
        retirar_variantes(producto.variantes.exclude(nombre__in=nombres_variantes))
        for orden, datos in enumerate(definicion["variantes"], start=1):
            variante, _ = VarianteProducto.objects.update_or_create(
                producto=producto,
                nombre=datos["nombre"],
                defaults={
                    "modelo": datos["modelo"],
                    "codigo": datos["codigo"],
                    "imagen": destinos[datos["imagen"]],
                    "disponible": True,
                    "orden": orden,
                },
            )
            variantes[datos["imagen"]] = variante
            nombres = {
                nombre for nombre, _valor, _unidad in datos["especificaciones"]
            }
            variante.especificaciones.exclude(nombre__in=nombres).delete()
            for posicion, (nombre, valor, unidad) in enumerate(
                datos["especificaciones"], start=1
            ):
                EspecificacionVariante.objects.update_or_create(
                    variante=variante,
                    nombre=nombre,
                    defaults={
                        "valor": valor,
                        "unidad": unidad,
                        "orden": posicion,
                    },
                )

        claves_imagen = [definicion["imagen"]]
        claves_imagen.extend(item["imagen"] for item in definicion["variantes"])
        claves_imagen = list(dict.fromkeys(claves_imagen))
        claves_importacion = {
            f"carga-ferrules-cintas-{clave}" for clave in claves_imagen
        }
        producto.imagenes_catalogo.filter(
            clave__startswith="carga-ferrules-cintas-"
        ).exclude(clave__in=claves_importacion).delete()
        for orden, clave in enumerate(claves_imagen, start=1):
            imagen, _ = ImagenProducto.objects.update_or_create(
                clave=f"carga-ferrules-cintas-{clave}",
                defaults={
                    "producto": producto,
                    "imagen": destinos[clave],
                    "texto_alternativo": IMAGENES[clave]["alt"],
                    "orden": orden,
                },
            )
            variante = variantes.get(clave)
            imagen.variantes.set([variante] if variante else [])
