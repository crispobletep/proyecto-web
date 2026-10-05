from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import (
    Categoria, EspecificacionProducto, EspecificacionVariante,
    ImagenProducto, Marca, Producto, VarianteProducto,
)


AMPERAJES = (9, 12, 18, 25, 32)
SLUG = "contactores-stanford-220v"


class Command(BaseCommand):
    help = "Carga contactores Stanford de 220 V con cinco variantes y fotografías."

    def add_arguments(self, parser):
        parser.add_argument("--origen", type=Path, default=Path(settings.MEDIA_ROOT) / "productos/catalogo/contactores-stanford")
        parser.add_argument("--aplicar", action="store_true")

    def handle(self, *args, **options):
        origen = options["origen"].resolve()
        rutas = {a: origen / f"contactor-{a}a-220v.png" for a in AMPERAJES}
        for ruta in rutas.values():
            if not ruta.is_file():
                raise CommandError(f"Falta la imagen: {ruta}")
        for a in AMPERAJES:
            existente = VarianteProducto.objects.filter(codigo=f"STF-CONT-{a}A-220V").first()
            if existente and existente.producto.slug != SLUG:
                raise CommandError(f"El código {existente.codigo} ya pertenece a otro producto.")
        self.stdout.write("Plan validado: 1 producto, 5 variantes y 5 imágenes.")
        if not options["aplicar"]:
            return
        # Las imágenes se incluyen en el proyecto para poder repetir la carga.
        media = Path(settings.MEDIA_ROOT).resolve()
        try:
            imagenes = {a: ruta.relative_to(media).as_posix() for a, ruta in rutas.items()}
        except ValueError as exc:
            raise CommandError("El origen debe estar dentro de MEDIA_ROOT.") from exc
        with transaction.atomic():
            familia, _ = Categoria.objects.get_or_create(
                slug="control-senalizacion",
                defaults={"nombre": "Control y señalización", "orden": 3, "activa": True},
            )
            categoria, _ = Categoria.objects.get_or_create(
                slug="contactores",
                defaults={"nombre": "Contactores", "padre": familia, "orden": 4, "activa": True},
            )
            marca, _ = Marca.objects.get_or_create(slug="stanford", defaults={"nombre": "Stanford", "activa": True})
            producto, _ = Producto.objects.update_or_create(
                slug=SLUG,
                defaults={
                    "nombre": "Contactores Stanford 220 V", "categoria": categoria,
                    "marca_nueva": marca, "modelo": "KNC1", "subtitulo": "Control eléctrico · bobina de 220 V",
                    "descripcion": "Contactores Stanford con bobina de 220 V. Selecciona la corriente nominal de 9, 12, 18, 25 o 32 A para solicitar una cotización.",
                    "imagen": imagenes[9], "texto_alternativo": "Contactor Stanford de 9 A y 220 V",
                    "etiqueta_visual": "CONTROL ELÉCTRICO", "publicado": True, "orden": 170,
                },
            )
            EspecificacionProducto.objects.update_or_create(
                producto=producto, nombre="Tensión de bobina",
                defaults={"valor": "220", "unidad": "V", "orden": 1},
            )
            for orden, a in enumerate(AMPERAJES, 1):
                variante, _ = VarianteProducto.objects.update_or_create(
                    producto=producto, nombre=f"{a} A · 220 V",
                    defaults={"codigo": f"STF-CONT-{a}A-220V", "imagen": imagenes[a], "orden": orden, "disponible": True},
                )
                # La foto de 18 A lleva una etiqueta D12: no se infiere el modelo.
                for posicion, (nombre, valor, unidad) in enumerate((
                    ("Corriente nominal", str(a), "A"),
                    ("Tensión de bobina", "220", "V"),
                ), 1):
                    EspecificacionVariante.objects.update_or_create(
                        variante=variante, nombre=nombre,
                        defaults={"valor": valor, "unidad": unidad, "orden": posicion},
                    )
                imagen, _ = ImagenProducto.objects.update_or_create(
                    clave=f"stanford-contactor-{a}a-220v",
                    defaults={"producto": producto, "imagen": imagenes[a], "texto_alternativo": f"Contactor Stanford de {a} A y 220 V", "orden": orden},
                )
                imagen.variantes.set([variante])
        self.stdout.write(self.style.SUCCESS("Carga terminada: contactores publicados con sus cinco variantes."))
