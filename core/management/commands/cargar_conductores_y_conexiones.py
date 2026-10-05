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
    Producto,
    VarianteProducto,
)


def imagen(origen, destino, alt):
    return {"origen": origen, "destino": destino, "alt": alt}


IMAGENES = {
    "barra-bronce-4p": imagen(
        "Barra Conexión Bronce Aislado 4P Riel Din.png",
        "barras/barra-conexion-bronce-4p-riel-din.png",
        "Barra de conexión de bronce aislada de 4 polos para riel DIN",
    ),
    "barra-bronce-6p": imagen(
        "Barra Conexión Bronce Aislado 6P Riel Din.png",
        "barras/barra-conexion-bronce-6p-riel-din.png",
        "Barra de conexión de bronce aislada de 6 polos para riel DIN",
    ),
    "barra-bronce-8p": imagen(
        "Barra Conexión Bronce Aislado 8P Riel Din.png",
        "barras/barra-conexion-bronce-8p-riel-din.png",
        "Barra de conexión de bronce aislada de 8 polos para riel DIN",
    ),
    "barra-bronce-12p": imagen(
        "Barra Conexión Bronce Aislado 12P Riel Din.png",
        "barras/barra-conexion-bronce-12p-riel-din.png",
        "Barra de conexión de bronce aislada de 12 polos para riel DIN",
    ),
    "barra-tetrapolar-4x4": imagen(
        "BARRA REPARTIDORA TETRAPOLAR 4X4 125A.png",
        "barras/barra-repartidora-tetrapolar-4x4-125a.png",
        "Barra repartidora tetrapolar 4 por 4 de 125 amperios",
    ),
    "barra-tetrapolar-4x7": imagen(
        "BARRA REPARTIDORA TETRAPOLAR 4X7 125A.png",
        "barras/barra-repartidora-tetrapolar-4x7-125a.png",
        "Barra repartidora tetrapolar 4 por 7 de 125 amperios",
    ),
    "barra-tetrapolar-4x11": imagen(
        "BARRA REPARTIDORA TETRAPOLAR 4X11 125A.png",
        "barras/barra-repartidora-tetrapolar-4x11-125a.png",
        "Barra repartidora tetrapolar 4 por 11 de 125 amperios",
    ),
    "barra-tetrapolar-4x15": imagen(
        "BARRA REPARTIDORA TETRAPOLAR 4X15 125A.png",
        "barras/barra-repartidora-tetrapolar-4x15-125a.png",
        "Barra repartidora tetrapolar 4 por 15 de 125 amperios",
    ),
    "barra-bipolar-2x7": imagen(
        "Barra Repartidora Regleta Bipolar 2x7 Polos 125 Amperios.png",
        "barras/barra-repartidora-bipolar-2x7-125a.png",
        "Barra repartidora bipolar 2 por 7 polos de 125 amperios",
    ),
    "barra-bipolar-2x11": imagen(
        "Barra Repartidora Regleta Bipolar 2x11 Polos 125 Amperios.png",
        "barras/barra-repartidora-bipolar-2x11-125a.png",
        "Barra repartidora bipolar 2 por 11 polos de 125 amperios",
    ),
    "barra-bipolar-2x15": imagen(
        "Barra Repartidora Regleta Bipolar 2x15Polos 125 Amperios.png",
        "barras/barra-repartidora-bipolar-2x15-125a.png",
        "Barra repartidora bipolar 2 por 15 polos de 125 amperios",
    ),
    "borne-gris": imagen(
        "BORNE GRIS 4.0.png",
        "bornes/borne-paso-gris-riel-din.png",
        "Borne de paso gris para montaje en riel DIN",
    ),
    "borne-tierra": imagen(
        "BORNE DE TIERRA 4,0.png",
        "bornes/borne-tierra-verde-amarillo-riel-din.png",
        "Borne de tierra verde y amarillo para montaje en riel DIN",
    ),
}


CABLES = {
    "1-5-negro": "Cable Libre de Halóge 1,5 mm2 Negro.png",
    "1-5-azul": "Cable Libre de Halógeno 1,5 mm2 azul.png",
    "1-5-blanco": "Cable Libre de Halógeno 1,5 mm2 Blanco.png",
    "1-5-verde": "Cable Libre de Halógeno 1,5 mm2 Verde.png",
    "1-5-rojo": "Cable Libre de Halógeno 1,5 mm2 Rojo.png",
    "2-5-negro": "Cable Libre de Halógeno 2,5 mm2  Negro.png",
    "2-5-azul": "Cable Libre de Halógeno 2,5 mm2  Azul.png",
    "2-5-blanco": "Cable Libre de Halógeno 2,5 mm2  Blanco.png",
    "2-5-verde": "Cable Libre de Halógeno 2,5 mm2  Verde.png",
    "2-5-rojo": "Cable Libre de Halógeno 2,5 mm2 Rojo.png",
    "4-negro": "Cable Libre de Halógeno 4mm2 Negro.png",
    "4-azul": "Cable Libre de Halógeno 4mm2 Azul.png",
    "4-blanco": "Cable Libre de Halógeno 4mm2 Blanco.png",
    "4-verde": "Cable Libre de Halógeno 4mm2 Verde.png",
    "4-rojo": "Cable Libre de Halógeno 4mm2 Rojo.png",
    "6-negro": "Cable Libre de Halógeno 6mm2  Negro.png",
    "6-azul": "Cable Libre de Halógeno 6mm2  Azul.png",
    "6-blanco": "Cable Libre de Halógeno 6mm2  Blanco.png",
    "6-verde": "Cable Libre de Halógeno 6mm2  Verde.png",
    "6-rojo": "Cable Libre de Halógeno 6mm2 Rojo.png",
}

for clave, origen in CABLES.items():
    seccion, color = clave.rsplit("-", 1)
    seccion_legible = {"1-5": "1,5", "2-5": "2,5"}.get(seccion, seccion)
    IMAGENES[f"cable-{clave}"] = imagen(
        origen,
        f"cables/cable-libre-halogeno-{clave}.png",
        f"Cable flexible libre de halógenos de {seccion_legible} mm², color {color}",
    )


def variante(nombre, codigo, clave_imagen, especificaciones):
    return {
        "nombre": nombre,
        "codigo": codigo,
        "imagen": clave_imagen,
        "especificaciones": especificaciones,
    }


def variantes_barra(prefijo, formatos, amperaje=None):
    resultado = []
    for orden, formato in enumerate(formatos, start=1):
        especificaciones = [("Configuración", formato, "")]
        if amperaje:
            especificaciones.append(("Corriente nominal", amperaje, "A"))
        resultado.append(
            variante(
                formato,
                f"PH-{prefijo.upper()}-{formato.upper()}",
                f"barra-{prefijo}-{formato.lower()}",
                tuple(especificaciones),
            )
        )
    return tuple(resultado)


COLORES = ("Negro", "Azul", "Blanco", "Verde", "Rojo")


def variantes_cable():
    resultado = []
    secciones = (("1,5", "1-5"), ("2,5", "2-5"), ("4", "4"), ("6", "6"))
    for seccion, clave_seccion in secciones:
        for color in COLORES:
            clave_color = color.lower()
            resultado.append(
                variante(
                    f"{seccion} mm² · {color}",
                    f"PH-LH-{clave_seccion.upper()}-{clave_color.upper()}",
                    f"cable-{clave_seccion}-{clave_color}",
                    (("Sección", seccion, "mm²"), ("Color", color, "")),
                )
            )
    # El usuario indicó expresamente que las presentaciones de 10 mm² deben
    # reutilizar las fotografías por color de 6 mm².
    for color in ("Rojo", "Verde", "Blanco", "Azul"):
        clave_color = color.lower()
        resultado.append(
            variante(
                f"10 mm² · {color}",
                f"PH-LH-10-{clave_color.upper()}",
                f"cable-6-{clave_color}",
                (("Sección", "10", "mm²"), ("Color", color, "")),
            )
        )
    return tuple(resultado)


PRODUCTOS = (
    {
        "slug": "barra-conexion-bronce-aislada-riel-din",
        "nombre": "Barra de conexión de bronce aislada para riel DIN",
        "categoria": "barras-distribucion",
        "subtitulo": "Distribución compacta para tableros eléctricos",
        "descripcion": (
            "Barra aislada para organizar conexiones de conductores dentro de "
            "tableros eléctricos. Disponible en cuatro tamaños para adaptar la "
            "cantidad de puntos de conexión a cada montaje."
        ),
        "imagen": "barra-bronce-4p",
        "etiqueta": "DISTRIBUCIÓN",
        "orden": 170,
        "caracteristicas": (
            "Cuerpo aislado para una instalación ordenada",
            "Montaje compatible con riel DIN",
            "Presentaciones de 4, 6, 8 y 12 polos",
        ),
        "especificaciones": (("Material conductor", "Bronce", ""), ("Montaje", "Riel DIN", "")),
        "variantes": variantes_barra("bronce", ("4P", "6P", "8P", "12P")),
    },
    {
        "slug": "barra-repartidora-tetrapolar-125a",
        "nombre": "Barra repartidora tetrapolar 125 A",
        "categoria": "barras-distribucion",
        "subtitulo": "Distribución tetrapolar para tableros",
        "descripcion": (
            "Barra repartidora tetrapolar con cubierta aislante para distribuir "
            "alimentación en tableros eléctricos y mantener las conexiones "
            "agrupadas y protegidas."
        ),
        "imagen": "barra-tetrapolar-4x4",
        "etiqueta": "DISTRIBUCIÓN",
        "orden": 180,
        "caracteristicas": (
            "Configuración tetrapolar",
            "Cubierta aislante transparente",
            "Cuatro capacidades de distribución",
        ),
        "especificaciones": (("Polos", "4", ""), ("Corriente nominal", "125", "A")),
        "variantes": variantes_barra("tetrapolar", ("4x4", "4x7", "4x11", "4x15"), "125"),
    },
    {
        "slug": "barra-repartidora-bipolar-125a",
        "nombre": "Barra repartidora bipolar 125 A",
        "categoria": "barras-distribucion",
        "subtitulo": "Distribución bipolar para tableros",
        "descripcion": (
            "Barra repartidora bipolar con cubierta aislante para centralizar y "
            "distribuir conexiones dentro de tableros eléctricos."
        ),
        "imagen": "barra-bipolar-2x7",
        "etiqueta": "DISTRIBUCIÓN",
        "orden": 190,
        "caracteristicas": (
            "Configuración bipolar",
            "Cubierta aislante transparente",
            "Presentaciones de 7, 11 y 15 polos por línea",
        ),
        "especificaciones": (("Polos", "2", ""), ("Corriente nominal", "125", "A")),
        "variantes": variantes_barra("bipolar", ("2x7", "2x11", "2x15"), "125"),
    },
    {
        "slug": "cable-flexible-libre-halogenos",
        "nombre": "Cable flexible libre de halógenos",
        "categoria": "cables-libres-halogeno",
        "subtitulo": "Conductor para instalaciones eléctricas",
        "descripcion": (
            "Cable flexible libre de halógenos para instalaciones eléctricas "
            "que requieren distintas secciones y colores de identificación. "
            "Consulte la presentación y longitud disponibles al cotizar."
        ),
        "imagen": "cable-1-5-negro",
        "etiqueta": "CONDUCTORES",
        "orden": 200,
        "caracteristicas": (
            "Aislación libre de halógenos",
            "Conductor flexible para canalizaciones eléctricas",
            "Secciones de 1,5 a 10 mm² en varios colores",
        ),
        "especificaciones": (("Tipo", "Cable flexible libre de halógenos", ""), ("Rango de sección", "1,5-10", "mm²")),
        "variantes": variantes_cable(),
    },
    {
        "slug": "borne-paso-gris-riel-din",
        "nombre": "Borne de paso gris para riel DIN",
        "categoria": "bornes-riel-din",
        "subtitulo": "Conexión modular de conductores",
        "descripcion": (
            "Borne de paso gris para organizar y conectar conductores en "
            "tableros eléctricos mediante montaje modular sobre riel DIN."
        ),
        "imagen": "borne-gris",
        "etiqueta": "CONEXIÓN",
        "orden": 210,
        "caracteristicas": (
            "Montaje modular sobre riel DIN",
            "Cuerpo aislante color gris",
            "Cuatro secciones nominales disponibles",
        ),
        "especificaciones": (("Tipo", "Borne de paso", ""), ("Color", "Gris", ""), ("Montaje", "Riel DIN", "")),
        "variantes": tuple(
            variante(
                f"BORNE GRIS {seccion}",
                f"PH-BG-{seccion.replace(',', '-')}",
                "borne-gris",
                (("Sección nominal", seccion, "mm²"), ("Color", "Gris", "")),
            )
            for seccion in ("4,0", "6,0", "10", "16")
        ),
    },
    {
        "slug": "borne-tierra-riel-din",
        "nombre": "Borne de tierra para riel DIN",
        "categoria": "bornes-riel-din",
        "subtitulo": "Conexión de protección a tierra",
        "descripcion": (
            "Borne verde y amarillo para conexiones de protección a tierra en "
            "tableros eléctricos, con montaje modular sobre riel DIN."
        ),
        "imagen": "borne-tierra",
        "etiqueta": "PUESTA A TIERRA",
        "orden": 220,
        "caracteristicas": (
            "Identificación verde y amarilla",
            "Montaje modular sobre riel DIN",
            "Dos secciones nominales disponibles",
        ),
        "especificaciones": (("Tipo", "Borne de tierra", ""), ("Montaje", "Riel DIN", "")),
        "variantes": tuple(
            variante(
                f"BORNE DE TIERRA {seccion}",
                f"PH-BT-{seccion.replace(',', '-')}",
                "borne-tierra",
                (("Sección nominal", seccion, "mm²"), ("Función", "Protección a tierra", "")),
            )
            for seccion in ("4,0", "6,0")
        ),
    },
)


class Command(BaseCommand):
    help = "Valida o carga conductores, barras repartidoras y bornes."

    def add_arguments(self, parser):
        parser.add_argument("--origen", type=Path, default=Path.home() / "Downloads")
        parser.add_argument("--aplicar", action="store_true")
        parser.add_argument("--no-publicar", action="store_true")
        parser.add_argument("--sobrescribir-imagenes", action="store_true")

    def handle(self, *args, **options):
        origen = options["origen"].expanduser().resolve()
        rutas = {clave: origen / datos["origen"] for clave, datos in IMAGENES.items()}
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
            self.stdout.write(self.style.WARNING("No se modificó el catálogo. Use --aplicar."))
            return

        destinos = {
            clave: self._copiar_imagen(datos, rutas[clave], options["sobrescribir_imagenes"])
            for clave, datos in IMAGENES.items()
        }
        with transaction.atomic():
            categorias = self._crear_categorias()
            for definicion in PRODUCTOS:
                self._cargar_producto(definicion, categorias, destinos, not options["no_publicar"])

        estado = "como borradores" if options["no_publicar"] else "publicados"
        self.stdout.write(self.style.SUCCESS(f"Carga terminada: {len(PRODUCTOS)} productos {estado}."))

    def _destino_imagen(self, datos):
        return (PurePosixPath("productos/catalogo/conductores-conexiones") / datos["destino"]).as_posix()

    def _copiar_imagen(self, datos, origen, sobrescribir=False):
        destino = self._destino_imagen(datos)
        if sobrescribir and default_storage.exists(destino):
            default_storage.delete(destino)
        if not default_storage.exists(destino):
            with origen.open("rb") as archivo:
                guardado = default_storage.save(destino, File(archivo))
            if guardado != destino:
                raise CommandError(f"El almacenamiento cambió {destino} por {guardado}.")
        return destino

    def _crear_categorias(self):
        conexion, _ = Categoria.objects.update_or_create(
            slug="conexion-y-aislacion",
            defaults={"nombre": "Conexión y aislación", "padre": None, "orden": 30, "activa": True},
        )
        conductores, _ = Categoria.objects.update_or_create(
            slug="conductores-electricos",
            defaults={"nombre": "Conductores eléctricos", "padre": None, "orden": 35, "activa": True},
        )
        definiciones = (
            ("barras-distribucion", "Barras de conexión y distribución", conexion, 3),
            ("bornes-riel-din", "Bornes para riel DIN", conexion, 4),
            ("cables-libres-halogeno", "Cables libres de halógenos", conductores, 1),
        )
        categorias = {}
        for slug, nombre, padre, orden in definiciones:
            categorias[slug], _ = Categoria.objects.update_or_create(
                slug=slug,
                defaults={"nombre": nombre, "padre": padre, "orden": orden, "activa": True},
            )
        Categoria.objects.filter(slug="mecanismos-electricos").update(
            nombre="Interruptores, enchufes y accesorios"
        )
        return categorias

    def _cargar_producto(self, definicion, categorias, destinos, publicar):
        producto, _ = Producto.objects.update_or_create(
            slug=definicion["slug"],
            defaults={
                "categoria": categorias[definicion["categoria"]],
                "nombre": definicion["nombre"],
                "marca_nueva": None,
                "marca": "",
                "modelo": "",
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

        textos = set(definicion["caracteristicas"])
        producto.caracteristicas.exclude(texto__in=textos).delete()
        for orden, texto in enumerate(definicion["caracteristicas"], start=1):
            CaracteristicaProducto.objects.update_or_create(
                producto=producto, texto=texto, defaults={"orden": orden}
            )

        nombres = {nombre for nombre, _valor, _unidad in definicion["especificaciones"]}
        producto.especificaciones.exclude(nombre__in=nombres).delete()
        for orden, (nombre, valor, unidad) in enumerate(definicion["especificaciones"], start=1):
            EspecificacionProducto.objects.update_or_create(
                producto=producto,
                nombre=nombre,
                defaults={"valor": valor, "unidad": unidad, "orden": orden},
            )

        variantes_por_imagen = {}
        nombres_variantes = {item["nombre"] for item in definicion["variantes"]}
        retirar_variantes(producto.variantes.exclude(nombre__in=nombres_variantes))
        for orden, datos in enumerate(definicion["variantes"], start=1):
            item, _ = VarianteProducto.objects.update_or_create(
                producto=producto,
                nombre=datos["nombre"],
                defaults={
                    "modelo": "",
                    "codigo": datos["codigo"],
                    "imagen": destinos[datos["imagen"]],
                    "disponible": True,
                    "orden": orden,
                },
            )
            variantes_por_imagen.setdefault(datos["imagen"], []).append(item)
            nombres_especificaciones = {
                nombre for nombre, _valor, _unidad in datos["especificaciones"]
            }
            item.especificaciones.exclude(nombre__in=nombres_especificaciones).delete()
            for posicion, (nombre, valor, unidad) in enumerate(datos["especificaciones"], start=1):
                EspecificacionVariante.objects.update_or_create(
                    variante=item,
                    nombre=nombre,
                    defaults={"valor": valor, "unidad": unidad, "orden": posicion},
                )

        claves = list(dict.fromkeys([definicion["imagen"]] + [v["imagen"] for v in definicion["variantes"]]))
        prefijo = "carga-conductores-conexiones-"
        claves_importacion = {f"{prefijo}{clave}" for clave in claves}
        producto.imagenes_catalogo.filter(clave__startswith=prefijo).exclude(
            clave__in=claves_importacion
        ).delete()
        for orden, clave in enumerate(claves, start=1):
            imagen_catalogo, _ = ImagenProducto.objects.update_or_create(
                clave=f"{prefijo}{clave}",
                defaults={
                    "producto": producto,
                    "imagen": destinos[clave],
                    "texto_alternativo": IMAGENES[clave]["alt"],
                    "orden": orden,
                },
            )
            imagen_catalogo.variantes.set(variantes_por_imagen.get(clave, []))
