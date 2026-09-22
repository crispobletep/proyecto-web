from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CotizacionForm, SERVICIOS

from .models import (
    Categoria,
    Producto,
    VarianteProducto,
)


def inicio(request):
    return render(request, "index.html")


def empresa(request):
    return render(request, "empresa.html")


def servicios(request):
    return render(request, "servicios.html")


def proyectos(request):
    return render(request, "proyectos.html")


def productos(request):
    familia_slug = request.GET.get("familia", "")
    categoria_slug = request.GET.get("categoria", "")

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

    if categoria_slug:
        productos_catalogo = productos_catalogo.filter(
            categoria__slug=categoria_slug,
        )

    elif familia_slug:
        productos_catalogo = productos_catalogo.filter(
            Q(categoria__padre__slug=familia_slug)
            | Q(categoria__slug=familia_slug)
        )

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
    }

    return render(
        request,
        "productos.html",
        contexto,
    )


def contacto(request):
    enviado = request.GET.get("enviado") == "1"
    producto_seleccionado = None
    variante_seleccionada = None

    if request.method == "POST":
        producto_id = request.POST.get("producto_id", "").strip()
        variante_id = request.POST.get("variante_id", "").strip()

        if producto_id.isdigit():
            producto_seleccionado = (
                Producto.objects
                .filter(
                    pk=producto_id,
                    publicado=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if variante_id.isdigit() and producto_seleccionado:
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
        variante_id = request.GET.get("variante", "").strip()

        if producto_slug:
            producto_seleccionado = (
                Producto.objects
                .filter(
                    slug=producto_slug,
                    publicado=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if variante_id.isdigit() and producto_seleccionado:
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

        mensaje_sugerido += "."

    valores_servicio = {valor for valor, _ in SERVICIOS if valor}
    servicio_solicitado = request.GET.get("servicio", "").strip()
    if servicio_solicitado not in valores_servicio:
        servicio_solicitado = ""

    inicial = {
        "servicio": "Productos" if producto_seleccionado else servicio_solicitado,
        "mensaje": mensaje_sugerido,
    }
    formulario = CotizacionForm(request.POST or None, initial=inicial)

    if request.method == "POST" and formulario.is_valid():
        cotizacion = formulario.save(commit=False)
        cotizacion.producto = producto_seleccionado
        cotizacion.variante = variante_seleccionada
        cotizacion.save()

        return redirect(f"{reverse('contacto')}?enviado=1")

    contexto = {
        "enviado": enviado,
        "formulario": formulario,
        "producto_seleccionado": producto_seleccionado,
        "variante_seleccionada": variante_seleccionada,
    }

    return render(
        request,
        "contacto.html",
        contexto,
    )
