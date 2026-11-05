import logging
import re

from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render
from django.urls import reverse

from .email_notifications import enviar_notificacion_cotizacion
from .forms import CotizacionForm, SERVICIOS

from .models import (
    Categoria,
    Marca,
    Producto,
    Proyecto,
    VarianteProducto,
)


logger = logging.getLogger(__name__)


def _unir_valores(valores):
    valores = [str(valor) for valor in valores]
    if len(valores) < 2:
        return valores[0] if valores else ""
    if len(valores) == 2:
        return " y ".join(valores)
    return f"{', '.join(valores[:-1])} y {valores[-1]}"


def _clave_especificacion(nombre, unidad=""):
    nombre_normalizado = " ".join(nombre.casefold().split())
    alias = {
        "número de polos": "polos",
        "configuración de polos": "polos",
        "polos": "polos",
        "curva de disparo": "curva de disparo",
        "capacidad de ruptura": "poder de corte",
        "poder de corte a 400 v": "poder de corte",
        "sección del conductor": "sección",
        "sección nominal": "sección",
        "diámetro nominal": "diámetro",
        "voltaje": "tensión nominal",
        "potencia nominal": "potencia",
        "color de señalización": "color",
        "color de senalizacion": "color",
        "color": "color",
    }
    return alias.get(nombre_normalizado, nombre_normalizado), (unidad or "").casefold()


def _normalizar_color(valor):
    nombre = " ".join(str(valor).casefold().split())
    colores = {
        "amarilla": "Amarillo", "amarillo": "Amarillo",
        "roja": "Rojo", "rojo": "Rojo",
        "blanca": "Blanco", "blanco": "Blanco",
        "negra": "Negro", "negro": "Negro",
        "azules": "Azul", "azul": "Azul",
        "verdes": "Verde", "verde": "Verde",
        "naranjas": "Naranja", "naranja": "Naranja",
        "grises": "Gris", "gris": "Gris",
        "violeta": "Violeta", "violetas": "Violeta",
        "morada": "Morado", "morado": "Morado",
        "marrón": "Marrón", "marrones": "Marrón",
        "café": "Café", "cafés": "Café",
        "transparentes": "Transparente", "transparente": "Transparente",
    }
    return colores.get(nombre, str(valor).strip())


def _atributos_variante(variante):
    atributos = [
        (
            item.nombre,
            _normalizar_color(item.valor)
            if _clave_especificacion(item.nombre, item.unidad)[0] == "color"
            else item.valor,
            item.unidad,
        )
        for item in variante.especificaciones.all()
    ]
    claves = {_clave_especificacion(nombre, unidad) for nombre, _, unidad in atributos}
    nombre = variante.nombre or ""
    patrones = (
        ("Color", r"\b(?:rojo|roja|rojos|rojas|verde|verdes|amarillo|amarilla|amarillos|amarillas|azul|azules|blanco|blanca|blancos|blancas|negro|negra|negros|negras|naranja|naranjas|gris|grises|violeta|violetas|morado|morada|marrón|marrones|café|cafés|transparente|transparentes)\b", ""),
        ("Configuración", r"\b(?:simple|doble)\b", ""),
        ("Tubos", r"\d+\s*[x×]\s*\d+(?:[.,]\d+)?\s*W\b", ""),
        ("Polos", r"(?<![\w])\d+P(?:\s*\+\s*N)?\b", ""),
        ("Corriente nominal", r"\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?\s*A\b", "A"),
        ("Curva de disparo", r"\bcurva\s+[A-Z]\b", ""),
        ("Poder de corte", r"\d+(?:[.,]\d+)?\s*kA\b", "kA"),
        ("Sensibilidad diferencial", r"\d+(?:[.,]\d+)?\s*mA\b", "mA"),
        ("Potencia", r"\d+(?:[.,]\d+)?\s*W\b", "W"),
        ("Flujo luminoso", r"\d+(?:[.,]\d+)?\s*lm\b", "lm"),
        ("Temperatura de color", r"\d{4,5}\s*K\b", "K"),
        ("Tensión nominal", r"\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?\s*V(?:\s*(?:AC|DC))?\b", "V"),
        ("Sección", r"\d+(?:[.,]\d+)?\s*mm(?:²|2)\b", "mm²"),
        ("Dimensiones", r"\d+(?:[.,]\d+)?\s*[x×]\s*\d+(?:[.,]\d+)?(?:\s*[x×]\s*\d+(?:[.,]\d+)?)?\s*mm\b", "mm"),
        ("Diámetro", r"\d+(?:[.,]\d+)?\s*mm\b", "mm"),
        ("Largo", r"\d+(?:[.,]\d+)?\s*cm\b", "cm"),
        ("Largo", r"\d+(?:[.,]\d+)?\s*m\b", "m"),
    )
    for etiqueta, patron, unidad in patrones:
        clave = _clave_especificacion(etiqueta, unidad)
        if etiqueta == "Diámetro" and any(nombre == "dimensiones" for nombre, _ in claves):
            continue
        if clave in claves:
            continue
        encontrados = re.findall(patron, nombre, flags=re.IGNORECASE)
        if not encontrados:
            continue
        if etiqueta == "Curva de disparo":
            valores = [re.search(r"[A-Z]", valor, re.IGNORECASE).group(0).upper() for valor in encontrados]
        elif etiqueta == "Color":
            valores = [_normalizar_color(valor) for valor in encontrados]
        elif etiqueta == "Configuración":
            valores = [valor.title() for valor in encontrados]
        elif etiqueta == "Tubos":
            valores = [re.match(r"\d+", valor).group(0) for valor in encontrados]
        else:
            valores = [
                re.sub(
                    r"\s*(?:kA|mA|A|W|lm|K|V(?:\s*(?:AC|DC))?|mm(?:²|2)?|cm|m)\s*$",
                    "",
                    " ".join(valor.split()).strip(),
                    flags=re.IGNORECASE,
                )
                for valor in encontrados
            ]
        atributos.append((etiqueta, valores[0], unidad))
        claves.add(clave)
        for valor in valores[1:]:
            atributos.append((etiqueta, valor, unidad))
    return atributos


def _grupos_de_variantes(variantes):
    grupos = {}
    for variante in variantes:
        for nombre, valor, unidad in _atributos_variante(variante):
            clave = _clave_especificacion(nombre, unidad)
            grupo = grupos.setdefault(clave, {"nombre": nombre, "unidad": unidad, "valores": []})
            if valor not in grupo["valores"]:
                grupo["valores"].append(valor)
    return grupos


def _resumen_variantes(producto, variantes, caracteristicas=()):
    grupos = _grupos_de_variantes(variantes)
    prioridad = (
        "color", "configuración", "tubos", "polos", "corriente nominal", "potencia",
        "flujo luminoso", "sección", "diámetro",
        "dimensiones", "grado de protección", "tensión nominal", "curva de disparo", "poder de corte",
        "sensibilidad diferencial", "temperatura de color", "largo",
    )
    orden = {nombre: indice for indice, nombre in enumerate(prioridad)}
    variables_detectadas = [
        (clave, grupo)
        for clave, grupo in grupos.items()
        if clave[0] in orden and len(grupo["valores"]) > 1
    ]
    elementos = []
    for clave, grupo in sorted(grupos.items(), key=lambda item: (orden.get(item[0][0], len(orden)), item[0][0])):
        nombre_clave = clave[0]
        if nombre_clave not in orden or len(grupo["valores"]) < 2:
            continue
        etiqueta = {
            "color": "Color",
            "configuración": "Formato",
            "tubos": "Tubos",
            "polos": "Polos",
            "corriente nominal": "Corriente",
            "potencia": "Potencia",
            "flujo luminoso": "Flujo luminoso",
            "sección": "Sección",
            "diámetro": "Diámetro",
            "dimensiones": "Medida",
            "grado de protección": "Protección IP",
            "tensión nominal": "Voltaje",
            "curva de disparo": "Curva",
            "poder de corte": "Poder de corte",
            "sensibilidad diferencial": "Sensibilidad",
            "temperatura de color": "Temperatura de color",
            "largo": "Largo",
        }.get(nombre_clave, grupo["nombre"])
        valor = _unir_valores(grupo["valores"])
        if grupo["unidad"]:
            valor = f"{valor} {grupo['unidad']}"
        if nombre_clave == "color" and len(variables_detectadas) == 1:
            return f"Colores disponibles: {valor}"
        elementos.append(f"{etiqueta}: {valor}")
    if elementos:
        return f"Opciones disponibles: {' · '.join(elementos)}"
    datos_fijos = [
        (clave, grupo)
        for clave, grupo in grupos.items()
        if clave[0] in orden and len(grupo["valores"]) == 1
    ]
    if datos_fijos:
        etiquetas = {
            "color": "Color", "configuración": "Formato", "tubos": "Tubos",
            "polos": "Polos", "corriente nominal": "Corriente", "potencia": "Potencia",
            "flujo luminoso": "Flujo luminoso", "sección": "Sección", "diámetro": "Diámetro",
            "dimensiones": "Medida", "grado de protección": "Protección IP",
            "tensión nominal": "Voltaje", "curva de disparo": "Curva",
            "poder de corte": "Poder de corte", "sensibilidad diferencial": "Sensibilidad",
            "temperatura de color": "Temperatura de color", "largo": "Largo",
        }
        detalles = []
        for clave, grupo in sorted(datos_fijos, key=lambda item: (orden[item[0][0]], item[0][0])):
            valor = grupo["valores"][0]
            if grupo["unidad"]:
                valor = f"{valor} {grupo['unidad']}"
            detalles.append(f"{etiquetas[clave[0]]}: {valor}")
        return f"Datos principales: {' · '.join(detalles)}"
    return _resumen_especificaciones(producto, caracteristicas)


def _resumen_especificaciones(producto, caracteristicas=()):
    prioridad = (
        "color", "polos", "corriente nominal", "tensión nominal", "curva de disparo",
        "poder de corte", "sensibilidad diferencial", "potencia", "sección",
        "diámetro", "dimensiones", "grado de protección", "largo",
    )
    etiqueta = {
        "color": "Color",
        "polos": "Polos",
        "corriente nominal": "Corriente",
        "tensión nominal": "Voltaje",
        "curva de disparo": "Curva",
        "poder de corte": "Poder de corte",
        "sensibilidad diferencial": "Sensibilidad",
        "potencia": "Potencia",
        "sección": "Sección",
        "diámetro": "Diámetro",
        "dimensiones": "Medida",
        "grado de protección": "Protección IP",
        "largo": "Largo",
    }
    especificaciones = []
    for item in producto.especificaciones.all():
        clave = _clave_especificacion(item.nombre, item.unidad)[0]
        if clave not in etiqueta:
            continue
        valor_completo = f"{item.valor}{(' ' + item.unidad) if item.unidad else ''}"
        if any(
            re.search(rf"(?<!\w){re.escape(valor_completo)}(?!\w)", caracteristica.texto, re.IGNORECASE)
            for caracteristica in caracteristicas
        ):
            continue
        especificaciones.append((clave, item.valor, item.unidad))
    if not especificaciones:
        return _resumen_nombre_producto(producto)
    orden = {nombre: indice for indice, nombre in enumerate(prioridad)}
    detalles = [
        f"{etiqueta[nombre]}: {valor}{(' ' + unidad) if unidad else ''}"
        for nombre, valor, unidad in sorted(especificaciones, key=lambda item: orden[item[0]])
    ]
    return f"Datos principales: {' · '.join(detalles)}"


def _resumen_nombre_producto(producto):
    nombre = producto.nombre or ""
    categoria = producto.categoria.slug
    if categoria == "cordones-electricos":
        coincidencia = re.search(
            r"\b(\d+)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*mm(?:²|2)\b",
            nombre,
            re.IGNORECASE,
        )
        if coincidencia:
            color = re.search(
                r"\b(negro|negra|rojo|roja|azul|verde|blanco|blanca|café|marrón)\b",
                nombre,
                re.IGNORECASE,
            )
            datos = [
                f"Conductores: {coincidencia.group(1)}",
                f"Sección: {coincidencia.group(2)} mm²",
            ]
            if color:
                datos.append(f"Color: {_normalizar_color(color.group(1))}")
            return f"Datos principales: {' · '.join(datos)}"
    if categoria == "tableros-plasticos":
        datos = []
        capacidad = re.search(
            r"\b(\d+)\s*(polos?|m[oó]dulos?|v[ií]as)\b",
            nombre,
            re.IGNORECASE,
        )
        if capacidad:
            unidad = capacidad.group(2).casefold()
            etiqueta = "Vías" if unidad.startswith("v") else "Capacidad"
            datos.append(f"{etiqueta}: {capacidad.group(1)} {unidad}")
        if re.search(r"\bsobrepuesto\b", nombre, re.IGNORECASE):
            datos.append("Montaje sobrepuesto")
        elif re.search(r"\bembutido\b", nombre, re.IGNORECASE):
            datos.append("Montaje embutido")
        if re.search(r"\bplástico\b", nombre, re.IGNORECASE):
            datos.append("Material plástico")
        if datos:
            return f"Datos principales: {' · '.join(datos)}"
    return ""


def _caracteristicas_mas_utiles(caracteristicas, cantidad=2):
    def relevancia(caracteristica):
        texto = caracteristica.texto.casefold()
        puntaje = sum(
            3 for palabra in (
                "protección", "sobrecarga", "cortocircuito", "curva", "corte",
                "ruptura", "sensibilidad", "polos", "corriente", "voltaje", "medida",
            ) if palabra in texto
        )
        puntaje -= sum(
            3 for palabra in (
                "montaje", "riel din", "aplicación", "residencial", "comercial",
                "botón de prueba", "formato compacto",
            ) if palabra in texto
        )
        return puntaje

    mejores = sorted(
        enumerate(caracteristicas),
        key=lambda item: (-relevancia(item[1]), item[0]),
    )[:cantidad]
    return [caracteristica for _, caracteristica in sorted(mejores)]


def _especificaciones_catalogo(producto):
    """Combina especificaciones comunes y rangos de las variantes visibles."""
    filas = [
        {"nombre": item.nombre, "valor": item.valor, "unidad": item.unidad}
        for item in producto.especificaciones.all()
        if not any(
            palabra in item.nombre.casefold()
            for palabra in ("referencia", "código", "codigo", "modelo")
        )
    ]
    indice = {
        _clave_especificacion(fila["nombre"], fila["unidad"]): fila
        for fila in filas
    }
    variantes = getattr(producto, "variantes_disponibles", [])
    for clave, grupo in _grupos_de_variantes(variantes).items():
        if clave[0] not in {
            "polos", "corriente nominal", "potencia", "sección", "diámetro",
            "dimensiones", "tensión nominal", "curva de disparo", "poder de corte",
            "sensibilidad diferencial", "temperatura de color", "largo", "color",
        }:
            continue
        nombre, unidad, valores = grupo["nombre"], grupo["unidad"], grupo["valores"]
        fila = indice.get(clave)
        if fila:
            fila["valor"] = _unir_valores(valores)
        else:
            fila = {
                "nombre": (
                    f"Opciones de {nombre.casefold()}"
                    if len(valores) > 1 else nombre
                ),
                "valor": _unir_valores(valores),
                "unidad": unidad,
            }
            filas.append(fila)
            indice[_clave_especificacion(nombre, unidad)] = fila

    nombres = [variante.nombre for variante in variantes if variante.nombre]
    if nombres:
        filas.append({
            "nombre": "Presentaciones disponibles",
            "valor": " · ".join(dict.fromkeys(nombres)),
            "unidad": "",
        })
    return filas


def identificador_valido(valor):
    """Aceptar únicamente IDs decimales dentro del rango de BigAutoField."""
    return (
        bool(valor) and len(valor) <= 19 and valor.isascii()
        and valor.isdecimal() and 0 < int(valor) <= 9223372036854775807
    )


def inicio(request):
    proyectos_destacados = list(
        Proyecto.objects.filter(publicado=True, destacado=True)[:4]
    )
    if len(proyectos_destacados) < 4:
        ids_destacados = [proyecto.pk for proyecto in proyectos_destacados]
        proyectos_destacados.extend(
            Proyecto.objects.filter(publicado=True)
            .exclude(pk__in=ids_destacados)[: 4 - len(proyectos_destacados)]
        )
    return render(
        request,
        "index.html",
        {
            "proyectos_destacados": proyectos_destacados,
            "proyecto_portada": (
                Proyecto.objects.filter(publicado=True, estado="finalizado")
                .exclude(imagen="").order_by("-destacado", "orden", "nombre").first()
                or Proyecto.objects.filter(publicado=True).exclude(imagen="").first()
            ),
        },
    )


def empresa(request):
    return render(request, "empresa.html")


def servicios(request):
    return render(request, "servicios.html")


def proyectos(request):
    proyectos_publicados = Proyecto.objects.filter(publicado=True)
    sectores_publicados = set(
        proyectos_publicados.values_list("sector", flat=True)
    )
    iconos = {
        "residencial": "▤",
        "hospitalario": "✚",
        "comercial": "▣",
        "industrial": "⚙",
        "infraestructura": "⌂",
    }
    sectores = [
        {
            "valor": valor,
            "nombre": nombre,
            "icono": iconos.get(valor, "▦"),
        }
        for valor, nombre in Proyecto.SECTORES
        if valor in sectores_publicados
    ]

    return render(
        request,
        "proyectos.html",
        {
            "proyectos": proyectos_publicados,
            "sectores": sectores,
        },
    )


def productos(request):
    familia_slug = request.GET.get("familia", "")
    categoria_slug = request.GET.get("categoria", "")
    busqueda = request.GET.get("q", "").strip()[:150]
    marca_id = request.GET.get("marca", "")
    if not identificador_valido(marca_id):
        marca_id = ""

    productos_catalogo = (
        Producto.objects
        .filter(
            publicado=True,
            categoria__activa=True,
            categoria__padre__activa=True,
        )
        .select_related(
            "categoria",
            "categoria__padre",
            "marca_nueva",
        )
        .prefetch_related(
            "caracteristicas",
            "especificaciones",
            "imagenes_catalogo",
            Prefetch(
                "variantes",
                queryset=(
                    VarianteProducto.objects
                    .filter(disponible=True)
                    .prefetch_related("especificaciones")
                ),
                to_attr="variantes_disponibles",
            ),
        )
    )

    # Las opciones permanecen estables al combinar o cambiar filtros.
    marcas = Marca.objects.filter(
        Q(pk__in=productos_catalogo.values_list("marca_nueva_id", flat=True))
        | Q(slug="megabright")
    ).exclude(slug="3m").order_by("nombre")
    if marca_id and not marcas.filter(pk=marca_id).exists():
        marca_id = ""

    if busqueda:
        productos_catalogo = productos_catalogo.filter(
            Q(nombre__icontains=busqueda) | Q(codigo__icontains=busqueda)
            | Q(modelo__icontains=busqueda)
            | Q(variantes__codigo__icontains=busqueda)
        ).distinct()
    if categoria_slug:
        productos_catalogo = productos_catalogo.filter(
            categoria__slug=categoria_slug,
        )

    elif familia_slug:
        productos_catalogo = productos_catalogo.filter(
            Q(categoria__padre__slug=familia_slug)
            | Q(categoria__slug=familia_slug)
        )

    if marca_id:
        productos_catalogo = productos_catalogo.filter(marca_nueva_id=marca_id)

    familias = (
        Categoria.objects
        .filter(
            padre__isnull=True,
            activa=True,
        )
        .prefetch_related("subcategorias")
    )

    paginador = Paginator(productos_catalogo, 8)
    pagina_productos = paginador.get_page(request.GET.get("pagina"))
    for producto in pagina_productos.object_list:
        caracteristicas = list(producto.caracteristicas.all())
        caracteristicas_utiles = _caracteristicas_mas_utiles(caracteristicas)
        resumen_variantes = _resumen_variantes(
            producto, producto.variantes_disponibles, caracteristicas_utiles
        )
        producto.caracteristicas_catalogo = (
            caracteristicas_utiles if resumen_variantes else caracteristicas[:3]
        )
        producto.resumen_caracteristicas = resumen_variantes
        producto.especificaciones_catalogo = _especificaciones_catalogo(producto)

    parametros_paginacion = request.GET.copy()
    parametros_paginacion.pop("pagina", None)

    contexto = {
        "productos": pagina_productos,
        "pagina_productos": pagina_productos,
        "parametros_paginacion": parametros_paginacion.urlencode(),
        "familias": familias,
        "familia_activa": familia_slug,
        "categoria_activa": categoria_slug,
        "busqueda": busqueda,
        "marcas": marcas,
        "marca_activa": marca_id,
    }

    return render(
        request,
        "productos.html",
        contexto,
    )


def contacto(request):
    enviado = request.GET.get("enviado") == "1"
    producto_seleccionado = None
    proyecto_seleccionado = None
    variante_seleccionada = None

    if request.method == "POST":
        producto_id = request.POST.get("producto_id", "").strip()
        proyecto_id = request.POST.get("proyecto_id", "").strip()
        variante_id = request.POST.get("variante_id", "").strip()

        if identificador_valido(producto_id):
            producto_seleccionado = (
                Producto.objects
                .filter(
                    pk=producto_id,
                    publicado=True,
                    categoria__activa=True,
                    categoria__padre__activa=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if identificador_valido(proyecto_id) and not producto_seleccionado:
            proyecto_seleccionado = Proyecto.objects.filter(
                pk=proyecto_id,
                publicado=True,
            ).first()

        if identificador_valido(variante_id) and producto_seleccionado:
            variante_seleccionada = (
                VarianteProducto.objects
                .filter(
                    pk=variante_id,
                    producto=producto_seleccionado,
                    disponible=True,
                )
                .first()
            )

    else:
        producto_slug = request.GET.get("producto", "").strip()
        proyecto_slug = request.GET.get("proyecto", "").strip()
        variante_id = request.GET.get("variante", "").strip()

        if producto_slug:
            producto_seleccionado = (
                Producto.objects
                .filter(
                    slug=producto_slug,
                    publicado=True,
                    categoria__activa=True,
                    categoria__padre__activa=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if proyecto_slug and not producto_seleccionado:
            proyecto_seleccionado = Proyecto.objects.filter(
                slug=proyecto_slug,
                publicado=True,
            ).first()

        if identificador_valido(variante_id) and producto_seleccionado:
            variante_seleccionada = (
                VarianteProducto.objects
                .filter(
                    pk=variante_id,
                    producto=producto_seleccionado,
                    disponible=True,
                )
                .first()
            )

    mensaje_sugerido = ""

    if producto_seleccionado:
        mensaje_sugerido = (
            f"Solicito una cotización para "
            f"{producto_seleccionado.nombre}"
        )

        if variante_seleccionada:
            mensaje_sugerido += (
                f", variante {variante_seleccionada.nombre}"
            )

        mensaje_sugerido += (
            ". Agradezco indicar disponibilidad, plazo de entrega y "
            "condiciones comerciales."
        )

    elif proyecto_seleccionado:
        mensaje_sugerido = (
            "Solicito una cotización para desarrollar un proyecto similar a "
            f"{proyecto_seleccionado.nombre}. Agradezco indicar los "
            "antecedentes necesarios para preparar una propuesta."
        )

    valores_servicio = {valor for valor, _ in SERVICIOS if valor}
    servicio_solicitado = request.GET.get("servicio", "").strip()
    if servicio_solicitado not in valores_servicio:
        servicio_solicitado = ""

    inicial = {
        "servicio": (
            "Productos"
            if producto_seleccionado
            else (
                "Proyecto especial / Otro"
                if proyecto_seleccionado
                else servicio_solicitado
            )
        ),
        "mensaje": mensaje_sugerido,
    }
    formulario = CotizacionForm(request.POST if request.method == "POST" else None, initial=inicial)

    if request.method == "POST" and formulario.is_valid():
        cotizacion = formulario.save(commit=False)
        cotizacion.producto = producto_seleccionado
        cotizacion.proyecto = proyecto_seleccionado
        cotizacion.variante = variante_seleccionada
        cotizacion.save()

        try:
            enviar_notificacion_cotizacion(cotizacion)
        except Exception:
            # La solicitud ya quedó resguardada en la base de datos. Un fallo
            # temporal del proveedor de correo no debe hacer que el cliente la
            # envíe nuevamente y genere registros duplicados.
            logger.exception(
                "No se pudo enviar la notificación de la cotización %s",
                cotizacion.pk,
            )

        return redirect(f"{reverse('contacto')}?enviado=1")

    contexto = {
        "enviado": enviado,
        "formulario": formulario,
        "producto_seleccionado": producto_seleccionado,
        "proyecto_seleccionado": proyecto_seleccionado,
        "variante_seleccionada": variante_seleccionada,
    }

    return render(
        request,
        "contacto.html",
        contexto,
    )
