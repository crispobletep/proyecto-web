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
    "medidor-va": {
        "origen": "Piloto LED Voltimetro Y Amperimetro 22mm.png",
        "destino": "pilotos/piloto-led-voltimetro-amperimetro-22mm.png",
        "alt": "Piloto LED voltímetro y amperímetro de 22 mm",
    },
    "voltimetro": {
        "origen": "Piloto Voltimetro Led 22mm.png",
        "destino": "pilotos/piloto-voltimetro-led-22mm.png",
        "alt": "Piloto voltímetro LED de 22 mm con display rojo",
    },
    "piloto-amarillo": {
        "origen": "Luz Piloto Led 220V  AMARILLA.png",
        "destino": "pilotos/luz-piloto-led-220v-amarilla.png",
        "alt": "Luz piloto LED amarilla de 220 V",
    },
    "piloto-rojo": {
        "origen": "Luz Piloto Led 220V roja.png",
        "destino": "pilotos/luz-piloto-led-220v-roja.png",
        "alt": "Luz piloto LED roja de 220 V",
    },
    "piloto-verde": {
        "origen": "Luz Piloto Led 220V Verde.png",
        "destino": "pilotos/luz-piloto-led-220v-verde.png",
        "alt": "Luz piloto LED verde de 220 V",
    },
    "riel-cnc": {
        "origen": "Piloto Led a riel Din 230VAC 50Hz CNC.png",
        "destino": "pilotos/piloto-led-riel-din-cnc-adm-1.png",
        "alt": "Piloto LED CNC ADM-1 para riel DIN de 230 V AC",
    },
    "slim-roja": {
        "origen": "Luz Piloto Led A Riel Din Slim roja.png",
        "destino": "pilotos/cnc-ycd9-1-slim-roja.png",
        "alt": "Luz piloto LED slim roja CNC YCD9-1 para riel DIN",
    },
    "slim-amarilla": {
        "origen": "Luz Piloto Led A Riel Din Slim amarilla.png",
        "destino": "pilotos/cnc-ycd9-1-slim-amarilla.png",
        "alt": "Luz piloto LED slim amarilla CNC YCD9-1 para riel DIN",
    },
    "slim-verde": {
        "origen": "Luz Piloto Led A Riel Din Slim verde.png",
        "destino": "pilotos/cnc-ycd9-1-slim-verde.png",
        "alt": "Luz piloto LED slim verde CNC YCD9-1 para riel DIN",
    },
    "riel-lexo": {
        "origen": "LUZ PILOTO ROJA RIEL DIN.png",
        "destino": "pilotos/luz-piloto-roja-riel-din-lexo-ebs1d.png",
        "alt": "Luz piloto roja LEXO EBS1D para riel DIN",
    },
    "legrand-40a": {
        "origen": "INTERRUPTOR AUT. RX3 1P 40A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c40-419844.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C40",
    },
    "legrand-32a": {
        "origen": "INTERRUPTOR AUT. RX3 1P 32A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c32-419843.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C32",
    },
    "legrand-25a": {
        "origen": "INTERRUPTOR AUT 25A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c25-419842.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C25",
    },
    "legrand-20a": {
        "origen": "INTERRUPTOR AUT. RX3 1P 20A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c20-419841.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C20",
    },
    "legrand-16a": {
        "origen": "INTERRUPTOR AUT 16A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c16-419840.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C16",
    },
    "legrand-10a": {
        "origen": "INTERRUPTOR AUT 10A 6KA C LEGRAND.png",
        "destino": "legrand/legrand-rx3-1p-c10-419838.png",
        "alt": "Interruptor magnetotérmico Legrand RX3 1P C10",
    },
}


def variante_color(nombre, imagen):
    return {
        "nombre": nombre,
        "modelo": "",
        "codigo": None,
        "imagen": imagen,
        "especificaciones": (
            ("Color de señalización", nombre, ""),
            ("Tensión nominal", "220", "V AC"),
            ("Diámetro de montaje", "22", "mm"),
        ),
    }


def variante_legrand(amperaje, referencia, imagen):
    return {
        "nombre": f"{amperaje} A · curva C",
        "modelo": "RX³",
        "codigo": referencia,
        "imagen": imagen,
        "especificaciones": (
            ("Corriente nominal", str(amperaje), "A"),
            ("Referencia Legrand", referencia, ""),
            ("Curva de disparo", "C", ""),
            ("Número de polos", "1P", ""),
        ),
    }


def variante_piloto_slim(nombre, color, imagen):
    return {
        "nombre": nombre,
        "modelo": "YCD9-1",
        "codigo": None,
        "imagen": imagen,
        "especificaciones": (
            ("Color de señalización", color, ""),
            ("Tensión nominal", "230", "V AC"),
            ("Modelo", "YCD9-1", ""),
            ("Montaje", "Riel DIN", ""),
        ),
    }


PRODUCTOS = (
    {
        "slug": "piloto-led-voltimetro-amperimetro-22mm",
        "nombre": "Piloto LED voltímetro y amperímetro 22 mm",
        "categoria": "instrumentos-panel",
        "marca": None,
        "modelo": "",
        "subtitulo": "Medición digital para panel",
        "descripcion": (
            "Indicador digital compacto para supervisar tensión y corriente "
            "desde el frente de un tablero o panel eléctrico."
        ),
        "imagen": "medidor-va",
        "orden": 60,
        "caracteristicas": (
            "Lectura simultánea de voltaje y corriente",
            "Display LED rojo de lectura directa",
            "Montaje empotrable en perforación de 22 mm",
        ),
        "especificaciones": (
            ("Funciones de medición", "Voltímetro y amperímetro", ""),
            ("Tipo de indicador", "Digital LED", ""),
            ("Diámetro de montaje", "22", "mm"),
        ),
        "variantes": (),
    },
    {
        "slug": "piloto-voltimetro-led-22mm",
        "nombre": "Piloto voltímetro LED 22 mm",
        "categoria": "instrumentos-panel",
        "marca": None,
        "modelo": "",
        "subtitulo": "Indicación digital de tensión",
        "descripcion": (
            "Voltímetro digital con display LED rojo para lectura de "
            "tensión en tableros y paneles eléctricos."
        ),
        "imagen": "voltimetro",
        "orden": 70,
        "caracteristicas": (
            "Lectura digital de voltaje",
            "Display LED rojo de tres dígitos",
            "Montaje empotrable en perforación de 22 mm",
        ),
        "especificaciones": (
            ("Función de medición", "Voltímetro", ""),
            ("Tipo de indicador", "Digital LED", ""),
            ("Diámetro de montaje", "22", "mm"),
        ),
        "variantes": (),
    },
    {
        "slug": "luces-piloto-led-220v-22mm",
        "nombre": "Luces piloto LED 220 V de 22 mm",
        "categoria": "pilotos-panel",
        "marca": None,
        "modelo": "",
        "subtitulo": "Señalización luminosa para panel",
        "descripcion": (
            "Luces piloto LED para indicar estados de operación, alarma o "
            "presencia de tensión en tableros y paneles."
        ),
        "imagen": "piloto-rojo",
        "orden": 80,
        "caracteristicas": (
            "Indicación visual de alta identificación",
            "Tecnología LED para uso prolongado",
            "Tres colores disponibles para diferenciar estados",
        ),
        "especificaciones": (
            ("Tensión nominal", "220", "V AC"),
            ("Tecnología luminosa", "LED", ""),
            ("Diámetro de montaje", "22", "mm"),
        ),
        "variantes": (
            variante_color("Amarilla", "piloto-amarillo"),
            variante_color("Roja", "piloto-rojo"),
            variante_color("Verde", "piloto-verde"),
        ),
    },
    {
        "slug": "piloto-led-riel-din-cnc-adm-1",
        "nombre": "Piloto LED para riel DIN CNC ADM-1",
        "categoria": "pilotos-riel-din",
        "marca": "cnc",
        "modelo": "ADM-1",
        "subtitulo": "Señalización modular de tablero",
        "descripcion": (
            "Piloto luminoso modular CNC para indicar presencia de tensión "
            "o estado de un circuito desde el frente del tablero."
        ),
        "imagen": "riel-cnc",
        "orden": 90,
        "caracteristicas": (
            "Montaje modular sobre riel DIN",
            "Indicador LED frontal",
            "Conexión mediante bornes atornillados",
        ),
        "especificaciones": (
            ("Modelo", "ADM-1", ""),
            ("Tensión nominal", "230", "V AC"),
            ("Frecuencia", "50", "Hz"),
            ("Montaje", "Riel DIN", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "luces-piloto-led-riel-din-slim-cnc-ycd9-1",
        "nombre": "Luces piloto LED slim para riel DIN CNC YCD9-1",
        "categoria": "pilotos-riel-din",
        "marca": "cnc",
        "modelo": "YCD9-1",
        "subtitulo": "Señalización modular de formato slim",
        "descripcion": (
            "Luces piloto LED modulares y compactas para señalizar estados "
            "o presencia de tensión en tableros con montaje sobre riel DIN."
        ),
        "imagen": "slim-roja",
        "orden": 95,
        "caracteristicas": (
            "Diseño slim para optimizar el espacio del tablero",
            "Indicador LED frontal de identificación rápida",
            "Tres colores disponibles para diferenciar estados",
        ),
        "especificaciones": (
            ("Modelo", "YCD9-1", ""),
            ("Tensión nominal", "230", "V AC"),
            ("Montaje", "Riel DIN", ""),
            ("Formato", "Slim", ""),
        ),
        "variantes": (
            variante_piloto_slim(
                "Luz Piloto Led A Riel Din Slim roja",
                "Rojo",
                "slim-roja",
            ),
            variante_piloto_slim(
                "Luz Piloto Led A Riel Din Slim amarilla",
                "Amarillo",
                "slim-amarilla",
            ),
            variante_piloto_slim(
                "Luz Piloto Led A Riel Din Slim verde",
                "Verde",
                "slim-verde",
            ),
        ),
    },
    {
        "slug": "luz-piloto-roja-riel-din-lexo-ebs1d",
        "nombre": "Luz piloto roja para riel DIN LEXO EBS1D",
        "categoria": "pilotos-riel-din",
        "marca": "lexo",
        "modelo": "EBS1D",
        "subtitulo": "Indicador modular rojo",
        "descripcion": (
            "Luz piloto modular roja LEXO para señalización de estado o "
            "presencia de tensión en tableros eléctricos."
        ),
        "imagen": "riel-lexo",
        "orden": 100,
        "caracteristicas": (
            "Señalización frontal de color rojo",
            "Montaje modular sobre riel DIN",
            "Conexión mediante bornes atornillados",
        ),
        "especificaciones": (
            ("Modelo", "EBS1D", ""),
            ("Tensión nominal", "220", "V AC"),
            ("Color de señalización", "Rojo", ""),
            ("Montaje", "Riel DIN", ""),
        ),
        "variantes": (),
    },
    {
        "slug": "interruptores-magnetotermicos-legrand-rx3-1p",
        "nombre": "Interruptores magnetotérmicos Legrand RX³ 1P",
        "categoria": "interruptores-automaticos",
        "marca": "legrand",
        "modelo": "RX³",
        "subtitulo": "Protección termomagnética curva C",
        "descripcion": (
            "Interruptores magnetotérmicos modulares Legrand RX³ de un "
            "polo para proteger circuitos contra sobrecargas y cortocircuitos."
        ),
        "imagen": "legrand-16a",
        "orden": 110,
        "caracteristicas": (
            "Protección contra sobrecargas y cortocircuitos",
            "Curva de disparo C y poder de corte de 6 kA a 400 V",
            "Montaje modular en riel DIN",
        ),
        "especificaciones": (
            ("Número de polos", "1P", ""),
            ("Tensión nominal", "230/400", "V AC"),
            ("Curva de disparo", "C", ""),
            ("Poder de corte a 400 V", "6", "kA"),
            ("Frecuencia", "50-60", "Hz"),
            ("Grado de protección", "IP20", ""),
            ("Montaje", "Riel DIN", ""),
        ),
        "variantes": (
            variante_legrand(10, "419838", "legrand-10a"),
            variante_legrand(16, "419840", "legrand-16a"),
            variante_legrand(20, "419841", "legrand-20a"),
            variante_legrand(25, "419842", "legrand-25a"),
            variante_legrand(32, "419843", "legrand-32a"),
            variante_legrand(40, "419844", "legrand-40a"),
        ),
    },
)


class Command(BaseCommand):
    help = (
        "Valida o carga pilotos LED, medidores de panel e interruptores "
        "Legrand RX3 a partir de las imágenes proporcionadas."
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

        self.stdout.write(
            self.style.SUCCESS(
                "Carga terminada: los productos quedaron "
                + ("como borradores." if options["no_publicar"] else "publicados.")
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
        control, _ = Categoria.objects.update_or_create(
            slug="control-senalizacion",
            defaults={
                "nombre": "Control y señalización",
                "padre": None,
                "orden": 20,
                "activa": True,
            },
        )
        proteccion, _ = Categoria.objects.update_or_create(
            slug="proteccion-electrica",
            defaults={
                "nombre": "Protección eléctrica",
                "padre": None,
                "orden": 10,
                "activa": True,
            },
        )
        definiciones = (
            ("instrumentos-panel", "Instrumentos de panel", control, 1),
            ("pilotos-panel", "Pilotos de panel", control, 2),
            ("pilotos-riel-din", "Pilotos para riel DIN", control, 3),
            (
                "interruptores-automaticos",
                "Interruptores automáticos",
                proteccion,
                1,
            ),
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
        for slug, nombre in (
            ("cnc", "CNC"),
            ("legrand", "Legrand"),
            ("lexo", "LEXO"),
        ):
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
                "etiqueta_visual": "SEÑALIZACIÓN"
                if definicion["categoria"] != "interruptores-automaticos"
                else "PROTECCIÓN",
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

        variantes = {}
        for orden, datos in enumerate(definicion["variantes"], start=1):
            criterios = (
                {"codigo": datos["codigo"]}
                if datos["codigo"]
                else {"producto": producto, "nombre": datos["nombre"]}
            )
            variante, _ = VarianteProducto.objects.update_or_create(
                **criterios,
                defaults={
                    "producto": producto,
                    "nombre": datos["nombre"],
                    "modelo": datos["modelo"],
                    "codigo": datos["codigo"],
                    "imagen": destinos[datos["imagen"]],
                    "disponible": True,
                    "orden": orden,
                },
            )
            variantes[datos["imagen"]] = variante
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
        claves_imagen.extend(
            datos["imagen"] for datos in definicion["variantes"]
        )
        for orden, clave in enumerate(dict.fromkeys(claves_imagen), start=1):
            imagen, _ = ImagenProducto.objects.update_or_create(
                clave=f"carga-pilotos-legrand-{clave}",
                defaults={
                    "producto": producto,
                    "imagen": destinos[clave],
                    "texto_alternativo": IMAGENES[clave]["alt"],
                    "orden": orden,
                },
            )
            variante = variantes.get(clave)
            imagen.variantes.set([variante] if variante else [])
