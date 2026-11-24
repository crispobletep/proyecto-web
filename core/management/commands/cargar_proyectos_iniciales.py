from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import ImagenProyecto, Proyecto


PROYECTOS = (
    {
        "slug": "edificio-el-estero",
        "nombre": "Edificio El Estero",
        "sector": "residencial",
        "descripcion": (
            "Proyecto habitacional actualmente en construcción en La Florida, "
            "con participación de PH Servicios Eléctricos en sus instalaciones."
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
    {
        "slug": "torres-de-vicuna-mackenna-1-y-2",
        "nombre": "Torres de Vicuña Mackenna 1 y 2",
        "sector": "residencial",
        "descripcion": (
            "Conjunto residencial de dos torres en Vicuña Mackenna. "
            "El registro fotográfico muestra sus espacios comunes, "
            "equipamiento y departamentos."
        ),
        "estado": "finalizado",
        "periodo": "Proyecto finalizado",
        "direccion": "Avenida Vicuña Mackenna, Santiago",
        "orden": 6,
        "imagen_origen": "WhatsApp Image 2026-11-23 at 10.35.16.jpeg",
        "imagen_destino": "proyectos/torres-vicuna-mackenna-1-y-2/portada.jpeg",
        "texto_alternativo": (
            "Fachada de las Torres de Vicuña Mackenna 1 y 2"
        ),
        "galeria": (
            (
                "WhatsApp Image 2026-11-23 at 10.35.39.jpeg",
                "Acceso y recepción del edificio",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.38.jpeg",
                "Sala de estar común",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.37.jpeg",
                "Espacio de cowork",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.36.jpeg",
                "Sala de estar y terraza",
            ),
            ("WhatsApp Image 2026-11-23 at 10.35.35.jpeg", "Comedor común"),
            (
                "WhatsApp Image 2026-11-23 at 10.35.34.jpeg",
                "Lavandería equipada",
            ),
            ("WhatsApp Image 2026-11-23 at 10.35.33.jpeg", "Gimnasio"),
            (
                "WhatsApp Image 2026-11-23 at 10.35.32.jpeg",
                "Área de máquinas del gimnasio",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.31.jpeg",
                "Terraza con quincho y vista a la ciudad",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.30.jpeg",
                "Interior de departamento",
            ),
            (
                "WhatsApp Image 2026-11-23 at 10.35.29.jpeg",
                "Cocina integrada y estar",
            ),
            ("WhatsApp Image 2026-11-23 at 10.35.28.jpeg", "Cocina equipada"),
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
        parser.add_argument(
            "--slug",
            help="Limita la carga a un proyecto específico.",
        )

    def handle(self, *args, **options):
        origen = options["origen"].expanduser().resolve()
        proyectos = [
            datos
            for datos in PROYECTOS
            if not options["slug"] or datos["slug"] == options["slug"]
        ]
        if options["slug"] and not proyectos:
            raise CommandError(
                f"No existe un proyecto inicial con slug {options['slug']!r}."
            )
        faltantes = []

        for datos in proyectos:
            nombre_archivo = datos.get("imagen_origen")
            destino = datos.get("imagen_destino")
            if destino and not default_storage.exists(destino):
                if not nombre_archivo or not (origen / nombre_archivo).is_file():
                    if not nombre_archivo:
                        faltantes.append(str(Path(settings.MEDIA_ROOT) / destino))
                    else:
                        faltantes.append(str(origen / nombre_archivo))
            for orden, (nombre, _) in enumerate(datos.get("galeria", ()), 1):
                destino_galeria = (
                    f"proyectos/{datos['slug']}/galeria-{orden:02}.jpeg"
                )
                if (
                    not default_storage.exists(destino_galeria)
                    and not (origen / nombre).is_file()
                ):
                    faltantes.append(str(origen / nombre))

        if faltantes:
            detalle = "\n".join(f"- {ruta}" for ruta in faltantes)
            raise CommandError(f"No se encontraron estas imágenes:\n{detalle}")

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Validación correcta: se prepararían {len(proyectos)} proyectos "
                    "y sus imágenes. "
                    "Ejecute nuevamente con --aplicar para guardar los cambios."
                )
            )
            return

        with transaction.atomic():
            for datos in proyectos:
                valores = {
                    clave: valor
                    for clave, valor in datos.items()
                    if clave
                    not in {"slug", "imagen_origen", "imagen_destino", "galeria"}
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

                for orden, (nombre, alt) in enumerate(datos.get("galeria", ()), 1):
                    destino_galeria = (
                        f"proyectos/{datos['slug']}/galeria-{orden:02}.jpeg"
                    )
                    if not default_storage.exists(destino_galeria):
                        with (origen / nombre).open("rb") as archivo:
                            destino_galeria = default_storage.save(
                                destino_galeria,
                                File(
                                    archivo,
                                    name=PurePosixPath(destino_galeria).name,
                                ),
                            )
                    ImagenProyecto.objects.update_or_create(
                        proyecto=proyecto,
                        orden=orden,
                        defaults={
                            "imagen": destino_galeria,
                            "texto_alternativo": alt,
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga terminada: {len(proyectos)} proyectos publicados y administrables."
            )
        )
