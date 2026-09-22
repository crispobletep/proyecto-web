import csv
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

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


COLUMNAS_REQUERIDAS = {
    "familia",
    "titulo",
    "archivo",
    "codigos",
    "uso",
    "lamina_fuente",
}

COLORES = {
    "BL": "Blanco",
    "NE": "Negro",
    "CH": "Champagne",
    "CA": "Café",
}

CARACTERISTICAS = {
    "plafones-led": (
        "Iluminación LED de bajo consumo",
        "Diseño delgado para instalación interior",
        "Disponible en distintas potencias",
    ),
    "canalizacion-electrica": (
        "Componente para canalización de conductores eléctricos",
        "Disponible en varios diámetros nominales",
        "Apto para instalaciones residenciales, comerciales e industriales",
    ),
    "staford-enchufes": (
        "Mecanismo modular de la línea STAFORD",
        "Disponible en diferentes colores",
        "Uso residencial y comercial",
    ),
    "staford-modulos": (
        "Módulo complementario de la línea STAFORD",
        "Diseño modular para placas compatibles",
    ),
    "staford-placas": (
        "Placa modular de la línea STAFORD",
        "Disponible en diferentes colores",
    ),
    "fotoceldas": (
        "Control automático de iluminación",
        "Uso residencial y comercial",
    ),
    "kalop-casquetes": (
        "Conexión modular industrial KALOP",
        "Sistema de montaje seguro",
    ),
    "kalop-modulos": (
        "Módulo de conexión industrial KALOP",
        "Compatible con casquetes de la misma cantidad de polos",
    ),
    "kalop-accesorios": (
        "Accesorio para el sistema modular KALOP",
        "Uso residencial, comercial e industrial",
    ),
    "tableros-cnc": (
        "Gabinete para instalaciones eléctricas exteriores",
        "Riel DIN incluido",
        "Cierre y entradas protegidas",
    ),
}


@dataclass(frozen=True)
class FilaManifiesto:
    numero: int
    familia: str
    titulo: str
    archivo: str
    codigos: tuple[str, ...]
    uso: str
    lamina_fuente: str
    ruta_imagen: Path


@dataclass
class GrupoProducto:
    clave: str
    filas: list[FilaManifiesto]


def clave_grupo(fila):
    primer_codigo = fila.codigos[0]

    if fila.familia in {"staford-enchufes", "staford-placas"}:
        codigo_base = primer_codigo.rsplit("-", 1)[0]
        return f"{fila.familia}:{codigo_base}"

    if fila.familia in {
        "kalop-casquetes",
        "kalop-modulos",
        "kalop-accesorios",
        "tableros-cnc",
    }:
        return fila.familia

    return f"{fila.familia}:{fila.archivo}"


def nombre_producto(grupo):
    fila = grupo.filas[0]

    if fila.familia == "staford-enchufes":
        nombre = re.sub(
            r"\s+(blanco|negro|champagne|cafe|café)$",
            "",
            fila.titulo,
            flags=re.IGNORECASE,
        )
        return f"{nombre} STAFORD"

    if fila.familia == "staford-placas":
        puestos = re.search(r"(\d+)\s+puesto", fila.titulo, re.IGNORECASE)
        cantidad = int(puestos.group(1)) if puestos else 1
        palabra = "puesto" if cantidad == 1 else "puestos"
        return f"Placa STAFORD de {cantidad} {palabra}"

    nombres_especiales = {
        "kalop-casquetes": "Casquetes industriales KALOP",
        "kalop-modulos": "Módulos para casquete KALOP",
        "kalop-accesorios": "Bases para casquete KALOP",
        "tableros-cnc": "Tableros eléctricos de exterior CNC IP65",
    }
    return nombres_especiales.get(fila.familia, fila.titulo)


def slug_producto(grupo):
    return f"catalogo-{slugify(grupo.clave)}"[:200].rstrip("-")


def clasificacion(fila):
    if fila.familia == "plafones-led":
        return (
            ("iluminacion", "Iluminación", 20),
            ("plafones-led", "Plafones LED", 10),
        )

    if fila.familia == "canalizacion-electrica":
        titulo = fila.titulo.upper()
        if "EMT" in titulo:
            subcategoria = ("canalizacion-emt", "Canalización EMT", 10)
        elif "PVC" in titulo:
            subcategoria = ("canalizacion-pvc", "Canalización PVC", 20)
        else:
            subcategoria = (
                "conduit-flexible",
                "Conduit flexible y accesorios",
                30,
            )
        return (
            ("canalizacion-electrica", "Canalización eléctrica", 30),
            subcategoria,
        )

    if fila.familia.startswith("staford-"):
        subcategorias = {
            "staford-enchufes": ("enchufes", "Enchufes", 10),
            "staford-modulos": ("modulos-electricos", "Módulos eléctricos", 20),
            "staford-placas": ("placas-electricas", "Placas eléctricas", 30),
        }
        return (
            ("mecanismos-electricos", "Mecanismos eléctricos", 40),
            subcategorias[fila.familia],
        )

    if fila.familia == "fotoceldas":
        return (
            ("control-iluminacion", "Control de iluminación", 50),
            ("fotoceldas-y-bases", "Fotoceldas, bases y soportes", 10),
        )

    if fila.familia.startswith("kalop-"):
        subcategorias = {
            "kalop-casquetes": ("casquetes-industriales", "Casquetes industriales", 10),
            "kalop-modulos": ("modulos-industriales", "Módulos industriales", 20),
            "kalop-accesorios": ("bases-industriales", "Bases industriales", 30),
        }
        return (
            ("conexiones-industriales", "Conexiones industriales", 60),
            subcategorias[fila.familia],
        )

    if fila.familia == "tableros-cnc":
        return (
            ("tableros-electricos", "Tableros eléctricos", 70),
            ("tableros-exterior", "Tableros de exterior", 10),
        )

    raise CommandError(f"Familia sin clasificación: {fila.familia}")


def marca_fila(fila):
    codigo = fila.codigos[0]

    if fila.familia == "plafones-led":
        prefijo = codigo.split("-", 1)[0]
        return {
            "AVC": ("avc", "AVC"),
            "FLS": ("fls", "FLS"),
            "YLM": ("yellmax", "Yellmax"),
        }.get(prefijo)

    if fila.familia.startswith("staford-"):
        return "staford", "STAFORD"

    if fila.familia == "fotoceldas":
        prefijo = codigo.split("-", 1)[0]
        return {
            "LEX": ("lexo", "LEXO"),
            "LEG": ("legrand", "Legrand"),
            "CHT": ("chint", "CHINT"),
            "STF": ("staford", "STAFORD"),
        }.get(prefijo)

    if fila.familia.startswith("kalop-"):
        return "kalop", "KALOP"

    if fila.familia == "tableros-cnc":
        return "cnc", "CNC"

    return None


def datos_variante(fila, codigo):
    especificaciones = []

    if fila.familia == "plafones-led":
        coincidencia = re.search(r"-(\d+)([ES])$", codigo)
        if not coincidencia:
            raise CommandError(f"Código LED no reconocido: {codigo}")
        potencia, montaje_codigo = coincidencia.groups()
        montaje = "Embutido" if montaje_codigo == "E" else "Sobrepuesto"
        medida = re.search(r"(60 x 60|120 x 30|120 x 60) cm", fila.titulo)
        especificaciones = [
            ("Potencia", potencia, "W"),
            ("Instalación", montaje, ""),
        ]
        if medida:
            especificaciones.append(("Dimensiones", medida.group(1), "cm"))
        return f"{potencia} W", especificaciones

    if fila.familia == "canalizacion-electrica":
        diametro = codigo.rsplit("-", 1)[-1]
        return f"{diametro} mm", [("Diámetro nominal", diametro, "mm")]

    if fila.familia in {"staford-enchufes", "staford-placas"}:
        color_codigo = codigo.rsplit("-", 1)[-1]
        color = COLORES.get(color_codigo, color_codigo)
        especificaciones.append(("Color", color, ""))

        corriente = re.search(r"(10/16|10)\s*A", fila.titulo)
        if corriente:
            especificaciones.extend(
                (
                    ("Corriente nominal", corriente.group(1), "A"),
                    ("Tensión nominal", "250", "V"),
                )
            )
        puestos = re.search(r"(\d+)\s+puesto", fila.titulo)
        if puestos:
            especificaciones.append(("Puestos", puestos.group(1), ""))
        return color, especificaciones

    if fila.familia == "staford-modulos":
        return "Presentación única", []

    if fila.familia == "fotoceldas":
        datos_fotocelda = {
            "LEX-FC01": (("Corriente nominal", "10", "A"), ("Protección", "IP44", ""), ("Tensión", "220", "V")),
            "LEG-412898": (("Corriente nominal", "10", "A"), ("Protección", "IP54", ""), ("Tensión", "220", "V")),
            "CHT-NY01": (("Corriente nominal", "10", "A"), ("Protección", "IP65", ""), ("Tensión", "220", "V")),
            "STF-FC10": (("Corriente nominal", "10", "A"), ("Protección", "IP44", ""), ("Tensión", "220", "V")),
            "LEX-BF01": (("Pines", "3", ""),),
            "LEG-412899": (("Pines", "3", ""),),
            "CHT-BY01": (("Pines", "3", ""),),
            "STF-BF10": (("Pines", "3", ""),),
        }
        return "Presentación única", list(datos_fotocelda.get(codigo, ()))

    if fila.familia in {"kalop-casquetes", "kalop-modulos"}:
        polos = re.search(r"(\d+)P$", codigo)
        cantidad = polos.group(1) if polos else ""
        especificaciones.append(("Polos", cantidad, ""))
        datos_casquete = {
            "KAL-2P": (("Corriente nominal", "10/16", "A"), ("Tensión nominal", "250", "V")),
            "KAL-3P": (("Corriente nominal", "16", "A"), ("Tensión nominal", "250", "V")),
            "KAL-4P": (("Corriente nominal", "16", "A"), ("Tensión nominal", "400", "V")),
            "KAL-6P": (("Corriente nominal", "16", "A"), ("Tensión nominal", "500", "V")),
        }
        especificaciones.extend(datos_casquete.get(codigo, ()))
        return f"{cantidad} polos", especificaciones

    if fila.familia == "kalop-accesorios":
        nombre = re.sub(r"\s+Kalop$", "", fila.titulo, flags=re.IGNORECASE)
        return nombre, []

    if fila.familia == "tableros-cnc":
        polos = re.search(r"-TB-(\d+)P$", codigo)
        cantidad = polos.group(1) if polos else ""
        return f"{cantidad} polos", [
            ("Capacidad", cantidad, "polos"),
            ("Protección", "IP65", ""),
        ]

    return codigo, []


def especificaciones_producto(grupo):
    fila = grupo.filas[0]

    if fila.familia == "plafones-led":
        medida = re.search(r"(60 x 60|120 x 30|120 x 60) cm", fila.titulo)
        montaje = "Embutido" if "embutido" in fila.titulo else "Sobrepuesto"
        datos = [("Tecnología", "LED", ""), ("Instalación", montaje, "")]
        if medida:
            datos.append(("Dimensiones", medida.group(1), "cm"))
        return datos

    if fila.familia == "canalizacion-electrica":
        titulo = fila.titulo.upper()
        if "EMT" in titulo:
            return [("Sistema", "EMT", ""), ("Material", "Acero galvanizado", "")]
        if "PVC" in titulo:
            return [("Sistema", "PVC eléctrico", "")]
        if "HALÓGENO" in titulo:
            return [("Tipo", "Libre de halógeno", "")]
        return [("Tipo", "Conduit flexible", "")]

    if fila.familia == "tableros-cnc":
        return [("Protección", "IP65", ""), ("Montaje", "Exterior", "")]

    return []


class Command(BaseCommand):
    help = (
        "Valida o importa el manifiesto código-imagen del catálogo. "
        "Sin --aplicar solamente valida y muestra el plan."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifiesto",
            type=Path,
            default=(
                Path(settings.MEDIA_ROOT)
                / "productos"
                / "extraidos"
                / "manifesto_imagenes.csv"
            ),
            help="Ruta del CSV generado por extraer_imagenes_catalogo.py.",
        )
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Crea o actualiza categorías, productos, variantes e imágenes.",
        )
        parser.add_argument(
            "--publicar",
            action="store_true",
            help="Publica los productos importados.",
        )
        parser.add_argument(
            "--sobrescribir-imagenes",
            action="store_true",
            help="Vuelve a copiar los archivos aunque ya existan en MEDIA_ROOT.",
        )

    def handle(self, *args, **options):
        manifiesto = options["manifiesto"].expanduser().resolve()
        filas = self._leer_manifiesto(manifiesto)
        grupos = self._agrupar(filas)
        self._validar_colisiones_db(grupos)
        codigos = {codigo for fila in filas for codigo in fila.codigos}

        self.stdout.write(f"Manifiesto: {manifiesto}")
        self.stdout.write(
            f"Plan validado: {len(filas)} imágenes, "
            f"{len(grupos)} productos y {len(codigos)} variantes únicas."
        )

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    "No se modificó la base de datos. Use --aplicar para importar."
                )
            )
            return

        destinos = {
            fila.archivo: self._copiar_imagen(
                fila,
                sobrescribir=options["sobrescribir_imagenes"],
            )
            for fila in filas
        }

        contadores = {
            "productos_creados": 0,
            "productos_actualizados": 0,
            "variantes_creadas": 0,
            "variantes_actualizadas": 0,
            "imagenes_creadas": 0,
            "imagenes_actualizadas": 0,
        }

        with transaction.atomic():
            categorias = self._crear_categorias(filas)
            marcas = self._crear_marcas(filas)

            for orden, grupo in enumerate(grupos.values(), start=1):
                self._cargar_grupo(
                    grupo,
                    orden,
                    categorias,
                    marcas,
                    destinos,
                    publicar=options["publicar"],
                    contadores=contadores,
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Importación terminada: "
                f"{contadores['productos_creados']} productos creados, "
                f"{contadores['productos_actualizados']} actualizados; "
                f"{contadores['variantes_creadas']} variantes creadas, "
                f"{contadores['variantes_actualizadas']} actualizadas; "
                f"{contadores['imagenes_creadas']} imágenes creadas, "
                f"{contadores['imagenes_actualizadas']} actualizadas."
            )
        )

    def _leer_manifiesto(self, manifiesto):
        if not manifiesto.is_file():
            raise CommandError(f"No existe el manifiesto: {manifiesto}")

        raiz = manifiesto.parent.resolve()
        filas = []

        with manifiesto.open("r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            columnas = set(lector.fieldnames or ())
            faltantes = COLUMNAS_REQUERIDAS - columnas
            if faltantes:
                raise CommandError(
                    "Faltan columnas requeridas: " + ", ".join(sorted(faltantes))
                )

            for numero, datos in enumerate(lector, start=2):
                codigos = tuple(
                    codigo.strip()
                    for codigo in datos["codigos"].split("|")
                    if codigo.strip()
                )
                if not codigos:
                    raise CommandError(f"Fila {numero}: no contiene códigos.")
                if len(codigos) != len(set(codigos)):
                    raise CommandError(f"Fila {numero}: contiene códigos repetidos.")

                ruta = (raiz / PurePosixPath(datos["archivo"])).resolve()
                if not ruta.is_relative_to(raiz):
                    raise CommandError(
                        f"Fila {numero}: la imagen sale de la carpeta del manifiesto."
                    )
                if not ruta.is_file():
                    raise CommandError(f"Fila {numero}: no existe {ruta}")

                filas.append(
                    FilaManifiesto(
                        numero=numero,
                        familia=datos["familia"].strip(),
                        titulo=datos["titulo"].strip(),
                        archivo=PurePosixPath(datos["archivo"]).as_posix(),
                        codigos=codigos,
                        uso=datos["uso"].strip(),
                        lamina_fuente=datos["lamina_fuente"].strip(),
                        ruta_imagen=ruta,
                    )
                )

        if not filas:
            raise CommandError("El manifiesto está vacío.")
        return filas

    def _agrupar(self, filas):
        grupos = OrderedDict()
        grupo_por_codigo = {}
        grupo_por_slug = {}

        for fila in filas:
            clave = clave_grupo(fila)
            grupo = grupos.setdefault(clave, GrupoProducto(clave=clave, filas=[]))
            grupo.filas.append(fila)

            for codigo in fila.codigos:
                grupo_anterior = grupo_por_codigo.setdefault(codigo, clave)
                if grupo_anterior != clave:
                    raise CommandError(
                        f"El código {codigo} aparece en productos diferentes: "
                        f"{grupo_anterior} y {clave}."
                    )

        for clave, grupo in grupos.items():
            slug = slug_producto(grupo)
            clave_anterior = grupo_por_slug.setdefault(slug, clave)
            if clave_anterior != clave:
                raise CommandError(
                    f"Los grupos {clave_anterior} y {clave} generan el mismo "
                    f"identificador de producto: {slug}."
                )

        return grupos

    def _validar_colisiones_db(self, grupos):
        grupos_por_codigo = {
            codigo: grupo
            for grupo in grupos.values()
            for fila in grupo.filas
            for codigo in fila.codigos
        }
        existentes = (
            VarianteProducto.objects
            .filter(codigo__in=grupos_por_codigo)
            .select_related("producto")
        )
        for variante in existentes:
            slug_esperado = slug_producto(grupos_por_codigo[variante.codigo])
            if variante.producto.slug != slug_esperado:
                raise CommandError(
                    f"El código {variante.codigo} ya pertenece a "
                    f"{variante.producto} y no se reasignará automáticamente."
                )

    def _copiar_imagen(self, fila, sobrescribir=False):
        destino = (
            PurePosixPath("productos")
            / "catalogo"
            / fila.familia
            / PurePosixPath(fila.archivo).name
        ).as_posix()

        if sobrescribir and default_storage.exists(destino):
            default_storage.delete(destino)

        if not default_storage.exists(destino):
            with fila.ruta_imagen.open("rb") as archivo:
                nombre_guardado = default_storage.save(destino, File(archivo))
            if nombre_guardado != destino:
                raise CommandError(
                    f"El almacenamiento cambió inesperadamente el nombre "
                    f"{destino} por {nombre_guardado}."
                )

        return destino

    def _crear_categorias(self, filas):
        configuraciones = OrderedDict()
        for fila in filas:
            familia, subcategoria = clasificacion(fila)
            configuraciones[(familia[0], subcategoria[0])] = (
                familia,
                subcategoria,
            )

        categorias = {}
        for familia, subcategoria in configuraciones.values():
            familia_obj, _ = Categoria.objects.update_or_create(
                slug=familia[0],
                defaults={
                    "nombre": familia[1],
                    "padre": None,
                    "orden": familia[2],
                    "activa": True,
                },
            )
            subcategoria_obj, _ = Categoria.objects.update_or_create(
                slug=subcategoria[0],
                defaults={
                    "nombre": subcategoria[1],
                    "padre": familia_obj,
                    "orden": subcategoria[2],
                    "activa": True,
                },
            )
            categorias[(familia[0], subcategoria[0])] = subcategoria_obj
        return categorias

    def _crear_marcas(self, filas):
        definiciones = {
            marca_fila(fila)
            for fila in filas
            if marca_fila(fila) is not None
        }
        marcas = {}
        for slug, nombre in sorted(definiciones):
            marcas[slug], _ = Marca.objects.update_or_create(
                slug=slug,
                defaults={"nombre": nombre, "activa": True},
            )
        return marcas

    def _cargar_grupo(
        self,
        grupo,
        orden,
        categorias,
        marcas,
        destinos,
        publicar,
        contadores,
    ):
        fila_inicial = grupo.filas[0]
        familia, subcategoria = clasificacion(fila_inicial)
        marca_definicion = marca_fila(fila_inicial)
        marca = marcas.get(marca_definicion[0]) if marca_definicion else None
        nombre = nombre_producto(grupo)
        slug = slug_producto(grupo)
        descripcion = (
            f"{nombre}. Producto incorporado desde el catálogo técnico; "
            "seleccione la variante correspondiente para solicitar cotización."
        )

        producto, creado = Producto.objects.update_or_create(
            slug=slug,
            defaults={
                "categoria": categorias[(familia[0], subcategoria[0])],
                "nombre": nombre,
                "marca_nueva": marca,
                "marca": "",
                "modelo": "",
                "codigo": None,
                "subtitulo": subcategoria[1],
                "descripcion": descripcion,
                "texto_alternativo": nombre,
                "etiqueta_visual": familia[1].upper(),
                "orden": orden * 10,
            },
        )
        contadores[
            "productos_creados" if creado else "productos_actualizados"
        ] += 1

        producto.imagen.name = destinos[fila_inicial.archivo]
        campos_producto = ["imagen", "actualizado"]
        if creado or publicar:
            producto.publicado = publicar
            campos_producto.append("publicado")
        producto.save(update_fields=campos_producto)

        self._cargar_caracteristicas(producto, fila_inicial.familia)
        self._cargar_especificaciones_producto(producto, grupo)

        variantes = {}
        fila_por_codigo = {}
        for fila in grupo.filas:
            for codigo in fila.codigos:
                fila_por_codigo.setdefault(codigo, fila)

        for posicion, (codigo, fila) in enumerate(fila_por_codigo.items(), start=1):
            nombre_variante, especificaciones = datos_variante(fila, codigo)
            existente = VarianteProducto.objects.filter(codigo=codigo).first()
            if existente and existente.producto_id != producto.id:
                raise CommandError(
                    f"El código {codigo} ya pertenece a {existente.producto} "
                    f"y no se reasignará automáticamente."
                )

            variante, creada = VarianteProducto.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "producto": producto,
                    "nombre": nombre_variante,
                    "modelo": "",
                    "disponible": True,
                    "orden": posicion,
                },
            )
            if not variante.imagen:
                variante.imagen.name = destinos[fila.archivo]
                variante.save(update_fields=("imagen",))

            contadores[
                "variantes_creadas" if creada else "variantes_actualizadas"
            ] += 1
            variantes[codigo] = variante

            for orden_especificacion, (nombre_esp, valor, unidad) in enumerate(
                especificaciones,
                start=1,
            ):
                EspecificacionVariante.objects.update_or_create(
                    variante=variante,
                    nombre=nombre_esp,
                    defaults={
                        "valor": valor,
                        "unidad": unidad,
                        "orden": orden_especificacion,
                    },
                )

        for posicion, fila in enumerate(grupo.filas, start=1):
            clave_imagen = (
                "manifiesto-"
                + slugify(f"{fila.familia}-{fila.archivo}")[:208].rstrip("-")
            )
            imagen, creada = ImagenProducto.objects.update_or_create(
                clave=clave_imagen,
                defaults={
                    "producto": producto,
                    "imagen": destinos[fila.archivo],
                    "texto_alternativo": fila.titulo,
                    "orden": posicion,
                },
            )
            imagen.variantes.set(variantes[codigo] for codigo in fila.codigos)
            contadores[
                "imagenes_creadas" if creada else "imagenes_actualizadas"
            ] += 1

    def _cargar_caracteristicas(self, producto, familia):
        for orden, texto in enumerate(CARACTERISTICAS.get(familia, ()), start=1):
            CaracteristicaProducto.objects.update_or_create(
                producto=producto,
                texto=texto,
                defaults={"orden": orden},
            )

    def _cargar_especificaciones_producto(self, producto, grupo):
        for orden, (nombre, valor, unidad) in enumerate(
            especificaciones_producto(grupo),
            start=1,
        ):
            EspecificacionProducto.objects.update_or_create(
                producto=producto,
                nombre=nombre,
                defaults={
                    "valor": valor,
                    "unidad": unidad,
                    "orden": orden,
                },
            )
