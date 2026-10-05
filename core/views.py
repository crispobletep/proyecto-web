import logging

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
        pk__in=productos_catalogo.values_list("marca_nueva_id", flat=True)
    ).order_by("nombre")

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
