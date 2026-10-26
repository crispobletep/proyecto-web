from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.catalog_imports import retirar_variantes
from core.models import (
    Categoria,
    CaracteristicaProducto,
    EspecificacionProducto,
    EspecificacionVariante,
    Producto,
    VarianteProducto,
)


DIRECTORIO_IMAGENES = Path("productos/catalogo/canaletas-accesorios")


def imagen(nombre):
    return (DIRECTORIO_IMAGENES / nombre).as_posix()


def variante(nombre, medida, foto="", especificaciones=()):
    return {
        "nombre": nombre,
        "imagen": imagen(foto) if foto else "",
        "especificaciones": (("Medida", medida, "mm"), *especificaciones),
    }


def variantes_accesorio(fotos):
    return tuple(
        variante(nombre, medida, fotos.get(medida, ""))
        for nombre, medida in (
            ("20 × 10 mm", "20 × 10"),
            ("40 × 16 mm", "40 × 16"),
            ("100 × 50 mm", "100 × 50"),
        )
    )


PRODUCTOS = (
    {
        "slug": "canaleta-pvc-2-metros",
        "nombre": "Canaleta PVC de 2 m",
        "imagen": imagen("canaleta-pvc-20x10-blanca-2m.png"),
        "orden": 260,
        "descripcion": (
            "Canaleta de PVC con tapa para conducir y ordenar cables en una "
            "instalación. Elige la medida, el color y la presentación con o "
            "sin adhesivo; la versión de 100 × 50 mm también está disponible "
            "libre de halógenos."
        ),
        "caracteristicas": (
            "Canaleta con tapa para organizar conductores",
            "Presentaciones de 2 m de largo",
            "Medidas de 20 × 10, 40 × 16 y 100 × 50 mm",
        ),
        "especificaciones": (("Material", "PVC", ""), ("Largo", "2", "m")),
        "variantes": (
            variante(
                "20 × 10 mm · Blanca · 2 m",
                "20 × 10",
                "canaleta-pvc-20x10-blanca-2m.png",
                (("Color", "Blanco", ""), ("Largo", "2", "m")),
            ),
            variante(
                "20 × 10 mm · Blanca con adhesivo · 2 m",
                "20 × 10",
                "canaleta-pvc-20x10-blanca-2m-con-adhesivo.png",
                (("Color", "Blanco", ""), ("Adhesivo", "Sí", ""), ("Largo", "2", "m")),
            ),
            variante(
                "20 × 10 mm · Color madera · 2 m",
                "20 × 10",
                "canaleta-pvc-20x10-madera-2m.png",
                (("Color", "Madera", ""), ("Largo", "2", "m")),
            ),
            variante(
                "20 × 10 mm · Color madera con adhesivo · 2 m",
                "20 × 10",
                "canaleta-pvc-20x10-madera-2m.png",
                (("Color", "Madera", ""), ("Adhesivo", "Sí", ""), ("Largo", "2", "m")),
            ),
            variante(
                "40 × 16 mm · Blanca · 2 m",
                "40 × 16",
                "canaleta-pvc-40x16-2m.png",
                (("Color", "Blanco", ""), ("Largo", "2", "m")),
            ),
            variante(
                "40 × 16 mm · Blanca con adhesivo · 2 m",
                "40 × 16",
                "canaleta-pvc-40x16-2m-con-adhesivo.png",
                (("Color", "Blanco", ""), ("Adhesivo", "Sí", ""), ("Largo", "2", "m")),
            ),
            variante(
                "100 × 50 mm · Blanca · 2 m",
                "100 × 50",
                "canaleta-pvc-100x50-2m.png",
                (("Color", "Blanco", ""), ("Largo", "2", "m")),
            ),
            variante(
                "100 × 50 mm · Libre de halógenos · 2 m",
                "100 × 50",
                "canaleta-pvc-100x50-2m.png",
                (("Aislación", "Libre de halógenos", ""), ("Largo", "2", "m")),
            ),
        ),
    },
    {
        "slug": "angulo-interno-canaleta-pvc",
        "nombre": "Ángulo interno para canaleta PVC",
        "imagen": "",
        "orden": 270,
        "descripcion": "Accesorio para resolver esquinas internas en canalizaciones de PVC.",
        "caracteristicas": ("Pieza de unión para esquinas internas", "Variantes según la medida de la canaleta"),
        "especificaciones": (("Material", "PVC", ""), ("Tipo", "Ángulo interno", "")),
        "variantes": variantes_accesorio({"20 × 10": "angulo-interno-20x10.png", "40 × 16": "angulo-interno-40x16.png"}),
    },
    {
        "slug": "angulo-exterior-canaleta-pvc",
        "nombre": "Ángulo exterior para canaleta PVC",
        "imagen": "",
        "orden": 280,
        "descripcion": "Accesorio para resolver esquinas externas en canalizaciones de PVC.",
        "caracteristicas": ("Pieza de unión para esquinas externas", "Variantes según la medida de la canaleta"),
        "especificaciones": (("Material", "PVC", ""), ("Tipo", "Ángulo exterior", "")),
        "variantes": variantes_accesorio({"20 × 10": "angulo-exterior-20x10.png", "40 × 16": "angulo-exterior-40x16.png"}),
    },
    {
        "slug": "tapa-final-canaleta-pvc",
        "nombre": "Tapa final para canaleta PVC",
        "imagen": "",
        "orden": 290,
        "descripcion": "Tapa de terminación para cerrar el extremo de una canaleta de PVC.",
        "caracteristicas": ("Cierra el extremo de la canaleta", "Variantes según la medida de la canaleta"),
        "especificaciones": (("Material", "PVC", ""), ("Tipo", "Tapa final", "")),
        "variantes": variantes_accesorio({"20 × 10": "tapa-final-20x10-40x16.png", "40 × 16": "tapa-final-20x10-40x16.png"}),
    },
    {
        "slug": "angulo-plano-canaleta-pvc",
        "nombre": "Ángulo plano para canaleta PVC",
        "imagen": "",
        "orden": 300,
        "descripcion": "Accesorio de unión plana para canalizaciones de PVC.",
        "caracteristicas": ("Permite realizar un cruce o cambio de dirección plano", "Variantes según la medida de la canaleta"),
        "especificaciones": (("Material", "PVC", ""), ("Tipo", "Ángulo plano", "")),
        "variantes": variantes_accesorio({"20 × 10": "angulo-plano-20x10.png", "40 × 16": "angulo-plano-40x16.png"}),
    },
    {
        "slug": "tee-derivacion-canaleta-pvc",
        "nombre": "Tee de derivación para canaleta PVC",
        "imagen": "",
        "orden": 310,
        "descripcion": "Accesorio en T para derivar una canalización de PVC.",
        "caracteristicas": ("Permite derivar una canalización", "Variantes según la medida de la canaleta"),
        "especificaciones": (("Material", "PVC", ""), ("Tipo", "Tee de derivación", "")),
        "variantes": variantes_accesorio({"20 × 10": "tee-derivacion-20x10.png", "40 × 16": "tee-derivacion-40x16.png"}),
    },
    {
        "slug": "portabastidor-universal-100x50",
        "nombre": "Portabastidor universal 100 × 50 mm",
        "imagen": imagen("portabastidor-universal-100x50.png"),
        "orden": 320,
        "descripcion": "Portabastidor universal para canaleta de 100 × 50 mm.",
        "caracteristicas": ("Formato universal", "Compatible con canaleta de 100 × 50 mm"),
        "especificaciones": (("Tipo", "Portabastidor universal", ""), ("Medida compatible", "100 × 50", "mm")),
        "variantes": (
            variante(
                "Universal · 100 × 50 mm",
                "100 × 50",
                "portabastidor-universal-100x50.png",
                (("Tipo", "Universal", ""),),
            ),
        ),
    },
)


class Command(BaseCommand):
    help = "Valida o carga canaletas PVC, accesorios y portabastidor."

    def add_arguments(self, parser):
        parser.add_argument("--aplicar", action="store_true")
        parser.add_argument("--no-publicar", action="store_true")

    def handle(self, *args, **options):
        rutas = {
            nombre
            for producto in PRODUCTOS
            for nombre in (
                producto["imagen"],
                *(item["imagen"] for item in producto["variantes"]),
            )
            if nombre
        }
        faltantes = [
            settings.MEDIA_ROOT / ruta
            for ruta in sorted(rutas)
            if not (settings.MEDIA_ROOT / ruta).is_file()
        ]
        if faltantes:
            detalle = "\n - ".join(str(ruta) for ruta in faltantes)
            raise CommandError(f"Faltan imágenes requeridas:\n - {detalle}")

        total_variantes = sum(len(item["variantes"]) for item in PRODUCTOS)
        self.stdout.write(
            f"Plan validado: {len(PRODUCTOS)} productos, "
            f"{total_variantes} variantes y {len(rutas)} imágenes."
        )
        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING("No se modificó el catálogo. Use --aplicar para cargarlo.")
            )
            return

        with transaction.atomic():
            familia, _ = Categoria.objects.update_or_create(
                slug="canalizacion-electrica",
                defaults={
                    "nombre": "Canalización eléctrica",
                    "padre": None,
                    "orden": 30,
                    "activa": True,
                },
            )
            categoria, _ = Categoria.objects.update_or_create(
                slug="canalizacion-pvc",
                defaults={
                    "nombre": "Canalización PVC",
                    "padre": familia,
                    "orden": 20,
                    "activa": True,
                },
            )

            productos_creados = 0
            variantes_creadas = 0
            for definicion in PRODUCTOS:
                producto, creado = Producto.objects.update_or_create(
                    slug=definicion["slug"],
                    defaults={
                        "categoria": categoria,
                        "nombre": definicion["nombre"],
                        "marca": "",
                        "marca_nueva": None,
                        "modelo": "",
                        "codigo": None,
                        "subtitulo": "Canalización PVC",
                        "descripcion": definicion["descripcion"],
                        "imagen": definicion["imagen"],
                        "texto_alternativo": definicion["nombre"],
                        "etiqueta_visual": "CANALIZACIÓN PVC",
                        "orden": definicion["orden"],
                        "publicado": not options["no_publicar"],
                    },
                )
                productos_creados += int(creado)

                caracteristicas = definicion["caracteristicas"]
                producto.caracteristicas.exclude(texto__in=caracteristicas).delete()
                for orden, texto in enumerate(caracteristicas, start=1):
                    CaracteristicaProducto.objects.update_or_create(
                        producto=producto,
                        texto=texto,
                        defaults={"orden": orden},
                    )

                especificaciones = definicion["especificaciones"]
                nombres_especificaciones = {nombre for nombre, _, _ in especificaciones}
                producto.especificaciones.exclude(
                    nombre__in=nombres_especificaciones
                ).delete()
                for orden, (nombre, valor, unidad) in enumerate(especificaciones, start=1):
                    EspecificacionProducto.objects.update_or_create(
                        producto=producto,
                        nombre=nombre,
                        defaults={"valor": valor, "unidad": unidad, "orden": orden},
                    )

                nombres_variantes = {item["nombre"] for item in definicion["variantes"]}
                retirar_variantes(producto.variantes.exclude(nombre__in=nombres_variantes))
                for orden, datos in enumerate(definicion["variantes"], start=1):
                    variante_obj, creada = VarianteProducto.objects.update_or_create(
                        producto=producto,
                        nombre=datos["nombre"],
                        defaults={
                            "modelo": "",
                            "codigo": None,
                            "imagen": datos["imagen"],
                            "disponible": True,
                            "orden": orden,
                        },
                    )
                    variantes_creadas += int(creada)
                    nombres = {nombre for nombre, _, _ in datos["especificaciones"]}
                    variante_obj.especificaciones.exclude(nombre__in=nombres).delete()
                    for posicion, (nombre, valor, unidad) in enumerate(
                        datos["especificaciones"], start=1
                    ):
                        EspecificacionVariante.objects.update_or_create(
                            variante=variante_obj,
                            nombre=nombre,
                            defaults={
                                "valor": valor,
                                "unidad": unidad,
                                "orden": posicion,
                            },
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Carga terminada: {productos_creados} productos y "
                f"{variantes_creadas} variantes creadas; "
                f"{len(PRODUCTOS) - productos_creados} productos y "
                f"{total_variantes - variantes_creadas} variantes actualizados."
            )
        )
