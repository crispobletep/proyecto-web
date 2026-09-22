"""Extrae imágenes individuales desde las láminas maestras del catálogo.

El script no crea productos ni modifica la base de datos. Genera fotografías
cuadradas, un manifiesto CSV y hojas de contacto para revisión visual.
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


FUENTES = {
    "led": "Imagen_de_Codex_13_sept_2026_05_16_29_p.m._1.png",
    "canalizacion": "Imagen_de_Codex_13_sept_2026_05_14_02_p.m..png",
    "staford": "Imagen_de_Codex_13_sept_2026_05_11_03_p.m._1.png",
    "varios": "Imagen_de_Codex_13_sept_2026_05_20_35_p.m..png",
}


@dataclass(frozen=True)
class Recurso:
    familia: str
    archivo: str
    titulo: str
    fuente: str
    caja: tuple[int, int, int, int]
    codigos: tuple[str, ...]
    uso: str = "principal"


def codigos_led(prefijo, medida, montaje):
    sufijo = "E" if montaje == "emb" else "S"
    return tuple(
        f"{prefijo}-{medida}-{potencia}{sufijo}"
        for potencia in (6, 12, 18, 24)
    )


def recursos_led():
    recursos = []
    marcas = (
        ("avc", "AVC", (143, 229)),
        ("fls", "FLS", (422, 506)),
        ("yellmax", "YLM", (703, 785)),
    )
    presentaciones = (
        ("6060", "60 x 60 cm embutido", "emb", (276, 451)),
        ("6060", "60 x 60 cm sobrepuesto", "sp", (475, 637)),
        ("12030", "120 x 30 cm embutido", "emb", (675, 876)),
        ("12030", "120 x 30 cm sobrepuesto", "sp", (886, 1073)),
        ("12060", "120 x 60 cm embutido", "emb", (1101, 1296)),
        ("12060", "120 x 60 cm sobrepuesto", "sp", (1310, 1515)),
    )

    for marca_slug, prefijo, (y1, y2) in marcas:
        for medida, titulo, montaje, (x1, x2) in presentaciones:
            recursos.append(
                Recurso(
                    familia="plafones-led",
                    archivo=f"{marca_slug}-{medida}-{montaje}.png",
                    titulo=f"{prefijo} {titulo}",
                    fuente="led",
                    caja=(x1, y1, x2, y2),
                    codigos=codigos_led(prefijo, medida, montaje),
                )
            )

    return recursos


def recursos_canalizacion():
    medidas_emt = (20, 25, 32)
    medidas_pvc = (16, 20, 25, 32, 40, 50)
    medidas_flex = (20, 25, 32)

    definiciones = (
        ("tuberia-emt", "Tubería EMT metálica", "EMT", medidas_emt, (10, 160, 301, 280)),
        ("curva-emt-90", "Curva EMT 90°", "CEMT", medidas_emt, (326, 142, 536, 261)),
        ("curva-emt-45", "Curva EMT 45°", "CEMT45", medidas_emt, (560, 142, 771, 261)),
        ("copla-emt", "Copla EMT", "CPL", medidas_emt, (817, 157, 1002, 261)),
        ("terminal-emt", "Terminal EMT", "TEMT", medidas_emt, (1057, 141, 1247, 261)),
        ("salida-caja-emt", "Salida a caja EMT", "SEMT", medidas_emt, (1311, 140, 1502, 261)),
        ("tuberia-pvc", "Tubería PVC eléctrica", "PVC", medidas_pvc, (10, 438, 323, 536)),
        ("curva-pvc-90", "Curva PVC 90°", "CPVC", medidas_pvc, (365, 419, 548, 535)),
        ("curva-pvc-45", "Curva PVC 45°", "CPVC45", medidas_pvc, (594, 420, 774, 535)),
        ("copla-pvc", "Copla PVC", "CP", medidas_pvc, (842, 428, 1008, 535)),
        ("terminal-pvc", "Terminal PVC", "TPVC", medidas_pvc, (1095, 414, 1249, 535)),
        ("salida-caja-pvc", "Salida a caja PVC", "SPVC", medidas_pvc, (1331, 420, 1505, 535)),
        ("flexible-metalico", "Flexible metálico", "FLEX", medidas_flex, (11, 752, 351, 850)),
        ("conector-recto-flex", "Conector recto flexible", "CMF", medidas_flex, (383, 738, 526, 838)),
        ("adaptador-caja-flex", "Adaptador a caja flexible", "AMF", medidas_flex, (568, 738, 707, 838)),
        ("conector-curvo-flex", "Conector curvo 90°", "CMF90", medidas_flex, (746, 744, 890, 838)),
        ("flexible-libre-halogeno", "Flexible libre de halógeno", "HLF", medidas_flex, (923, 754, 1185, 849)),
        ("conector-libre-halogeno", "Conector libre de halógeno", "CHL", medidas_flex, (1221, 746, 1349, 838)),
        ("adaptador-libre-halogeno", "Adaptador libre de halógeno", "AHL", medidas_flex, (1384, 746, 1514, 838)),
    )

    return [
        Recurso(
            familia="canalizacion-electrica",
            archivo=f"{slug}.png",
            titulo=titulo,
            fuente="canalizacion",
            caja=caja,
            codigos=tuple(f"{prefijo}-{medida}" for medida in medidas),
        )
        for slug, titulo, prefijo, medidas, caja in definiciones
    ]


def recursos_staford():
    recursos = []
    colores = (
        ("blanco", "BL"),
        ("negro", "NE"),
        ("champagne", "CH"),
        ("cafe", "CA"),
    )
    columnas = {
        "simple": ((16, 124), (142, 250), (270, 378), (398, 506)),
        "doble": ((528, 636), (655, 763), (783, 891), (910, 1018)),
        "triple": ((1040, 1148), (1168, 1276), (1297, 1405), (1424, 1532)),
    }

    for indice, (color, sufijo) in enumerate(colores):
        for tipo, prefijo, etiqueta in (
            ("simple", "ES", "Enchufe simple"),
            ("doble", "ED", "Enchufe doble"),
            ("triple", "ET", "Enchufe triple"),
        ):
            x1, x2 = columnas[tipo][indice]
            recursos.append(
                Recurso(
                    familia="staford-enchufes",
                    archivo=f"staford-{tipo}-10a-{color}.png",
                    titulo=f"{etiqueta} 10 A {color}",
                    fuente="staford",
                    caja=(x1, 174, x2, 305),
                    codigos=(f"STF-{prefijo}-10A-{sufijo}",),
                )
            )

        for tipo, prefijo, etiqueta in (
            ("simple", "ES", "Enchufe simple"),
            ("doble", "ED", "Enchufe doble"),
        ):
            x1, x2 = columnas[tipo][indice]
            recursos.append(
                Recurso(
                    familia="staford-enchufes",
                    archivo=f"staford-{tipo}-10-16a-{color}.png",
                    titulo=f"{etiqueta} 10/16 A {color}",
                    fuente="staford",
                    caja=(x1, 397, x2, 514),
                    codigos=(f"STF-{prefijo}-10/16-{sufijo}",),
                )
            )

    recursos.append(
        Recurso(
            familia="staford-enchufes",
            archivo="staford-triple-10-16a-blanco.png",
            titulo="Enchufe triple 10/16 A blanco",
            fuente="staford",
            caja=(1040, 397, 1148, 514),
            codigos=("STF-ET-10/16-BL",),
        )
    )

    modulos = (
        ("tapa-ciega", "Tapa ciega", "STF-MC", (20, 672, 102, 808)),
        ("tv-coaxial", "Módulo TV coaxial", "STF-MTV", (126, 672, 208, 808)),
        ("telefono-rj11", "Módulo teléfono RJ11", "STF-MTEL", (234, 672, 316, 808)),
        ("datos-rj45", "Módulo datos RJ45", "STF-MDAT", (341, 672, 423, 808)),
    )
    for slug, titulo, codigo, caja in modulos:
        recursos.append(
            Recurso(
                familia="staford-modulos",
                archivo=f"staford-{slug}.png",
                titulo=titulo,
                fuente="staford",
                caja=caja,
                codigos=(codigo,),
            )
        )

    columnas_placas = ((466, 541), (587, 664), (711, 789), (835, 914))
    filas_placas = ((646, 682), (736, 777), (827, 871))
    for puestos, (y1, y2) in enumerate(filas_placas, start=1):
        for indice, (color, sufijo) in enumerate(colores):
            x1, x2 = columnas_placas[indice]
            recursos.append(
                Recurso(
                    familia="staford-placas",
                    archivo=f"staford-placa-{puestos}p-{color}.png",
                    titulo=f"Placa Staford {puestos} puesto(s) {color}",
                    fuente="staford",
                    caja=(x1, y1, x2, y2),
                    codigos=(f"STF-P{puestos}-{sufijo}",),
                )
            )

    return recursos


def recursos_varios():
    recursos = []
    fotoceldas = (
        ("lexo", "Fotocelda LEXO", "LEX-FC01", (30, 143, 138, 263)),
        ("legrand", "Fotocelda Legrand", "LEG-412898", (177, 143, 285, 263)),
        ("chint", "Fotocelda CHINT", "CHT-NY01", (326, 143, 434, 263)),
        ("staford", "Fotocelda Staford", "STF-FC10", (473, 143, 581, 263)),
    )
    bases = (
        ("lexo", "Base para fotocelda LEXO", "LEX-BF01", (621, 143, 731, 263)),
        ("legrand", "Base para fotocelda Legrand", "LEG-412899", (770, 143, 879, 263)),
        ("chint", "Base para fotocelda CHINT", "CHT-BY01", (917, 143, 1027, 263)),
        ("staford", "Base para fotocelda Staford", "STF-BF10", (1065, 143, 1177, 263)),
    )
    accesorios_fotocelda = (
        ("soporte-metalico", "Soporte metálico para fotocelda", "SOP-FC01", (1217, 143, 1348, 263)),
        ("soporte-muro-poste", "Soporte muro/poste ajustable", "SOP-FC02", (1377, 143, 1514, 263)),
    )
    for slug, titulo, codigo, caja in fotoceldas + bases + accesorios_fotocelda:
        recursos.append(
            Recurso(
                familia="fotoceldas",
                archivo=f"{slug}-{codigo.lower()}.png",
                titulo=titulo,
                fuente="varios",
                caja=caja,
                codigos=(codigo,),
            )
        )

    casquetes = (
        ("2p", "Casquete Kalop 2 polos", "KAL-2P", (24, 493, 124, 589)),
        ("3p", "Casquete Kalop 3 polos", "KAL-3P", (153, 493, 253, 589)),
        ("4p", "Casquete Kalop 4 polos", "KAL-4P", (283, 493, 383, 589)),
        ("6p", "Casquete Kalop 6 polos", "KAL-6P", (413, 493, 513, 589)),
    )
    modulos = (
        ("2p", "Módulo Kalop 2 polos", "KAL-MOD-2P", (548, 493, 645, 589)),
        ("3p", "Módulo Kalop 3 polos", "KAL-MOD-3P", (678, 493, 775, 589)),
        ("4p", "Módulo Kalop 4 polos", "KAL-MOD-4P", (808, 493, 905, 589)),
        ("6p", "Módulo Kalop 6 polos", "KAL-MOD-6P", (938, 493, 1035, 589)),
    )
    accesorios_kalop = (
        ("base-superficie", "Base de superficie Kalop", "KAL-BS", (1070, 493, 1186, 589)),
        ("base-inclinada", "Base inclinada Kalop", "KAL-BI", (1227, 493, 1344, 589)),
        ("base-empotrable", "Base empotrable Kalop", "KAL-BE", (1384, 493, 1503, 589)),
    )
    for slug, titulo, codigo, caja in casquetes:
        recursos.append(
            Recurso("kalop-casquetes", f"kalop-casquete-{slug}.png", titulo, "varios", caja, (codigo,))
        )
    for slug, titulo, codigo, caja in modulos:
        recursos.append(
            Recurso("kalop-modulos", f"kalop-modulo-{slug}.png", titulo, "varios", caja, (codigo,))
        )
    for slug, titulo, codigo, caja in accesorios_kalop:
        recursos.append(
            Recurso("kalop-accesorios", f"kalop-{slug}.png", titulo, "varios", caja, (codigo,))
        )

    codigos_cnc = tuple(
        f"CNC-TB-{polos}P" for polos in (2, 4, 6, 8, 12, 16, 18, 24)
    )
    recursos.extend(
        (
            Recurso(
                "tableros-cnc",
                "cnc-tablero-exterior-cerrado.png",
                "Tablero exterior CNC IP65 cerrado",
                "varios",
                (24, 787, 216, 986),
                codigos_cnc,
            ),
            Recurso(
                "tableros-cnc",
                "cnc-tablero-exterior-abierto.png",
                "Tablero exterior CNC IP65 abierto",
                "varios",
                (218, 787, 454, 986),
                codigos_cnc,
                uso="secundaria",
            ),
        )
    )

    return recursos


RECURSOS = tuple(
    recursos_led()
    + recursos_canalizacion()
    + recursos_staford()
    + recursos_varios()
)


def normalizar_recorte(imagen, caja, lado=900):
    recorte = imagen.crop(caja).convert("RGB")
    recorte = ImageOps.contain(recorte, (lado - 100, lado - 100), Image.Resampling.LANCZOS)
    lienzo = Image.new("RGB", (lado, lado), "white")
    posicion = ((lado - recorte.width) // 2, (lado - recorte.height) // 2)
    lienzo.paste(recorte, posicion)
    return lienzo


def crear_previsualizaciones(recursos, salida):
    fuente = ImageFont.load_default()
    carpeta = salida / "_previsualizaciones"
    carpeta.mkdir(parents=True, exist_ok=True)

    for familia in sorted({recurso.familia for recurso in recursos}):
        elementos = [r for r in recursos if r.familia == familia]
        columnas = 4
        ancho_celda = 240
        alto_celda = 280
        filas = (len(elementos) + columnas - 1) // columnas
        hoja = Image.new("RGB", (columnas * ancho_celda, filas * alto_celda), "#eef2f6")
        dibujo = ImageDraw.Draw(hoja)

        for indice, recurso in enumerate(elementos):
            fila, columna = divmod(indice, columnas)
            x = columna * ancho_celda
            y = fila * alto_celda
            imagen = Image.open(salida / recurso.familia / recurso.archivo).convert("RGB")
            imagen.thumbnail((210, 210), Image.Resampling.LANCZOS)
            hoja.paste(imagen, (x + 15, y + 10))
            dibujo.text(
                (x + 12, y + 226),
                recurso.archivo[:34],
                fill="#102c50",
                font=fuente,
            )
            dibujo.text(
                (x + 12, y + 244),
                ", ".join(recurso.codigos)[:36],
                fill="#52657d",
                font=fuente,
            )

        hoja.save(carpeta / f"{familia}.jpg", quality=88, optimize=True)


def ejecutar(origen, salida, forzar=False):
    imagenes = {}
    for clave, nombre in FUENTES.items():
        ruta = origen / nombre
        if not ruta.is_file():
            raise FileNotFoundError(f"No se encontró la lámina: {ruta}")
        imagenes[clave] = Image.open(ruta).convert("RGB")

    salida.mkdir(parents=True, exist_ok=True)
    creados = 0
    omitidos = 0

    for recurso in RECURSOS:
        carpeta = salida / recurso.familia
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / recurso.archivo
        if destino.exists() and not forzar:
            omitidos += 1
            continue

        normalizar_recorte(imagenes[recurso.fuente], recurso.caja).save(
            destino,
            optimize=True,
        )
        creados += 1

    with (salida / "manifesto_imagenes.csv").open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=(
                "familia",
                "titulo",
                "archivo",
                "codigos",
                "uso",
                "lamina_fuente",
            ),
        )
        escritor.writeheader()
        for recurso in RECURSOS:
            escritor.writerow(
                {
                    "familia": recurso.familia,
                    "titulo": recurso.titulo,
                    "archivo": f"{recurso.familia}/{recurso.archivo}",
                    "codigos": " | ".join(recurso.codigos),
                    "uso": recurso.uso,
                    "lamina_fuente": FUENTES[recurso.fuente],
                }
            )

    crear_previsualizaciones(RECURSOS, salida)
    return creados, omitidos


def main():
    raiz_proyecto = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--origen",
        type=Path,
        default=Path.home() / "Downloads",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=raiz_proyecto / "media" / "productos" / "extraidos",
    )
    parser.add_argument("--forzar", action="store_true")
    opciones = parser.parse_args()

    creados, omitidos = ejecutar(
        opciones.origen.resolve(),
        opciones.salida.resolve(),
        opciones.forzar,
    )
    print(f"Recursos definidos: {len(RECURSOS)}")
    print(f"Imágenes creadas: {creados}")
    print(f"Imágenes existentes omitidas: {omitidos}")
    print(f"Salida: {opciones.salida.resolve()}")


if __name__ == "__main__":
    main()
