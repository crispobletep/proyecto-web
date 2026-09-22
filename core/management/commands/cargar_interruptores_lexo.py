from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Categoria,
    CaracteristicaProducto,
    EspecificacionProducto,
    EspecificacionVariante,
    Marca,
    Producto,
    VarianteProducto,
)


def variante_automatico(polos, amperaje, imagen=None):
    codigo_polos = "1PN" if polos == "1P+N" else polos
    datos = {
        "nombre": f"{polos} · {amperaje} A · curva C",
        "codigo": f"LEXO-AUT-{codigo_polos}-C{amperaje}",
        "imagen": imagen,
        "especificaciones": (
            ("Polos", polos, ""),
            ("Corriente nominal", str(amperaje), "A"),
            ("Curva de disparo", "C", ""),
            ("Poder de corte", "6", "kA"),
        ),
    }

    if polos == "1P+N":
        datos["codigo_anterior"] = f"LEXO-AUT-1PNN-C{amperaje}"

    return datos


def variante_diferencial(polos, amperaje, imagen=None):
    return {
        "nombre": f"{polos} · {amperaje} A · 30 mA",
        "codigo": f"LEXO-DIF-{polos}-{amperaje}A-30MA",
        "imagen": imagen,
        "especificaciones": (
            ("Polos", polos, ""),
            ("Corriente nominal", str(amperaje), "A"),
            ("Sensibilidad diferencial", "30", "mA"),
            ("Poder de corte", "6", "kA"),
        ),
    }


PRODUCTOS = (
    {
        "slug": "interruptores-automaticos-lexo-1p",
        "nombre": "Interruptores automáticos LEXO 1P",
        "subcategoria": "interruptores-automaticos",
        "modelo": "EBS6BN",
        "subtitulo": "Protección termomagnética monofásica",
        "descripcion": (
            "Interruptores automáticos modulares de un polo para la "
            "protección de circuitos contra sobrecargas y cortocircuitos."
        ),
        "orden": 10,
        "caracteristicas": (
            "Protección contra sobrecargas y cortocircuitos",
            "Curva de disparo C y poder de corte de 6 kA",
            "Montaje modular en riel DIN",
        ),
        "especificaciones": (
            ("Número de polos", "1P", ""),
            ("Curva de disparo", "C", ""),
            ("Poder de corte", "6", "kA"),
            ("Norma de referencia", "IEC 60898", ""),
        ),
        "variantes": (
            variante_automatico("1P", 2, "960.png"),
            variante_automatico("1P", 6, "9601.png"),
            variante_automatico("1P", 10, "9603.png"),
            variante_automatico("1P", 16, "9604.png"),
            variante_automatico("1P", 20, "9605.png"),
            variante_automatico("1P", 25),
            variante_automatico("1P", 32, "9606.png"),
            variante_automatico("1P", 40, "9607.png"),
            variante_automatico("1P", 50),
            variante_automatico("1P", 63, "9608.png"),
        ),
    },
    {
        "slug": "interruptores-automaticos-lexo-1p-n",
        "nombre": "Interruptores automáticos LEXO 1P+N",
        "subcategoria": "interruptores-automaticos",
        "modelo": "EBS6BN",
        "subtitulo": "Protección termomagnética fase más neutro",
        "descripcion": (
            "Interruptores automáticos modulares 1P+N con corte simultáneo "
            "de fase y neutro para circuitos monofásicos."
        ),
        "orden": 20,
        "caracteristicas": (
            "Corte simultáneo de fase y neutro",
            "Curva de disparo C y poder de corte de 6 kA",
            "Montaje modular en riel DIN",
        ),
        "especificaciones": (
            ("Número de polos", "1P+N", ""),
            ("Curva de disparo", "C", ""),
            ("Poder de corte", "6", "kA"),
            ("Norma de referencia", "IEC 60898", ""),
        ),
        "variantes": (
            variante_automatico("1P+N", 10, "9609.png"),
            variante_automatico("1P+N", 16, "9610.png"),
            variante_automatico("1P+N", 20, "9611.png"),
            variante_automatico("1P+N", 25, "9612.png"),
            variante_automatico("1P+N", 32, "9613.png"),
            variante_automatico("1P+N", 40, "9614.png"),
        ),
    },
    {
        "slug": "interruptores-automaticos-trifasicos-lexo-3p",
        "nombre": "Interruptores automáticos trifásicos LEXO 3P",
        "subcategoria": "interruptores-automaticos",
        "modelo": "EBS6BN",
        "subtitulo": "Protección termomagnética trifásica",
        "descripcion": (
            "Interruptores automáticos tripolares para protección y "
            "seccionamiento conjunto de circuitos trifásicos."
        ),
        "orden": 30,
        "caracteristicas": (
            "Accionamiento conjunto de tres polos",
            "Curva de disparo C y poder de corte de 6 kA",
            "Montaje modular en riel DIN",
        ),
        "especificaciones": (
            ("Número de polos", "3P", ""),
            ("Curva de disparo", "C", ""),
            ("Poder de corte", "6", "kA"),
            ("Norma de referencia", "IEC 60898", ""),
        ),
        "variantes": (
            variante_automatico("3P", 10, "1472.png"),
            variante_automatico("3P", 16, "1334.png"),
            variante_automatico(
                "3P",
                20,
                "D_NQ_NP_726182-MLA79454310007_092024-O.png",
            ),
            variante_automatico(
                "3P",
                25,
                "D_NQ_NP_854066-MLA100083948805_122025-O.png",
            ),
            variante_automatico(
                "3P",
                32,
                "D_NQ_NP_932522-MLA99521849786_122025-O.png",
            ),
            variante_automatico(
                "3P",
                40,
                "d87a2432-fee1-4a65-93fd-44474708700c.5905ab22a7fb6ebbf5fea199bb69d06c.png",
            ),
            variante_automatico(
                "3P",
                50,
                "a4fda68e-75aa-48cb-a77b-f32c1943c0d9.147577abfc87981b8ca2475d7bc2958d.png",
            ),
            variante_automatico(
                "3P",
                63,
                "D_NQ_NP_714281-MLA76111631226_052024-O-int-automatico-lexo-3x63a-06ka-c--5300163.png",
            ),
        ),
    },
    {
        "slug": "interruptores-diferenciales-lexo-2p",
        "nombre": "Interruptores diferenciales LEXO 2P",
        "subcategoria": "interruptores-diferenciales",
        "modelo": "EBS6R",
        "subtitulo": "Protección diferencial monofásica",
        "descripcion": (
            "Interruptores diferenciales bipolares de 30 mA para protección "
            "de personas y circuitos frente a corrientes de fuga."
        ),
        "orden": 40,
        "caracteristicas": (
            "Sensibilidad diferencial de 30 mA",
            "Botón de prueba para verificación periódica",
            "Montaje modular en riel DIN",
        ),
        "especificaciones": (
            ("Número de polos", "2P", ""),
            ("Sensibilidad diferencial", "30", "mA"),
            ("Norma de referencia", "IEC 61008", ""),
        ),
        "variantes": (
            variante_diferencial(
                "2P",
                25,
                "X_new-template-photoroom-2023-05-15t142326-4774624.png",
            ),
            variante_diferencial(
                "2P",
                40,
                "X_template-bag-1-photoroom-2023-09-05t174812-9310117.png",
            ),
            variante_diferencial(
                "2P",
                63,
                "X_new-template-photoroom-2023-05-15t142344-0201469.png",
            ),
        ),
    },
    {
        "slug": "interruptores-diferenciales-lexo-4p",
        "nombre": "Interruptores diferenciales LEXO 4P",
        "subcategoria": "interruptores-diferenciales",
        "modelo": "EBS6R",
        "subtitulo": "Protección diferencial trifásica",
        "descripcion": (
            "Interruptores diferenciales tetrapolares de 30 mA para redes "
            "trifásicas con neutro."
        ),
        "orden": 50,
        "caracteristicas": (
            "Sensibilidad diferencial de 30 mA",
            "Corte conjunto de tres fases y neutro",
            "Botón de prueba para verificación periódica",
        ),
        "especificaciones": (
            ("Número de polos", "4P", ""),
            ("Sensibilidad diferencial", "30", "mA"),
            ("Norma de referencia", "IEC 61008", ""),
        ),
        "variantes": (
            variante_diferencial(
                "4P",
                25,
                "X_template-bag-1-photoroom-2023-09-05t175240-4347366.png",
            ),
            variante_diferencial(
                "4P",
                40,
                "X_template-bag-1-photoroom-2023-09-05t175700-5911738.png",
            ),
            variante_diferencial("4P", 63),
        ),
    },
)


class Command(BaseCommand):
    help = (
        "Valida o carga las familias y variantes de interruptores LEXO. "
        "Sin --aplicar solo muestra el plan y no modifica la base de datos."
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
            help="Crea o actualiza los registros y copia las imágenes.",
        )
        parser.add_argument(
            "--publicar",
            action="store_true",
            help="Publica las cinco familias al aplicar la carga.",
        )

    def handle(self, *args, **options):
        origen = options["origen"].expanduser().resolve()
        imagenes = {
            variante["imagen"]
            for producto in PRODUCTOS
            for variante in producto["variantes"]
            if variante["imagen"]
        }
        faltantes = sorted(
            nombre for nombre in imagenes if not (origen / nombre).is_file()
        )

        self.stdout.write(
            f"Plan: {len(PRODUCTOS)} productos y "
            f"{sum(len(p['variantes']) for p in PRODUCTOS)} variantes."
        )
        self.stdout.write(f"Origen de imágenes: {origen}")

        if faltantes:
            detalle = "\n - ".join(faltantes)
            raise CommandError(f"Faltan imágenes requeridas:\n - {detalle}")

        sin_imagen = [
            f"{producto['nombre']} — {variante['nombre']}"
            for producto in PRODUCTOS
            for variante in producto["variantes"]
            if not variante["imagen"]
        ]

        if sin_imagen:
            self.stdout.write(
                self.style.WARNING(
                    "Se crearán sin imagen (no se adjuntó una coincidencia "
                    "segura):\n - " + "\n - ".join(sin_imagen)
                )
            )

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    "Validación terminada. No se modificó la base de datos. "
                    "Ejecute nuevamente con --aplicar cuando quiera cargar."
                )
            )
            return

        with transaction.atomic():
            marca, _ = Marca.objects.update_or_create(
                slug="lexo",
                defaults={
                    "nombre": "LEXO",
                    "activa": True,
                },
            )
            familia, _ = Categoria.objects.update_or_create(
                slug="proteccion-electrica",
                defaults={
                    "nombre": "Protección eléctrica",
                    "padre": None,
                    "orden": 10,
                    "activa": True,
                },
            )
            subcategorias = {}
            for orden, (slug, nombre) in enumerate(
                (
                    ("interruptores-automaticos", "Interruptores automáticos"),
                    ("interruptores-diferenciales", "Interruptores diferenciales"),
                ),
                start=1,
            ):
                subcategorias[slug], _ = Categoria.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "nombre": nombre,
                        "padre": familia,
                        "orden": orden,
                        "activa": True,
                    },
                )

            for definicion in PRODUCTOS:
                producto, creado = Producto.objects.update_or_create(
                    slug=definicion["slug"],
                    defaults={
                        "categoria": subcategorias[definicion["subcategoria"]],
                        "nombre": definicion["nombre"],
                        "marca_nueva": marca,
                        "marca": "",
                        "modelo": definicion["modelo"],
                        "codigo": None,
                        "subtitulo": definicion["subtitulo"],
                        "descripcion": definicion["descripcion"],
                        "texto_alternativo": definicion["nombre"],
                        "etiqueta_visual": "PROTECCIÓN",
                        "orden": definicion["orden"],
                    },
                )
                if creado or options["publicar"]:
                    producto.publicado = options["publicar"]
                    producto.save(update_fields=("publicado", "actualizado"))

                self._cargar_caracteristicas(producto, definicion)
                self._cargar_especificaciones_producto(producto, definicion)
                self._cargar_variantes(producto, definicion, origen)

        self.stdout.write(
            self.style.SUCCESS(
                "Carga LEXO terminada. Revise las fichas en el administrador "
                "antes de publicarlas."
            )
        )

    def _cargar_caracteristicas(self, producto, definicion):
        for orden, texto in enumerate(definicion["caracteristicas"], start=1):
            CaracteristicaProducto.objects.update_or_create(
                producto=producto,
                texto=texto,
                defaults={"orden": orden},
            )

    def _cargar_especificaciones_producto(self, producto, definicion):
        for orden, (nombre, valor, unidad) in enumerate(
            definicion["especificaciones"],
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

    def _cargar_variantes(self, producto, definicion, origen):
        for orden, datos in enumerate(definicion["variantes"], start=1):
            variante = VarianteProducto.objects.filter(
                codigo=datos["codigo"],
            ).first()
            if not variante and datos.get("codigo_anterior"):
                variante = VarianteProducto.objects.filter(
                    codigo=datos["codigo_anterior"],
                ).first()

            if not variante:
                variante = VarianteProducto()

            variante.producto = producto
            variante.nombre = datos["nombre"]
            variante.modelo = definicion["modelo"]
            variante.codigo = datos["codigo"]
            variante.disponible = True
            variante.orden = orden
            variante.save()

            nombre_imagen = datos["imagen"]
            destino_imagen = (
                f"lexo/{datos['codigo'].lower()}.png"
                if nombre_imagen
                else None
            )
            if destino_imagen and not variante.imagen.name.endswith(
                destino_imagen
            ):
                imagen_anterior = variante.imagen.name
                with (origen / nombre_imagen).open("rb") as archivo:
                    variante.imagen.save(
                        destino_imagen,
                        File(archivo),
                        save=True,
                    )

                if (
                    imagen_anterior
                    and imagen_anterior != variante.imagen.name
                    and imagen_anterior.startswith(
                        "productos/variantes/lexo/"
                    )
                ):
                    variante.imagen.storage.delete(imagen_anterior)

            for posicion, (nombre, valor, unidad) in enumerate(
                datos["especificaciones"],
                start=1,
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
