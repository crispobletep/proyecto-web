from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Proyecto


PROYECTOS = (
    {
        "slug": "edificio-el-estero",
        "nombre": "Edificio El Estero",
        "sector": "residencial",
        "descripcion": (
            "Proyecto habitacional actualmente en construcción en La Florida, "
            "con participación de PH Servicios Electrónicos en sus instalaciones."
        ),
        "constructora": "ICAFAL",
        "mandante": "Simonetti Inmobiliaria S.A.",
        "estado": "en_construccion",
        "periodo": "En construcción · entrega estimada 2027",
        "direccion": "El Estero 303, La Florida, Santiago",
        "url_referencia": "https://simonetti.cl/edificio-el-estero/",
        "orden": 1,
        "imagen_destino": "proyectos/edificio-el-estero.png",
        "texto_alternativo": (
            "Vista exterior del proyecto residencial Edificio El Estero"
        ),
    },
    {
        "slug": "edificio-froilan-lagos",
        "nombre": "Edificio Froilán Lagos",
        "sector": "residencial",
        "descripcion": (
            "Edificio residencial de 23 pisos y 284 departamentos, con dos "
            "niveles subterráneos, ejecutado en la comuna de La Florida."
        ),
        "constructora": "ICAFAL",
        "mandante": "Simonetti Inmobiliaria S.A.",
        "estado": "finalizado",
        "periodo": "Septiembre 2023 – octubre 2025",
        "direccion": "Froilán Lagos Sepúlveda 1360, La Florida, Santiago",
        "url_referencia": (
            "https://www.icafal.cl/proyecto/edificio-froilan-lagos/"
        ),
        "orden": 2,
        "imagen_destino": "proyectos/edificio-froilan-lagos.jpg",
        "texto_alternativo": (
            "Obras de construcción del Edificio Froilán Lagos en La Florida"
        ),
    },
    {
        "slug": "edificios-mirador-azul",
        "nombre": "Edificios Mirador Azul",
        "sector": "residencial",
        "descripcion": (
            "Conjunto residencial de dos torres de 22 pisos, 332 departamentos "
            "y dos niveles subterráneos, terminado en 2023."
        ),
        "constructora": "ICAFAL",
        "mandante": "Simonetti Inmobiliaria S.A.",
        "estado": "finalizado",
        "periodo": "Abril 2021 – mayo 2023",
        "direccion": "Froilán Lagos 6333, La Florida, Santiago",
        "url_referencia": (
            "https://www.icafal.cl/proyecto/edificios-mirador-azul/"
        ),
        "orden": 3,
        "imagen_origen": "fueron dos torres en mirador azul.jpeg",
        "imagen_destino": "proyectos/edificios-mirador-azul.jpeg",
        "texto_alternativo": (
            "Torres A y B del proyecto residencial Edificios Mirador Azul"
        ),
    },
    {
        "slug": "remodelacion-edificio-a-hospital-del-trabajador",
        "nombre": "Remodelación Edificio A · Hospital del Trabajador",
        "sector": "hospitalario",
        "descripcion": (
            "Remodelación del Edificio A del Hospital del Trabajador ACHS en "
            "Providencia, desarrollada para renovar su infraestructura."
        ),
        "constructora": "Consorcio LD Constructora–ICAFAL",
        "mandante": "Hospital del Trabajador ACHS",
        "estado": "finalizado",
        "periodo": "Finalizado en 2026",
        "direccion": "Av. Ramón Carnicer 185, Providencia, Santiago",
        "url_referencia": (
            "https://www.hospitaldeltrabajador.cl/ubicaciones"
        ),
        "orden": 4,
        "imagen_origen": (
            "Remodelación Edificio A, Hospital del trabajador.jpeg"
        ),
        "imagen_destino": (
            "proyectos/remodelacion-edificio-a-hospital-del-trabajador.jpeg"
        ),
        "texto_alternativo": (
            "Fachada del Edificio A del Hospital del Trabajador en Providencia"
        ),
    },
    {
        "slug": "edificio-martin-de-zamora",
        "nombre": "Edificio Martín de Zamora",
        "sector": "residencial",
        "descripcion": (
            "Edificio residencial de 10 pisos, 58 departamentos y dos niveles "
            "subterráneos, ejecutado en la comuna de Las Condes."
        ),
        "constructora": "ICAFAL",
        "mandante": "Inmobiliaria Zamora SPA (Numancia)",
        "estado": "finalizado",
        "periodo": "Junio 2021 – octubre 2023",
        "direccion": "Martín de Zamora 6233, Las Condes, Santiago",
        "url_referencia": (
            "https://www.icafal.cl/proyecto/edificio-martin-de-zamora/"
        ),
        "orden": 5,
        "imagen_destino": "proyectos/edificio-martin-de-zamora.jpg",
        "texto_alternativo": (
            "Vista exterior del Edificio Martín de Zamora en Las Condes"
        ),
    },
)


class Command(BaseCommand):
    help = (
        "Valida o carga los proyectos iniciales y sus imágenes en la base "
        "de datos. Sin --aplicar solo realiza una simulación."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--origen",
            type=Path,
            default=Path.home() / "Downloads",
            help="Carpeta donde están las imágenes proporcionadas.",
        )
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Guarda los proyectos y copia sus imágenes.",
        )

    def handle(self, *args, **options):
        origen = options["origen"].expanduser().resolve()
        faltantes = []

        for datos in PROYECTOS:
            nombre_archivo = datos.get("imagen_origen")
            destino = datos.get("imagen_destino")
            if not destino or default_storage.exists(destino):
                continue
            if not nombre_archivo or not (origen / nombre_archivo).is_file():
                if not nombre_archivo:
                    faltantes.append(str(Path(settings.MEDIA_ROOT) / destino))
                    continue
                faltantes.append(str(origen / nombre_archivo))

        if faltantes:
            detalle = "\n".join(f"- {ruta}" for ruta in faltantes)
            raise CommandError(f"No se encontraron estas imágenes:\n{detalle}")

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    "Validación correcta: se prepararían 5 proyectos y 5 imágenes. "
                    "Ejecute nuevamente con --aplicar para guardar los cambios."
                )
            )
            return

        with transaction.atomic():
            for datos in PROYECTOS:
                valores = {
                    clave: valor
                    for clave, valor in datos.items()
                    if clave
                    not in {"slug", "imagen_origen", "imagen_destino"}
                }
                valores["publicado"] = True
                destino = datos.get("imagen_destino")

                if destino:
                    if not default_storage.exists(destino):
                        origen_imagen = origen / datos["imagen_origen"]
                        with origen_imagen.open("rb") as archivo:
                            destino = default_storage.save(
                                destino,
                                File(archivo, name=PurePosixPath(destino).name),
                            )
                    valores["imagen"] = destino

                proyecto, creado = Proyecto.objects.update_or_create(
                    slug=datos["slug"],
                    defaults=valores,
                )
                accion = "Creado" if creado else "Actualizado"
                self.stdout.write(f"{accion}: {proyecto.nombre}")

        self.stdout.write(
            self.style.SUCCESS(
                "Carga terminada: 5 proyectos publicados y administrables."
            )
        )
