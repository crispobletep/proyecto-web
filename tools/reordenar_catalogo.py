"""Reordena las fichas y variantes del catálogo sin modificar el esquema."""

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django

django.setup()

from django.conf import settings
from django.db import connection, transaction
from core.models import Producto, VarianteProducto


def clave_natural(texto):
    normalizado = unicodedata.normalize("NFKD", texto or "").casefold()
    partes = re.split(r"(\d+(?:[,.]\d+)?)", normalizado)
    clave = []
    for parte in partes:
        if not parte:
            continue
        if re.fullmatch(r"\d+(?:[,.]\d+)?", parte):
            clave.append((0, Decimal(parte.replace(",", "."))))
        else:
            clave.append((1, parte))
    return tuple(clave)


def marca_producto(producto):
    marca = producto.marca_nueva.nombre if producto.marca_nueva_id else producto.marca
    return (marca or "\uffff").casefold()


def clave_marca(producto):
    marca = marca_producto(producto)
    if producto.categoria.slug in {"interruptores-automaticos", "interruptores-diferenciales"}:
        prioridad = {"lexo": 0, "legrand": 1}
        return (prioridad.get(marca, 2), marca)
    return (0, marca)


def clave_producto(producto):
    categoria = producto.categoria
    familia = categoria.padre
    if familia and familia.slug == "proteccion-electrica":
        return (
            familia.orden,
            0,
            clave_marca(producto),
            categoria.orden,
            clave_natural(categoria.nombre),
            clave_polos_producto(producto),
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "tableros-plasticos":
        calotas_kalop = (
            "kalop-calota-sp-2-puestos-transparente",
            "kalop-calota-sobrepuesta-2-modulos-ip20-sin-tapa",
            "kalop-calota-interior-1-4cc-tapa-transparente-gris",
            "kalop-calota-interior-1-6cc-tapa-transparente-gris",
            "kalop-caja-gris-ip55-tapa-2-modulos-2-puestos",
            "kalop-caja-gris-ip55-tapa-3-modulos-3-puestos",
        )
        if producto.slug in calotas_kalop:
            return (
                familia.orden if familia else categoria.orden,
                1,
                categoria.orden if familia else 0,
                clave_natural(categoria.nombre),
                2,
                calotas_kalop.index(producto.slug),
                clave_natural(producto.nombre),
                marca_producto(producto),
                producto.pk,
            )
        capacidad = re.search(
            r"\b(\d+)\s*(?:polos?|m[oó]dulos?|v[ií]as)\b",
            producto.nombre,
            re.IGNORECASE,
        )
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            1 if not capacidad else 0,
            int(capacidad.group(1)) if capacidad else 0,
            clave_natural(producto.nombre),
            marca_producto(producto),
            producto.pk,
        )
    if categoria.slug == "enchufes-horizontales":
        texto = producto.nombre.casefold()
        tipo = (
            0 if " simple " in f" {texto} "
            else 1 if " doble " in f" {texto} "
            else 2 if " triple " in f" {texto} "
            else 3
        )
        amperajes = re.search(r"(\d+)(?:\s*/\s*(\d+))?\s*a\b", texto)
        capacidad = (
            (int(amperajes.group(1)), int(amperajes.group(2) or amperajes.group(1)))
            if amperajes else (999, 999)
        )
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            tipo,
            capacidad,
            clave_natural(producto.nombre),
            marca_producto(producto),
            producto.pk,
        )
    if categoria.slug == "instrumentos-medicion":
        prioridad = {
            "amperimetro-tenaza-ut202-plus": 0,
            "amperimetro-tenaza-ut203-plus": 1,
            "detector-de-voltaje-ut12d": 2,
            "uni-t-tester-digital-ut33c-plus": 3,
            "uni-t-multimetro-profesional-nct-ut89x": 4,
            "uni-t-escaner-de-pared-ut387a": 5,
            "uni-t-luxometro-ut381a": 6,
            "uni-t-mini-luxometro-ut383": 7,
            "uni-t-telemetro-laser-lm50a": 8,
            "uni-t-telemetro-laser-lm70a": 9,
            "uni-t-telemetro-laser-lm600": 10,
        }
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            prioridad.get(producto.slug, 999),
            clave_natural(producto.nombre),
            marca_producto(producto),
            producto.pk,
        )
    if categoria.slug == "proyectores-area-led":
        nombre = producto.nombre.casefold()
        potencia = re.search(r"\b(\d+)\s*w\b", nombre)
        temperatura = (
            0 if "3000k" in nombre
            else 1 if "6500k" in nombre
            else 2
        )
        es_proyector_area = producto.slug.startswith("proyector-area-led-")
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            0 if es_proyector_area else 1,
            temperatura,
            int(potencia.group(1)) if potencia else 999,
            clave_natural(producto.nombre),
            marca_producto(producto),
            producto.pk,
        )
    if categoria.slug == "canoas-led":
        longitud = re.search(r"\b(\d+)\s*cm\b", producto.nombre, re.IGNORECASE)
        tipo = 0 if re.search(r"\bsimple\b", producto.nombre, re.IGNORECASE) else 1
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            int(longitud.group(1)) if longitud else 0,
            tipo,
            marca_producto(producto),
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "gabinetes-metalicos":
        dimensiones = re.search(
            r"\b(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*mm\b",
            producto.nombre,
            re.IGNORECASE,
        )
        configuracion = (
            1 if re.search(r"\bcon chasis\b", producto.nombre, re.IGNORECASE)
            else 0 if re.search(r"\best[aá]ndar\b", producto.nombre, re.IGNORECASE)
            else 0
        )
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            1 if not dimensiones else 0,
            tuple(int(dimensiones.group(indice)) for indice in (1, 2, 3)) if dimensiones else (0, 0, 0),
            configuracion,
            marca_producto(producto),
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "cajas-estancas":
        dimensiones = re.search(
            r"\b(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*mm\b",
            producto.nombre,
            re.IGNORECASE,
        )
        tipo_entrada = 1 if re.search(r"\bcon conos\b", producto.nombre, re.IGNORECASE) else 0
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            1 if not dimensiones else 0,
            tuple(int(dimensiones.group(indice)) for indice in (1, 2, 3)) if dimensiones else (0, 0, 0),
            tipo_entrada,
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "cajas-metalicas":
        dimensiones = re.search(
            r"\b(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*mm\b",
            producto.nombre,
            re.IGNORECASE,
        )
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            1 if not dimensiones else 0,
            tuple(int(dimensiones.group(indice)) for indice in (1, 2, 3)) if dimensiones else (0, 0, 0),
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "tableros-exterior":
        polos = re.search(r"\b(\d+)\s*polos\b", producto.nombre, re.IGNORECASE)
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            1 if not polos else 0,
            int(polos.group(1)) if polos else 0,
            clave_natural(producto.nombre),
            producto.pk,
        )
    if categoria.slug == "casquetes-industriales":
        if re.search(r"\bvolante\b", producto.nombre, re.IGNORECASE):
            tipo = 0
        elif re.search(r"\bsobrepuest[oa]\b", producto.nombre, re.IGNORECASE):
            tipo = 1
        else:
            tipo = 2
        genero = (
            0 if re.search(r"\bmacho\b", producto.nombre, re.IGNORECASE)
            else 1 if re.search(r"\bhembra\b", producto.nombre, re.IGNORECASE)
            else 2
        )
        return (
            familia.orden if familia else categoria.orden,
            1,
            categoria.orden if familia else 0,
            clave_natural(categoria.nombre),
            tipo,
            genero,
            clave_natural(producto.nombre),
            producto.pk,
        )
    return (
        familia.orden if familia else categoria.orden,
        1,
        categoria.orden if familia else 0,
        clave_natural(categoria.nombre),
        clave_polos_producto(producto),
        clave_natural(producto.nombre),
        marca_producto(producto),
        producto.pk,
    )


def clave_polos(nombre):
    coincidencia = re.search(r"\b(\d+)\s*(P)(\s*\+\s*N)?\b|\b(\d+)\s+polos?\b", nombre, re.IGNORECASE)
    if not coincidencia:
        return (1, 999, 0)
    cantidad = int(coincidencia.group(1) or coincidencia.group(4))
    con_neutro = bool(coincidencia.group(3))
    return (0, cantidad, int(con_neutro))


def clave_polos_producto(producto):
    claves = [clave_polos(producto.nombre)]
    claves.extend(clave_polos(variante.nombre) for variante in producto.variantes.all())
    return min(claves)


def crear_backup(productos, variantes):
    estado = {
        "database": connection.settings_dict["NAME"],
        "created_at": datetime.now().astimezone().isoformat(),
        "products": [{"id": item.pk, "slug": item.slug, "order": item.orden} for item in productos],
        "variants": [{"id": item.pk, "product_id": item.producto_id, "order": item.orden} for item in variantes],
    }
    ruta = Path(tempfile.gettempdir()) / (
        "proyecto-web-orden-catalogo-"
        + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        + ".json"
    )
    ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Guardar el nuevo orden en la base activa")
    args = parser.parse_args()

    if connection.vendor != "mysql":
        raise SystemExit("Se esperaba la conexión MySQL/MariaDB configurada para el catálogo.")

    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()[0]
    expected_database = settings.DATABASES["default"]["NAME"]
    if database != expected_database:
        raise SystemExit("La base conectada no coincide con la base configurada; no se aplicaron cambios.")

    productos = list(
        Producto.objects.select_related("categoria__padre", "marca_nueva")
        .prefetch_related("variantes").all()
    )
    variantes = list(VarianteProducto.objects.all())
    productos_ordenados = sorted(productos, key=clave_producto)
    orden_por_producto = {item.pk: posicion * 10 for posicion, item in enumerate(productos_ordenados, 1)}

    variantes_por_producto = {}
    for variante in variantes:
        variantes_por_producto.setdefault(variante.producto_id, []).append(variante)
    productos_por_id = {producto.pk: producto for producto in productos}

    def clave_variante(variante):
        producto = productos_por_id[variante.producto_id]
        if producto.categoria.slug == "casquetes-industriales":
            polos = re.search(r"\b(\d+)P", variante.nombre, re.IGNORECASE)
            corriente = re.search(r"\b(\d+)\s*A\b", variante.nombre, re.IGNORECASE)
            neutro = bool(re.search(r"\b\d+P\+N\+T\b", variante.nombre, re.IGNORECASE))
            if "sobrepuesta" in producto.slug or "sobrepuesto" in producto.slug:
                return (
                    0 if not corriente else int(corriente.group(1)),
                    0 if not polos else int(polos.group(1)),
                    int(neutro),
                    clave_natural(variante.nombre),
                    variante.pk,
                )
            return (
                0 if not polos else int(polos.group(1)),
                int(neutro),
                0 if not corriente else int(corriente.group(1)),
                clave_natural(variante.nombre),
                clave_natural(variante.modelo),
                variante.pk,
            )
        return (
            clave_natural(variante.nombre),
            clave_natural(variante.modelo),
            variante.pk,
        )

    variantes_ordenadas = []
    for grupo in variantes_por_producto.values():
        variantes_ordenadas.extend(sorted(grupo, key=clave_variante))
    orden_por_variante = {}
    anterior = None
    posicion = 0
    for variante in variantes_ordenadas:
        if variante.producto_id != anterior:
            anterior = variante.producto_id
            posicion = 0
        posicion += 1
        orden_por_variante[variante.pk] = posicion * 10

    cambios_producto = [
        item for item in productos_ordenados if item.orden != orden_por_producto[item.pk]
    ]
    cambios_variante = [
        item for item in variantes if item.orden != orden_por_variante[item.pk]
    ]
    print(f"Base confirmada: {database}")
    print(f"Fichas: {len(productos)}; fichas que cambian de orden: {len(cambios_producto)}")
    print(f"Variantes: {len(variantes)}; variantes que cambian de orden: {len(cambios_variante)}")
    print("Primeras fichas del nuevo catálogo:")
    for item in productos_ordenados[:20]:
        marca = item.marca_nueva.nombre if item.marca_nueva_id else item.marca
        print(f"  {orden_por_producto[item.pk]:>4} | {item.categoria.nombre} | {marca or 'Sin marca'} | {item.nombre}")

    if not args.apply:
        print("Vista previa solamente. Usa --apply para guardar los cambios.")
        return

    backup = crear_backup(productos, variantes)
    for item in productos_ordenados:
        item.orden = orden_por_producto[item.pk]
    for item in variantes:
        item.orden = orden_por_variante[item.pk]
    with transaction.atomic():
        Producto.objects.bulk_update(productos_ordenados, ["orden"], batch_size=500)
        VarianteProducto.objects.bulk_update(variantes, ["orden"], batch_size=500)
    print(f"Respaldo de órdenes anteriores: {backup}")
    print("Orden del catálogo actualizado.")


if __name__ == "__main__":
    main()
